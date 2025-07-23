import google.generativeai as genai
from datetime import datetime
from fastapi import HTTPException
from config.settings import settings
from utils.storage import pdf_contexts, chat_histories
from models.chat import (
    ChatMessage,
    ChatResponse,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse,
    QuizAnswer
)

# Configure Gemini AI
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel(settings.GEMINI_MODEL)

class ChatService:
    @staticmethod
    async def chat(message: ChatMessage, token: str) -> ChatResponse:
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Initialize chat history if not exists
        if token not in chat_histories:
            chat_histories[token] = []

        # Check if this is a Q&A generation request (needs full content)
        is_qa_generation = any(keyword in message.message.lower() for keyword in [
            'generate', 'create', 'analyze this document', 'questions', 'sections', 'comprehensive'
        ])

        # Use more content for Q&A generation, limited content for regular chat
        content_limit = 50000 if is_qa_generation else 15000
        pdf_content = pdf_context['content'][:content_limit]

        # Add indication if content was truncated
        content_suffix = "..." if len(pdf_context['content']) > content_limit else ""

        # Prepare context for Gemini
        context = f"""
        You are an AI assistant helping students learn from their selected PDF document.

        Document: {pdf_context['filename']}
        Content: {pdf_content}{content_suffix}

        Previous conversation:
        {chr(10).join([f"User: {msg['user']}{chr(10)}Assistant: {msg['assistant']}" for msg in chat_histories[token][-3:]])}

        Current question: {message.message}

        Please provide a helpful, educational response based on the document content and conversation history.
        """

        try:
            # Generate response using Gemini
            response = model.generate_content(context)
            ai_response = response.text

            # Store in chat history
            chat_histories[token].append({
                "user": message.message,
                "assistant": ai_response,
                "timestamp": datetime.now().isoformat()
            })

            return ChatResponse(
                response=ai_response,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to generate response: {str(e)}")

    @staticmethod
    def get_chat_history(token: str) -> dict:
        if token not in chat_histories:
            return {"history": []}

        return {"history": chat_histories[token]}
    
    @staticmethod
    def clear_chat_history(token: str) -> dict:
        if token in chat_histories:
            chat_histories[token] = []
        return {"message": "Chat history cleared"}

    @staticmethod
    async def generate_questions(token: str, topic: str = None, count: int = 25) -> ChatResponse:
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Get the full PDF content for question generation
        full_content = pdf_context['content']

        print(f"Generating questions for PDF: {pdf_context['filename']}")
        print(f"Content length: {len(full_content)} characters")
        print(f"Content preview: {full_content[:500]}...")

        # Check if content is too short
        if len(full_content.strip()) < 100:
            raise HTTPException(status_code=400, detail="Document content is too short to generate meaningful questions")

        # Prepare context for Gemini with full content
        topic_instruction = ""
        if topic and topic.strip():
            topic_instruction = f"""
        SPECIFIC TOPIC FOCUS: "{topic.strip()}"
        Focus your questions specifically on this topic, but use the full document content as context to ensure accuracy and completeness.
        """

        context = f"""
        You are an educational AI assistant. Analyze the following document content and create comprehensive questions for learning.

        Document: {pdf_context['filename']}
        {topic_instruction}

        FULL DOCUMENT CONTENT:
        {full_content}

        TASK: Create exactly {count} educational questions based on the document content above{' focusing on the specified topic' if topic and topic.strip() else ''}.

        REQUIREMENTS:
        1. Read and analyze the ENTIRE document content provided above
        2. {'Focus specifically on the topic: "' + topic.strip() + '" while using the full document as context' if topic and topic.strip() else 'Create questions that cover the full scope of the document'}
        3. Include questions about:
           - Key concepts and definitions from the text
           - Important details and facts mentioned
           - Practical applications discussed
           - Examples and case studies provided
           - Critical thinking questions about the content
           - Main themes and ideas
           - Specific processes or methods described
           - Important people, places, or events mentioned
           - Cause and effect relationships
           - Comparisons and contrasts made in the text

        FORMAT: Respond with ONLY a valid JSON object in this exact format:
        {{
          "questions": [
            "What is [specific concept from document]?",
            "How does [specific process from document] work?",
            "What are the key benefits of [specific topic] mentioned in the text?",
            "Can you explain the relationship between [concept A] and [concept B] as described?",
            "What examples are provided to illustrate [specific concept]?",
            "What are the main steps involved in [specific process from text]?",
            "How does the document define [important term]?",
            "What problems does [solution mentioned] solve according to the text?",
            "What are the different types of [category from document] mentioned?",
            "How can [concept from text] be applied in practice?",
            "What are the advantages and disadvantages of [approach from document]?",
            "What recommendations does the text make regarding [topic]?",
            "How does [concept] compare to [alternative] according to the document?",
            "What are the key takeaways from the document?",
            "What future implications are discussed for [topic from text]?",
            "Who are the main people mentioned in the document and what are their contributions?",
            "What are the most important facts or statistics presented?",
            "What real-world applications are discussed in the text?",
            "What challenges or problems are identified in the document?",
            "How does the author support their main arguments?",
            "What conclusions does the document reach?",
            "What are the practical implications of the concepts discussed?",
            "How do the different sections of the document relate to each other?",
            "What evidence is provided to support the main points?",
            "What questions does the document leave unanswered?"
          ]
        }}

        Make sure:
        - Questions are specific to the actual document content provided above
        - Each question can be answered using information from the document
        - Questions progress from basic to advanced understanding
        - {'Focus specifically on the topic "' + topic.strip() + '" while ensuring all questions can be answered from the document content' if topic and topic.strip() else 'Cover all major topics and themes in the document'}
        - Use actual terms, concepts, and examples from the text provided
        - Questions are diverse and cover different aspects of the {'specified topic' if topic and topic.strip() else 'content'}

        Generate exactly {count} questions now based on the full document content provided above{' focusing on the specified topic' if topic and topic.strip() else ''}.
        """

        try:
            # Generate response using Gemini
            print("Sending request to Gemini AI...")
            response = model.generate_content(context)

            if not response or not response.text:
                raise HTTPException(status_code=500, detail="AI service returned empty response")

            ai_response = response.text

            print(f"AI Response length: {len(ai_response)} characters")
            print(f"AI Response preview: {ai_response[:500]}...")

            # Validate that response contains JSON-like structure
            if '{' not in ai_response or '}' not in ai_response:
                print("Warning: Response doesn't appear to contain JSON structure")
                print(f"Full response: {ai_response}")

            return ChatResponse(
                response=ai_response,
                timestamp=datetime.now().isoformat()
            )

        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Failed to generate questions: {str(e)}")

    @staticmethod
    async def evaluate_answer(request: AnswerEvaluationRequest, token: str) -> AnswerEvaluationResponse:
        """Evaluate a single user answer using AI"""
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Get evaluation level settings
        evaluation_level = request.evaluation_level or "medium"

        # Define evaluation criteria based on level
        if evaluation_level == "easy":
            criteria_text = """
        EVALUATION LEVEL: EASY (Lenient)
        - Focus on basic understanding and effort
        - Give credit for partial answers and good attempts
        - Be encouraging and supportive in feedback

        SCORING SCALE (0-10):
        - 8-10: Shows basic understanding, good effort
        - 6-7: Partially correct, some understanding shown
        - 4-5: Minimal understanding but attempted
        - 2-3: Little understanding but some effort
        - 0-1: No answer or completely off-topic"""
        elif evaluation_level == "strict":
            criteria_text = """
        EVALUATION LEVEL: STRICT (Rigorous)
        - Require precise, detailed, and comprehensive answers
        - Expect specific examples and thorough explanations
        - Be critical of incomplete or vague responses

        SCORING SCALE (0-10):
        - 9-10: Exceptional - Precise, comprehensive, with specific examples
        - 7-8: Very Good - Accurate and detailed, minor gaps acceptable
        - 5-6: Adequate - Correct but lacks depth or detail
        - 3-4: Below Standard - Significant gaps or inaccuracies
        - 1-2: Poor - Major errors or very incomplete
        - 0: No answer or completely wrong"""
        else:  # medium
            criteria_text = """
        EVALUATION LEVEL: MEDIUM (Balanced)
        - Expect reasonable understanding and adequate detail
        - Balance between being supportive and maintaining standards
        - Look for key concepts and main points

        SCORING SCALE (0-10):
        - 9-10: Excellent - Accurate, complete, demonstrates deep understanding
        - 7-8: Good - Mostly accurate, covers main points, good understanding
        - 5-6: Satisfactory - Partially correct, basic understanding shown
        - 3-4: Needs Improvement - Some correct elements but significant gaps
        - 1-2: Poor - Mostly incorrect or irrelevant
        - 0: No answer or completely wrong"""

        # Prepare context for evaluation
        evaluation_context = f"""
        You are an expert educational evaluator. Your task is to evaluate a student's answer to a question based on the provided document content.

        Document: {pdf_context['filename']}
        Document Content: {pdf_context['content'][:20000]}

        Question: {request.question}
        Student's Answer: {request.user_answer}

        EVALUATION CRITERIA:
        1. Accuracy: How correct is the answer based on the document content?
        2. Completeness: Does the answer cover all important aspects?
        3. Understanding: Does the student demonstrate clear understanding?
        4. Relevance: Is the answer relevant to the question asked?

        {criteria_text}

        Please provide your evaluation in the following JSON format:
        {{
            "score": [0-10 integer],
            "feedback": "[Detailed feedback explaining the score, highlighting what was correct and what was missing]",
            "suggestions": "[Specific suggestions for improvement]",
            "correct_answer_hint": "[Brief hint about the correct answer without giving it away completely]"
        }}

        Be constructive and encouraging in your feedback while being honest about areas for improvement.
        """

        try:
            response = model.generate_content(evaluation_context)
            ai_response = response.text

            # Try to extract JSON from the response
            import json
            import re

            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response)
            if json_match:
                try:
                    evaluation_data = json.loads(json_match.group())

                    return AnswerEvaluationResponse(
                        question_id=request.question_id,
                        score=min(max(evaluation_data.get('score', 0), 0), 10),  # Ensure score is 0-10
                        feedback=evaluation_data.get('feedback', 'No feedback provided'),
                        suggestions=evaluation_data.get('suggestions', 'No suggestions provided'),
                        correct_answer_hint=evaluation_data.get('correct_answer_hint')
                    )
                except json.JSONDecodeError:
                    pass

            # Fallback if JSON parsing fails
            return AnswerEvaluationResponse(
                question_id=request.question_id,
                score=5,  # Default middle score
                feedback=ai_response,
                suggestions="Please review the document content for more accurate information.",
                correct_answer_hint="Refer to the relevant sections in the document."
            )

        except Exception as e:
            print(f"Error evaluating answer: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to evaluate answer: {str(e)}")

    @staticmethod
    async def evaluate_quiz(request: QuizSubmissionRequest, token: str) -> QuizSubmissionResponse:
        """Evaluate a complete quiz submission"""
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected. Please select a PDF first.")

        pdf_context = pdf_contexts[token]

        # Evaluate each answer individually
        individual_results = []
        total_score = 0

        for answer in request.answers:
            eval_request = AnswerEvaluationRequest(
                question=answer.question,
                user_answer=answer.user_answer,
                question_id=answer.question_id,
                evaluation_level=request.evaluation_level
            )

            result = await ChatService.evaluate_answer(eval_request, token)
            individual_results.append(result)
            total_score += result.score

        # Calculate overall metrics
        max_possible_score = len(request.answers) * 10
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

        # Generate overall feedback using AI
        overall_context = f"""
        You are an educational AI providing comprehensive feedback on a student's quiz performance.

        Document: {pdf_context['filename']}
        Topic: {request.topic or 'General'}

        Quiz Results:
        - Total Score: {total_score}/{max_possible_score} ({percentage:.1f}%)
        - Grade: {grade}
        - Number of Questions: {len(request.answers)}

        Individual Question Performance:
        """

        for i, (answer, result) in enumerate(zip(request.answers, individual_results), 1):
            overall_context += f"""
        Question {i}: {answer.question}
        Student Answer: {answer.user_answer}
        Score: {result.score}/10
        """

        overall_context += f"""

        Based on this performance, provide:
        1. Overall feedback (2-3 sentences about the student's performance)
        2. Study suggestions (3-4 specific recommendations)
        3. Strengths (2-3 areas where the student performed well)
        4. Areas for improvement (2-3 specific areas needing work)

        Provide your response in JSON format:
        {{
            "overall_feedback": "[Overall assessment of performance]",
            "study_suggestions": ["suggestion1", "suggestion2", "suggestion3"],
            "strengths": ["strength1", "strength2"],
            "areas_for_improvement": ["area1", "area2", "area3"]
        }}

        Be encouraging and constructive while providing actionable feedback.
        """

        try:
            response = model.generate_content(overall_context)
            ai_response = response.text

            # Parse AI response
            import json
            import re

            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', ai_response)
            if json_match:
                try:
                    feedback_data = json.loads(json_match.group())

                    return QuizSubmissionResponse(
                        overall_score=total_score,
                        max_score=max_possible_score,
                        percentage=round(percentage, 1),
                        grade=grade,
                        individual_results=individual_results,
                        overall_feedback=feedback_data.get('overall_feedback', f'You scored {total_score}/{max_possible_score} ({percentage:.1f}%)'),
                        study_suggestions=feedback_data.get('study_suggestions', ['Review the document content', 'Practice more questions']),
                        strengths=feedback_data.get('strengths', ['Attempted all questions']),
                        areas_for_improvement=feedback_data.get('areas_for_improvement', ['Focus on accuracy', 'Provide more detailed answers'])
                    )
                except json.JSONDecodeError:
                    pass

            # Fallback response
            return QuizSubmissionResponse(
                overall_score=total_score,
                max_score=max_possible_score,
                percentage=round(percentage, 1),
                grade=grade,
                individual_results=individual_results,
                overall_feedback=f'You scored {total_score}/{max_possible_score} ({percentage:.1f}%). {"Great job!" if percentage >= 80 else "Keep practicing to improve your understanding."}',
                study_suggestions=['Review the document content thoroughly', 'Focus on key concepts and definitions', 'Practice explaining concepts in your own words'],
                strengths=['Completed all questions', 'Showed effort in answering'],
                areas_for_improvement=['Accuracy of responses', 'Depth of understanding', 'Use of specific examples from the text']
            )

        except Exception as e:
            print(f"Error generating overall feedback: {str(e)}")
            # Return basic response without AI-generated feedback
            return QuizSubmissionResponse(
                overall_score=total_score,
                max_score=max_possible_score,
                percentage=round(percentage, 1),
                grade=grade,
                individual_results=individual_results,
                overall_feedback=f'Quiz completed. Score: {total_score}/{max_possible_score} ({percentage:.1f}%)',
                study_suggestions=['Review the document content', 'Practice more questions'],
                strengths=['Completed the quiz'],
                areas_for_improvement=['Continue studying the material']
            )
