from fastapi import APIRouter
from models.auth import LoginRequest, LoginResponse
from services.auth_service import AuthService

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    return AuthService.login(request)

@router.post("/logout")
async def logout():
    return AuthService.logout()

@router.get("/verify")
async def verify_auth():
    # Simple verification endpoint - always returns success if reached
    return {"valid": True, "message": "Session is valid"}
