"""
Evaluation Service - Optimized for batch processing
Handles answer and quiz evaluation with parallel processing and intelligent caching.
"""

import os
import asyncio
import hashlib
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging

# Import shared modules
import sys
sys.path.append('/app/shared')

from database.config import db_manager, get_async_db_session
from database.models import Evaluation, Question, PDF, PDFExtractedText, QuizSession
from cache.redis_config import redis_manager, evaluation_cache
from ai.api_key_manager import get_api_key, record_api_request

# Celery for background processing
from celery import Celery
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
celery_app = Celery(
    "evaluation_service",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/3"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/4")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=20 * 60,  # 20 minutes max
    task_soft_time_limit=15 * 60,  # 15 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Evaluation Service...")
    yield
    logger.info("Shutting down Evaluation Service...")
    await redis_manager.close()

app = FastAPI(
    title="Evaluation Service",
    version="2.0.0",
    description="High-performance answer evaluation with batch processing",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class AnswerEvaluationRequest(BaseModel):
    question_id: str
    question: str
    user_answer: str
    evaluation_level: str = "medium"  # easy, medium, strict
    user_id: str

class AnswerEvaluationResponse(BaseModel):
    question_id: str
    score: int
    max_score: int = 10
    feedback: str
    suggestions: str
    correct_answer_hint: Optional[str] = None

class QuizAnswer(BaseModel):
    question_id: str
    question: str
    user_answer: str
    question_type: str = "open_ended"
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None

class QuizSubmissionRequest(BaseModel):
    answers: List[QuizAnswer]
    topic: Optional[str] = None
    evaluation_level: str = "medium"
    user_id: str
    pdf_id: str

class QuizSubmissionResponse(BaseModel):
    overall_score: int
    max_score: int
    percentage: float
    grade: str
    individual_results: List[AnswerEvaluationResponse]
    overall_feedback: str
    study_suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]

# Utility functions
def generate_answer_hash(question: str, answer: str) -> str:
    """Generate hash for answer caching"""
    content = f"{question.strip().lower()}:{answer.strip().lower()}"
    return hashlib.md5(content.encode()).hexdigest()

def chunk_answers(answers: List[QuizAnswer], chunk_size: int = 5) -> List[List[QuizAnswer]]:
    """Split answers into chunks for batch processing"""
    chunks = []
    for i in range(0, len(answers), chunk_size):
        chunks.append(answers[i:i + chunk_size])
    return chunks

async def evaluate_mcq_answer(answer: QuizAnswer) -> AnswerEvaluationResponse:
    """Fast evaluation for MCQ questions"""
    user_answer_clean = answer.user_answer.strip().upper()
    correct_answer_clean = answer.correct_answer.strip().upper() if answer.correct_answer else ""
    
    # Binary scoring for MCQ
    if user_answer_clean == correct_answer_clean:
        score = 10
        feedback = f"✅ Correct! You selected the right answer."
        suggestions = "Great job! Continue studying to maintain this level of understanding."
    elif not answer.user_answer or answer.user_answer.strip() == "":
        score = 0
        feedback = f"❌ No answer was provided for this question."
        suggestions = "Please provide an answer based on the document content to receive a score."
    else:
        score = 0
        feedback = f"❌ Incorrect. The correct answer is '{correct_answer_clean}'."
        suggestions = "Review the relevant section in the document to understand the correct answer."
    
    return AnswerEvaluationResponse(
        question_id=answer.question_id,
        score=score,
        feedback=feedback,
        suggestions=suggestions
    )

async def evaluate_answers_batch(
    answers: List[QuizAnswer],
    pdf_content: str,
    filename: str,
    evaluation_level: str
) -> List[AnswerEvaluationResponse]:
    """Evaluate multiple answers in a single AI request for efficiency"""
    
    # Separate MCQ and open-ended questions
    mcq_answers = [a for a in answers if a.question_type == "mcq" and a.correct_answer]
    open_ended_answers = [a for a in answers if a.question_type != "mcq" or not a.correct_answer]
    
    results = []
    
    # Process MCQ answers instantly
    for mcq_answer in mcq_answers:
        result = await evaluate_mcq_answer(mcq_answer)
        results.append(result)
    
    # Process open-ended answers with AI if any
    if open_ended_answers:
        ai_results = await evaluate_open_ended_batch(
            open_ended_answers, pdf_content, filename, evaluation_level
        )
        results.extend(ai_results)
    
    return results

