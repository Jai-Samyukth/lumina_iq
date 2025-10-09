# Lumina IQ - AI-Powered Learning Assistant

## 🚀 Complete Installation & Setup Guide

Lumina IQ is a comprehensive AI-powered learning platform that enables users to interact with PDF documents through multiple learning modalities. This guide provides complete instructions for development setup and production deployment.

## 📋 Prerequisites & System Requirements

### Software Requirements
- **Python**: 3.11.9+ (recommended) or 3.10+
- **Node.js**: 18.17.0+ or 20+
- **npm**: 9.6.7+ or yarn 1.22+
- **Git**: For version control

### Minimum Hardware Requirements
- **CPU**: 4+ cores (8+ recommended for high concurrency)
- **RAM**: 8GB+ (16GB+ recommended for optimal performance)
- **Storage**: 10GB+ free space for PDF storage and caching
- **OS**: Windows Server 2019+ or Linux (Ubuntu 20.04+ recommended)

### Network Requirements
- Port 8000 open for backend API
- Port 3000 open for frontend (development)
- Internet access for Google Gemini API calls

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API   │
│   (Next.js)     │◄──►│   (FastAPI)     │
└─────────────────┘    └─────────────────┘
        │                      │
        ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│   User Browser  │    │   Gemini AI     │
│                 │    │   API Service   │
└─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
lumina-iq/
├── backend/                 # FastAPI backend
│   ├── config/             # Configuration settings
│   ├── routes/             # API endpoints
│   ├── services/           # Business logic
│   ├── utils/              # Utility functions
│   ├── main.py            # Main application entry
│   ├── requirements.txt    # Python dependencies
│   └── .gitignore         # Git ignore rules
├── frontend/               # Next.js frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── package.json       # Node.js dependencies
│   └── .env.example      # Environment template
├── api_rotation/          # API key management
│   ├── api_key_rotator.py # Key rotation logic
│   └── README.md          # API key setup guide
└── README.md             # This file
```

## 🔧 Complete Installation & Setup

### Step 1: Backend Setup

#### 1.1 Install Python and Create Virtual Environment

```bash
# Check Python version (requires 3.11.9+)
python --version

# Navigate to backend directory
cd backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

#### 1.2 Install Python Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# For production performance on Unix systems (optional but recommended):
pip install uvloop httptools

# For Windows systems, install additional performance packages:
pip install pywin32
```

#### 1.3 Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your configuration
# Required: Add your Gemini API keys
# Required: Change security keys for production
```

#### 1.4 Required Environment Variables (.env)

```env
# Server Configuration
Server Configuration in backend/config.py
```

### Step 2: Frontend Setup

#### 2.1 Install Node.js and npm

```bash
# Check Node.js version (requires 18.17.0+)
node --version
npm --version

# Navigate to frontend directory
cd frontend
```

#### 2.2 Install Dependencies

```bash
# Install all dependencies
npm install

# Alternative with yarn (if preferred)
yarn install
```

#### 2.3 Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your backend API URL
```

#### 2.4 Frontend Environment Variables (.env)

```env
# Backend API Configuration
# The base URL for the backend API (including /api path)
# For development: http://localhost:8000/api
# For production: http://your-domain.com:8000/api
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api
```

**Important**: The frontend uses this environment variable to connect to the backend API. Make sure this URL matches your backend server address.

## 🚀 Running the Application

### Development Mode

#### Start Backend Server

```bash
cd backend

# Activate virtual environment if not already active
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Start development server
python main.py
# or use the optimized runner:
python run.py
```

Backend will be available at: `http://localhost:8000`
API documentation: `http://localhost:8000/docs`

#### Start Frontend Server

```bash
cd frontend

# Start development server
npm run dev
# or with yarn:
yarn dev
```

Frontend will be available at: `http://localhost:3000`

### Production Deployment

#### Option 1: Traditional Deployment

##### Backend (Using Gunicorn for production)

```bash
cd backend

# Install Gunicorn
pip install gunicorn

# Start production server with multiple workers
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or use the provided run script:
python run.py
```

##### Frontend (Build and serve)

```bash
cd frontend

# Build for production
npm run build

# Start production server
npm start
```

