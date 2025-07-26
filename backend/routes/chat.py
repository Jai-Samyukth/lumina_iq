from fastapi import APIRouter
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
import sys
import os

# Add the parent directory to the path to import from api_rotation
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

try:
    from api_rotation.api_key_rotator import api_key_rotator
    ROTATION_AVAILABLE = True
except ImportError:
    ROTATION_AVAILABLE = False

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Use a simple session key for chat operations
DEFAULT_SESSION = "default_user"

class QuestionGenerationRequest(BaseModel):
    topic: Optional[str] = None
    count: Optional[int] = 25
    mode: Optional[str] = "practice"  # "quiz" for MCQ, "practice" for open-ended

@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Send a message to the AI assistant about the selected PDF"""
    return await ChatService.chat(message, DEFAULT_SESSION)

@router.get("/history")
async def get_chat_history():
    """Get the chat history for the current session"""
    return ChatService.get_chat_history(DEFAULT_SESSION)

@router.delete("/history")
async def clear_chat_history():
    """Clear the chat history for the current session"""
    return ChatService.clear_chat_history(DEFAULT_SESSION)

@router.post("/generate-questions", response_model=ChatResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """Generate Q&A questions from the selected PDF content, optionally focused on a specific topic"""
    print(f"DEBUG: Route received request: topic={request.topic}, count={request.count}, mode={request.mode}")
    return await ChatService.generate_questions(DEFAULT_SESSION, request.topic, request.count, request.mode)

@router.post("/evaluate-answer", response_model=AnswerEvaluationResponse)
async def evaluate_answer(request: AnswerEvaluationRequest):
    """Evaluate a single user answer using AI"""
    return await ChatService.evaluate_answer(request, DEFAULT_SESSION)

@router.post("/evaluate-quiz", response_model=QuizSubmissionResponse)
async def evaluate_quiz(request: QuizSubmissionRequest):
    """Evaluate a complete quiz submission with overall feedback"""
    return await ChatService.evaluate_quiz(request, DEFAULT_SESSION)

@router.get("/api-rotation-status")
async def get_api_rotation_status():
    """Get the current status of API key rotation"""
    if not ROTATION_AVAILABLE:
        return {
            "enabled": False,
            "message": "API key rotation is not available"
        }

    stats = api_key_rotator.get_current_stats()
    return {
        "enabled": True,
        "stats": stats,
        "message": f"API rotation active with {stats['total_keys']} keys"
    }