async def evaluate_open_ended_batch(
    answers: List[QuizAnswer],
    pdf_content: str,
    filename: str,
    evaluation_level: str
) -> List[AnswerEvaluationResponse]:
    """Evaluate open-ended answers using AI in batch"""
    
    # Check cache for each answer
    cached_results = []
    uncached_answers = []
    
    for answer in answers:
        question_hash = hashlib.md5(answer.question.encode()).hexdigest()
        answer_hash = generate_answer_hash(answer.question, answer.user_answer)
        
        cached_result = await evaluation_cache.get_evaluation(
            question_hash, answer_hash, evaluation_level
        )
        
        if cached_result:
            cached_results.append(AnswerEvaluationResponse(
                question_id=answer.question_id,
                **cached_result
            ))
        else:
            uncached_answers.append(answer)
    
    # If all answers are cached, return cached results
    if not uncached_answers:
        return cached_results
    
    # Get API key for AI evaluation
    key_info = await get_api_key()
    if not key_info:
        raise Exception("No API key available")
    
    key_id, api_key = key_info
    
    # Configure AI model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Define evaluation criteria
    criteria_map = {
        "easy": {
            "description": "EASY (Lenient) - Focus on basic understanding and effort",
            "scale": "8-10: Basic understanding; 6-7: Partial; 4-5: Minimal; 2-3: Little; 0-1: None"
        },
        "medium": {
            "description": "MEDIUM (Balanced) - Reasonable understanding and adequate detail",
            "scale": "9-10: Excellent; 7-8: Good; 5-6: Satisfactory; 3-4: Needs improvement; 1-2: Poor; 0: None"
        },
        "strict": {
            "description": "STRICT (Rigorous) - Precise, detailed, comprehensive answers required",
            "scale": "9-10: Exceptional; 7-8: Very good; 5-6: Adequate; 3-4: Below standard; 1-2: Poor; 0: Wrong"
        }
    }
    
    criteria = criteria_map.get(evaluation_level, criteria_map["medium"])
    
    # Prepare batch evaluation prompt
    qa_pairs = []
    for i, answer in enumerate(uncached_answers):
        qa_pairs.append(f"""
Question {i+1}: {answer.question}
Student Answer {i+1}: {answer.user_answer}
""")
    
    context = f"""
You are an expert educational evaluator. Evaluate these {len(uncached_answers)} student answers based on the document content.

Document: {filename}
Document Content: {pdf_content[:20000]}

EVALUATION LEVEL: {criteria['description']}
SCORING SCALE (0-10): {criteria['scale']}

{"".join(qa_pairs)}

Provide evaluation for each answer in this EXACT JSON format:
{{
  "evaluations": [
    {{
      "question_number": 1,
      "score": 8,
      "feedback": "Detailed feedback explaining the score",
      "suggestions": "Specific suggestions for improvement",
      "correct_answer_hint": "Brief hint about the correct answer"
    }},
    {{
      "question_number": 2,
      "score": 6,
      "feedback": "Detailed feedback explaining the score",
      "suggestions": "Specific suggestions for improvement",
      "correct_answer_hint": "Brief hint about the correct answer"
    }}
  ]
}}

Evaluate all {len(uncached_answers)} answers. Be constructive and encouraging while maintaining standards.
"""
    
    start_time = time.time()
    
    try:
        response = model.generate_content(context)
        response_time = time.time() - start_time
        
        # Record successful API request
        await record_api_request(key_id, True, response_time)
        
        if not response or not response.text:
            raise Exception("Empty response from AI")
        
        # Parse JSON response
        response_text = response.text.strip()
        
        # Clean markdown if present
        if response_text.startswith('```json'):
            response_text = response_text[7:]
        if response_text.startswith('```'):
            response_text = response_text[3:]
        if response_text.endswith('```'):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        try:
            parsed_response = json.loads(response_text)
            evaluations = parsed_response.get('evaluations', [])
            
            if len(evaluations) != len(uncached_answers):
                logger.warning(f"Expected {len(uncached_answers)} evaluations, got {len(evaluations)}")
            
            # Process AI results
            ai_results = []
            for i, evaluation in enumerate(evaluations):
                if i < len(uncached_answers):
                    answer = uncached_answers[i]
                    
                    result = AnswerEvaluationResponse(
                        question_id=answer.question_id,
                        score=min(max(evaluation.get('score', 0), 0), 10),
                        feedback=evaluation.get('feedback', 'No feedback provided'),
                        suggestions=evaluation.get('suggestions', 'No suggestions provided'),
                        correct_answer_hint=evaluation.get('correct_answer_hint')
                    )
                    
                    ai_results.append(result)
                    
                    # Cache the result
                    question_hash = hashlib.md5(answer.question.encode()).hexdigest()
                    answer_hash = generate_answer_hash(answer.question, answer.user_answer)
                    
                    await evaluation_cache.cache_evaluation(
                        question_hash, answer_hash, evaluation_level, {
                            "score": result.score,
                            "feedback": result.feedback,
                            "suggestions": result.suggestions,
                            "correct_answer_hint": result.correct_answer_hint
                        }
                    )
            
            # Combine cached and AI results
            all_results = cached_results + ai_results
            return all_results
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, Response: {response_text[:500]}")
            raise Exception("Invalid JSON response from AI")
    
    except Exception as e:
        response_time = time.time() - start_time
        await record_api_request(key_id, False, response_time)
        
        # Return fallback results for uncached answers
        fallback_results = []
        for answer in uncached_answers:
            fallback_results.append(AnswerEvaluationResponse(
                question_id=answer.question_id,
                score=5,  # Default middle score
                feedback=f"Unable to evaluate due to system error: {str(e)}",
                suggestions="Please review the document content and try again.",
                correct_answer_hint="Refer to the relevant sections in the document."
            ))
        
        return cached_results + fallback_results

