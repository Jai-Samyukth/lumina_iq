from datetime import datetime, timedelta
from fastapi import HTTPException
from config.settings import settings
from utils.security import create_session_token
from utils.storage import sessions
from models.auth import LoginRequest, LoginResponse

class AuthService:
    @staticmethod
    def login(request: LoginRequest) -> LoginResponse:
        if (request.username == settings.LOGIN_USERNAME and 
            request.password == settings.LOGIN_PASSWORD):
            
            token = create_session_token()
            sessions[token] = {
                "username": request.username,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=settings.SESSION_EXPIRE_HOURS)
            }
            
            return LoginResponse(
                access_token=token,
                token_type="bearer",
                message="Login successful"
            )
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    @staticmethod
    def logout(token: str) -> dict:
        if token in sessions:
            del sessions[token]
        return {"message": "Logout successful"}
    
    @staticmethod
    def verify_auth(token: str) -> dict:
        session = sessions.get(token)
        if session and session["expires_at"] > datetime.now():
            return {"valid": True, "username": session["username"]}
        else:
            if token in sessions:
                del sessions[token]
            raise HTTPException(status_code=401, detail="Token expired")
