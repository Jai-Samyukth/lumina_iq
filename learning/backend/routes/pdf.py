from fastapi import APIRouter, UploadFile, File, HTTPException, Query, Request
from models.pdf import PDFListResponse, PDFSelectRequest, PDFUploadResponse
from services.pdf_service import PDFService
from utils.cache import cache_service
from typing import Optional
import hashlib

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

def get_simple_user_id(request: Request) -> str:
    """
    Create a simple user ID based on client IP to isolate users.
    Each user gets their own chat history and PDF context.
    Same function as in chat.py for consistency.
    """
    client_ip = request.client.host if request.client else "unknown"
    # Create a simple hash of the IP for session isolation
    user_id = hashlib.md5(client_ip.encode()).hexdigest()[:12]
    return f"user_{user_id}"

@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return (max 100)"),
    search: Optional[str] = Query(None, description="Search term to filter PDFs by title or filename")
):
    """List PDFs available in the books folder with pagination and optional search"""
    return await PDFService.list_pdfs(offset=offset, limit=limit, search=search)

@router.post("/select")
async def select_pdf(request: PDFSelectRequest, http_request: Request):
    """Select a PDF from the books folder for the current session"""
    user_session = get_simple_user_id(http_request)
    return await PDFService.select_pdf(request.filename, user_session)

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...), request: Request = None):
    """Upload a new PDF to the books folder"""
    user_session = get_simple_user_id(request)
    return await PDFService.upload_pdf(file, user_session)

@router.get("/metadata")
async def get_pdf_metadata(request: Request):
    """Get metadata of the currently selected PDF"""
    from utils.storage import pdf_metadata
    user_session = get_simple_user_id(request)
    if user_session not in pdf_metadata:
        raise HTTPException(status_code=400, detail="No PDF selected")
    return pdf_metadata[user_session]

@router.get("/metadata/{filename}")
async def get_full_pdf_metadata(filename: str):
    """Get full metadata for a specific PDF file (uses PyPDF2)"""
    from pathlib import Path
    from config.settings import settings
    
    books_dir = Path(settings.BOOKS_DIR)
    file_path = books_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="PDF file not found")
    
    if not file_path.suffix.lower() == '.pdf':
        raise HTTPException(status_code=400, detail="File is not a PDF")
    
    # Extract full metadata using PyPDF2
    metadata = await PDFService.get_pdf_metadata(str(file_path), extract_full_metadata=True)
    return metadata

@router.get("/info")
async def get_pdf_info(request: Request):
    """Get information about the currently selected PDF"""
    user_session = get_simple_user_id(request)
    return PDFService.get_pdf_info(user_session)

@router.get("/cache/info")
async def get_cache_info():
    """Get information about the PDF text extraction cache"""
    return cache_service.get_cache_info()

@router.delete("/cache/clear")
async def clear_cache():
    """Clear all cached PDF text extractions"""
    deleted_count = cache_service.clear_cache()
    return {
        "message": f"Successfully cleared cache",
        "deleted_files": deleted_count
    }
