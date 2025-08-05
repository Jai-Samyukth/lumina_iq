from pydantic import BaseModel
from typing import List, Optional

class PDFInfo(BaseModel):
    filename: str
    title: str
    author: str
    pages: int
    file_size: int
    file_path: str

class PDFListResponse(BaseModel):
    items: List[PDFInfo]  # Changed from 'pdfs' to 'items' for consistency
    total: int
    offset: int
    limit: int

class PDFSelectRequest(BaseModel):
    filename: str

class PDFUploadResponse(BaseModel):
    message: str
    filename: str
    metadata: dict
    text_length: int

class PDFMetadata(BaseModel):
    title: str
    author: str
    subject: str
    creator: str
    producer: str
    creation_date: str
    modification_date: str
    pages: int
    file_size: int
