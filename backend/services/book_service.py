import os
import json
import hashlib
from pathlib import Path
from datetime import datetime
from fastapi import HTTPException
from typing import Dict, List, Optional
from config.settings import settings
from services.pdf_service import PDFService
from utils.storage import pdf_contexts, pdf_metadata

class BookService:
    @staticmethod
    def get_cache_path(book_title: str) -> Path:
        """Generate cache file path for a book"""
        # Create a safe filename from book title
        safe_title = "".join(c for c in book_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')
        
        # Create hash for uniqueness
        title_hash = hashlib.md5(book_title.encode()).hexdigest()[:8]
        cache_filename = f"{safe_title}_{title_hash}.json"
        
        cache_dir = Path(settings.BASE_DIR) / "cache" / "books"
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        return cache_dir / cache_filename

    @staticmethod
    async def extract_and_cache_book_text(book_title: str, book_author: str = "Unknown") -> Dict:
        """Extract text from a book and cache it"""
        try:
            # Check if we have a corresponding PDF file
            books_dir = Path(settings.BOOKS_DIR)
            pdf_file = None
            
            # Try to find a matching PDF file
            for file_path in books_dir.glob("*.pdf"):
                if book_title.lower() in file_path.stem.lower():
                    pdf_file = file_path
                    break
            
            if not pdf_file:
                # Create a mock text content for demo books
                mock_content = f"""
# {book_title}
By {book_author}

This is a sample book content for "{book_title}". In a real implementation, this would contain the actual book text extracted from PDF files or other sources.

## Chapter 1: Introduction
This book covers various topics related to the subject matter. The content would be extracted from the actual PDF file if available.

## Chapter 2: Main Content
Here you would find the detailed content of the book, including:
- Key concepts and ideas
- Examples and case studies
- Practical applications
- Important insights

## Chapter 3: Conclusion
The book concludes with important takeaways and recommendations for further reading.

This is a demonstration of how the book content would be cached and used for AI interactions.
                """.strip()
                
                cache_data = {
                    "title": book_title,
                    "author": book_author,
                    "content": mock_content,
                    "text_length": len(mock_content),
                    "cached_at": datetime.now().isoformat(),
                    "source": "mock_content",
                    "metadata": {
                        "title": book_title,
                        "author": book_author,
                        "pages": 10,
                        "file_size": len(mock_content.encode()),
                        "subject": "General",
                        "creator": "LuminaIQ-AI",
                        "producer": "Book Service"
                    }
                }
            else:
                # Extract text from PDF
                text_content = await PDFService.extract_text_from_pdf(str(pdf_file))
                metadata = await PDFService.get_pdf_metadata(str(pdf_file))
                
                cache_data = {
                    "title": book_title,
                    "author": book_author,
                    "content": text_content,
                    "text_length": len(text_content),
                    "cached_at": datetime.now().isoformat(),
                    "source": "pdf_extraction",
                    "pdf_file": str(pdf_file),
                    "metadata": metadata
                }
            
            # Save to cache
            cache_path = BookService.get_cache_path(book_title)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"Book '{book_title}' cached successfully at {cache_path}")
            return cache_data
            
        except Exception as e:
            print(f"Error caching book '{book_title}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to cache book: {str(e)}")

    @staticmethod
    def get_cached_book(book_title: str) -> Optional[Dict]:
        """Get cached book content"""
        try:
            cache_path = BookService.get_cache_path(book_title)
            if cache_path.exists():
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return None
        except Exception as e:
            print(f"Error reading cached book '{book_title}': {str(e)}")
            return None

    @staticmethod
    async def select_book(book_title: str, book_author: str, token: str) -> Dict:
        """Select a book and ensure its content is cached"""
        try:
            # Check if book is already cached
            cached_book = BookService.get_cached_book(book_title)
            
            if not cached_book:
                # Extract and cache the book
                cached_book = await BookService.extract_and_cache_book_text(book_title, book_author)
            
            # Store in session for AI context
            pdf_contexts[token] = {
                "filename": f"{book_title}.pdf",
                "content": cached_book["content"],
                "selected_at": datetime.now().isoformat(),
                "book_title": book_title,
                "book_author": book_author,
                "source": "book_selection"
            }
            
            pdf_metadata[token] = cached_book["metadata"]
            
            return {
                "message": "Book selected successfully",
                "title": book_title,
                "author": book_author,
                "text_length": cached_book["text_length"],
                "cached_at": cached_book["cached_at"],
                "metadata": cached_book["metadata"]
            }
            
        except Exception as e:
            print(f"Error selecting book '{book_title}': {str(e)}")
            raise HTTPException(status_code=500, detail=f"Failed to select book: {str(e)}")

    @staticmethod
    def list_cached_books() -> List[Dict]:
        """List all cached books"""
        try:
            cache_dir = Path(settings.BASE_DIR) / "cache" / "books"
            if not cache_dir.exists():
                return []
            
            books = []
            for cache_file in cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        book_data = json.load(f)
                        books.append({
                            "title": book_data["title"],
                            "author": book_data["author"],
                            "text_length": book_data["text_length"],
                            "cached_at": book_data["cached_at"],
                            "source": book_data.get("source", "unknown")
                        })
                except Exception as e:
                    print(f"Error reading cache file {cache_file}: {str(e)}")
                    continue
            
            return books
        except Exception as e:
            print(f"Error listing cached books: {str(e)}")
            return []
