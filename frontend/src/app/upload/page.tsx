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
    <div className="min-h-screen relative" style={{ backgroundColor: '#FFE8D6' }}>
      {/* Advanced Multi-Layer Background Animation System */}

      {/* Ambient light rays - Deepest layer */}
      <div className="light-rays">
        <div className="light-ray"></div>
        <div className="light-ray"></div>
        <div className="light-ray"></div>
      </div>

      {/* Floating orbs with light effects */}
      <div className="floating-orbs">
        <div className="orb"></div>
        <div className="orb"></div>
        <div className="orb"></div>
      </div>

      {/* Geometric shapes */}
      <div className="geometric-shapes">
        <div className="geometric-shape triangle" style={{ left: '15%', animationDelay: '0s' }}></div>
        <div className="geometric-shape square" style={{ left: '35%', animationDelay: '15s' }}></div>
        <div className="geometric-shape hexagon" style={{ left: '65%', animationDelay: '30s' }}></div>
        <div className="geometric-shape triangle" style={{ left: '85%', animationDelay: '45s' }}></div>
        <div className="geometric-shape square" style={{ left: '25%', animationDelay: '22s' }}></div>
        <div className="geometric-shape hexagon" style={{ left: '75%', animationDelay: '8s' }}></div>
      </div>

      {/* Enhanced flowing waves */}
      <div className="flowing-waves">
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
        <div className="wave"></div>
      </div>

      {/* Enhanced floating particles */}
      <div className="floating-particles">
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
        <div className="particle"></div>
      </div>

      {/* Advanced floating bubbles */}
      <div className="floating-bubbles">
        <div className="bubble xlarge"></div>
        <div className="bubble large"></div>
        <div className="bubble medium"></div>
        <div className="bubble small"></div>
        <div className="bubble large"></div>
        <div className="bubble medium"></div>
        <div className="bubble xlarge"></div>
        <div className="bubble small"></div>
        <div className="bubble medium"></div>
        <div className="bubble large"></div>
      </div>
      {/* Header */}
      <div className="backdrop-blur-sm border-b" style={{ backgroundColor: 'rgba(255, 232, 214, 0.9)', borderColor: '#DDBEA9' }}>
        <div className="max-w-7xl mx-auto">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-4">
              <div className="p-3 rounded-2xl" style={{ background: 'linear-gradient(135deg, #CB997E, #A5A58D)' }}>
                <BookOpen className="h-7 w-7 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold" style={{ color: '#6B705C' }}>LuminalQ</h1>
                <p className="text-xs font-medium" style={{ color: '#A5A58D' }}>made with Genrec-AI</p>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-medium" style={{ color: '#6B705C' }}>Welcome, {user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 rounded-xl elegant-transition hover:scale-105"
                style={{
                  color: '#6B705C',
                  backgroundColor: 'rgba(221, 190, 169, 0.3)',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(203, 153, 126, 0.2)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(221, 190, 169, 0.3)';
                }}
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-6 py-12">
        <div className="text-center mb-8">
          <h2 className="text-4xl font-bold mb-6" style={{ color: '#6B705C' }}>
            Your Learning Library
          </h2>
          <p className="text-lg max-w-2xl mx-auto mb-8" style={{ color: '#A5A58D' }}>
            Choose from your collection or upload new materials to enhance your learning journey.
          </p>
        </div>

        {/* Search Bar */}
        <div className="mb-8">
          <div className="relative">
            <input
              type="text"
              placeholder="Book Search ....."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-6 py-4 text-lg rounded-2xl border-2 elegant-transition focus:outline-none focus:scale-[1.02] breathing"
              style={{
                backgroundColor: '#DDBEA9',
                borderColor: '#B7B7A4',
                color: '#6B705C',
                fontFamily: 'Poppins, sans-serif'
              }}
              onFocus={(e) => {
                e.target.style.borderColor = '#CB997E';
                e.target.style.boxShadow = '0 0 0 3px rgba(203, 153, 126, 0.1)';
              }}
              onBlur={(e) => {
                e.target.style.borderColor = '#B7B7A4';
                e.target.style.boxShadow = 'none';
              }}
            />
          </div>
        </div>

        {/* Books  */}
        <div className="rounded-3xl shadow-2xl border-2" style={{ backgroundColor: 'rgba(255, 232, 214, 0.8)', borderColor: '#DDBEA9' }}>
          <div className="p-4">
            <div className="flex items-center space-x-3 mb-4">
              <Book className="h-6 w-6" style={{ color: '#CB997E' }} />
              <h3 className="text-2xl font-bold" style={{ color: '#6B705C' }}>Books</h3>
            </div>

            {loading ? (
              <div className="text-center py-16">
                <div className="upload-pulse rounded-full h-16 w-16 border-4 mx-auto mb-6" style={{ borderColor: '#CB997E', borderTopColor: 'transparent' }}></div>
                <p className="text-lg font-medium" style={{ color: '#6B705C' }}>Loading your PDF library...</p>
              </div>
            ) : filteredPDFs.length === 0 ? (
              /* Empty State */
              <div className="text-center py-16">
                <div className="p-6 rounded-full w-20 h-20 mx-auto flex items-center justify-center mb-6" style={{ backgroundColor: 'rgba(203, 153, 126, 0.2)' }}>
                  <BookOpen className="h-10 w-10" style={{ color: '#CB997E' }} />
                </div>
                <h3 className="text-3xl font-bold mb-4" style={{ color: '#6B705C' }}>
                  {searchTerm ? 'No Books Found' : 'Your Library Awaits'}
                </h3>
                <p className="text-lg mb-8 max-w-md mx-auto" style={{ color: '#A5A58D' }}>
                  {searchTerm
                    ? `No books match "${searchTerm}". Try a different search term.`
                    : 'Your collection of learning materials will appear here.'
                  }
                </p>
              </div>
            ) : (
              /* PDF List */
              <div className="space-y-3 max-h-96 overflow-y-auto pr-2 book-list-scroll">
                {filteredPDFs.map((pdf) => (
                  <div
                    key={pdf.filename}
                    className="border-2 rounded-2xl p-4 cursor-pointer elegant-transition hover:shadow-lg"
                    style={{
                      borderColor: '#DDBEA9',
                      backgroundColor: 'rgba(255, 232, 214, 0.6)'
                    }}
                    onClick={() => handleSelectPDF(pdf.filename)}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.borderColor = '#CB997E';
                      e.currentTarget.style.transform = 'translateY(-4px)';
                      e.currentTarget.style.boxShadow = '0 10px 25px rgba(203, 153, 126, 0.15)';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.borderColor = '#DDBEA9';
                      e.currentTarget.style.transform = 'translateY(0px)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  >
                    <div className="flex items-center space-x-4">
                      <div className="p-3 rounded-xl flex-shrink-0" style={{ backgroundColor: 'rgba(203, 153, 126, 0.2)' }}>
                        <FileIcon className="h-6 w-6" style={{ color: '#CB997E' }} />
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-bold mb-1" style={{ color: '#6B705C' }}>
                          {pdf.title !== 'Unknown' ? pdf.title : pdf.filename}
                        </h3>
                        <p className="text-sm mb-2" style={{ color: '#A5A58D' }}>
                          {pdf.filename}
                        </p>
                        <div className="flex items-center space-x-4 text-sm" style={{ color: '#B7B7A4' }}>
                          <div className="flex items-center space-x-2">
                            <User className="h-5 w-5" />
                            <span>{pdf.author !== 'Unknown' ? pdf.author : 'Unknown Author'}</span>
                          </div>
                          <div className="flex items-center space-x-2">
                            <FileText className="h-5 w-5" />
                            <span>{pdf.pages} pages</span>
                          </div>
                        </div>
                      </div>
                      {selecting ? (
                        <div className="flex items-center justify-center">
                          <div className="upload-pulse rounded-full h-6 w-6 border-2" style={{ borderColor: '#CB997E', borderTopColor: 'transparent' }}></div>
                        </div>
                      ) : (
                        <div className="text-right">
                          <div className="px-4 py-2 rounded-xl text-sm font-medium elegant-transition" style={{ backgroundColor: 'rgba(203, 153, 126, 0.1)', color: '#CB997E' }}>
                            Click to Select
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {error && (
              <div className="mt-8 p-6 rounded-2xl border-2 flex items-center space-x-4 fade-in" style={{ backgroundColor: 'rgba(239, 68, 68, 0.1)', borderColor: 'rgba(239, 68, 68, 0.3)' }}>
                <AlertCircle className="h-6 w-6 text-red-500 flex-shrink-0" />
                <span className="text-red-700 text-base font-medium">{error}</span>
              </div>
            )}
          </div>
        </div>

        {/* Features */}

        
      </div>
    </div>
  );
}
