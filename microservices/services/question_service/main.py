"""
Question Generation Service - Optimized for high performance
Handles question generation with parallel processing and intelligent caching.
"""

import os
import asyncio
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from contextlib import asynccontextmanager
import logging

# Import shared modules
import sys
sys.path.append('/app/shared')

from database.config import db_manager, get_async_db_session
from database.models import Question, PDF, BackgroundJob, PDFExtractedText
from cache.redis_config import redis_manager, question_cache
from ai.api_key_manager import get_api_key, record_api_request

# Celery for background processing
from celery import Celery
import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Celery configuration
celery_app = Celery(
    "question_service",
    broker=os.getenv("CELERY_BROKER_URL", "redis://redis:6379/1"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://redis:6379/2")
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes max
    task_soft_time_limit=25 * 60,  # 25 minutes soft limit
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, job_id: str):
        await websocket.accept()
        self.active_connections[job_id] = websocket

    def disconnect(self, job_id: str):
        if job_id in self.active_connections:
            del self.active_connections[job_id]

    async def send_progress(self, job_id: str, message: dict):
        if job_id in self.active_connections:
            try:
                await self.active_connections[job_id].send_json(message)
            except:
                self.disconnect(job_id)

manager = ConnectionManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    logger.info("Starting Question Generation Service...")
    yield
    logger.info("Shutting down Question Generation Service...")
    await redis_manager.close()

app = FastAPI(
    title="Question Generation Service",
    version="2.0.0",
    description="High-performance question generation with parallel processing",
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
class QuestionGenerationRequest(BaseModel):
    pdf_id: str
    topic: Optional[str] = None
    count: int = 25
    mode: str = "practice"  # "practice" or "quiz"
    user_id: str

class QuestionGenerationResponse(BaseModel):
    job_id: str
    status: str
    message: str
    estimated_time: int  # seconds

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress_percentage: int
    progress_message: str
    result: Optional[Dict] = None
    error_message: Optional[str] = None

# Utility functions
def generate_cache_key(pdf_hash: str, topic: str, count: int, mode: str) -> str:
    """Generate cache key for question generation"""
    key_data = f"{pdf_hash}:{topic or 'general'}:{count}:{mode}"
    return hashlib.md5(key_data.encode()).hexdigest()

def chunk_content(content: str, max_chunk_size: int = 15000) -> List[str]:
    """Split content into manageable chunks for AI processing"""
    words = content.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > max_chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks

async def generate_ai_questions(
    content_chunk: str,
    filename: str,
    topic: str,
    questions_per_chunk: int,
    mode: str
) -> List[Dict]:
    """Generate questions for a content chunk using AI"""
    
    # Get API key
    key_info = await get_api_key()
    if not key_info:
        raise Exception("No API key available")
    
    key_id, api_key = key_info
    
    # Configure AI model
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.5-flash")
    
    # Prepare optimized prompt
    if mode == "quiz":
        format_instruction = """
        FORMAT: Create Multiple Choice Questions (MCQ) with 4 options each.
        Respond with ONLY a valid JSON object:
        {
          "questions": [
            {
              "question": "What is the main concept discussed?",
              "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
              "correctAnswer": "A"
            }
          ]
        }
        """
    else:
        format_instruction = """
        FORMAT: Create open-ended questions. Respond with ONLY a valid JSON object:
        {
          "questions": [
            "What is the main concept discussed?",
            "Explain the key principles mentioned."
          ]
        }
        """
    
    topic_instruction = f"\nFOCUS ON TOPIC: {topic}" if topic else ""
    
    context = f"""
    You are an educational AI. Create exactly {questions_per_chunk} questions from this content.
    
    Document: {filename}
    {topic_instruction}
    
    CONTENT:
    {content_chunk}
    
    {format_instruction}
    
    Requirements:
    - Questions must be answerable from the content above
    - Use actual terms and concepts from the text
    - Progress from basic to advanced understanding
    """
    
    start_time = asyncio.get_event_loop().time()
    
    try:
        response = model.generate_content(context)
        response_time = asyncio.get_event_loop().time() - start_time
        
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
            questions = parsed_response.get('questions', [])
            
            if not questions:
                raise Exception("No questions in response")
            
            return questions
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}, Response: {response_text[:500]}")
            raise Exception("Invalid JSON response from AI")
    
    except Exception as e:
        response_time = asyncio.get_event_loop().time() - start_time
        await record_api_request(key_id, False, response_time)
        raise

# Celery task for background question generation
@celery_app.task(bind=True)
def generate_questions_task(self, pdf_id: str, topic: str, count: int, mode: str, user_id: str):
    """Background task for question generation with progress updates"""
    
    job_id = self.request.id
    
    try:
        # Update job status to running
        asyncio.run(update_job_status(job_id, "running", 0, "Starting question generation..."))
        
        # Get PDF content from database
        pdf_content = asyncio.run(get_pdf_content(pdf_id))
        if not pdf_content:
            raise Exception("PDF content not found")
        
        content, filename, content_hash = pdf_content
        
        # Check cache first
        cache_key = generate_cache_key(content_hash, topic or "", count, mode)
        cached_questions = asyncio.run(question_cache.get_questions(
            content_hash, topic or "", count, mode
        ))
        
        if cached_questions:
            logger.info(f"Cache hit for job {job_id}")
            asyncio.run(update_job_status(
                job_id, "completed", 100, "Questions retrieved from cache", cached_questions
            ))
            return cached_questions
        
        # Split content into chunks for parallel processing
        chunks = chunk_content(content, max_chunk_size=15000)
        questions_per_chunk = max(1, count // len(chunks))
        remaining_questions = count % len(chunks)
        
        logger.info(f"Processing {len(chunks)} chunks, {questions_per_chunk} questions per chunk")
        
        # Update progress
        asyncio.run(update_job_status(
            job_id, "running", 10, f"Processing {len(chunks)} content chunks..."
        ))
        
        # Generate questions for each chunk in parallel
        all_questions = []
        
        async def process_chunks():
            tasks = []
            for i, chunk in enumerate(chunks):
                chunk_questions = questions_per_chunk
                if i < remaining_questions:
                    chunk_questions += 1
                
                if chunk_questions > 0:
                    task = generate_ai_questions(
                        chunk, filename, topic or "", chunk_questions, mode
                    )
                    tasks.append(task)
            
            # Process chunks in parallel (limited concurrency)
            semaphore = asyncio.Semaphore(3)  # Max 3 concurrent AI requests
            
            async def process_chunk_with_semaphore(task, chunk_index):
                async with semaphore:
                    try:
                        questions = await task
                        progress = 20 + (chunk_index + 1) * 60 // len(tasks)
                        await update_job_status(
                            job_id, "running", progress,
                            f"Processed chunk {chunk_index + 1}/{len(tasks)}"
                        )
                        return questions
                    except Exception as e:
                        logger.error(f"Error processing chunk {chunk_index}: {e}")
                        return []
            
            chunk_results = await asyncio.gather(*[
                process_chunk_with_semaphore(task, i) 
                for i, task in enumerate(tasks)
            ])
            
            return chunk_results
        
        # Run parallel processing
        chunk_results = asyncio.run(process_chunks())
        
        # Combine results
        for chunk_questions in chunk_results:
            all_questions.extend(chunk_questions)
        
        # Limit to requested count
        all_questions = all_questions[:count]
        
        if len(all_questions) < count * 0.8:  # Less than 80% of requested questions
            logger.warning(f"Generated only {len(all_questions)} out of {count} requested questions")
        
        # Update progress
        asyncio.run(update_job_status(
            job_id, "running", 85, "Saving questions to database..."
        ))
        
        # Save to database and cache
        saved_questions = asyncio.run(save_questions_to_db(
            pdf_id, all_questions, topic, mode, job_id, user_id
        ))
        
        # Cache the results
        asyncio.run(question_cache.cache_questions(
            content_hash, topic or "", count, mode, saved_questions
        ))
        
        # Complete the job
        asyncio.run(update_job_status(
            job_id, "completed", 100, f"Generated {len(saved_questions)} questions successfully",
            {"questions": saved_questions}
        ))
        
        return saved_questions
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Question generation failed for job {job_id}: {error_msg}")
        asyncio.run(update_job_status(
            job_id, "failed", 0, f"Question generation failed: {error_msg}"
        ))
        raise

# Helper functions
async def get_pdf_content(pdf_id: str) -> Optional[tuple]:
    """Get PDF content from database"""
    async with db_manager.get_async_session() as session:
        # Get PDF info
        pdf = await session.get(PDF, pdf_id)
        if not pdf:
            return None
        
        # Get extracted text
        extracted_text = await session.get(PDFExtractedText, pdf_id)
        if not extracted_text:
            return None
        
        return extracted_text.extracted_text, pdf.filename, pdf.content_hash

async def update_job_status(job_id: str, status: str, progress: int, message: str, result: Dict = None):
    """Update job status in database and notify via WebSocket"""
    async with db_manager.get_async_session() as session:
        job = await session.get(BackgroundJob, job_id)
        if job:
            job.status = status
            job.progress_percentage = progress
            job.progress_message = message
            if result:
                job.result = result
            if status == "completed":
                job.completed_at = datetime.now()
            elif status == "running" and not job.started_at:
                job.started_at = datetime.now()
            
            await session.commit()
    
    # Send WebSocket update
    await manager.send_progress(job_id, {
        "job_id": job_id,
        "status": status,
        "progress": progress,
        "message": message,
        "result": result
    })

async def save_questions_to_db(
    pdf_id: str, questions: List[Dict], topic: str, mode: str, 
    question_set_id: str, user_id: str
) -> List[Dict]:
    """Save generated questions to database"""
    async with db_manager.get_async_session() as session:
        saved_questions = []
        
        for i, q in enumerate(questions):
            if isinstance(q, str):
                # Open-ended question
                question = Question(
                    pdf_id=pdf_id,
                    question_set_id=question_set_id,
                    question_text=q,
                    question_type="open_ended",
                    topic=topic,
                    cache_key=generate_cache_key(pdf_id, topic or "", len(questions), mode)
                )
            else:
                # MCQ question
                question = Question(
                    pdf_id=pdf_id,
                    question_set_id=question_set_id,
                    question_text=q.get("question", ""),
                    question_type="mcq",
                    topic=topic,
                    options=q.get("options", []),
                    correct_answer=q.get("correctAnswer", ""),
                    cache_key=generate_cache_key(pdf_id, topic or "", len(questions), mode)
                )
            
            session.add(question)
            saved_questions.append({
                "id": question.id,
                "question": question.question_text,
                "type": question.question_type,
                "options": question.options,
                "correct_answer": question.correct_answer
            })
        
        await session.commit()
        return saved_questions

# API Endpoints
@app.post("/api/questions/generate", response_model=QuestionGenerationResponse)
async def generate_questions(request: QuestionGenerationRequest, background_tasks: BackgroundTasks):
    """Start question generation job"""
    
    # Create background job record
    job = BackgroundJob(
        job_type="question_generation",
        status="pending",
        user_id=request.user_id,
        parameters={
            "pdf_id": request.pdf_id,
            "topic": request.topic,
            "count": request.count,
            "mode": request.mode
        }
    )
    
    async with db_manager.get_async_session() as session:
        session.add(job)
        await session.commit()
        job_id = job.id
    
    # Start Celery task
    task = generate_questions_task.delay(
        request.pdf_id, request.topic, request.count, request.mode, request.user_id
    )
    
    # Update job with Celery task ID
    async with db_manager.get_async_session() as session:
        job = await session.get(BackgroundJob, job_id)
        job.celery_task_id = task.id
        await session.commit()
    
    # Estimate time based on question count
    estimated_time = min(max(request.count * 3, 30), 180)  # 3 seconds per question, 30s min, 3min max
    
    return QuestionGenerationResponse(
        job_id=job_id,
        status="pending",
        message="Question generation started",
        estimated_time=estimated_time
    )

@app.get("/api/questions/status/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get question generation job status"""
    async with db_manager.get_async_session() as session:
        job = await session.get(BackgroundJob, job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return JobStatusResponse(
            job_id=job.id,
            status=job.status,
            progress_percentage=job.progress_percentage,
            progress_message=job.progress_message or "",
            result=job.result,
            error_message=job.error_message
        )

@app.websocket("/api/questions/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket, job_id)
    try:
        while True:
            await websocket.receive_text()  # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(job_id)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "question_generation"}

@app.get("/stats")
async def get_stats():
    """Get service statistics"""
    # Get API key stats
    from ai.api_key_manager import get_api_stats
    api_stats = await get_api_stats()
    
    return {
        "service": "question_generation",
        "api_keys": api_stats,
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
