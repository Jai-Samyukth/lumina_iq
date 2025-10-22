import os
import socket
from pathlib import Path
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
    LOGIN_USERNAME = os.getenv("LOGIN_USERNAME", "vsbec")
    LOGIN_PASSWORD = os.getenv("LOGIN_PASSWORD", "vsbec")

    # Gemini AI
    GEMINI_API_KEY = os.getenv(
        "GEMINI_API_KEY", "AIzaSyBiKBADQGhRuFn5glEU-frmORFc0KRleVQ"
    )
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-lite")

    # Together.ai Configuration
    TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY", "")
    TOGETHER_MODEL = os.getenv("TOGETHER_MODEL", "openai/gpt-oss-20b")
    TOGETHER_BASE_URL = os.getenv("TOGETHER_BASE_URL", "https://api.together.xyz/v1")

    # Embedding Configuration
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-large-en-v1.5")
    EMBEDDING_DIMENSIONS = int(os.getenv("EMBEDDING_DIMENSIONS", "1024"))

    # Qdrant Cloud Configuration
    QDRANT_URL = os.getenv(
        "QDRANT_URL",
        "https://1f6b3bbc-d09e-40c2-b333-0a823825f876.europe-west3-0.gcp.cloud.qdrant.io:6333",
    )
    QDRANT_API_KEY = os.getenv(
        "QDRANT_API_KEY",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.O8xNwnZuHGOxo1dcIdcgKrRVZGryxKPYyGaCVyNXziQ",
    )
    QDRANT_COLLECTION_NAME = os.getenv(
        "QDRANT_COLLECTION_NAME", "learning_app_documents"
    )

    # CORS - Dynamic IP detection for development
    @property
    def CORS_ORIGINS(self):
        local_ip = get_local_ip()
        origins = [
            "http://localhost:3000",
            "http://127.0.0.1:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3001",
            f"http://{local_ip}:3000",
            f"http://{local_ip}:3001",
            "*",
        ]
        return list(set(origins))  # Remove duplicates

    # File paths - Use relative paths from project root
    @property
    def BOOKS_DIR(self):
        # Get the project root directory (parent of backend)
        backend_dir = Path(__file__).parent.parent
        project_root = backend_dir.parent
        books_dir = project_root / "books"
        return str(books_dir)

    CACHE_DIR = "cache"

    # Session
    SESSION_EXPIRE_HOURS = 24

    # Server
    HOST = "0.0.0.0"
    PORT = 8000


settings = Settings()
