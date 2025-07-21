#!/usr/bin/env python3
"""
Run script for the Learning App FastAPI backend.
This script starts the FastAPI server with uvicorn.
"""

import uvicorn
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config.settings import settings

def main():
    """Start the FastAPI server."""
    print("🚀 Starting Learning App Backend...")
    print(f"📍 Server will run on: http://{settings.HOST}:{settings.PORT}")
    print(f"📚 Books directory: {settings.BOOKS_DIR}")
    print(f"🔑 Using Gemini model: {settings.GEMINI_MODEL}")
    print("=" * 50)
    
    try:
        uvicorn.run(
            "main:app",
            host=settings.HOST,
            port=settings.PORT,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
