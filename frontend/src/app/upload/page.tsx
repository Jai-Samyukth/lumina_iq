'use client';

import { useState, useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useDropzone } from 'react-dropzone';
import { useAuth } from '@/contexts/AuthContext';
import { pdfApi, PDFInfo } from '@/lib/api';
import { Upload, FileText, CheckCircle, AlertCircle, LogOut, BookOpen, Book, User, Calendar, FileIcon, HelpCircle, MessageSquare } from 'lucide-react';

export default function UploadPage() {
  const [uploading, setUploading] = useState(false);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const [error, setError] = useState('');
  const [uploadedFile, setUploadedFile] = useState<string>('');
  const [availablePDFs, setAvailablePDFs] = useState<PDFInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

  const { logout, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadAvailablePDFs();
  }, []);

  const loadAvailablePDFs = async () => {
    try {
      setLoading(true);
      const result = await pdfApi.listPDFs();
      setAvailablePDFs(result.pdfs);
    } catch (err: any) {
      setError('Failed to load available PDFs');
    } finally {
      setLoading(false);
    }
  };

  const handleSelectPDF = async (filename: string) => {
    try {
      setSelecting(true);
      setError('');
      await pdfApi.selectPDF(filename);
      router.push('/qa');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to select PDF');
    } finally {
      setSelecting(false);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    setUploading(true);
    setError('');
    setUploadSuccess(false);

    try {
      const result = await pdfApi.uploadPDF(file);
      setUploadedFile(result.filename);
      setUploadSuccess(true);
      
      // Redirect to Q&A after successful upload
      setTimeout(() => {
        router.push('/qa');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setUploading(false);
    }
  }, [router]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxFiles: 1,
    disabled: uploading || uploadSuccess
  });

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <BookOpen className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-xl font-semibold text-gray-900">LearnAI</h1>
            </div>
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <span className="text-sm text-gray-600">Welcome, {user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-gray-600 hover:text-gray-900 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 mb-4">
            Select Your Learning Material
          </h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Choose a PDF document from your library or upload a new one to start your AI-powered learning session.
          </p>
        </div>

        {/* PDF Selection Area */}
        <div className="bg-white rounded-2xl shadow-xl border border-gray-100">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex">
              <button
                onClick={() => setShowUpload(false)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  !showUpload
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Book className="h-4 w-4" />
                  <span>Select from Library</span>
                </div>
              </button>
              <button
                onClick={() => setShowUpload(true)}
                className={`px-6 py-4 text-sm font-medium border-b-2 transition-colors ${
                  showUpload
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <div className="flex items-center space-x-2">
                  <Upload className="h-4 w-4" />
                  <span>Upload New PDF</span>
                </div>
              </button>
            </nav>
          </div>

          <div className="p-8">
            {!showUpload ? (
              /* PDF Library */
              <div>
                {loading ? (
                  <div className="text-center py-12">
                    <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading your PDF library...</p>
                  </div>
                ) : availablePDFs.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="bg-gray-100 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center mb-4">
                      <BookOpen className="h-8 w-8 text-gray-400" />
                    </div>
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No PDFs Available</h3>
                    <p className="text-gray-600 mb-6">
                      Your library is empty. Upload your first PDF to get started.
                    </p>
                    <button
                      onClick={() => setShowUpload(true)}
                      className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                    >
                      Upload PDF
                    </button>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {availablePDFs.map((pdf) => (
                      <div
                        key={pdf.filename}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                        onClick={() => handleSelectPDF(pdf.filename)}
                      >
                        <div className="flex items-start space-x-3">
                          <div className="bg-red-100 p-2 rounded-lg flex-shrink-0">
                            <FileIcon className="h-6 w-6 text-red-600" />
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-sm font-medium text-gray-900 truncate">
                              {pdf.title !== 'Unknown' ? pdf.title : pdf.filename}
                            </h3>
                            <p className="text-xs text-gray-500 mt-1">
                              {pdf.filename}
                            </p>
                            <div className="flex items-center space-x-4 mt-2 text-xs text-gray-500">
                              <div className="flex items-center space-x-1">
                                <User className="h-3 w-3" />
                                <span>{pdf.author !== 'Unknown' ? pdf.author : 'Unknown Author'}</span>
                              </div>
                              <div className="flex items-center space-x-1">
                                <FileText className="h-3 w-3" />
                                <span>{pdf.pages} pages</span>
                              </div>
                            </div>
                          </div>
                        </div>
                        {selecting && (
                          <div className="mt-3 flex items-center justify-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              /* Upload Interface */
              !uploadSuccess ? (
                <div
                  {...getRootProps()}
                  className={`border-2 border-dashed rounded-xl p-12 text-center cursor-pointer transition-all duration-200 ${
                    isDragActive
                      ? 'border-blue-500 bg-blue-50'
                      : uploading
                      ? 'border-gray-300 bg-gray-50 cursor-not-allowed'
                      : 'border-gray-300 hover:border-blue-400 hover:bg-blue-50'
                  }`}
                >
                  <input {...getInputProps()} />

                  {uploading ? (
                    <div className="space-y-4">
                      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
                      <p className="text-lg font-medium text-gray-700">Processing your PDF...</p>
                      <p className="text-sm text-gray-500">This may take a few moments</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                        <Upload className="h-8 w-8 text-white" />
                      </div>

                      {isDragActive ? (
                        <p className="text-lg font-medium text-blue-600">
                          Drop your PDF file here...
                        </p>
                      ) : (
                        <>
                          <p className="text-lg font-medium text-gray-700">
                            Drag & drop your PDF file here
                          </p>
                          <p className="text-gray-500">or click to browse</p>
                        </>
                      )}

                      <div className="flex items-center justify-center space-x-2 text-sm text-gray-500">
                        <FileText className="h-4 w-4" />
                        <span>PDF files only • Max 50MB</span>
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center space-y-6">
                  <div className="bg-green-100 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
                    <CheckCircle className="h-8 w-8 text-green-600" />
                  </div>

                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Upload Successful!
                    </h3>
                    <p className="text-gray-600 mb-4">
                      <span className="font-medium">{uploadedFile}</span> has been processed successfully.
                    </p>
                    <p className="text-sm text-gray-500">
                      Redirecting to chat interface...
                    </p>
                  </div>

                  <button
                    onClick={() => router.push('/qa')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                  >
                    Start Learning
                  </button>
                </div>
              )
            )}

            {error && (
              <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-center space-x-3">
                <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0" />
                <span className="text-red-700 text-sm">{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Features */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="bg-blue-100 p-3 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
              <FileText className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Smart Extraction</h3>
            <p className="text-sm text-gray-600">
              Advanced PDF processing to extract and understand your document content.
            </p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="bg-purple-100 p-3 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
              <BookOpen className="h-6 w-6 text-purple-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">AI Learning</h3>
            <p className="text-sm text-gray-600">
              Powered by Gemini AI to provide intelligent answers and explanations.
            </p>
          </div>
          
          <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
            <div className="bg-green-100 p-3 rounded-lg w-12 h-12 flex items-center justify-center mb-4">
              <CheckCircle className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-semibold text-gray-900 mb-2">Interactive Chat</h3>
            <p className="text-sm text-gray-600">
              Ask questions and get detailed explanations about your document.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
