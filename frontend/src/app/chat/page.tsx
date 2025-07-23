'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi, pdfApi, ChatHistoryItem, PDFSessionInfo } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  BookOpen,
  LogOut,
  FileText,
  Calendar,
  User,
  Hash,
  HardDrive,
  Upload as UploadIcon,
  MessageCircle,
  Bot,
  Sparkles,
  Copy,
  Check,
  HelpCircle,
  Brain,
  StickyNote
} from 'lucide-react';

export default function ChatPage() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [pdfInfo, setPdfInfo] = useState<PDFSessionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const { logout, user } = useAuth();
  const router = useRouter();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    loadInitialData();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [chatHistory]);

  const loadInitialData = async () => {
    try {
      const [historyData, pdfData] = await Promise.all([
        chatApi.getChatHistory(),
        pdfApi.getPDFInfo()
      ]);
      
      setChatHistory(historyData.history);
      setPdfInfo(pdfData);
    } catch (error) {
      console.error('Failed to load initial data:', error);
      // If no PDF is uploaded, redirect to upload page
      router.push('/upload');
    } finally {
      setInitialLoading(false);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || loading) return;

    const userMessage = message.trim();
    setMessage('');
    setLoading(true);

    try {
      const response = await chatApi.sendMessage(userMessage);
      
      // Add the new message to chat history
      const newMessage: ChatHistoryItem = {
        user: userMessage,
        assistant: response.response,
        timestamp: response.timestamp
      };
      
      setChatHistory(prev => [...prev, newMessage]);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.push('/login');
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string) => {
    if (dateString === 'Unknown') return 'Unknown';
    try {
      return new Date(dateString).toLocaleDateString();
    } catch {
      return 'Unknown';
    }
  };

  const copyToClipboard = async (text: string, index: number) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedIndex(index);
      setTimeout(() => setCopiedIndex(null), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading your learning session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex flex-col">
      {/* Header */}
      <div className="bg-white/80 backdrop-blur-sm shadow-lg border-b border-white/20">
        <div className="max-w-6xl mx-auto px-4">
          <div className="flex justify-between items-center py-3">
            <div className="flex items-center space-x-4">
              <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 p-3 rounded-xl shadow-lg">
                <Sparkles className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  LearnAI Chat
                </h1>
                {pdfInfo && (
                  <p className="text-sm text-slate-600 font-medium">{pdfInfo.filename}</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <button
                onClick={() => router.push('/qa')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-indigo-600 text-white rounded-lg hover:from-purple-600 hover:to-indigo-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <HelpCircle className="h-4 w-4" />
                <span className="text-sm font-medium">Q&A</span>
              </button>
              <button
                onClick={() => router.push('/answer-questions')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <Brain className="h-4 w-4" />
                <span className="text-sm font-medium">Answer Quiz</span>
              </button>
              <button
                onClick={() => router.push('/notes')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-green-500 to-teal-600 text-white rounded-lg hover:from-green-600 hover:to-teal-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <StickyNote className="h-4 w-4" />
                <span className="text-sm font-medium">Notes</span>
              </button>
              <button
                onClick={() => router.push('/upload')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg hover:from-emerald-600 hover:to-teal-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <UploadIcon className="h-4 w-4" />
                <span className="text-sm font-medium">New PDF</span>
              </button>
              <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <span className="text-sm font-medium text-slate-700">{user?.username}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-all duration-200"
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex w-full">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 chat-scroll">
            {chatHistory.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Start Your Learning Journey
                </h3>
                <p className="text-slate-600 max-w-md mx-auto leading-relaxed">
                  Ask any question about your selected PDF. I'm here to help you understand and learn from the content.
                </p>
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto">
                  <div className="bg-white/60 backdrop-blur-sm rounded-lg p-3 border border-white/20">
                    <h4 className="font-medium text-slate-700 mb-1">💡 Ask for explanations</h4>
                    <p className="text-xs text-slate-600">"Explain the main concepts"</p>
                  </div>
                  <div className="bg-white/60 backdrop-blur-sm rounded-lg p-3 border border-white/20">
                    <h4 className="font-medium text-slate-700 mb-1">🔍 Get specific details</h4>
                    <p className="text-xs text-slate-600">"What are the key points..."</p>
                  </div>
                </div>
              </div>
            ) : (
              chatHistory.map((chat, index) => (
                <div key={index} className="space-y-4">
                  {/* User Message */}
                  <div className="flex justify-end">
                    <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white rounded-2xl rounded-tr-md px-4 py-3 max-w-xs md:max-w-2xl shadow-lg">
                      <p className="text-sm leading-relaxed">{chat.user}</p>
                    </div>
                  </div>

                  {/* AI Response */}
                  <div className="flex items-start space-x-3">
                    <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-2 rounded-lg flex-shrink-0 shadow-lg">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="bg-white/80 backdrop-blur-sm rounded-2xl rounded-tl-md px-4 py-3 shadow-xl border border-white/20 flex-1">
                      <div className="prose prose-sm max-w-none">
                        <ReactMarkdown
                          remarkPlugins={[remarkGfm]}
                          components={{
                            code: ({ className, children, ...props }) => {
                              const match = /language-(\w+)/.exec(className || '');
                              const isInline = 'inline' in props;
                              return !isInline ? (
                                <div className="relative my-3">
                                  <pre className="bg-slate-900 text-slate-100 rounded-lg p-3 overflow-x-auto text-sm">
                                    <code className={className} {...props}>
                                      {children}
                                    </code>
                                  </pre>
                                  <button
                                    onClick={() => copyToClipboard(String(children), index)}
                                    className="absolute top-2 right-2 p-1.5 bg-slate-700 hover:bg-slate-600 rounded transition-colors"
                                  >
                                    {copiedIndex === index ? (
                                      <Check className="h-3 w-3 text-green-400" />
                                    ) : (
                                      <Copy className="h-3 w-3 text-slate-300" />
                                    )}
                                  </button>
                                </div>
                              ) : (
                                <code className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm" {...props}>
                                  {children}
                                </code>
                              );
                            },
                            h1: ({ children }) => (
                              <h1 className="text-lg font-bold text-slate-800 mb-2 border-b border-slate-200 pb-1">
                                {children}
                              </h1>
                            ),
                            h2: ({ children }) => (
                              <h2 className="text-base font-semibold text-slate-800 mb-2 mt-3">
                                {children}
                              </h2>
                            ),
                            h3: ({ children }) => (
                              <h3 className="text-sm font-semibold text-slate-700 mb-1 mt-2">
                                {children}
                              </h3>
                            ),
                            p: ({ children }) => (
                              <p className="text-slate-700 leading-relaxed mb-2">
                                {children}
                              </p>
                            ),
                            ul: ({ children }) => (
                              <ul className="list-disc list-inside text-slate-700 space-y-0.5 mb-2 ml-2">
                                {children}
                              </ul>
                            ),
                            ol: ({ children }) => (
                              <ol className="list-decimal list-inside text-slate-700 space-y-0.5 mb-2 ml-2">
                                {children}
                              </ol>
                            ),
                            li: ({ children }) => (
                              <li className="text-slate-700 text-sm">{children}</li>
                            ),
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-3 border-blue-500 pl-3 italic text-slate-600 bg-blue-50 py-2 rounded-r mb-2">
                                {children}
                              </blockquote>
                            ),
                            strong: ({ children }) => (
                              <strong className="font-semibold text-slate-800">{children}</strong>
                            ),
                            em: ({ children }) => (
                              <em className="italic text-slate-700">{children}</em>
                            ),
                          }}
                        >
                          {chat.assistant}
                        </ReactMarkdown>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-slate-200">
                        <p className="text-xs text-slate-500">
                          {formatDate(chat.timestamp)}
                        </p>
                        <button
                          onClick={() => copyToClipboard(chat.assistant, index + 1000)}
                          className="flex items-center space-x-1 text-xs text-slate-500 hover:text-slate-700 transition-colors"
                        >
                          {copiedIndex === index + 1000 ? (
                            <>
                              <Check className="h-3 w-3" />
                              <span>Copied!</span>
                            </>
                          ) : (
                            <>
                              <Copy className="h-3 w-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}

            {loading && (
              <div className="flex items-start space-x-3">
                <div className="bg-gradient-to-r from-emerald-500 to-teal-500 p-2 rounded-lg flex-shrink-0 shadow-lg">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-white/80 backdrop-blur-sm rounded-2xl rounded-tl-md px-4 py-3 shadow-xl border border-white/20">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-purple-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-slate-600">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Message Input */}
          <div className="border-t border-white/20 bg-white/60 backdrop-blur-sm p-4">
            <form onSubmit={handleSendMessage} className="flex space-x-3 max-w-4xl mx-auto">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask a question about your PDF..."
                  className="w-full border border-slate-200 rounded-xl px-4 py-3 pr-10 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200 bg-white/80 backdrop-blur-sm shadow-md text-slate-700 placeholder-slate-400"
                  disabled={loading}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <MessageCircle className="h-4 w-4 text-slate-400" />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading || !message.trim()}
                className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:from-blue-700 hover:via-purple-700 hover:to-indigo-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>

        {/* PDF Metadata Panel */}
        {pdfInfo && (
          <div className="w-72 bg-white/60 backdrop-blur-sm border-l border-white/20 p-4 overflow-y-auto">
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg p-3 mb-4">
              <h3 className="text-base font-bold text-white mb-1 flex items-center space-x-2">
                <FileText className="h-4 w-4" />
                <span>Document Info</span>
              </h3>
              <p className="text-blue-100 text-xs">Currently learning from</p>
            </div>

            <div className="space-y-4">
              <div className="bg-white/80 rounded-lg p-3 shadow-sm">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Filename</label>
                <p className="text-xs text-slate-800 font-medium break-words mt-1">{pdfInfo.filename}</p>
              </div>

              <div className="bg-white/80 rounded-lg p-3 shadow-sm">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Title</label>
                <p className="text-xs text-slate-800 font-medium mt-1">{pdfInfo.metadata.title}</p>
              </div>

              <div className="bg-white/80 rounded-lg p-3 shadow-sm">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide flex items-center space-x-1">
                  <User className="h-3 w-3" />
                  <span>Author</span>
                </label>
                <p className="text-xs text-slate-800 font-medium mt-1">{pdfInfo.metadata.author}</p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <div className="bg-white/80 rounded-lg p-2 shadow-sm">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide flex items-center space-x-1">
                    <Hash className="h-3 w-3" />
                    <span>Pages</span>
                  </label>
                  <p className="text-sm font-bold text-slate-800 mt-1">{pdfInfo.metadata.pages}</p>
                </div>

                <div className="bg-white/80 rounded-lg p-2 shadow-sm">
                  <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide flex items-center space-x-1">
                    <HardDrive className="h-3 w-3" />
                    <span>Size</span>
                  </label>
                  <p className="text-xs font-bold text-slate-800 mt-1">{formatFileSize(pdfInfo.metadata.file_size)}</p>
                </div>
              </div>

              <div className="bg-white/80 rounded-lg p-3 shadow-sm">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide flex items-center space-x-1">
                  <Calendar className="h-3 w-3" />
                  <span>Selected</span>
                </label>
                <p className="text-xs text-slate-800 font-medium mt-1">{formatDate(pdfInfo.selected_at || pdfInfo.uploaded_at || 'Unknown')}</p>
              </div>

              <div className="bg-white/80 rounded-lg p-3 shadow-sm">
                <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Subject</label>
                <p className="text-xs text-slate-800 font-medium mt-1">{pdfInfo.metadata.subject}</p>
              </div>

              <div className="bg-gradient-to-r from-emerald-500 to-teal-500 rounded-lg p-3 text-white">
                <label className="text-xs font-semibold text-emerald-100 uppercase tracking-wide">Content Length</label>
                <p className="text-sm font-bold mt-1">{pdfInfo.text_length.toLocaleString()}</p>
                <p className="text-xs text-emerald-100">characters extracted</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
