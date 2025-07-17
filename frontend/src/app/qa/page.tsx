'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { chatApi, pdfApi, PDFSessionInfo } from '@/lib/api';
import { 
  BookOpen, 
  LogOut, 
  FileText, 
  User, 
  Hash,
  HardDrive,
  Calendar,
  Upload as UploadIcon,
  HelpCircle,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Brain,
  MessageSquare
} from 'lucide-react';

interface Question {
  id: string;
  question: string;
  answer?: string;
  loading?: boolean;
}

interface Chapter {
  id: string;
  title: string;
  questions: Question[];
  expanded: boolean;
  loading: boolean;
}

export default function QAPage() {
  const [chapters, setChapters] = useState<Chapter[]>([]);
  const [pdfInfo, setPdfInfo] = useState<PDFSessionInfo | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  const [testingAI, setTestingAI] = useState(false);
  
  const { logout, user } = useAuth();
  const router = useRouter();

  useEffect(() => {
    loadPDFInfo();
  }, []);

  const loadPDFInfo = async () => {
    try {
      console.log('Loading PDF info...');
      const info = await pdfApi.getPDFInfo();
      console.log('PDF info loaded:', info);
      setPdfInfo(info);
      await generateChapterQuestions();
    } catch (error) {
      console.error('Error loading PDF info:', error);
      // Show error message instead of redirecting immediately
      alert('No PDF selected. Please select a PDF first.');
      router.push('/upload');
    } finally {
      setInitialLoading(false);
    }
  };

  const generateChapterQuestions = async () => {
    if (!pdfInfo) return;

    setGeneratingQuestions(true);
    try {
      console.log('Starting question generation for:', pdfInfo.filename);

      // Use the dedicated question generation endpoint that includes full PDF content
      const response = await chatApi.generateQuestions();

      console.log('AI Response received:', response.response.substring(0, 200) + '...');

      // Parse the AI response to extract chapters and questions
      const aiResponse = response.response;

      // Try to extract JSON from the response
      let jsonMatch = aiResponse.match(/\{[\s\S]*\}/);

      if (!jsonMatch) {
        // Try to find JSON between code blocks
        const codeBlockMatch = aiResponse.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
        if (codeBlockMatch) {
          jsonMatch = [codeBlockMatch[1]];
        }
      }

      if (jsonMatch) {
        try {
          const parsedData = JSON.parse(jsonMatch[0]);
          console.log('Parsed data:', parsedData);

          if (parsedData.chapters && Array.isArray(parsedData.chapters)) {
            const generatedChapters: Chapter[] = parsedData.chapters.map((chapter: any, index: number) => ({
              id: `chapter-${index}`,
              title: chapter.title || `Chapter ${index + 1}`,
              questions: (chapter.questions || []).slice(0, 15).map((q: string, qIndex: number) => ({
                id: `q-${index}-${qIndex}`,
                question: q,
                answer: undefined,
                loading: false
              })),
              expanded: false,
              loading: false
            }));

            console.log('Generated chapters:', generatedChapters.length);
            setChapters(generatedChapters);
          } else {
            throw new Error('Invalid chapter structure');
          }
        } catch (parseError) {
          console.error('JSON parsing error:', parseError);
          console.log('Raw response:', aiResponse);
          createDefaultChapters();
        }
      } else {
        console.log('No JSON found in response:', aiResponse);
        createDefaultChapters();
      }
    } catch (error) {
      console.error('Error generating questions:', error);
      createDefaultChapters();
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const createDefaultChapters = async () => {
    console.log('Creating default chapters...');

    // Try a simpler approach for question generation using the dedicated endpoint
    try {
      const response = await chatApi.generateQuestions();

      // Try to parse the JSON response from the dedicated endpoint
      const aiResponse = response.response;
      let jsonMatch = aiResponse.match(/\{[\s\S]*\}/);

      if (!jsonMatch) {
        const codeBlockMatch = aiResponse.match(/```(?:json)?\s*(\{[\s\S]*?\})\s*```/);
        if (codeBlockMatch) {
          jsonMatch = [codeBlockMatch[1]];
        }
      }

      if (jsonMatch) {
        try {
          const parsedData = JSON.parse(jsonMatch[0]);
          console.log('Parsed data from default chapters:', parsedData);

          if (parsedData.chapters && Array.isArray(parsedData.chapters)) {
            const generatedChapters: Chapter[] = parsedData.chapters.map((chapter: any, index: number) => ({
              id: `chapter-${index}`,
              title: chapter.title || `Chapter ${index + 1}`,
              questions: (chapter.questions || []).slice(0, 15).map((q: string, qIndex: number) => ({
                id: `q-${index}-${qIndex}`,
                question: q,
                answer: undefined,
                loading: false
              })),
              expanded: false,
              loading: false
            }));

            if (generatedChapters.length > 0) {
              setChapters(generatedChapters);
              return;
            }
          }
        } catch (parseError) {
          console.error('JSON parsing error in default chapters:', parseError);
        }
      }

      // Final fallback
      setChapters([{
        id: 'chapter-1',
        title: 'Document Analysis',
        questions: Array.from({ length: 10 }, (_, i) => ({
          id: `q-1-${i}`,
          question: `What are the key points discussed in this document?`,
          answer: undefined,
          loading: false
        })),
        expanded: false,
        loading: false
      }]);
    } catch (error) {
      console.error('Error in default chapters:', error);
      // Final fallback
      setChapters([{
        id: 'chapter-1',
        title: 'Document Analysis',
        questions: Array.from({ length: 10 }, (_, i) => ({
          id: `q-1-${i}`,
          question: `What are the key points discussed in this document?`,
          answer: undefined,
          loading: false
        })),
        expanded: false,
        loading: false
      }]);
    }
  };

  const toggleChapter = (chapterId: string) => {
    setChapters(prev => prev.map(chapter => 
      chapter.id === chapterId 
        ? { ...chapter, expanded: !chapter.expanded }
        : chapter
    ));
  };

  const handleQuestionClick = async (chapterId: string, questionId: string) => {
    const chapter = chapters.find(c => c.id === chapterId);
    const question = chapter?.questions.find(q => q.id === questionId);

    if (!question || question.answer) return;

    console.log('Answering question:', question.question);

    // Set loading state for this question
    setChapters(prev => prev.map(chapter =>
      chapter.id === chapterId
        ? {
            ...chapter,
            questions: chapter.questions.map(q =>
              q.id === questionId ? { ...q, loading: true } : q
            )
          }
        : chapter
    ));

    try {
      const response = await chatApi.sendMessage({
        message: `You are an educational AI assistant. Based on the FULL content of the document "${pdfInfo?.filename}", please provide a comprehensive and detailed answer to this question:

QUESTION: "${question.question}"

REQUIREMENTS:
1. Use ONLY information from the document content
2. Provide specific details, examples, and explanations from the text
3. Make the answer educational and easy to understand
4. Include relevant quotes or references from the document when applicable
5. Structure the answer clearly with proper formatting
6. If the question asks for examples, provide the actual examples from the document
7. If the question asks for definitions, use the exact definitions from the text

Please provide a thorough, well-structured answer that helps the user learn from the document content.`
      });

      console.log('Answer received for question:', question.question);

      // Update the question with the answer
      setChapters(prev => prev.map(chapter =>
        chapter.id === chapterId
          ? {
              ...chapter,
              questions: chapter.questions.map(q =>
                q.id === questionId
                  ? { ...q, answer: response.response, loading: false }
                  : q
              )
            }
          : chapter
      ));
    } catch (error) {
      console.error('Error getting answer:', error);
      setChapters(prev => prev.map(chapter =>
        chapter.id === chapterId
          ? {
              ...chapter,
              questions: chapter.questions.map(q =>
                q.id === questionId
                  ? { ...q, loading: false }
                  : q
              )
            }
          : chapter
      ));
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

  const testAIConnection = async () => {
    setTestingAI(true);
    try {
      const response = await chatApi.sendMessage({
        message: "Please respond with 'AI connection working' to test the connection."
      });
      alert(`AI Response: ${response.response}`);
    } catch (error) {
      alert(`AI Connection Error: ${error}`);
    } finally {
      setTestingAI(false);
    }
  };

  if (initialLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading Q&A...</p>
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
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Q&A Learning
                </h1>
                {pdfInfo && (
                  <p className="text-sm text-slate-600 font-medium">{pdfInfo.filename}</p>
                )}
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <button
                onClick={() => router.push('/chat')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg hover:from-emerald-600 hover:to-teal-700 transition-all duration-200 shadow-md hover:shadow-lg"
              >
                <MessageSquare className="h-4 w-4" />
                <span className="text-sm font-medium">Chat</span>
              </button>
              <button
                onClick={() => router.push('/upload')}
                className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-orange-500 to-red-600 text-white rounded-lg hover:from-orange-600 hover:to-red-700 transition-all duration-200 shadow-md hover:shadow-lg"
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
        {/* Q&A Area */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto">
          <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6 chat-scroll">
            {generatingQuestions ? (
              <div className="text-center py-12">
                <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg animate-pulse">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Generating Questions...
                </h3>
                <p className="text-slate-600 max-w-md mx-auto leading-relaxed">
                  AI is analyzing your document "{pdfInfo?.filename}" and creating comprehensive questions for each chapter.
                </p>
                <div className="mt-4 text-sm text-slate-500">
                  This may take 30-60 seconds...
                </div>
              </div>
            ) : chapters.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-red-100 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                  <HelpCircle className="h-8 w-8 text-red-600" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  No Questions Generated
                </h3>
                <p className="text-slate-600 max-w-md mx-auto leading-relaxed mb-4">
                  Unable to generate questions from the document. This might be due to:
                </p>
                <ul className="text-sm text-slate-600 text-left max-w-md mx-auto space-y-1">
                  <li>• Document content is too short</li>
                  <li>• AI service is temporarily unavailable</li>
                  <li>• Document format is not supported</li>
                </ul>
                <div className="mt-4 space-x-3">
                  <button
                    onClick={() => generateChapterQuestions()}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200"
                  >
                    Try Again
                  </button>
                  <button
                    onClick={testAIConnection}
                    disabled={testingAI}
                    className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-2 rounded-lg font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-200 disabled:opacity-50"
                  >
                    {testingAI ? 'Testing...' : 'Test AI'}
                  </button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {chapters.map((chapter) => (
                  <div key={chapter.id} className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20">
                    <button
                      onClick={() => toggleChapter(chapter.id)}
                      className="w-full flex items-center justify-between p-4 hover:bg-white/60 transition-colors rounded-xl"
                    >
                      <div className="flex items-center space-x-3">
                        <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-2 rounded-lg">
                          <BookOpen className="h-4 w-4 text-white" />
                        </div>
                        <h3 className="text-lg font-semibold text-slate-800">{chapter.title}</h3>
                        <span className="text-sm text-slate-500">({chapter.questions.length} questions)</span>
                      </div>
                      {chapter.expanded ? (
                        <ChevronDown className="h-5 w-5 text-slate-600" />
                      ) : (
                        <ChevronRight className="h-5 w-5 text-slate-600" />
                      )}
                    </button>
                    
                    {chapter.expanded && (
                      <div className="px-4 pb-4 space-y-2">
                        {chapter.questions.map((question) => (
                          <div key={question.id} className="border border-slate-200 rounded-lg">
                            <button
                              onClick={() => handleQuestionClick(chapter.id, question.id)}
                              className="w-full text-left p-3 hover:bg-slate-50 transition-colors flex items-center justify-between"
                              disabled={question.loading}
                            >
                              <div className="flex items-center space-x-2">
                                <HelpCircle className="h-4 w-4 text-blue-500 flex-shrink-0" />
                                <span className="text-sm text-slate-700">{question.question}</span>
                              </div>
                              {question.loading && (
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                              )}
                            </button>
                            
                            {question.answer && (
                              <div className="px-3 pb-3 border-t border-slate-200 bg-slate-50/50">
                                <div className="pt-3 text-sm text-slate-700 leading-relaxed">
                                  {question.answer}
                                </div>
                              </div>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
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
              <p className="text-blue-100 text-xs">Q&A Learning Mode</p>
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
              
              <div className="bg-gradient-to-r from-purple-500 to-indigo-500 rounded-lg p-3 text-white">
                <label className="text-xs font-semibold text-purple-100 uppercase tracking-wide">Questions Generated</label>
                <p className="text-sm font-bold mt-1">{chapters.reduce((total, chapter) => total + chapter.questions.length, 0)}</p>
                <p className="text-xs text-purple-100">across {chapters.length} chapters</p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
