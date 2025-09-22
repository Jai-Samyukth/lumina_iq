"""
API Gateway for Learning App Microservices
Routes requests to appropriate services with load balancing and rate limiting.
"""

import os
import time
import asyncio
import httpx
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional
import logging
from datetime import datetime

# Import shared modules
import sys
sys.path.append('/app/shared')

from database.config import db_manager, check_database_health
from cache.redis_config import redis_manager, check_redis_health

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Service URLs
SERVICE_URLS = {
    "pdf": os.getenv("PDF_SERVICE_URL", "http://pdf_service:8001"),
    "questions": os.getenv("QUESTION_SERVICE_URL", "http://question_service:8002"),
    "evaluation": os.getenv("EVALUATION_SERVICE_URL", "http://evaluation_service:8003"),
    "chat": os.getenv("CHAT_SERVICE_URL", "http://chat_service:8004"),
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth_service:8005"),
}

# HTTP client for service communication
http_client: Optional[httpx.AsyncClient] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global http_client
    
    # Startup
    logger.info("Starting API Gateway...")
    
    # Initialize HTTP client with connection pooling
    http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(60.0),  # 60 second timeout
        limits=httpx.Limits(
            max_keepalive_connections=100,
            max_connections=200,
            keepalive_expiry=30.0
        )
    )
    
    # Health checks
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()
    
    if not db_healthy:
        logger.error("Database health check failed")
    if not redis_healthy:
        logger.error("Redis health check failed")
    
    logger.info("API Gateway started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down API Gateway...")
    if http_client:
        await http_client.aclose()
    await redis_manager.close()
    logger.info("API Gateway shutdown complete")

