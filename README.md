# 🎓 LuminaIQ - AI-Powered Learning Desktop Application

[![Windows](https://img.shields.io/badge/Windows-10%2B-blue?logo=windows)](https://www.microsoft.com/windows)
[![Next.js](https://img.shields.io/badge/Next.js-15.4.1-black?logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Latest-green?logo=fastapi)](https://fastapi.tiangolo.com/)
[![Tauri](https://img.shields.io/badge/Tauri-2.8.2-orange?logo=tauri)](https://tauri.app/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)](https://python.org/)

A comprehensive desktop learning platform that combines AI-powered chat, PDF processing, intelligent note-taking, and automated quiz generation in a native Windows application.

## ✨ Features

- 🤖 **AI-Powered Chat**: Interactive conversations with context awareness
- 📚 **PDF Processing**: Upload and extract content from PDF documents
- 📝 **Smart Notes**: Markdown-supported note-taking with AI assistance
- 🧠 **Quiz Generation**: Automated quiz creation with multiple difficulty levels
- 💻 **Native Desktop**: True Windows desktop application with system integration
- 🔄 **API Key Rotation**: Intelligent API key management for uninterrupted service
- 🎨 **Modern UI**: Clean, responsive interface built with Next.js and Tailwind CSS

## 🏗️ Architecture

### Frontend (Desktop App)
- **Framework**: Next.js 15.4.1 with TypeScript
- **UI**: Tailwind CSS with custom components
- **Desktop**: Tauri 2.8.2 for native Windows integration
- **Features**: Static export, responsive design, syntax highlighting

### Backend (API Server)
- **Framework**: FastAPI with Python
- **AI Integration**: Google Generative AI with automatic key rotation
- **PDF Processing**: PyPDF2 and pdfplumber for text extraction
- **Authentication**: JWT-based user management
- **Caching**: Intelligent response caching for performance

## 📦 Installation

### Prerequisites
- Windows 10 or later (64-bit)
- 4 GB RAM minimum, 8 GB recommended
- 500 MB free disk space
- Internet connection for AI features

### Quick Install
1. Download the latest release from the [Releases](../../releases) page
2. Extract the package to a folder
3. Right-click `install.bat` and select "Run as administrator"
4. Follow the installation wizard

### Manual Installation
1. Install frontend: Run `installers/LuminaIQ_1.0.0_x64_en-US.msi`
2. Copy backend: Place `backend/luminaiq-backend.exe` in desired location
3. Start backend first, then launch LuminaIQ from Start Menu

## 🚀 Usage

### Starting the Application
1. **Start Backend**: Run `luminaiq-backend.exe` (starts on port 8000)
2. **Launch Frontend**: Open LuminaIQ from Start Menu or desktop shortcut
3. **Login/Register**: Create account or login with existing credentials

### Core Workflows
1. **PDF Learning**: Upload PDF → AI processes content → Generate notes/quizzes
2. **Interactive Chat**: Ask questions about uploaded content → Get AI responses
3. **Note Taking**: Create markdown notes → Use AI for suggestions/improvements
4. **Quiz Practice**: Generate quizzes → Take tests → Review AI feedback

## 🛠️ Development Setup

### Prerequisites
- Node.js 18+ and npm
- Python 3.8+ and pip
- Rust and Cargo (for Tauri)
- Visual Studio Build Tools (for Windows compilation)

### Backend Setup
```bash
cd learning/backend
pip install -r requirements.txt
python main.py
```

### Frontend Setup
```bash
cd learning/frontend
npm install
npm run dev
```

### Building Desktop App
```bash
cd learning/frontend
npm run build
npx tauri build
```

### Creating Distribution Package
```bash
cd learning
powershell -ExecutionPolicy Bypass -File .\create-unified-installer.ps1
```

## 📁 Project Structure

```
learning/
├── frontend/                 # Next.js desktop application
│   ├── src/                 # Source code
│   ├── src-tauri/           # Tauri configuration and Rust code
│   ├── out/                 # Static export output
│   └── package.json         # Dependencies and scripts
├── backend/                 # FastAPI server
│   ├── routes/              # API endpoints
│   ├── services/            # Business logic
│   ├── models/              # Data models
│   ├── utils/               # Utilities
│   ├── config/              # Configuration
│   └── main.py              # Application entry point
├── api_rotation/            # API key management
├── dist-unified/            # Distribution package
└── create-unified-installer.ps1  # Build script
```

## 🔧 Configuration

### API Keys
1. Create `learning/api_rotation/API_Keys.txt`
2. Add one API key per line
3. System automatically rotates keys for optimal performance

### Environment Variables
- `NEXT_PUBLIC_API_BASE_URL`: Backend URL (default: http://localhost:8000)
- `PYTHONPATH`: Include project root for imports

## 🧪 Testing

### Backend Testing
```bash
cd learning/backend
python -m pytest tests/
```

### Frontend Testing
```bash
cd learning/frontend
npm test
```

### Integration Testing
1. Start backend server
2. Launch frontend application
3. Test complete user workflows

## 📋 System Requirements

### Minimum Requirements
- Windows 10 (64-bit)
- 4 GB RAM
- 500 MB storage
- Internet connection

### Recommended Requirements
- Windows 11 (64-bit)
- 8 GB RAM
- 1 GB storage
- Stable broadband connection

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Tauri](https://tauri.app/) for the desktop framework
- [Next.js](https://nextjs.org/) for the frontend framework
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework
- [Google AI](https://ai.google.dev/) for the generative AI capabilities

## 📞 Support

For support, please open an issue in the [Issues](../../issues) section or contact the development team.

---

**Made with ❤️ for enhanced learning experiences**
