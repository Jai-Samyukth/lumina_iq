import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.settings import settings

# Security
security = HTTPBearer()

def create_session_token():
    return str(uuid.uuid4())

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    from utils.storage import sessions  # Import here to avoid circular import
    
    token = credentials.credentials
    if token not in sessions:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    session = sessions.get(token)
    if session and session["expires_at"] > datetime.now():
        return token
    else:
        if token in sessions:
            del sessions[token]
        raise HTTPException(status_code=401, detail="Token expired")
