import uuid
from datetime import datetime, timedelta
from config.settings import settings

def create_session_id():
    """Create a simple session ID"""
    return str(uuid.uuid4())

def is_valid_session(session_id: str = None) -> bool:
    """Simple session validation - optional and flexible"""
    from utils.storage import user_sessions

    if not session_id:
        return True  # Allow access without strict validation

    session = user_sessions.get(session_id)
    if session and session["expires_at"] > datetime.now():
        return True
    else:
        if session_id in user_sessions:
            del user_sessions[session_id]
        return False
