from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from utils.security import verify_token
from services.book_service import BookService

router = APIRouter(prefix="/api/books", tags=["books"])

class BookSelectionRequest(BaseModel):
    title: str
    author: str

class BookSelectionResponse(BaseModel):
    message: str
    title: str
    author: str
    text_length: int
    cached_at: str
    metadata: Dict

class CachedBookInfo(BaseModel):
    title: str
    author: str
    text_length: int
    cached_at: str
    source: str

class CachedBooksResponse(BaseModel):
    books: List[CachedBookInfo]

@router.post("/select", response_model=BookSelectionResponse)
async def select_book(
    request: BookSelectionRequest,
    token: str = Depends(verify_token)
):
    """Select a book and cache its content for AI interactions"""
    try:
        result = await BookService.select_book(
            book_title=request.title,
            book_author=request.author,
            token=token
        )
        
        return BookSelectionResponse(
            message=result["message"],
            title=result["title"],
            author=result["author"],
            text_length=result["text_length"],
            cached_at=result["cached_at"],
            metadata=result["metadata"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/cached", response_model=CachedBooksResponse)
async def list_cached_books(token: str = Depends(verify_token)):
    """List all cached books"""
    try:
        books = BookService.list_cached_books()
        return CachedBooksResponse(
            books=[CachedBookInfo(**book) for book in books]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current")
async def get_current_book(token: str = Depends(verify_token)):
    """Get information about the currently selected book"""
    try:
        from services.pdf_service import PDFService
        return PDFService.get_pdf_info(token)
    except HTTPException as e:
        if e.status_code == 400:
            return {"message": "No book selected"}
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
