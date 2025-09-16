# The entire software project is a comprehensive AI-powered learning assistant called \*\*Lumina IQ\*\* that enables users to interact with PDF documents through multiple learning modalities. Below is a detailed explanation of its architecture, components, and functionality.

# 

# \## Overview

# Lumina IQ is a full-stack web application built with:

# \- \*\*Backend\*\*: Python FastAPI (version 1.0.0) serving as the API layer

# \- \*\*Frontend\*\*: Next.js with TypeScript and Tailwind CSS for the user interface

# \- \*\*AI Integration\*\*: Google Gemini for natural language processing and document understanding

# \- \*\*Additional Components\*\*: API key rotation system, caching layer, and logging framework

# 

# \## Core Architecture

# 

# \### Backend (FastAPI)

# The backend handles all server-side logic and API endpoints:

# 

# \#### Authentication Service (`backend/routes/auth.py`)

# \- Simple verification endpoint `/verify`

# \- Manages user authentication state

# 

# \#### PDF Service (`backend/routes/pdf.py`)  

# \- File upload handling with validation

# \- PDF text extraction and metadata parsing

# \- PDF listing and selection

# \- Cache management and clearing

# \- Error handling for unsupported formats

# 

# \#### Chat Service (`backend/routes/chat.py`)

# \- Real-time conversation with AI about PDF content

# \- Chat history persistence per session

# \- Question generation from PDF content

# \- Answer evaluation and scoring

# \- Quiz generation and scoring

# \- Performance monitoring and statistics

# \- Integration with Gemini AI models via rotated API keys

# 

# \#### Services Layer (`backend/services/`)

# \- \*\*auth\_service.py\*\*: Authentication logic

# \- \*\*chat\_service.py\*\*: Gemini integration, conversation management

# \- \*\*pdf\_service.py\*\*: PDF processing, text extraction cache

# 

# \#### Utilities (`backend/utils/`)

# \- \*\*cache.py\*\*: Caching system for PDF content and responses

# \- \*\*ip\_detector.py\*\*: Client IP detection for security

# \- \*\*logger.py\*\*: Structured logging with multiple log files

# \- \*\*security.py\*\*: Security utilities and IP filtering

# \- \*\*storage.py\*\*: File storage management

# 

# \### API Key Rotation System (`api\_rotation/`)

# A sophisticated system to manage multiple Gemini API keys:

# \- Automatic rotation across requests to avoid rate limits

# \- Thread-safe implementation for concurrent users

# \- Persistent state storage across application restarts

# \- Fault-tolerant handling of invalid/missing keys

# \- Monitoring endpoint to check rotation status

# 

# \### Frontend (Next.js)

# The frontend provides an intuitive learning interface:

# 

# \#### Authentication (`frontend/src/app/login/page.tsx`)

# \- User login with form validation

# \- Integration with backend authentication

# 

# \#### Chat Interface (`frontend/src/app/chat/page.tsx`)

# \- Real-time conversation with AI

# \- Markdown-supported responses with syntax highlighting

# \- Copy-to-clipboard functionality

# \- Mobile-responsive design with collapsible sidebar

# \- Loading states and error handling

# 

# \#### Additional Learning Features (`frontend/src/app/{notes,qa,answer-questions}`)

# \- \*\*Notes\*\*: Review session notes and summaries

# \- \*\*Q\&A Generation\*\*: Generate questions from PDF content  

# \- \*\*Quiz System\*\*: Take quizzes and get evaluations

# 

# \#### Components and Architecture

# \- \*\*AuthContext\*\*: Global authentication state management

# \- \*\*Protected Route\*\*: Route guards for authenticated sections

# \- \*\*LoadingBox\*\*: Consistent loading indicators

# \- \*\*DataCleaner\*\*: Response processing and formatting

# 

# \### Caching and Performance

# \- \*\*Cache System\*\*: MD5-hashed PDF content storage

# \- \*\*Performance Monitoring\*\*: Request timing and statistics

# \- \*\*Logging\*\*: Daily rotation logs for monitoring

# \- \*\*Worker Management\*\*: Gunicorn-compatible for production scaling

# 

# \### Data Flow

# 1\. \*\*PDF Upload\*\*: User uploads PDF → Backend extracts text → Cached in file system

# 2\. \*\*AI Interaction\*\*: User asks question → Request routed through API key rotation → Gemini processes with PDF context → Response cached and returned

# 3\. \*\*Learning Activities\*\*: Questions/quiz generated → User answers → AI evaluates → Progress tracked

# 

# \### Security Features

# \- Remote IP detection and logging

# \- API key masking in logs

# \- File type validation

# \- Session management

# \- Rate limiting through API key rotation

# 

# \### Deployment Considerations

# \- \*\*Windows/Unix\*\*: Platform-specific optimizations (asyncio, uvloop)

# \- \*\*Docker\*\*: Prepared with individual directories

# \- \*\*Production\*\*: Multiple worker support with logging

# \- \*\*Caching\*\*: File-based cache with hashing for performance

# 

# \### Directory Structure Analysis

# \- \*\*`backend/`\*\*: Main FastAPI application

# \- \*\*`frontend/`\*\*: Next.js React application  

# \- \*\*`api\_rotation/`\*\*: Standalone API key management system

# \- \*\*`books/`\*\*: Sample PDF documents for learning

# \- \*\*`learning/`\*\*: Development/backup directory with similar structure

# \- \*\*`cache/`\*\*: Shared cache files from backend processing

# \- \*\*`logs/`\*\*: Application logs categorized by service and date

# 

# \## Key Features and Benefits

# \- \*\*Multi-modal Learning\*\*: Chat, Q\&A generation, quiz evaluation, notes

# \- \*\*Scalable Architecture\*\*: Modular services with clear separation of concerns

# \- \*\*Performance Optimized\*\*: Caching, async processing, concurrent handling

# \- \*\*User-Friendly Interface\*\*: Mobile-responsive with smooth interactions

# \- \*\*Robust Logging\*\*: Comprehensive monitoring and debugging capabilities

# 

# This architecture provides a solid foundation for an AI-powered learning platform that can handle multiple concurrent users while maintaining responsive performance and security.

