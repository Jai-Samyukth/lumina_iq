import hashlib
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
import logging

# Setup logging
pdf_logger = logging.getLogger("pdf_logger")
pdf_logger.setLevel(logging.DEBUG)
handler = RichHandler()
handler.setLevel(logging.DEBUG)
pdf_logger.addHandler(handler)

class FileHashService:
    """Service for calculating file hashes to detect duplicate uploads"""
    
    @staticmethod
    def calculate_file_hash(file_path: str, algorithm: str = "sha256") -> Optional[str]:
        """
        Calculate hash of a file

        Args:
            file_path: Path to the file
            algorithm: Hash algorithm to use (md5, sha1, sha256)
            
        Returns:
            Hexadecimal hash string or None if error occurs
        """
        if not Path(file_path).exists():
            pdf_logger.error(f"File not found: {file_path}")
            return None
            
        try:
            hash_obj = hashlib.new(algorithm)
            
            # Read file in chunks to handle large files
            with open(file_path, 'rb') as f:
                while chunk := f.read(8192):
                    hash_obj.update(chunk)
            
            file_hash = hash_obj.hexdigest()
            pdf_logger.debug(f"Calculated {algorithm} hash for {file_path}: {file_hash[:16]}...")
            return file_hash
            
        except Exception as e:
            pdf_logger.error(f"Failed to calculate hash for {file_path}: {str(e)}")
            return None
    
    @staticmethod
    def calculate_content_hash(content: bytes, algorithm: str = "sha256") -> Optional[str]:
        """
        Calculate hash of content bytes

        Args:
            content: File content as bytes
            algorithm: Hash algorithm to use (md5, sha1, sha256)
            
        Returns:
            Hexadecimal hash string or None if error occurs
        """
        try:
            hash_obj = hashlib.new(algorithm)
            hash_obj.update(content)
            return hash_obj.hexdigest()
        except Exception as e:
            pdf_logger.error(f"Failed to calculate content hash: {str(e)}")
            return None
