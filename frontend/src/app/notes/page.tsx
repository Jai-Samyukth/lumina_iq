'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi, pdfApi, PDFSessionInfo } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  BookOpen,
  LogOut,
  FileText,
  User,
  Hash,
  HardDrive,
  Upload as UploadIcon,
  MessageSquare,
  Sparkles,
  Clock,
  Download,
  Copy,
  Check,
  StickyNote,
  Brain,
  AlertCircle,
  Layers
} from 'lucide-react';

type NotesSize = 'brief' | 'detailed' | 'comprehensive';
type CurrentStep = 'setup' | 'generating' | 'result';

export default function NotesPage() {
  const [pdfInfo, setPdfInfo] = useState<PDFSessionInfo | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState<CurrentStep>('setup');
  
  // Setup state
  const [notesTopic, setNotesTopic] = useState('');
  const [notesSize, setNotesSize] = useState<NotesSize>('detailed');
  const [generatingNotes, setGeneratingNotes] = useState(false);
  
  // Result state
  const [generatedNotes, setGeneratedNotes] = useState('');
  const [copiedToClipboard, setCopiedToClipboard] = useState(false);

  const { logout, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadPDFInfo();
  }, []);

  const loadPDFInfo = async () => {
    try {
      const info = await pdfApi.getPDFInfo();
      setPdfInfo(info);
    } catch (error) {
      console.error('Failed to load PDF info:', error);
      router.push('/upload');
    } finally {
      setInitialLoading(false);
    }
  };

  const generateNotes = async () => {
    if (!pdfInfo || !notesTopic.trim()) return;

    setGeneratingNotes(true);
    setCurrentStep('generating');
    
    try {
      const topicToUse = notesTopic.trim();
      console.log('Starting notes generation for:', pdfInfo.filename, 'Topic:', topicToUse, 'Size:', notesSize);

      // Create a detailed prompt for notes generation
      const notesPrompt = `Generate comprehensive study notes on the topic "${topicToUse}" based on the document "${pdfInfo.filename}". 

Size requirement: ${notesSize === 'brief' ? 'Brief (1-2 pages)' : notesSize === 'detailed' ? 'Detailed (3-5 pages)' : 'Comprehensive (5+ pages)'}

Please format the notes in clean Markdown with:
- Clear headings and subheadings
- Bullet points for key concepts
- Numbered lists for processes/steps
- Code blocks for examples (if applicable)
- Bold text for important terms
- Tables for comparisons (if relevant)
- Blockquotes for important quotes or definitions

Structure the notes with:
1. Introduction/Overview
2. Key Concepts
3. Detailed Explanations
4. Examples and Applications
5. Summary/Conclusion

Make the notes comprehensive, well-organized, and suitable for studying.`;

      const response = await chatApi.sendMessage(notesPrompt);
      console.log('Notes generated successfully');
      
      setGeneratedNotes(response.response);
      setCurrentStep('result');
    } catch (error) {
      console.error('Failed to generate notes:', error);
      alert('Failed to generate notes. Please try again.');
      setCurrentStep('setup');
    } finally {
      setGeneratingNotes(false);
    }
  };

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(generatedNotes);
      setCopiedToClipboard(true);
      setTimeout(() => setCopiedToClipboard(false), 2000);
    } catch (err) {
      console.error('Failed to copy notes: ', err);
    }
  };

  const downloadNotes = () => {
    // Create a new window for PDF generation
    const printWindow = window.open('', '_blank');
    if (!printWindow) return;

    // Create HTML content with the rendered markdown
    const htmlContent = `
      <!DOCTYPE html>
      <html>
        <head>
          <title>${notesTopic} - Study Notes</title>
          <style>
            body {
              font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
              line-height: 1.6;
              color: #333;
              max-width: 800px;
              margin: 0 auto;
              padding: 20px;
            }
            h1 {
              color: #059669;
              border-bottom: 3px solid #059669;
              padding-bottom: 10px;
              margin-bottom: 30px;
            }
            h2 {
              color: #374151;
              border-bottom: 1px solid #d1d5db;
              padding-bottom: 5px;
              margin-top: 30px;
              margin-bottom: 15px;
            }
            h3 {
              color: #4b5563;
              margin-top: 25px;
              margin-bottom: 10px;
            }
            h4 {
              color: #6b7280;
              margin-top: 20px;
              margin-bottom: 8px;
            }
            p {
              margin-bottom: 15px;
              text-align: justify;
            }
            ul, ol {
              margin-bottom: 15px;
              padding-left: 25px;
            }
            li {
              margin-bottom: 5px;
            }
            blockquote {
              border-left: 4px solid #059669;
              margin: 20px 0;
              padding: 10px 20px;
              background-color: #f0fdf4;
              font-style: italic;
            }
            code {
              background-color: #f3f4f6;
              padding: 2px 6px;
              border-radius: 4px;
              font-family: 'Courier New', monospace;
              font-size: 0.9em;
            }
            pre {
              background-color: #1f2937;
              color: #f9fafb;
              padding: 15px;
              border-radius: 8px;
              overflow-x: auto;
              margin: 15px 0;
            }
            pre code {
              background: none;
              padding: 0;
              color: inherit;
            }
            table {
              width: 100%;
              border-collapse: collapse;
              margin: 15px 0;
            }
            th, td {
              border: 1px solid #d1d5db;
              padding: 8px 12px;
              text-align: left;
            }
            th {
              background-color: #f3f4f6;
              font-weight: 600;
            }
            strong {
              font-weight: 600;
              color: #1f2937;
            }
            em {
              font-style: italic;
              color: #4b5563;
            }
            .header {
              text-align: center;
              margin-bottom: 40px;
              padding-bottom: 20px;
              border-bottom: 2px solid #e5e7eb;
            }
            .footer {
              margin-top: 40px;
              padding-top: 20px;
              border-top: 1px solid #e5e7eb;
              text-align: center;
              font-size: 0.9em;
              color: #6b7280;
            }
            @media print {
              body { margin: 0; padding: 15px; }
              .no-print { display: none; }
            }
          </style>
        </head>
        <body>
          <div class="header">
            <h1>${notesTopic}</h1>
            <p style="color: #6b7280; margin: 0;">Study Notes • ${notesSize.charAt(0).toUpperCase() + notesSize.slice(1)} Format</p>
            <p style="color: #9ca3af; font-size: 0.9em; margin: 5px 0 0 0;">Generated from: ${pdfInfo?.filename || 'PDF Document'}</p>
          </div>
          <div id="content"></div>
          <div class="footer">
            <p>Generated by LearnAI • ${new Date().toLocaleDateString()}</p>
          </div>
        </body>
      </html>
    `;

    printWindow.document.write(htmlContent);
    printWindow.document.close();

    // Convert markdown to HTML and insert into content div
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = generatedNotes
      .replace(/^# (.*$)/gim, '<h1>$1</h1>')
      .replace(/^## (.*$)/gim, '<h2>$1</h2>')
      .replace(/^### (.*$)/gim, '<h3>$1</h3>')
      .replace(/^#### (.*$)/gim, '<h4>$1</h4>')
      .replace(/^\* (.*$)/gim, '<li>$1</li>')
      .replace(/^- (.*$)/gim, '<li>$1</li>')
      .replace(/^\d+\. (.*$)/gim, '<li>$1</li>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/`(.*?)`/g, '<code>$1</code>')
      .replace(/^> (.*$)/gim, '<blockquote>$1</blockquote>')
      .replace(/\n\n/g, '</p><p>')
      .replace(/^(?!<[h|l|b])/gm, '<p>')
      .replace(/(?<![>])$/gm, '</p>');

    // Wrap consecutive list items in ul tags
    tempDiv.innerHTML = tempDiv.innerHTML
      .replace(/(<li>.*?<\/li>)(?=\s*<li>)/gs, '$1')
      .replace(/(<li>.*?<\/li>)(?!\s*<li>)/gs, '</ul>$1')
      .replace(/(<li>.*?<\/li>)(?=\s*<li>)/gs, '$1')
      .replace(/(?<!<\/ul>)(<li>)/g, '<ul>$1');

    printWindow.document.getElementById('content').innerHTML = tempDiv.innerHTML;

    // Wait for content to load, then print
    setTimeout(() => {
      printWindow.print();
      printWindow.close();
    }, 500);
  };

  const resetNotes = () => {
    setCurrentStep('setup');
    setGeneratedNotes('');
    setNotesTopic('');
    setNotesSize('detailed');
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg animate-pulse">
            <Sparkles className="h-8 w-8 text-white" />
          </div>
          <p className="text-slate-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!pdfInfo) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-slate-800 mb-2">No PDF Selected</h2>
          <p className="text-slate-600 mb-4">Please select a PDF document first.</p>
          <button
            onClick={() => router.push('/upload')}
            className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
          >
            Select PDF
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm border-b border-white/20 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-green-600 to-teal-600 p-2 rounded-lg">
                <StickyNote className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Generate Notes</h1>
                <p className="text-sm text-slate-600">Create structured study notes from your PDF</p>
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2 text-sm text-slate-600">
                <User className="h-4 w-4" />
                <span>{user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* PDF Info Bar */}
      <div className="bg-white/60 backdrop-blur-sm border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <FileText className="h-5 w-5 text-green-600" />
              <div>
                <p className="font-medium text-slate-800">{pdfInfo.filename}</p>
                <div className="flex items-center space-x-4 text-sm text-slate-600">
                  <span className="flex items-center space-x-1">
                    <Hash className="h-3 w-3" />
                    <span>{pdfInfo.metadata.pages} pages</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <HardDrive className="h-3 w-3" />
                    <span>{(pdfInfo.metadata.file_size / 1024).toFixed(1)} KB</span>
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              <button
                onClick={() => router.push('/upload')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
              >
                <UploadIcon className="h-4 w-4" />
                <span>Change PDF</span>
              </button>
              <button
                onClick={() => router.push('/chat')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
              >
                <MessageSquare className="h-4 w-4" />
                <span>Chat</span>
              </button>
              <button
                onClick={() => router.push('/qa')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
              >
                <Brain className="h-4 w-4" />
                <span>Q&A</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-6xl mx-auto px-4 py-8">
        {currentStep === 'setup' && (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-8">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-green-500 via-teal-500 to-blue-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                <BookOpen className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">Setup Your Notes</h2>
              <p className="text-slate-600">Configure your study notes generation</p>
            </div>

            <div className="space-y-6">
              {/* Topic Input */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Notes Topic <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={notesTopic}
                  onChange={(e) => setNotesTopic(e.target.value)}
                  placeholder="e.g., Machine Learning Algorithms, Chapter 5 Summary, Data Structures..."
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  required
                />
                <p className="text-sm text-slate-500 mt-1">
                  Specify the topic you want to create notes for
                </p>
              </div>

              {/* Notes Size Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Notes Size
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => setNotesSize('brief')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      notesSize === 'brief'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <Layers className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Brief</h3>
                    <p className="text-sm text-slate-600">
                      Concise notes (1-2 pages) with key points
                    </p>
                  </button>
                  
                  <button
                    onClick={() => setNotesSize('detailed')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      notesSize === 'detailed'
                        ? 'border-green-500 bg-green-50 text-green-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <BookOpen className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Detailed</h3>
                    <p className="text-sm text-slate-600">
                      Comprehensive notes (3-5 pages) with explanations
                    </p>
                  </button>

                  <button
                    onClick={() => setNotesSize('comprehensive')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      notesSize === 'comprehensive'
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <FileText className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Comprehensive</h3>
                    <p className="text-sm text-slate-600">
                      Extensive notes (5+ pages) with examples
                    </p>
                  </button>
                </div>
              </div>

              {/* Generate Button */}
              <div className="text-center pt-4">
                <button
                  onClick={generateNotes}
                  disabled={generatingNotes || !notesTopic.trim()}
                  className="bg-gradient-to-r from-green-600 to-teal-600 text-white px-8 py-3 rounded-lg font-medium hover:from-green-700 hover:to-teal-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {generatingNotes ? (
                    <>
                      <Clock className="h-5 w-5 inline mr-2 animate-spin" />
                      Generating Notes...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 inline mr-2" />
                      Generate {notesSize.charAt(0).toUpperCase() + notesSize.slice(1)} Notes
                    </>
                  )}
                </button>
                
                {!notesTopic.trim() && (
                  <p className="text-sm text-slate-500 mt-2">
                    Please enter a topic to generate notes
                  </p>
                )}
              </div>
            </div>
          </div>
        )}

        {currentStep === 'generating' && (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-8">
            <div className="text-center">
              <div className="bg-gradient-to-r from-green-500 via-teal-500 to-blue-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                <Clock className="h-8 w-8 text-white animate-spin" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">Generating Your Notes</h2>
              <p className="text-slate-600 mb-4">
                Creating {notesSize} notes on "{notesTopic}"...
              </p>
              <div className="flex justify-center">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-green-500 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-teal-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                  <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {currentStep === 'result' && generatedNotes && (
          <div className="space-y-6">
            {/* Notes Header */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-xl font-bold text-slate-800">Generated Notes</h2>
                  <p className="text-sm text-slate-600">
                    Topic: {notesTopic} • Size: {notesSize.charAt(0).toUpperCase() + notesSize.slice(1)}
                  </p>
                </div>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={copyToClipboard}
                    className="flex items-center space-x-2 px-4 py-2 bg-slate-600 text-white rounded-lg hover:bg-slate-700 transition-colors"
                  >
                    {copiedToClipboard ? (
                      <>
                        <Check className="h-4 w-4" />
                        <span className="text-sm">Copied!</span>
                      </>
                    ) : (
                      <>
                        <Copy className="h-4 w-4" />
                        <span className="text-sm">Copy</span>
                      </>
                    )}
                  </button>
                  <button
                    onClick={downloadNotes}
                    className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                  >
                    <Download className="h-4 w-4" />
                    <span className="text-sm">Download PDF</span>
                  </button>
                </div>
              </div>
            </div>

            {/* Notes Content */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-8">
              <div className="prose prose-slate max-w-none">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ children }) => (
                      <h1 className="text-3xl font-bold text-slate-800 mb-6 pb-2 border-b-2 border-green-500">
                        {children}
                      </h1>
                    ),
                    h2: ({ children }) => (
                      <h2 className="text-2xl font-bold text-slate-800 mb-4 mt-8 pb-1 border-b border-slate-300">
                        {children}
                      </h2>
                    ),
                    h3: ({ children }) => (
                      <h3 className="text-xl font-semibold text-slate-700 mb-3 mt-6">
                        {children}
                      </h3>
                    ),
                    h4: ({ children }) => (
                      <h4 className="text-lg font-semibold text-slate-700 mb-2 mt-4">
                        {children}
                      </h4>
                    ),
                    p: ({ children }) => (
                      <p className="text-slate-700 leading-relaxed mb-4">
                        {children}
                      </p>
                    ),
                    ul: ({ children }) => (
                      <ul className="list-disc list-inside text-slate-700 space-y-2 mb-4 ml-4">
                        {children}
                      </ul>
                    ),
                    ol: ({ children }) => (
                      <ol className="list-decimal list-inside text-slate-700 space-y-2 mb-4 ml-4">
                        {children}
                      </ol>
                    ),
                    li: ({ children }) => (
                      <li className="text-slate-700">{children}</li>
                    ),
                    blockquote: ({ children }) => (
                      <blockquote className="border-l-4 border-green-500 pl-4 italic text-slate-600 bg-green-50 py-3 rounded-r mb-4">
                        {children}
                      </blockquote>
                    ),
                    code: ({ className, children, ...props }) => {
                      const isInline = 'inline' in props;
                      return !isInline ? (
                        <div className="relative my-4">
                          <pre className="bg-slate-900 text-slate-100 rounded-lg p-4 overflow-x-auto text-sm">
                            <code className={className} {...props}>
                              {children}
                            </code>
                          </pre>
                        </div>
                      ) : (
                        <code className="bg-slate-100 text-slate-800 px-2 py-1 rounded text-sm font-mono" {...props}>
                          {children}
                        </code>
                      );
                    },
                    table: ({ children }) => (
                      <div className="overflow-x-auto mb-4">
                        <table className="min-w-full border border-slate-300 rounded-lg">
                          {children}
                        </table>
                      </div>
                    ),
                    thead: ({ children }) => (
                      <thead className="bg-slate-100">
                        {children}
                      </thead>
                    ),
                    th: ({ children }) => (
                      <th className="border border-slate-300 px-4 py-2 text-left font-semibold text-slate-700">
                        {children}
                      </th>
                    ),
                    td: ({ children }) => (
                      <td className="border border-slate-300 px-4 py-2 text-slate-700">
                        {children}
                      </td>
                    ),
                    strong: ({ children }) => (
                      <strong className="font-bold text-slate-800">{children}</strong>
                    ),
                    em: ({ children }) => (
                      <em className="italic text-slate-700">{children}</em>
                    ),
                  }}
                >
                  {generatedNotes}
                </ReactMarkdown>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="text-center space-x-4">
              <button
                onClick={resetNotes}
                className="bg-gradient-to-r from-green-600 to-teal-600 text-white px-6 py-3 rounded-lg font-medium hover:from-green-700 hover:to-teal-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Sparkles className="h-5 w-5 inline mr-2" />
                Generate New Notes
              </button>

              <button
                onClick={() => router.push('/chat')}
                className="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <MessageSquare className="h-5 w-5 inline mr-2" />
                Chat Mode
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
