from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from models.chat import (
    ChatMessage,
    ChatResponse,
    AnswerEvaluationRequest,
    AnswerEvaluationResponse,
    QuizSubmissionRequest,
    QuizSubmissionResponse
)
from services.chat_service import ChatService
from utils.security import verify_token

router = APIRouter(prefix="/api/chat", tags=["chat"])

class QuestionGenerationRequest(BaseModel):
    topic: Optional[str] = None
    count: Optional[int] = 25

@router.post("/", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    token: str = Depends(verify_token)
):
    """Send a message to the AI assistant about the selected PDF"""
    return await ChatService.chat(message, token)

@router.get("/history")
async def get_chat_history(token: str = Depends(verify_token)):
    """Get the chat history for the current session"""
    return ChatService.get_chat_history(token)

@router.delete("/history")
async def clear_chat_history(token: str = Depends(verify_token)):
    """Clear the chat history for the current session"""
    return ChatService.clear_chat_history(token)

@router.post("/generate-questions", response_model=ChatResponse)
async def generate_questions(
    request: QuestionGenerationRequest,
    token: str = Depends(verify_token)
):
    """Generate Q&A questions from the selected PDF content, optionally focused on a specific topic"""
    return await ChatService.generate_questions(token, request.topic, request.count)

@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_answer(
    request: AnswerEvaluationRequest,
    token: str = Depends(verify_token)
):
    """Evaluate a single user answer using AI"""
    return await ChatService.evaluate_answer(request, token)

@router.post("/evaluate-quiz", response_model=QuizSubmissionResponse)
async def evaluate_quiz(
    request: QuizSubmissionRequest,
    token: str = Depends(verify_token)
):
    """Evaluate a complete quiz submission with overall feedback"""
    return await ChatService.evaluate_quiz(request, token)
