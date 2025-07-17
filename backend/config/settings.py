import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # Authentication
    LOGIN_USERNAME = os.getenv("LOGIN_USERNAME", "vsbec")
    LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "vsbec")
    
    # Gemini AI
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBiKBADQGhRuFn5glEU-frmORFc0KRleVQ")
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    
    # CORS
    CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"]
    
    # File paths
    BOOKS_DIR = "../books"
    
    # Session
    SESSION_EXPIRE_HOURS = 24
    
    # Server
    HOST = "0.0.0.0"
    PORT = 8000

settings = Settings()
