import os
import PyPDF2
import pdfplumber
import aiofiles
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException, UploadFile
from typing import List
from config.settings import settings
from utils.storage import pdf_contexts, pdf_metadata
from utils.cache import cache_service
from models.pdf import PDFInfo, PDFListResponse, PDFUploadResponse, PDFMetadata

class PDFService:
    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> str:
        print(f"Processing PDF: {file_path}")

        # Check cache first
        cached_text = await cache_service.get_cached_text(file_path)
        if cached_text is not None:
            print(f"Using cached text for {file_path} ({len(cached_text)} characters)")
            return cached_text

        # Cache miss - extract text from PDF
        text = ""
        print(f"Cache miss - extracting text from PDF: {file_path}")

        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                print(f"PDF has {len(pdf_reader.pages)} pages")

                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                        print(f"Page {i+1}: extracted {len(page_text)} characters")
                    else:
                        print(f"Page {i+1}: no text extracted")

        except Exception as e:
            print(f"PyPDF2 extraction failed: {e}, trying pdfplumber...")
            # Fallback to pdfplumber
            try:
                with pdfplumber.open(file_path) as pdf:
                    print(f"PDF has {len(pdf.pages)} pages (pdfplumber)")

                    for i, page in enumerate(pdf.pages):
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                            print(f"Page {i+1}: extracted {len(page_text)} characters (pdfplumber)")
                        else:
                            print(f"Page {i+1}: no text extracted (pdfplumber)")

            except Exception as e2:
                print(f"Both extraction methods failed: PyPDF2={e}, pdfplumber={e2}")
                raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {str(e2)}")

        extracted_text = text.strip()
        print(f"Total extracted text: {len(extracted_text)} characters")

        if len(extracted_text) < 50:
            print("Warning: Very little text extracted from PDF")
            print(f"Extracted content: '{extracted_text[:100]}'")

        # Save to cache for future use
        cache_saved = await cache_service.save_to_cache(file_path, extracted_text)
        if cache_saved:
            print(f"Successfully cached extracted text for {file_path}")
        else:
            print(f"Failed to cache extracted text for {file_path}")

        return extracted_text

    @staticmethod
    async def get_pdf_metadata(file_path: str) -> dict:
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                metadata = {
                    "title": pdf_reader.metadata.get('/Title', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "author": pdf_reader.metadata.get('/Author', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "subject": pdf_reader.metadata.get('/Subject', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "creator": pdf_reader.metadata.get('/Creator', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "producer": pdf_reader.metadata.get('/Producer', 'Unknown') if pdf_reader.metadata else 'Unknown',
                    "creation_date": str(pdf_reader.metadata.get('/CreationDate', 'Unknown')) if pdf_reader.metadata else 'Unknown',
                    "modification_date": str(pdf_reader.metadata.get('/ModDate', 'Unknown')) if pdf_reader.metadata else 'Unknown',
                    "pages": len(pdf_reader.pages),
                    "file_size": os.path.getsize(file_path)
                }
                return metadata
        except Exception as e:
            return {
                "title": "Unknown",
                "author": "Unknown", 
                "subject": "Unknown",
                "creator": "Unknown",
                "producer": "Unknown",
                "creation_date": "Unknown",
                "modification_date": "Unknown",
                "pages": 0,
                "file_size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }

    @staticmethod
    async def list_pdfs() -> PDFListResponse:
        """List all PDFs in the books folder"""
        books_dir = Path(settings.BOOKS_DIR)
        if not books_dir.exists():
            books_dir.mkdir(exist_ok=True)
            return PDFListResponse(pdfs=[])
        
        pdfs = []
        for file_path in books_dir.glob("*.pdf"):
            try:
                metadata = await PDFService.get_pdf_metadata(str(file_path))
                pdf_info = PDFInfo(
                    filename=file_path.name,
                    title=metadata.get("title", "Unknown"),
                    author=metadata.get("author", "Unknown"),
                    pages=metadata.get("pages", 0),
                    file_size=metadata.get("file_size", 0),
                    file_path=str(file_path)
                )
                pdfs.append(pdf_info)
            except Exception as e:
                # Skip files that can't be processed
                continue
        
        return PDFListResponse(pdfs=pdfs)

    @staticmethod
    async def select_pdf(filename: str, token: str) -> dict:
        """Select a PDF from the books folder for the session"""
        books_dir = Path(settings.BOOKS_DIR)
        file_path = books_dir / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="PDF file not found")
        
        if not file_path.suffix.lower() == '.pdf':
            raise HTTPException(status_code=400, detail="File is not a PDF")
        
        try:
            # Extract text and metadata
            text_content = await PDFService.extract_text_from_pdf(str(file_path))
            metadata = await PDFService.get_pdf_metadata(str(file_path))
            
            # Store in session
            pdf_contexts[token] = {
                "filename": filename,
                "content": text_content,
                "selected_at": datetime.now().isoformat()
            }
            pdf_metadata[token] = metadata
            
            return {
                "message": "PDF selected successfully",
                "filename": filename,
                "metadata": metadata,
                "text_length": len(text_content)
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    @staticmethod
    async def upload_pdf(file: UploadFile, token: str) -> PDFUploadResponse:
        """Upload a new PDF to the books folder"""
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")

        # Create books directory if it doesn't exist
        books_dir = Path(settings.BOOKS_DIR)
        books_dir.mkdir(exist_ok=True)

        # Save file
        file_path = books_dir / file.filename
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Extract text and metadata
        try:
            text_content = await PDFService.extract_text_from_pdf(str(file_path))
            metadata = await PDFService.get_pdf_metadata(str(file_path))

            # Store in memory (replace with database in production)
            pdf_contexts[token] = {
                "filename": file.filename,
                "content": text_content,
                "uploaded_at": datetime.now().isoformat()
            }
            pdf_metadata[token] = metadata

            return PDFUploadResponse(
                message="PDF uploaded and processed successfully",
                filename=file.filename,
                metadata=metadata,
                text_length=len(text_content)
            )

        except Exception as e:
            # Clean up file if processing failed
            if file_path.exists():
                file_path.unlink()
            raise HTTPException(status_code=500, detail=f"Failed to process PDF: {str(e)}")

    @staticmethod
    def get_pdf_info(token: str) -> dict:
        """Get info about the currently selected PDF"""
        if token not in pdf_contexts:
            raise HTTPException(status_code=400, detail="No PDF selected")

        pdf_context = pdf_contexts[token]
        metadata = pdf_metadata.get(token, {})

        return {
            "filename": pdf_context["filename"],
            "selected_at": pdf_context.get("selected_at") or pdf_context.get("uploaded_at"),
            "text_length": len(pdf_context["content"]),
            "metadata": metadata
        }
