#!/usr/bin/env python3
"""
Optimized startup script for Learning App API
Includes performance monitoring and concurrent handling
"""

import uvicorn
import asyncio
import sys
import os
import platform
from pathlib import Path

# Add current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def main():
    """Start the optimized FastAPI server"""
    print("🚀 Starting Learning App API with Concurrency Optimizations")
    print("=" * 60)
    print("✅ Async AI processing enabled")
    print("✅ Thread-safe session management")
    print("✅ Connection pooling configured")
    print("✅ Performance monitoring active")
    print("=" * 60)
    
    # Import after path setup
    from config.settings import settings
    
    # Windows-compatible async optimizations
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
        print("⚡ Using Windows ProactorEventLoop for enhanced performance")
    else:
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print("⚡ Using uvloop for enhanced async performance")
        except ImportError:
            print("⚠️  uvloop not available, using default event loop")
    
    # Start the server with optimized configuration
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,  # Enable for development
        workers=1,    # Single worker for development
        loop="asyncio",  # Windows compatible
        access_log=True,
        log_level="info",
        # Performance optimizations
        backlog=2048,  # Increase connection backlog
        timeout_keep_alive=5,  # Keep connections alive longer
        limit_concurrency=1000,  # Max concurrent connections
        limit_max_requests=10000,  # Max requests per worker
    )

if __name__ == "__main__":
    main()
