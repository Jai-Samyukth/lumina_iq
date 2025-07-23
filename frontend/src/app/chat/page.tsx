'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useBook } from '@/contexts/BookContext';
import { chatApi, pdfApi, ChatHistoryItem, PDFSessionInfo } from '@/lib/api';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import {
  Send,
  MessageCircle,
  Bot,
  Copy,
  Check,
} from 'lucide-react';


export default function ChatPage() {
  const [message, setMessage] = useState('');
  const [chatHistory, setChatHistory] = useState<ChatHistoryItem[]>([]);
  const [pdfInfo, setPdfInfo] = useState<PDFSessionInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(true);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const { user } = useAuth();
  const { selectedBook } = useBook();
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
      // Try to load chat history, but don't require PDF info
      const historyData = await chatApi.getChatHistory().catch(() => ({ history: [] }));
      setChatHistory(historyData.history);

      // Try to load PDF info if available, but don't fail if not
      try {
        const pdfData = await pdfApi.getPDFInfo();
        setPdfInfo(pdfData);
      } catch (pdfError) {
        console.log('No PDF loaded yet, using book selection mode');
        setPdfInfo(null);
      }
    } catch (error) {
      console.error('Failed to load initial data:', error);
      // Don't redirect, just continue with empty state
      setChatHistory([]);
      setPdfInfo(null);
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
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-text-secondary">Loading your learning session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-6 py-6 space-y-6 chat-scroll">
            {chatHistory.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-primary p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                  <MessageCircle className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-text mb-2">
                  Start Your Learning Journey
                </h3>
                <p className="text-text-secondary max-w-md mx-auto leading-relaxed">
                  {selectedBook ?
                    `Ask any question about "${selectedBook.title}". I'm here to help you understand and learn from the content.` :
                    pdfInfo ?
                    `Ask any question about "${pdfInfo.filename}". I'm here to help you understand and learn from the content.` :
                    'Select a book using the floating button and start asking questions about it!'
                  }
                </p>
                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-3 max-w-lg mx-auto">
                  <div className="bg-card-bg rounded-lg p-3 border border-border">
                    <h4 className="font-medium text-text mb-1">💡 Ask for explanations</h4>
                    <p className="text-xs text-text-secondary">"Explain the main concepts"</p>
                  </div>
                  <div className="bg-card-bg rounded-lg p-3 border border-border">
                    <h4 className="font-medium text-text mb-1">🔍 Get specific details</h4>
                    <p className="text-xs text-text-secondary">"What are the key points..."</p>
                  </div>
                </div>
              </div>
            ) : (
              chatHistory.map((chat, index) => (
                <div key={index} className="space-y-4">
                  {/* User Message */}
                  <div className="flex justify-end">
                    <div className="bg-primary text-white rounded-2xl rounded-tr-md px-4 py-3 max-w-xs md:max-w-2xl shadow-lg">
                      <p className="text-sm leading-relaxed">{chat.user}</p>
                    </div>
                  </div>

                  {/* AI Response */}
                  <div className="flex items-start space-x-3">
                    <div className="bg-secondary p-2 rounded-lg flex-shrink-0 shadow-lg">
                      <Bot className="h-4 w-4 text-white" />
                    </div>
                    <div className="bg-card-bg rounded-2xl rounded-tl-md px-4 py-3 shadow-xl border border-border flex-1">
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
                              <h1 className="text-lg font-bold text-text mb-2 border-b border-border pb-1">
                                {children}
                              </h1>
                            ),
                            h2: ({ children }) => (
                              <h2 className="text-base font-semibold text-text mb-2 mt-3">
                                {children}
                              </h2>
                            ),
                            h3: ({ children }) => (
                              <h3 className="text-sm font-semibold text-text mb-1 mt-2">
                                {children}
                              </h3>
                            ),
                            p: ({ children }) => (
                              <p className="text-text leading-relaxed mb-2">
                                {children}
                              </p>
                            ),
                            ul: ({ children }) => (
                              <ul className="list-disc list-inside text-text space-y-0.5 mb-2 ml-2">
                                {children}
                              </ul>
                            ),
                            ol: ({ children }) => (
                              <ol className="list-decimal list-inside text-text space-y-0.5 mb-2 ml-2">
                                {children}
                              </ol>
                            ),
                            li: ({ children }) => (
                              <li className="text-text text-sm">{children}</li>
                            ),
                            blockquote: ({ children }) => (
                              <blockquote className="border-l-3 border-primary pl-3 italic text-text-secondary bg-primary/10 py-2 rounded-r mb-2">
                                {children}
                              </blockquote>
                            ),
                            strong: ({ children }) => (
                              <strong className="font-semibold text-text">{children}</strong>
                            ),
                            em: ({ children }) => (
                              <em className="italic text-text">{children}</em>
                            ),
                          }}
                        >
                          {chat.assistant}
                        </ReactMarkdown>
                      </div>
                      <div className="flex items-center justify-between mt-3 pt-2 border-t border-border">
                        <p className="text-xs text-text-secondary">
                          {formatDate(chat.timestamp)}
                        </p>
                        <button
                          onClick={() => copyToClipboard(chat.assistant, index + 1000)}
                          className="flex items-center space-x-1 text-xs text-text-secondary hover:text-text transition-colors"
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
                <div className="bg-secondary p-2 rounded-lg flex-shrink-0 shadow-lg">
                  <Bot className="h-4 w-4 text-white" />
                </div>
                <div className="bg-card-bg rounded-2xl rounded-tl-md px-4 py-3 shadow-xl border border-border">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full animate-bounce"></div>
                      <div className="w-1.5 h-1.5 bg-secondary rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-1.5 h-1.5 bg-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-sm text-text-secondary">AI is thinking...</span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Message Input - Fixed at bottom */}
          <div className="border-t border-border bg-card-bg p-4">
            <form onSubmit={handleSendMessage} className="flex space-x-3 max-w-4xl mx-auto">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder={selectedBook ? `Ask a question about "${selectedBook.title}"...` : pdfInfo ? `Ask a question about "${pdfInfo.filename}"...` : "Select a book first, then ask questions..."}
                  className="w-full border border-border rounded-xl px-4 py-3 pr-10 focus:ring-2 focus:ring-primary focus:border-primary transition-all duration-200 bg-background shadow-md text-text placeholder-text-secondary"
                  disabled={loading}
                />
                <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                  <MessageCircle className="h-4 w-4 text-text-secondary" />
                </div>
              </div>
              <button
                type="submit"
                disabled={loading || !message.trim()}
                className="btn-primary px-6 py-3 rounded-xl font-medium focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
  );
}
