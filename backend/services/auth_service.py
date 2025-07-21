from datetime import datetime, timedelta
from fastapi import HTTPException
from config.settings import settings
from utils.security import create_session_token
from utils.storage import sessions
from models.auth import LoginRequest, LoginResponse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    def login(request: LoginRequest) -> LoginResponse:
        logger.info(f"Login attempt for username: {request.username}")
        logger.info(f"Expected username: {settings.LOGIN_USERNAME}")
        logger.info(f"Expected password: {settings.LOGIN_PASSWORD}")

        if (request.username == settings.LOGIN_USERNAME and
            request.password == settings.LOGIN_PASSWORD):

            logger.info("Login successful - credentials match")
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
            logger.warning("Login failed - invalid credentials")
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
