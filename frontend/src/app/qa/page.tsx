'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useBook } from '@/contexts/BookContext';
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
  HelpCircle,
  ChevronDown,
  ChevronRight,
  Sparkles,
  Brain,
  MessageSquare,
  StickyNote
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
  const [questionTopic, setQuestionTopic] = useState('');
  const [questionCount, setQuestionCount] = useState(25);
  
  const { logout, user } = useAuth();
  const { selectedBook } = useBook();
  const router = useRouter();

  useEffect(() => {
    // No need to load PDF info - we use book context instead
    setInitialLoading(false);
  }, []);

  const generateChapterQuestions = async (topic?: string) => {
    if (!selectedBook && !pdfInfo) return;

    setGeneratingQuestions(true);
    try {
      const topicToUse = topic || questionTopic.trim();
      const documentName = selectedBook ? selectedBook.title : pdfInfo?.filename || 'Unknown Document';
      console.log('Starting question generation for:', documentName, 'Topic:', topicToUse);

      // Use the dedicated question generation endpoint that includes full PDF content
      const response = await chatApi.generateQuestions(topicToUse, questionCount);

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

          if (parsedData.questions && Array.isArray(parsedData.questions)) {
            // Create a single chapter with all questions
            const generatedChapters: Chapter[] = [{
              id: 'main-questions',
              title: `Questions for: ${documentName}${topicToUse ? ` - Topic: ${topicToUse}` : ''}`,
              questions: parsedData.questions.map((q: string, qIndex: number) => ({
                id: `q-${qIndex}`,
                question: q,
                answer: undefined,
                loading: false
              })),
              expanded: true, // Always expanded since there's only one section
              loading: false
            }];

            console.log('Generated questions:', parsedData.questions.length);
            setChapters(generatedChapters);
          } else {
            throw new Error('Invalid questions structure - expected questions array');
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

          if (parsedData.questions && Array.isArray(parsedData.questions)) {
            // Create a single chapter with all questions
            const generatedChapters: Chapter[] = [{
              id: 'main-questions',
              title: `Questions for: ${selectedBook ? selectedBook.title : pdfInfo?.filename || 'Unknown Document'}${questionTopic.trim() ? ` - Topic: ${questionTopic.trim()}` : ''}`,
              questions: parsedData.questions.map((q: string, qIndex: number) => ({
                id: `q-${qIndex}`,
                question: q,
                answer: undefined,
                loading: false
              })),
              expanded: true,
              loading: false
            }];

            if (generatedChapters[0].questions.length > 0) {
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
      const documentName = selectedBook ? selectedBook.title : pdfInfo?.filename || 'the selected document';
      const response = await chatApi.sendMessage(`You are an educational AI assistant. Based on the FULL content of the document "${documentName}", please provide a comprehensive and detailed answer to this question:

QUESTION: "${question.question}"

REQUIREMENTS:
1. Use ONLY information from the document content
2. Provide specific details, examples, and explanations from the text
3. Make the answer educational and easy to understand
4. Include relevant quotes or references from the document when applicable
5. Structure the answer clearly with proper formatting
6. If the question asks for examples, provide the actual examples from the document
7. If the question asks for definitions, use the exact definitions from the text

Please provide a thorough, well-structured answer that helps the user learn from the document content.`);

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
      const response = await chatApi.sendMessage("Please respond with 'AI connection working' to test the connection.");
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
    <div className="min-h-screen bg-background flex flex-col">
      {/* Main Content */}
      <div className="flex-1 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-text font-display mb-2">
              Q&A Learning
            </h1>
            {selectedBook ? (
              <p className="text-text-secondary">Generate questions and answers for "{selectedBook.title}"</p>
            ) : pdfInfo ? (
              <p className="text-text-secondary">Generate questions and answers for "{pdfInfo.filename}"</p>
            ) : (
              <p className="text-text-secondary">Select a book to start generating questions and answers</p>
            )}
          </div>
          {/* Q&A Content */}
          <div className="space-y-6">
            {generatingQuestions ? (
              <div className="text-center py-12">
                <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg animate-pulse">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Generating Questions...
                </h3>
                <p className="text-slate-600 max-w-md mx-auto leading-relaxed">
                  AI is analyzing your document "{selectedBook ? selectedBook.title : pdfInfo?.filename || 'Unknown Document'}" and creating 25 comprehensive questions{questionTopic.trim() ? ` focused on "${questionTopic.trim()}"` : ' based on the entire content'}.
                </p>
                <div className="mt-4 text-sm text-slate-500">
                  This may take 30-60 seconds...
                </div>
              </div>
            ) : chapters.length === 0 ? (
              <div className="text-center py-12">
                <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                  <Sparkles className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-xl font-bold text-slate-800 mb-2">
                  Ready to Generate Questions
                </h3>
                <p className="text-slate-600 max-w-md mx-auto leading-relaxed mb-6">
                  Your document "{selectedBook ? selectedBook.title : pdfInfo?.filename || 'Unknown Document'}" is loaded and ready. You can generate questions for the entire document or focus on a specific topic.
                </p>

                {/* Topic Input Box */}
                <div className="max-w-md mx-auto mb-6">
                  <label htmlFor="questionTopic" className="block text-sm font-medium text-slate-700 mb-2 text-left">
                    Specific Topic (Optional)
                  </label>
                  <input
                    id="questionTopic"
                    type="text"
                    value={questionTopic}
                    onChange={(e) => setQuestionTopic(e.target.value)}
                    placeholder="e.g., 'machine learning algorithms', 'chapter 3', 'data structures'..."
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-colors text-sm"
                  />
                  <p className="text-xs text-slate-500 mt-1 text-left">
                    Leave empty to generate questions about the entire document, or specify a topic to focus on specific content.
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 max-w-md mx-auto mb-6">
                  <p className="text-sm text-blue-800">
                    <strong>What you'll get:</strong>
                  </p>
                  <ul className="text-sm text-blue-700 text-left mt-2 space-y-1">
                    <li>• 25 comprehensive questions {questionTopic.trim() ? `focused on "${questionTopic.trim()}"` : 'covering the entire document'}</li>
                    <li>• Questions about key concepts, definitions, and examples</li>
                    <li>• Critical thinking questions for deeper understanding</li>
                    <li>• Click any question to get detailed AI-powered answers</li>
                  </ul>
                </div>
                <button
                  onClick={() => generateChapterQuestions()}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                >
                  <Sparkles className="h-5 w-5 inline mr-2" />
                  Generate Questions{questionTopic.trim() ? ` about "${questionTopic.trim()}"` : ''}
                </button>
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
                        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded-full">
                          {chapter.questions.length} questions
                        </span>
                      </div>
                      <div className="flex items-center space-x-2">
                        {chapter.loading && (
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        )}
                        {chapter.expanded ? (
                          <ChevronDown className="h-5 w-5 text-slate-600" />
                        ) : (
                          <ChevronRight className="h-5 w-5 text-slate-600" />
                        )}
                      </div>
                    </button>

                    {chapter.expanded && (
                      <div className="px-4 pb-4 space-y-3">
                        {chapter.questions.map((question) => (
                          <div key={question.id} className="bg-white/60 backdrop-blur-sm rounded-lg border border-white/30">
                            <button
                              onClick={() => handleQuestionClick(chapter.id, question.id)}
                              className="w-full text-left p-4 hover:bg-white/40 transition-colors rounded-lg"
                              disabled={question.loading}
                            >
                              <div className="flex items-start space-x-3">
                                <div className="flex-shrink-0 mt-1">
                                  {question.loading ? (
                                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                                  ) : question.answer ? (
                                    <div className="w-4 h-4 bg-green-500 rounded-full flex items-center justify-center">
                                      <div className="w-2 h-2 bg-white rounded-full"></div>
                                    </div>
                                  ) : (
                                    <HelpCircle className="h-4 w-4 text-blue-500" />
                                  )}
                                </div>
                                <div className="flex-1">
                                  <p className="text-slate-800 font-medium mb-2">{question.question}</p>
                                  {question.answer && (
                                    <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-3 border border-blue-100">
                                      <div className="prose prose-sm max-w-none text-slate-700">
                                        <ReactMarkdown
                                          remarkPlugins={[remarkGfm]}
                                          components={{
                                            h1: ({ children }) => (
                                              <h1 className="text-lg font-bold text-slate-800 mb-3 mt-4 first:mt-0">
                                                {children}
                                              </h1>
                                            ),
                                            h2: ({ children }) => (
                                              <h2 className="text-base font-semibold text-slate-800 mb-2 mt-3">
                                                {children}
                                              </h2>
                                            ),
                                            h3: ({ children }) => (
                                              <h3 className="text-sm font-semibold text-slate-700 mb-2 mt-3">
                                                {children}
                                              </h3>
                                            ),
                                            p: ({ children }) => (
                                              <p className="text-slate-700 leading-relaxed mb-2">
                                                {children}
                                              </p>
                                            ),
                                            ul: ({ children }) => (
                                              <ul className="list-disc list-inside text-slate-700 space-y-1 mb-2 ml-2">
                                                {children}
                                              </ul>
                                            ),
                                            ol: ({ children }) => (
                                              <ol className="list-decimal list-inside text-slate-700 space-y-1 mb-2 ml-2">
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
                                            code: ({ className, children, ...props }) => {
                                              const isInline = 'inline' in props;
                                              return !isInline ? (
                                                <div className="relative my-2">
                                                  <pre className="bg-slate-800 text-slate-100 rounded p-2 overflow-x-auto text-xs">
                                                    <code className={className} {...props}>
                                                      {children}
                                                    </code>
                                                  </pre>
                                                </div>
                                              ) : (
                                                <code className="bg-slate-200 text-slate-800 px-1 py-0.5 rounded text-xs font-mono" {...props}>
                                                  {children}
                                                </code>
                                              );
                                            },
                                            strong: ({ children }) => (
                                              <strong className="font-semibold text-slate-800">{children}</strong>
                                            ),
                                            em: ({ children }) => (
                                              <em className="italic text-slate-700">{children}</em>
                                            ),
                                            table: ({ children }) => (
                                              <div className="overflow-x-auto mb-2">
                                                <table className="min-w-full border border-slate-300 rounded text-xs">
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
                                              <th className="border border-slate-300 px-2 py-1 text-left font-semibold text-slate-700">
                                                {children}
                                              </th>
                                            ),
                                            td: ({ children }) => (
                                              <td className="border border-slate-300 px-2 py-1 text-slate-700">
                                                {children}
                                              </td>
                                            ),
                                          }}
                                        >
                                          {question.answer}
                                        </ReactMarkdown>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              </div>
                            </button>
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

        {/* Sidebar */}
        {(selectedBook || pdfInfo) && (
          <div className="w-80 bg-white/60 backdrop-blur-sm border-l border-white/20 p-6 overflow-y-auto">
            <div className="space-y-6">
              <div>
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
                  <FileText className="h-5 w-5 mr-2 text-blue-600" />
                  Document Info
                </h3>
                <div className="space-y-3">
                  <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 border border-white/30">
                    <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      {selectedBook ? 'Book Title' : 'Filename'}
                    </label>
                    <p className="text-sm font-medium text-slate-800 mt-1 break-words">
                      {selectedBook ? selectedBook.title : pdfInfo?.filename || 'Unknown'}
                    </p>
                  </div>

                  {selectedBook && (
                    <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 border border-white/30">
                      <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Author</label>
                      <p className="text-sm font-medium text-slate-800 mt-1">{selectedBook.author}</p>
                    </div>
                  )}

                  <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 border border-white/30">
                    <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">File Size</label>
                    <p className="text-sm font-medium text-slate-800 mt-1">
                      {formatFileSize(
                        selectedBook ? (selectedBook.metadata?.file_size || 0) : (pdfInfo?.metadata?.file_size || 0)
                      )}
                    </p>
                  </div>

                  <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 border border-white/30">
                    <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Pages</label>
                    <p className="text-sm font-medium text-slate-800 mt-1">
                      {selectedBook ?
                        (selectedBook.metadata?.pages || 10) :
                        (pdfInfo?.metadata?.pages || 'Unknown')
                      }
                    </p>
                  </div>

                  <div className="bg-white/80 backdrop-blur-sm rounded-lg p-3 border border-white/30">
                    <label className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Selected Date</label>
                    <p className="text-sm font-medium text-slate-800 mt-1">
                      {formatDate(
                        selectedBook ? (selectedBook.selected_at || 'Unknown') : (pdfInfo?.selected_at || 'Unknown')
                      )}
                    </p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
                  <Hash className="h-5 w-5 mr-2 text-purple-600" />
                  Quick Actions
                </h3>
                <div className="space-y-3">
                  <button
                    onClick={testAIConnection}
                    disabled={testingAI}
                    className="w-full bg-gradient-to-r from-emerald-500 to-teal-600 text-white px-4 py-2 rounded-lg font-medium hover:from-emerald-600 hover:to-teal-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {testingAI ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Testing...</span>
                      </div>
                    ) : (
                      'Test AI Connection'
                    )}
                  </button>

                  <button
                    onClick={() => generateChapterQuestions()}
                    disabled={generatingQuestions}
                    className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white px-4 py-2 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-md hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {generatingQuestions ? (
                      <div className="flex items-center justify-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        <span>Generating...</span>
                      </div>
                    ) : (
                      'Regenerate Questions'
                    )}
                  </button>
                </div>
              </div>

              {chapters.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold text-slate-800 mb-4 flex items-center">
                    <HardDrive className="h-5 w-5 mr-2 text-indigo-600" />
                    Statistics
                  </h3>
                  <div className="space-y-3">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-lg p-3 text-white">
                      <label className="text-xs font-semibold text-blue-100 uppercase tracking-wide">Total Chapters</label>
                      <p className="text-sm font-bold mt-1">{chapters.length}</p>
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
        )}
      </div>
    </div>
  );
}