"""
Shared database models for the Learning App microservices architecture.
These models define the database schema for all services.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class User(Base):
    """User model for authentication and session management"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    sessions = relationship("UserSession", back_populates="user")
    pdfs = relationship("PDF", back_populates="user")
    chat_sessions = relationship("ChatSession", back_populates="user")

class UserSession(Base):
    """User session model for authentication tracking"""
    __tablename__ = "user_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="sessions")

class PDF(Base):
    """PDF document model"""
    __tablename__ = "pdfs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)  # For caching
    
    # Metadata
    title = Column(String(500), nullable=True)
    author = Column(String(255), nullable=True)
    subject = Column(String(500), nullable=True)
    pages = Column(Integer, nullable=True)
    
    # Processing status
    is_processed = Column(Boolean, default=False)
    processing_error = Column(Text, nullable=True)
    
    # Timestamps
    uploaded_at = Column(DateTime, default=func.now())
    processed_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="pdfs")
    extracted_text = relationship("PDFExtractedText", back_populates="pdf", uselist=False)
    questions = relationship("Question", back_populates="pdf")
    chat_sessions = relationship("ChatSession", back_populates="pdf")

class PDFExtractedText(Base):
    """Extracted text content from PDFs with caching"""
    __tablename__ = "pdf_extracted_text"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False, unique=True)
    extracted_text = Column(Text, nullable=False)
    text_length = Column(Integer, nullable=False)
    extraction_method = Column(String(50), nullable=False)  # 'pypdf2' or 'pdfplumber'
    extracted_at = Column(DateTime, default=func.now())
    
    # Relationships
    pdf = relationship("PDF", back_populates="extracted_text")

class Question(Base):
    """Generated questions from PDFs"""
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False)
    question_set_id = Column(String, nullable=False, index=True)  # Groups questions from same generation
    
    # Question content
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # 'mcq' or 'open_ended'
    topic = Column(String(255), nullable=True)
    difficulty_level = Column(String(20), nullable=True)  # 'easy', 'medium', 'hard'
    
    # MCQ specific fields
    options = Column(JSON, nullable=True)  # Array of options for MCQ
    correct_answer = Column(String(10), nullable=True)  # 'A', 'B', 'C', 'D' for MCQ
    
    # Generation metadata
    generation_parameters = Column(JSON, nullable=True)  # Store generation params for caching
    cache_key = Column(String(64), nullable=False, index=True)  # For caching identical requests
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    pdf = relationship("PDF", back_populates="questions")
    evaluations = relationship("Evaluation", back_populates="question")

class ChatSession(Base):
    """Chat sessions between users and AI"""
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False)
    session_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="chat_sessions")
    pdf = relationship("PDF", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session")

class ChatMessage(Base):
    """Individual chat messages"""
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())
    
    # AI response metadata
    ai_model = Column(String(50), nullable=True)
    response_time = Column(Float, nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")

class Evaluation(Base):
    """Answer evaluations and quiz results"""
    __tablename__ = "evaluations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    question_id = Column(String, ForeignKey("questions.id"), nullable=False)
    
    # Answer content
    user_answer = Column(Text, nullable=False)
    score = Column(Integer, nullable=False)  # 0-10
    max_score = Column(Integer, default=10)
    
    # Evaluation details
    feedback = Column(Text, nullable=True)
    suggestions = Column(Text, nullable=True)
    correct_answer_hint = Column(Text, nullable=True)
    evaluation_level = Column(String(20), nullable=False)  # 'easy', 'medium', 'strict'
    
    # Processing metadata
    evaluation_time = Column(Float, nullable=True)  # Time taken to evaluate
    ai_model = Column(String(50), nullable=True)
    cache_hit = Column(Boolean, default=False)
    
    # Timestamps
    evaluated_at = Column(DateTime, default=func.now())
    
    # Relationships
    question = relationship("Question", back_populates="evaluations")

class QuizSession(Base):
    """Quiz sessions for tracking complete quiz attempts"""
    __tablename__ = "quiz_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    pdf_id = Column(String, ForeignKey("pdfs.id"), nullable=False)
    question_set_id = Column(String, nullable=False)  # Links to questions used
    
    # Quiz metadata
    topic = Column(String(255), nullable=True)
    total_questions = Column(Integer, nullable=False)
    evaluation_level = Column(String(20), nullable=False)
    
    # Results
    total_score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    percentage = Column(Float, nullable=False)
    grade = Column(String(2), nullable=False)  # 'A', 'B', 'C', 'D', 'F'
    
    # AI-generated feedback
    overall_feedback = Column(Text, nullable=True)
    study_suggestions = Column(JSON, nullable=True)  # Array of suggestions
    strengths = Column(JSON, nullable=True)  # Array of strengths
    areas_for_improvement = Column(JSON, nullable=True)  # Array of areas
    
    # Timestamps
    started_at = Column(DateTime, default=func.now())
    completed_at = Column(DateTime, nullable=True)
    
class CacheEntry(Base):
    """Generic caching table for various cached data"""
    __tablename__ = "cache_entries"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String(255), unique=True, nullable=False, index=True)
    cache_type = Column(String(50), nullable=False, index=True)  # 'question_gen', 'evaluation', 'pdf_text'
    data = Column(JSON, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    accessed_at = Column(DateTime, default=func.now())
    access_count = Column(Integer, default=1)

class BackgroundJob(Base):
    """Background job tracking for async operations"""
    __tablename__ = "background_jobs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(50), nullable=False, index=True)  # 'question_generation', 'evaluation'
    status = Column(String(20), nullable=False, index=True)  # 'pending', 'running', 'completed', 'failed'
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Job parameters
    parameters = Column(JSON, nullable=False)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Progress tracking
    progress_percentage = Column(Integer, default=0)
    progress_message = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Celery task ID for tracking
    celery_task_id = Column(String(255), nullable=True, index=True)