# Celery task for background quiz evaluation
@celery_app.task(bind=True)
def evaluate_quiz_task(self, quiz_data: dict):
    """Background task for quiz evaluation"""
    return asyncio.run(process_quiz_evaluation(quiz_data))

async def process_quiz_evaluation(quiz_data: dict) -> dict:
    """Process quiz evaluation with batch optimization"""
    
    answers = [QuizAnswer(**answer) for answer in quiz_data['answers']]
    user_id = quiz_data['user_id']
    pdf_id = quiz_data['pdf_id']
    topic = quiz_data.get('topic')
    evaluation_level = quiz_data.get('evaluation_level', 'medium')
    
    # Get PDF content
    async with db_manager.get_async_session() as session:
        pdf = await session.get(PDF, pdf_id)
        if not pdf:
            raise Exception("PDF not found")
        
        extracted_text = await session.get(PDFExtractedText, pdf_id)
        if not extracted_text:
            raise Exception("PDF content not found")
        
        pdf_content = extracted_text.extracted_text
        filename = pdf.filename
    
    # Process answers in batches for optimal performance
    answer_chunks = chunk_answers(answers, chunk_size=8)  # 8 answers per batch
    all_results = []
    
    # Process chunks in parallel (limited concurrency)
    semaphore = asyncio.Semaphore(2)  # Max 2 concurrent AI requests
    
    async def process_chunk_with_semaphore(chunk):
        async with semaphore:
            return await evaluate_answers_batch(
                chunk, pdf_content, filename, evaluation_level
            )
    
    chunk_results = await asyncio.gather(*[
        process_chunk_with_semaphore(chunk) for chunk in answer_chunks
    ])
    
    # Flatten results
    for chunk_result in chunk_results:
        all_results.extend(chunk_result)
    
    # Calculate overall metrics
    total_score = sum(result.score for result in all_results)
    max_possible_score = len(answers) * 10
    percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0
    
    # Determine grade
    if percentage >= 90:
        grade = "A"
    elif percentage >= 80:
        grade = "B"
    elif percentage >= 70:
        grade = "C"
    elif percentage >= 60:
        grade = "D"
    else:
        grade = "F"
    
    # Generate overall feedback (simplified for performance)
    if percentage >= 80:
        overall_feedback = f"Excellent work! You scored {total_score}/{max_possible_score} ({percentage:.1f}%). You demonstrate strong understanding of the material."
        strengths = ["Strong comprehension", "Good attention to detail"]
        areas_for_improvement = ["Continue practicing to maintain excellence"]
    elif percentage >= 60:
        overall_feedback = f"Good effort! You scored {total_score}/{max_possible_score} ({percentage:.1f}%). There's room for improvement in some areas."
        strengths = ["Shows understanding of key concepts", "Attempted all questions"]
        areas_for_improvement = ["Focus on accuracy", "Review challenging topics"]
    else:
        overall_feedback = f"You scored {total_score}/{max_possible_score} ({percentage:.1f}%). Consider reviewing the material more thoroughly."
        strengths = ["Completed the assessment", "Shows effort"]
        areas_for_improvement = ["Review fundamental concepts", "Practice more questions", "Focus on understanding"]
    
    study_suggestions = [
        "Review the document content thoroughly",
        "Focus on key concepts and definitions",
        "Practice explaining concepts in your own words"
    ]
    
    # Save quiz session to database
    async with db_manager.get_async_session() as session:
        quiz_session = QuizSession(
            user_id=user_id,
            pdf_id=pdf_id,
            question_set_id=f"quiz_{int(time.time())}",
            topic=topic,
            total_questions=len(answers),
            evaluation_level=evaluation_level,
            total_score=total_score,
            max_score=max_possible_score,
            percentage=percentage,
            grade=grade,
            overall_feedback=overall_feedback,
            study_suggestions=study_suggestions,
            strengths=strengths,
            areas_for_improvement=areas_for_improvement,
            completed_at=datetime.now()
        )
        session.add(quiz_session)
        
        # Save individual evaluations
        for result in all_results:
            evaluation = Evaluation(
                user_id=user_id,
                question_id=result.question_id,
                user_answer=next(a.user_answer for a in answers if a.question_id == result.question_id),
                score=result.score,
                feedback=result.feedback,
                suggestions=result.suggestions,
                correct_answer_hint=result.correct_answer_hint,
                evaluation_level=evaluation_level
            )
            session.add(evaluation)
        
        await session.commit()
    
    return {
        "overall_score": total_score,
        "max_score": max_possible_score,
        "percentage": round(percentage, 1),
        "grade": grade,
        "individual_results": [result.dict() for result in all_results],
        "overall_feedback": overall_feedback,
        "study_suggestions": study_suggestions,
        "strengths": strengths,
        "areas_for_improvement": areas_for_improvement
    }

