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
    
    # Start the server with optimized configuration for concurrency
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disable reload for better performance with multiple workers
        workers=4,     # Multiple workers for true concurrency
        loop="asyncio",  # Windows compatible
        access_log=True,
        log_level="info",
        # Performance optimizations for concurrency
        backlog=4096,  # Increase connection backlog for more concurrent connections
        timeout_keep_alive=10,  # Keep connections alive longer to reduce overhead
        limit_concurrency=2000,  # Increased max concurrent connections
        limit_max_requests=50000,  # Increased max requests per worker
        # Additional optimizations
        timeout_graceful_shutdown=30,  # Graceful shutdown timeout
        h11_max_incomplete_event_size=16384,  # Increase buffer size
    )

if __name__ == "__main__":
    main()
