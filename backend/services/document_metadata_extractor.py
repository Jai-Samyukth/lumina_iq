"""
Document Metadata Extractor Service
Extracts rich structural metadata from documents for advanced RAG
"""
from typing import Dict, List, Any, Optional, Tuple
import re
from utils.logger import chat_logger


class DocumentMetadataExtractor:
    """
    Extract structural metadata from documents:
    - Chapter numbers and titles
    - Section numbers and titles
    - Page numbers
    - Heading hierarchy
    - Content type (definition, example, theory, etc.)
    """
    
    # Patterns for detecting chapters
    CHAPTER_PATTERNS = [
        r'(?i)^chapter\s+(\d+)[:\s]+(.+?)$',
        r'(?i)^chapter\s+(\d+)(?:\s|$)',
        r'(?i)^ch\.\s*(\d+)[:\s]+(.+?)$',
        r'(?i)^(\d+)\.\s+(.+?)(?:chapter)?$',
        r'(?i)^unit\s+(\d+)[:\s]+(.+?)$',
        r'(?i)^lesson\s+(\d+)[:\s]+(.+?)$',
    ]
    
    # Patterns for detecting sections
    SECTION_PATTERNS = [
        r'(?i)^section\s+(\d+(?:\.\d+)?)[:\s]+(.+?)$',
        r'(?i)^(\d+\.\d+)[:\s]+(.+?)$',
        r'(?i)^(\d+\.\d+\.\d+)[:\s]+(.+?)$',
    ]
    
    # Patterns for page numbers
    PAGE_PATTERNS = [
        r'(?i)page\s+(\d+)',
        r'(?i)p\.\s*(\d+)',
        r'(?i)\[(\d+)\]',
    ]
    
    # Content type indicators
    CONTENT_TYPE_INDICATORS = {
        'definition': [
            'is defined as', 'is called', 'refers to', 'is known as',
            'definition:', 'def:', 'means that', 'is a term'
        ],
        'example': [
            'for example', 'for instance', 'e.g.', 'such as',
            'example:', 'consider', 'suppose', 'let us'
        ],
        'theorem': [
            'theorem', 'lemma', 'corollary', 'proposition',
            'proof:', 'we prove', 'to prove'
        ],
        'formula': [
            '=', '≈', '≠', '≤', '≥', '∑', '∫', '∂',
            'formula:', 'equation:', 'where:'
        ],
        'concept': [
            'important', 'key concept', 'fundamental', 'essential',
            'note that', 'remember', 'it is important'
        ],
        'application': [
            'application', 'used to', 'applied in', 'practical',
            'in practice', 'real world', 'use case'
        ],
        'summary': [
            'in summary', 'to summarize', 'in conclusion', 'overall',
            'key points', 'main ideas', 'recap'
        ]
    }
    
    @staticmethod
    def extract_chapter_info(text: str) -> Optional[Tuple[int, str]]:
        """
        Extract chapter number and title from text.
        
        Returns:
            Tuple of (chapter_number, chapter_title) or None
        """
        for pattern in DocumentMetadataExtractor.CHAPTER_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                try:
                    chapter_num = int(match.group(1))
                    chapter_title = match.group(2).strip() if len(match.groups()) > 1 else f"Chapter {chapter_num}"
                    return (chapter_num, chapter_title)
                except (ValueError, IndexError):
                    continue
        return None
    
    @staticmethod
    def extract_section_info(text: str) -> Optional[Tuple[str, str]]:
        """
        Extract section number and title from text.
        
        Returns:
            Tuple of (section_number, section_title) or None
        """
        for pattern in DocumentMetadataExtractor.SECTION_PATTERNS:
            match = re.search(pattern, text, re.MULTILINE)
            if match:
                try:
                    section_num = match.group(1)
                    section_title = match.group(2).strip() if len(match.groups()) > 1 else f"Section {section_num}"
                    return (section_num, section_title)
                except IndexError:
                    continue
        return None
    
    @staticmethod
    def extract_page_number(text: str) -> Optional[int]:
        """Extract page number from text."""
        for pattern in DocumentMetadataExtractor.PAGE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue
        return None
    
    @staticmethod
    def detect_content_type(text: str) -> List[str]:
        """
        Detect content types present in text.
        
        Returns:
            List of content types found (can be multiple)
        """
        content_types = []
        text_lower = text.lower()
        
        for content_type, indicators in DocumentMetadataExtractor.CONTENT_TYPE_INDICATORS.items():
            for indicator in indicators:
                if indicator in text_lower:
                    content_types.append(content_type)
                    break  # Found this type, move to next
        
        # Default to 'content' if no specific type found
        if not content_types:
            content_types.append('content')
        
        return content_types
    
    @staticmethod
    def detect_heading_level(line: str) -> Optional[int]:
        """
        Detect if line is a heading and its level.
        
        Returns:
            Heading level (1-6) or None
        """
        line = line.strip()
        
        # Check for markdown-style headings
        if line.startswith('#'):
            level = 0
            for char in line:
                if char == '#':
                    level += 1
                else:
                    break
            return min(level, 6)
        
        # Check for numbered headings (1., 1.1, 1.1.1, etc.)
        number_match = re.match(r'^(\d+(?:\.\d+)*)\s', line)
        if number_match:
            dots = number_match.group(1).count('.')
            return min(dots + 1, 6)
        
        # Check for all-caps (potential heading)
        if line.isupper() and len(line) > 5 and len(line) < 100:
            return 2
        
        return None
    
    @staticmethod
    def extract_metadata_from_chunk(
        chunk_text: str,
        chunk_index: int,
        total_chunks: int,
        document_name: str,
        context_before: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from a chunk.
        
        Args:
            chunk_text: The text content of the chunk
            chunk_index: Index of this chunk in the document
            total_chunks: Total number of chunks in document
            document_name: Name of the document
            context_before: Text before this chunk for context
            
        Returns:
            Dictionary with extracted metadata
        """
        metadata = {
            "chunk_index": chunk_index,
            "sequential_id": chunk_index,
            "total_chunks": total_chunks,
            "document_name": document_name,
            "chunk_position": f"{chunk_index + 1}/{total_chunks}",
            "is_first": chunk_index == 0,
            "is_last": chunk_index == total_chunks - 1
        }
        
        # Extract chapter information
        chapter_info = DocumentMetadataExtractor.extract_chapter_info(chunk_text)
        if not chapter_info and context_before:
            # Try to find chapter in context
            chapter_info = DocumentMetadataExtractor.extract_chapter_info(context_before)
        
        if chapter_info:
            metadata["chapter_number"] = chapter_info[0]
            metadata["chapter_title"] = chapter_info[1]
        else:
            metadata["chapter_number"] = None
            metadata["chapter_title"] = None
        
        # Extract section information
        section_info = DocumentMetadataExtractor.extract_section_info(chunk_text)
        if section_info:
            metadata["section_number"] = section_info[0]
            metadata["section_title"] = section_info[1]
        else:
            metadata["section_number"] = None
            metadata["section_title"] = None
        
        # Extract page number
        page_num = DocumentMetadataExtractor.extract_page_number(chunk_text)
        if page_num:
            metadata["page_number"] = page_num
        else:
            metadata["page_number"] = None
        
        # Detect content types
        content_types = DocumentMetadataExtractor.detect_content_type(chunk_text)
        metadata["content_types"] = content_types
        metadata["primary_content_type"] = content_types[0] if content_types else "content"
        
        # Detect if contains headings
        lines = chunk_text.split('\n')
        heading_levels = []
        for line in lines[:5]:  # Check first 5 lines
            level = DocumentMetadataExtractor.detect_heading_level(line)
            if level:
                heading_levels.append(level)
        
        metadata["has_headings"] = len(heading_levels) > 0
        metadata["min_heading_level"] = min(heading_levels) if heading_levels else None
        
        # Calculate text statistics
        metadata["char_count"] = len(chunk_text)
        metadata["word_count"] = len(chunk_text.split())
        metadata["sentence_count"] = len(re.findall(r'[.!?]+', chunk_text))
        
        # Detect if contains lists or bullet points
        metadata["has_lists"] = bool(re.search(r'^\s*[-•*]\s', chunk_text, re.MULTILINE))
        
        # Detect if contains code or technical content
        metadata["has_code"] = bool(re.search(r'```|`|def |class |function|import |#include', chunk_text))
        
        # Detect if contains questions
        metadata["has_questions"] = bool(re.search(r'\?', chunk_text))
        
        return metadata
    
    @staticmethod
    def propagate_chapter_metadata(chunks_metadata: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Propagate chapter/section info forward through chunks that don't have it.
        Chunks inherit chapter/section from previous chunks.
        
        Args:
            chunks_metadata: List of chunk metadata dictionaries
            
        Returns:
            Updated list with propagated metadata
        """
        current_chapter = None
        current_chapter_title = None
        current_section = None
        current_section_title = None
        
        for metadata in chunks_metadata:
            # Update current chapter if this chunk has one
            if metadata.get("chapter_number"):
                current_chapter = metadata["chapter_number"]
                current_chapter_title = metadata["chapter_title"]
            # Otherwise inherit from previous
            elif current_chapter:
                metadata["chapter_number"] = current_chapter
                metadata["chapter_title"] = current_chapter_title
            
            # Update current section if this chunk has one
            if metadata.get("section_number"):
                current_section = metadata["section_number"]
                current_section_title = metadata["section_title"]
            # Otherwise inherit from previous
            elif current_section:
                metadata["section_number"] = current_section
                metadata["section_title"] = current_section_title
        
        return chunks_metadata


document_metadata_extractor = DocumentMetadataExtractor()
