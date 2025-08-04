'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { pdfApi, PDFInfo } from '@/lib/api';
import { FileText, AlertCircle, LogOut, BookOpen, Book, User, FileIcon, MessageSquare } from 'lucide-react';

export default function UploadPage() {
  const [error, setError] = useState('');
  const [availablePDFs, setAvailablePDFs] = useState<PDFInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [selecting, setSelecting] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  const { logout, user } = useAuth();
  const router = useRouter();

  // Filter PDFs based on search term
  const filteredPDFs = availablePDFs.filter(pdf =>
    pdf.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    pdf.filename.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
      router.push('/chat');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to select PDF');
    } finally {
      setSelecting(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  return (
    <div className="min-h-screen relative bg-cream">
      {/* Simplified background with subtle animation */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="floating-bubbles">
          <div className="bubble large"></div>
          <div className="bubble medium"></div>
          <div className="bubble small"></div>
        </div>
      </div>
      {/* Header - PC Optimized */}
      <header className="backdrop-blur-sm border-b border-sandy-beige bg-cream/90">
        <div className="max-w-7xl mx-auto px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-2xl bg-gradient-to-br from-terracotta to-muted-sage">
                <BookOpen className="h-8 w-8 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-olive-green">LuminalQ</h1>
                <p className="text-sm font-medium text-muted-sage">made with Genrec-AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <span className="text-lg font-medium text-olive-green">Welcome, {user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-6 py-3 rounded-xl bg-sandy-beige/30 text-olive-green hover:bg-terracotta/20 transition-all duration-200 hover:scale-105"
                aria-label="Logout"
              >
                <LogOut className="h-5 w-5" />
                <span className="text-lg font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content - PC Optimized */}
      <main className="max-w-6xl mx-auto px-8 py-12">
        <div className="text-center mb-10">
          <h2 className="text-5xl font-bold mb-6 text-olive-green">
            Your Learning Library
          </h2>
          <p className="text-xl max-w-3xl mx-auto mb-8 text-muted-sage">
            Choose from your collection or upload new materials to enhance your learning journey.
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-10">
          <div className="relative">
            <input
              type="text"
              placeholder="Search your books..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-8 py-5 text-xl rounded-2xl border-2 border-light-sage bg-sandy-beige text-olive-green placeholder-muted-sage focus:outline-none focus:border-terracotta focus:ring-2 focus:ring-terracotta/10 transition-all duration-200"
              aria-label="Search books"
            />
          </div>
        </div>

        {/* Books Section */}
        <section className="rounded-2xl lg:rounded-3xl shadow-xl border-2 border-sandy-beige bg-cream/80 backdrop-blur-sm">
          <div className="p-4 lg:p-6">
            <div className="flex items-center space-x-3 mb-4 lg:mb-6">
              <Book className="h-5 w-5 lg:h-6 lg:w-6 text-terracotta" />
              <h3 className="text-xl lg:text-2xl font-bold text-olive-green">Books</h3>
            </div>

            {loading ? (
              <div className="text-center py-12 lg:py-16">
                <div className="animate-spin rounded-full h-12 w-12 lg:h-16 lg:w-16 border-4 border-terracotta border-t-transparent mx-auto mb-4 lg:mb-6"></div>
                <p className="text-base lg:text-lg font-medium text-olive-green">Loading your PDF library...</p>
              </div>
            ) : filteredPDFs.length === 0 ? (
              /* Empty State */
              <div className="text-center py-12 lg:py-16">
                <div className="p-4 lg:p-6 rounded-full w-16 h-16 lg:w-20 lg:h-20 mx-auto flex items-center justify-center mb-4 lg:mb-6 bg-terracotta/20">
                  <BookOpen className="h-8 w-8 lg:h-10 lg:w-10 text-terracotta" />
                </div>
                <h3 className="text-2xl lg:text-3xl font-bold mb-3 lg:mb-4 text-olive-green">
                  {searchTerm ? 'No Books Found' : 'Your Library Awaits'}
                </h3>
                <p className="text-base lg:text-lg mb-6 lg:mb-8 max-w-md mx-auto text-muted-sage">
                  {searchTerm
                    ? `No books match "${searchTerm}". Try a different search term.`
                    : 'Your collection of learning materials will appear here.'
                  }
                </p>
              </div>
            ) : (
              /* PDF List */
              <div className="space-y-3 lg:space-y-4 max-h-80 lg:max-h-96 overflow-y-auto pr-2 book-list-scroll">
                {filteredPDFs.map((pdf) => (
                  <div
                    key={pdf.filename}
                    className="border-2 border-sandy-beige bg-cream/60 rounded-xl lg:rounded-2xl p-3 lg:p-4 cursor-pointer transition-all duration-200 hover:border-terracotta hover:shadow-lg hover:-translate-y-1 hover:bg-cream/80"
                    onClick={() => handleSelectPDF(pdf.filename)}
                    role="button"
                    tabIndex={0}
                    aria-label={`Select ${pdf.title !== 'Unknown' ? pdf.title : pdf.filename}`}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        handleSelectPDF(pdf.filename);
                      }
                    }}
                  >
                    <div className="flex items-center space-x-3 lg:space-x-4">
                      <div className="p-2 lg:p-3 rounded-lg lg:rounded-xl flex-shrink-0 bg-terracotta/20">
                        <FileIcon className="h-5 w-5 lg:h-6 lg:w-6 text-terracotta" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-base lg:text-lg font-bold mb-1 text-olive-green line-clamp-2">
                          {pdf.title !== 'Unknown' ? pdf.title : pdf.filename}
                        </h3>
                        <p className="text-xs lg:text-sm mb-2 text-muted-sage truncate">
                          {pdf.filename}
                        </p>
                        <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-1 sm:space-y-0 text-xs lg:text-sm text-light-sage">
                          <div className="flex items-center space-x-1 lg:space-x-2">
                            <User className="h-4 w-4" />
                            <span className="truncate">{pdf.author !== 'Unknown' ? pdf.author : 'Unknown Author'}</span>
                          </div>
                          <div className="flex items-center space-x-1 lg:space-x-2">
                            <FileText className="h-4 w-4" />
                            <span>{pdf.pages} pages</span>
                          </div>
                        </div>
                      </div>
                      {selecting ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-5 w-5 lg:h-6 lg:w-6 border-2 border-terracotta border-t-transparent"></div>
                        </div>
                      ) : (
                        <div className="text-right">
                          <div className="px-3 lg:px-4 py-1 lg:py-2 rounded-lg lg:rounded-xl text-xs lg:text-sm font-medium bg-terracotta/10 text-terracotta">
                            <span className="hidden sm:inline">Click to </span>Select
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div className="mt-6 lg:mt-8 p-4 lg:p-6 rounded-xl lg:rounded-2xl border-2 border-red-200 bg-red-50 flex items-start space-x-3 lg:space-x-4 animate-fadeIn">
                <AlertCircle className="h-5 w-5 lg:h-6 lg:w-6 text-red-500 flex-shrink-0 mt-0.5" />
                <span className="text-red-700 text-sm lg:text-base font-medium">{error}</span>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
