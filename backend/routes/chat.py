from fastapi import APIRouter, Depends
from models.chat import ChatMessage, ChatResponse
from services.chat_service import ChatService
from utils.security import verify_token

router = APIRouter(prefix="/api/chat", tags=["chat"])

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
    token: str = Depends(verify_token)
):
    """Generate Q&A questions from the selected PDF content"""
    return await ChatService.generate_questions(token)