# API Endpoints
@app.post("/api/evaluation/answer", response_model=AnswerEvaluationResponse)
async def evaluate_single_answer(request: AnswerEvaluationRequest):
    """Evaluate a single answer"""
    
    # Check cache first
    question_hash = hashlib.md5(request.question.encode()).hexdigest()
    answer_hash = generate_answer_hash(request.question, request.user_answer)
    
    cached_result = await evaluation_cache.get_evaluation(
        question_hash, answer_hash, request.evaluation_level
    )
    
    if cached_result:
        return AnswerEvaluationResponse(
            question_id=request.question_id,
            **cached_result
        )
    
    # Create quiz answer for batch processing
    quiz_answer = QuizAnswer(
        question_id=request.question_id,
        question=request.question,
        user_answer=request.user_answer,
        question_type="open_ended"
    )
    
    # Get PDF content (simplified - in production, this should be optimized)
    async with db_manager.get_async_session() as session:
        question = await session.get(Question, request.question_id)
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        pdf = await session.get(PDF, question.pdf_id)
        extracted_text = await session.get(PDFExtractedText, question.pdf_id)
        
        if not pdf or not extracted_text:
            raise HTTPException(status_code=404, detail="PDF content not found")
    
    # Evaluate using batch function
    results = await evaluate_answers_batch(
        [quiz_answer], extracted_text.extracted_text, pdf.filename, request.evaluation_level
    )
    
    return results[0]

@app.post("/api/evaluation/quiz", response_model=QuizSubmissionResponse)
async def evaluate_quiz(request: QuizSubmissionRequest, background_tasks: BackgroundTasks):
    """Evaluate a complete quiz submission"""
    
    # For small quizzes (< 10 questions), process immediately
    if len(request.answers) < 10:
        result = await process_quiz_evaluation(request.dict())
        return QuizSubmissionResponse(**result)
    
    # For larger quizzes, use background processing
    task = evaluate_quiz_task.delay(request.dict())
    
    # Wait for completion (with timeout)
    try:
        result = task.get(timeout=300)  # 5 minute timeout
        return QuizSubmissionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "evaluation"}

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    from ai.api_key_manager import get_api_stats
    api_stats = await get_api_stats()
    
    return {
        "service": "evaluation",
        "api_keys": api_stats,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
