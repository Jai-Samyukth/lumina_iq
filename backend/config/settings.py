import os
import socket
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_local_ip():
    """Get the local IP address for CORS configuration."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except Exception:
        return "127.0.0.1"

class Settings:
    # Authentication
    LOGIN_USERNAME = os.getenv('LOGIN_USERNAME', 'vsbec')
    LOGIN_PASSWORD = os.getenv('LOGIN_PASSWORD', 'vsbec')
    
    # Gemini AI
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'AIzaSyBiKBADQGhRuFn5glEU-frmORFc0KRleVQ')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-2.0-flash-lite')
    
    # CORS - Dynamic IP detection for development
    @property
    def CORS_ORIGINS(self):
        local_ip = get_local_ip()
        origins = [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:3001',
            'http://127.0.0.1:3001',
            f'http://{local_ip}:3000',
            f'http://{local_ip}:3001',
            "*"
        ]
        return list(set(origins))  # Remove duplicates
    
    # File paths
    BOOKS_DIR = r"S:\software\PDFFiles"
    CACHE_DIR = 'cache'
    
    # Session
    SESSION_EXPIRE_HOURS = 24
    
    # Server
    HOST = '0.0.0.0'
    PORT = 8000

settings = Settings()