app = FastAPI(
    title="Learning App API Gateway",
    version="2.0.0",
    description="Microservices API Gateway for Learning App",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rate limiting middleware
class RateLimitMiddleware:
    def __init__(self, requests_per_minute: int = 100):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1 minute
    
    async def __call__(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Get request count from Redis
        key = f"rate_limit:{client_ip}"
        try:
            count = await redis_manager.get(key) or 0
            
            if count >= self.requests_per_minute:
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Rate limit exceeded"}
                )
            
            # Increment counter
            await redis_manager.set(key, count + 1, ttl=self.window_size)
            
        except Exception as e:
            logger.error(f"Rate limiting error: {e}")
            # Continue without rate limiting if Redis is down
        
        response = await call_next(request)
        return response

# Add rate limiting middleware
app.middleware("http")(RateLimitMiddleware(requests_per_minute=200))

async def forward_request(
    service_name: str,
    path: str,
    request: Request,
    method: str = "GET",
    json_data: Any = None
) -> Dict[str, Any]:
    """Forward request to appropriate microservice"""
    if service_name not in SERVICE_URLS:
        raise HTTPException(status_code=404, detail=f"Service {service_name} not found")
    
    service_url = SERVICE_URLS[service_name]
    full_url = f"{service_url}{path}"
    
    # Prepare headers (forward relevant headers)
    headers = {
        "Content-Type": request.headers.get("Content-Type", "application/json"),
        "User-Agent": request.headers.get("User-Agent", "API-Gateway/2.0"),
        "X-Forwarded-For": request.client.host,
        "X-Gateway-Request-ID": f"gw-{int(time.time() * 1000)}"
    }
    
    # Forward authorization header if present
    if "authorization" in request.headers:
        headers["authorization"] = request.headers["authorization"]
    
    try:
        start_time = time.time()
        
        if method.upper() == "GET":
            response = await http_client.get(
                full_url,
                headers=headers,
                params=dict(request.query_params)
            )
        elif method.upper() == "POST":
            response = await http_client.post(
                full_url,
                headers=headers,
                json=json_data,
                params=dict(request.query_params)
            )
        elif method.upper() == "PUT":
            response = await http_client.put(
                full_url,
                headers=headers,
                json=json_data,
                params=dict(request.query_params)
            )
        elif method.upper() == "DELETE":
            response = await http_client.delete(
                full_url,
                headers=headers,
                params=dict(request.query_params)
            )
        else:
            raise HTTPException(status_code=405, detail="Method not allowed")
        
        response_time = time.time() - start_time
        
        # Log request
        logger.info(
            f"{method} {service_name}{path} -> {response.status_code} "
            f"({response_time:.3f}s)"
        )
        
        # Return response
        if response.status_code >= 400:
            raise HTTPException(
                status_code=response.status_code,
                detail=response.text
            )
        
        return response.json()
    
    except httpx.RequestError as e:
        logger.error(f"Service communication error: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service {service_name} unavailable"
        )
    except Exception as e:
        logger.error(f"Request forwarding error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Gateway health check"""
    db_healthy = await check_database_health()
    redis_healthy = await check_redis_health()
    
    # Check service health
    service_health = {}
    for service_name, service_url in SERVICE_URLS.items():
        try:
            response = await http_client.get(f"{service_url}/health", timeout=5.0)
            service_health[service_name] = response.status_code == 200
        except:
            service_health[service_name] = False
    
    overall_healthy = db_healthy and redis_healthy and all(service_health.values())
    
    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "database": db_healthy,
            "redis": redis_healthy,
            **service_health
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """API Gateway root endpoint"""
    return {
        "message": "Learning App API Gateway",
        "version": "2.0.0",
        "services": list(SERVICE_URLS.keys()),
        "timestamp": datetime.now().isoformat()
    }

# Authentication routes
@app.post("/api/auth/login")
async def login(request: Request):
    """Forward login request to auth service"""
    json_data = await request.json()
    return await forward_request("auth", "/api/auth/login", request, "POST", json_data)

@app.post("/api/auth/logout")
async def logout(request: Request):
    """Forward logout request to auth service"""
    return await forward_request("auth", "/api/auth/logout", request, "POST")

@app.get("/api/auth/me")
async def get_current_user(request: Request):
    """Forward user info request to auth service"""
    return await forward_request("auth", "/api/auth/me", request, "GET")

# PDF routes
@app.get("/api/pdf/list")
async def list_pdfs(request: Request):
    """Forward PDF list request to PDF service"""
    return await forward_request("pdf", "/api/pdf/list", request, "GET")

@app.post("/api/pdf/select")
async def select_pdf(request: Request):
    """Forward PDF selection to PDF service"""
    json_data = await request.json()
    return await forward_request("pdf", "/api/pdf/select", request, "POST", json_data)

@app.post("/api/pdf/upload")
async def upload_pdf(request: Request):
    """Forward PDF upload to PDF service"""
    # Note: File uploads need special handling
    return await forward_request("pdf", "/api/pdf/upload", request, "POST")

@app.get("/api/pdf/info")
async def get_pdf_info(request: Request):
    """Forward PDF info request to PDF service"""
    return await forward_request("pdf", "/api/pdf/info", request, "GET")

# Question generation routes
@app.post("/api/questions/generate")
async def generate_questions(request: Request):
    """Forward question generation to question service"""
    json_data = await request.json()
    return await forward_request("questions", "/api/questions/generate", request, "POST", json_data)

@app.get("/api/questions/status/{job_id}")
async def get_question_status(job_id: str, request: Request):
    """Get question generation job status"""
    return await forward_request("questions", f"/api/questions/status/{job_id}", request, "GET")

@app.get("/api/questions/result/{job_id}")
async def get_question_result(job_id: str, request: Request):
    """Get question generation result"""
    return await forward_request("questions", f"/api/questions/result/{job_id}", request, "GET")

# Evaluation routes
@app.post("/api/evaluation/answer")
async def evaluate_answer(request: Request):
    """Forward answer evaluation to evaluation service"""
    json_data = await request.json()
    return await forward_request("evaluation", "/api/evaluation/answer", request, "POST", json_data)

@app.post("/api/evaluation/quiz")
async def evaluate_quiz(request: Request):
    """Forward quiz evaluation to evaluation service"""
    json_data = await request.json()
    return await forward_request("evaluation", "/api/evaluation/quiz", request, "POST", json_data)

# Chat routes
@app.post("/api/chat/")
async def chat(request: Request):
    """Forward chat request to chat service"""
    json_data = await request.json()
    return await forward_request("chat", "/api/chat/", request, "POST", json_data)

@app.get("/api/chat/history")
async def get_chat_history(request: Request):
    """Forward chat history request to chat service"""
    return await forward_request("chat", "/api/chat/history", request, "GET")

@app.delete("/api/chat/history")
async def clear_chat_history(request: Request):
    """Forward chat history clear to chat service"""
    return await forward_request("chat", "/api/chat/history", request, "DELETE")

# System monitoring routes
@app.get("/api/system/stats")
async def get_system_stats():
    """Get system-wide statistics"""
    stats = {}
    
    # Get stats from each service
    for service_name, service_url in SERVICE_URLS.items():
        try:
            response = await http_client.get(f"{service_url}/stats", timeout=5.0)
            if response.status_code == 200:
                stats[service_name] = response.json()
        except:
            stats[service_name] = {"error": "Service unavailable"}
    
    return {
        "gateway": {
            "uptime": time.time(),
            "services": stats
        },
        "timestamp": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=1,
        loop="asyncio",
        access_log=True,
        log_level="info"
    )