#### Option 2: Docker Deployment

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - HOST=0.0.0.0
      - PORT=8000
    volumes:
      - ./uploaded_books:/app/uploaded_books
      - ./cache:/app/cache

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_BASE_URL=http://backend:8000/api
```

## 🔍 Verification & Testing

### Verify Backend Installation

```bash
# Test backend health
curl http://localhost:8000/

# Expected response: {"message":"Learning App API is running"}

# Test API endpoints
curl http://localhost:8000/api/auth/verify

# Check API documentation
# Open in browser: http://localhost:8000/docs
```

### Verify Frontend Installation

```bash
# Test frontend build
npm run build

# Check for any build errors
```

### Verify Backend-Frontend Connection

1. Start both backend and frontend servers
2. Open browser to `http://localhost:3000`
3. Check browser developer console for any connection errors
4. Test login functionality
5. Test PDF upload functionality

## 🛠️ Troubleshooting

### Common Installation Issues

#### Python Version Issues

**Problem**: Backend won't start due to Python version
**Solution**: Use Python 3.11.9+ or 3.10+

```bash
# Check Python version
python --version

# Install specific Python version (using pyenv)
pyenv install 3.11.9
pyenv local 3.11.9
```

#### Dependency Installation Issues

**Problem**: `pip install -r requirements.txt` fails
**Solution**: 

```bash
# Upgrade pip first
pip install --upgrade pip

# Try installing with no cache
pip install --no-cache-dir -r requirements.txt

# Or install dependencies one by one
pip install fastapi uvicorn python-multipart
```

#### Port Conflicts

**Problem**: Port 8000 or 3000 already in use
**Solution**: 

```bash
# Find processes using port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                # Linux/Mac

# Kill the process or use different ports
# Change in .env: PORT=8001
```

#### Frontend Connection Issues

**Problem**: Frontend can't connect to backend
**Solution**: 

1. Verify backend URL in frontend `.env` file
2. Check backend is running on correct port
3. Verify CORS configuration in backend
4. Check firewall settings

```bash
# Test backend connectivity from frontend directory
curl http://localhost:8000/
```



### Performance Issues

- Increase worker count for higher concurrency
- Monitor memory usage during PDF processing
- Check network connectivity to Gemini API
- Use `uvloop` and `httptools` on Unix systems for better performance

## 📞 Support & Maintenance

### Regular Maintenance Tasks

1. **Dependency Updates**: Regularly update Python and Node.js dependencies
2. **Log Rotation**: Monitor and manage log file sizes in `backend/logs/`
3. **Storage Management**: Clean up old cached files and uploaded PDFs
4. **API Key Rotation**: Regularly rotate Gemini API keys using the API rotation system

### Emergency Procedures

1. **Service Outage**: Restart backend and frontend services
2. **API Limit Exceeded**: Add more API keys or wait for quota reset
3. **Storage Full**: Clear cache directory and old uploaded files

## 📋 Deployment Checklist

- [ ] Python 3.11.9+ installed and verified
- [ ] Node.js 18.17.0+ installed and verified
- [ ] Backend dependencies installed (`pip install -r requirements.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Environment variables configured for both backend and frontend
- [ ] Gemini API keys set up and tested
- [ ] Required directories created (`uploaded_books`, `cache`, `logs`)
- [ ] CORS origins properly configured
- [ ] Backend server starts successfully on port 8000
- [ ] Frontend server starts successfully on port 3000
- [ ] Frontend can connect to backend API
- [ ] Basic functionality tested (login, PDF upload, chat)

## 🎯 Post-Installation Verification

1. **Backend Health**: `curl http://localhost:8000/` should return success
2. **Frontend Access**: Access `http://localhost:3000` in browser
3. **Authentication**: Test login functionality
4. **PDF Upload**: Upload and process a test PDF
5. **AI Interaction**: Test chat functionality with PDF content
6. **API Documentation**: Verify `http://localhost:8000/docs` is accessible

---

**Note**: For development-specific instructions and advanced configuration, refer to individual component README files in each directory.

**Support**: If you encounter issues during installation, check the troubleshooting section above or review the logs in `backend/logs/` for detailed error information
