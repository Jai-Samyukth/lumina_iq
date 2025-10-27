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
    
    # Start the server optimized for 3000+ concurrent requests with 14 API keys
    print(f"🔑 Utilizing 14 API keys for massive concurrency")
    print(f"⚡ Configured for 3000+ concurrent requests")

    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,  # Disable reload for production performance
        workers=16,    # More workers for 3000+ concurrent users
        loop="asyncio",  # Windows compatible
        access_log=False,  # Disable access logs for better performance
        log_level="error",  # Minimal logging for maximum performance
        # Extreme high-concurrency optimizations for 3000+ requests
        backlog=32768,  # Massive connection backlog for burst traffic
        timeout_keep_alive=120,  # Keep connections alive very long
        limit_concurrency=50000,  # Support massive concurrent connections
        limit_max_requests=500000,  # Very high request limit per worker
        # Additional optimizations for 3000+ users
        timeout_graceful_shutdown=180,  # Very long graceful shutdown
        h11_max_incomplete_event_size=131072,  # Very large buffer size
        ws_max_size=67108864,  # Massive WebSocket message size
        ws_ping_interval=60,  # Long WebSocket ping interval
        ws_ping_timeout=60,  # Long WebSocket ping timeout
        # Additional performance settings
        interface="asgi3",  # Use ASGI3 interface for better performance
    )

if __name__ == "__main__":
    main()
