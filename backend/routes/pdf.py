from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from models.pdf import PDFListResponse, PDFSelectRequest, PDFUploadResponse
from services.pdf_service import PDFService
from utils.security import verify_token

router = APIRouter(prefix="/api/pdf", tags=["pdf"])

@router.get("/list", response_model=PDFListResponse)
async def list_pdfs(token: str = Depends(verify_token)):
    """List all PDFs available in the books folder"""
    return await PDFService.list_pdfs()

@router.post("/select")
async def select_pdf(
    request: PDFSelectRequest,
    token: str = Depends(verify_token)
):
    """Select a PDF from the books folder for the current session"""
    return await PDFService.select_pdf(request.filename, token)

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_pdf(
    file: UploadFile = File(...),
    token: str = Depends(verify_token)
):
    """Upload a new PDF to the books folder"""
    return await PDFService.upload_pdf(file, token)

@router.get("/metadata")
async def get_pdf_metadata(token: str = Depends(verify_token)):
    """Get metadata of the currently selected PDF"""
    from utils.storage import pdf_metadata
    if token not in pdf_metadata:
        raise HTTPException(status_code=400, detail="No PDF selected")
    return pdf_metadata[token]

@router.get("/info")
async def get_pdf_info(token: str = Depends(verify_token)):
    """Get information about the currently selected PDF"""
    return PDFService.get_pdf_info(token)
