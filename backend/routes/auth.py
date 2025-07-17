from fastapi import APIRouter, Depends
from models.auth import LoginRequest, LoginResponse
from services.auth_service import AuthService
from utils.security import verify_token

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    return AuthService.login(request)

@router.post("/logout")
async def logout(token: str = Depends(verify_token)):
    return AuthService.logout(token)

@router.get("/verify")
async def verify_auth(token: str = Depends(verify_token)):
    return AuthService.verify_auth(token)
