from fastapi import APIRouter, UploadFile, File, HTTPException
from models.pdf import PDFListResponse, PDFSelectRequest, PDFUploadResponse
from services.pdf_service import PDFService

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

# Use a simple session key for PDF operations
DEFAULT_SESSION = "default_user"

@router.get("/list", response_model=PDFListResponse)
async def list_pdfs():
    """List all PDFs available in the books folder"""
    return await PDFService.list_pdfs()

@router.post("/select")
async def select_pdf(request: PDFSelectRequest):
    """Select a PDF from the books folder for the current session"""
    return await PDFService.select_pdf(request.filename, DEFAULT_SESSION)

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a new PDF to the books folder"""
    return await PDFService.upload_pdf(file, DEFAULT_SESSION)

@router.get("/metadata")
async def get_pdf_metadata():
    """Get metadata of the currently selected PDF"""
    from utils.storage import pdf_metadata
    if DEFAULT_SESSION not in pdf_metadata:
        raise HTTPException(status_code=400, detail="No PDF selected")
    return pdf_metadata[DEFAULT_SESSION]

@router.get("/info")
async def get_pdf_info():
    """Get information about the currently selected PDF"""
    return PDFService.get_pdf_info(DEFAULT_SESSION)
