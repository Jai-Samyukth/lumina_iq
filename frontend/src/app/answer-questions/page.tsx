'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { useBook } from '@/contexts/BookContext';
import { 
  chatApi, 
  pdfApi, 
  PDFSessionInfo, 
  AnswerEvaluationResponse, 
  QuizSubmissionResponse,
  QuizAnswer 
} from '@/lib/api';
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
  CheckCircle,
  Clock,
  Target,
  Award,
  TrendingUp,
  AlertCircle,
  StickyNote
} from 'lucide-react';

interface Question {
  id: string;
  question: string;
  userAnswer: string;
  evaluation?: AnswerEvaluationResponse;
  isAnswered: boolean;
}

type QuestionMode = 'quiz' | 'practice';
type EvaluationLevel = 'easy' | 'medium' | 'strict';
type CurrentStep = 'setup' | 'answering' | 'results';

export default function AnswerQuestionsPage() {
  const [pdfInfo, setPdfInfo] = useState<PDFSessionInfo | null>(null);
  const [initialLoading, setInitialLoading] = useState(true);
  const [currentStep, setCurrentStep] = useState<CurrentStep>('setup');
  
  // Setup state
  const [questionTopic, setQuestionTopic] = useState('');
  const [questionCount, setQuestionCount] = useState(10);
  const [questionMode, setQuestionMode] = useState<QuestionMode>('quiz');
  const [evaluationLevel, setEvaluationLevel] = useState<EvaluationLevel>('medium');
  const [generatingQuestions, setGeneratingQuestions] = useState(false);
  
  // Questions and answers state
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [evaluatingAnswers, setEvaluatingAnswers] = useState(false);
  
  // Results state
  const [quizResults, setQuizResults] = useState<QuizSubmissionResponse | null>(null);
  
  const { logout, user } = useAuth();
  const { selectedBook } = useBook();
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
      // Don't redirect, just continue with book selection mode
      setPdfInfo(null);
    } finally {
      setInitialLoading(false);
    }
  };

  const generateQuestions = async () => {
    if (!pdfInfo) return;

    setGeneratingQuestions(true);
    try {
      const topicToUse = questionTopic.trim();
      console.log('Starting question generation for:', pdfInfo.filename, 'Topic:', topicToUse);

      const response = await chatApi.generateQuestions(topicToUse, questionCount);
      console.log('AI Response received:', response.response.substring(0, 200) + '...');

      // Parse the AI response to extract questions
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

          if (parsedData.questions && Array.isArray(parsedData.questions)) {
            const generatedQuestions: Question[] = parsedData.questions.map((q: string, qIndex: number) => ({
              id: `q-${qIndex}`,
              question: q,
              userAnswer: '',
              isAnswered: false
            }));

            console.log('Generated questions:', parsedData.questions.length);
            setQuestions(generatedQuestions);
            setCurrentStep('answering');
          } else {
            throw new Error('Invalid questions structure - expected questions array');
          }
        } catch (parseError) {
          console.error('Failed to parse questions JSON:', parseError);
          alert('Failed to parse generated questions. Please try again.');
        }
      } else {
        console.error('No JSON found in AI response');
        alert('Failed to generate questions. Please try again.');
      }
    } catch (error) {
      console.error('Failed to generate questions:', error);
      alert('Failed to generate questions. Please try again.');
    } finally {
      setGeneratingQuestions(false);
    }
  };

  const handleAnswerChange = (questionId: string, answer: string) => {
    setQuestions(prev => prev.map(q => 
      q.id === questionId 
        ? { ...q, userAnswer: answer, isAnswered: answer.trim().length > 0 }
        : q
    ));
  };

  const evaluateAnswers = async () => {
    if (!questions.length) return;

    setEvaluatingAnswers(true);
    try {
      if (questionMode === 'quiz') {
        // Evaluate all answers together for quiz mode
        const quizAnswers: QuizAnswer[] = questions.map(q => ({
          question_id: q.id,
          question: q.question,
          user_answer: q.userAnswer
        }));

        const results = await chatApi.evaluateQuiz({
          answers: quizAnswers,
          topic: questionTopic.trim() || undefined,
          evaluation_level: evaluationLevel
        });

        setQuizResults(results);
        
        // Update questions with individual evaluations
        setQuestions(prev => prev.map(q => {
          const evaluation = results.individual_results.find(r => r.question_id === q.id);
          return evaluation ? { ...q, evaluation } : q;
        }));
      } else {
        // Evaluate answers individually for practice mode
        const evaluatedQuestions = [...questions];
        
        for (let i = 0; i < questions.length; i++) {
          const question = questions[i];
          if (question.userAnswer.trim()) {
            try {
              const evaluation = await chatApi.evaluateAnswer({
                question: question.question,
                user_answer: question.userAnswer,
                question_id: question.id,
                evaluation_level: evaluationLevel
              });
              evaluatedQuestions[i] = { ...question, evaluation };
            } catch (error) {
              console.error(`Failed to evaluate question ${question.id}:`, error);
            }
          }
        }
        
        setQuestions(evaluatedQuestions);
        
        // Create summary results for practice mode
        const totalScore = evaluatedQuestions.reduce((sum, q) => sum + (q.evaluation?.score || 0), 0);
        const maxScore = evaluatedQuestions.length * 10;
        const percentage = (totalScore / maxScore) * 100;
        
        setQuizResults({
          overall_score: totalScore,
          max_score: maxScore,
          percentage: Math.round(percentage * 10) / 10,
          grade: percentage >= 90 ? 'A' : percentage >= 80 ? 'B' : percentage >= 70 ? 'C' : percentage >= 60 ? 'D' : 'F',
          individual_results: evaluatedQuestions.map(q => q.evaluation!).filter(Boolean),
          overall_feedback: `Practice session completed. You scored ${totalScore}/${maxScore} (${Math.round(percentage)}%).`,
          study_suggestions: ['Review questions you scored low on', 'Practice more questions on challenging topics'],
          strengths: ['Completed all questions'],
          areas_for_improvement: ['Focus on accuracy', 'Provide more detailed answers']
        });
      }

      setCurrentStep('results');
    } catch (error) {
      console.error('Failed to evaluate answers:', error);
      alert('Failed to evaluate answers. Please try again.');
    } finally {
      setEvaluatingAnswers(false);
    }
  };

  const resetQuiz = () => {
    setCurrentStep('setup');
    setQuestions([]);
    setQuizResults(null);
    setCurrentQuestionIndex(0);
    setQuestionTopic('');
    setEvaluationLevel('medium');
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

  if (!pdfInfo && !selectedBook) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-16 w-16 text-primary mx-auto mb-4" />
          <h2 className="text-xl font-bold text-text mb-2">No Book Selected</h2>
          <p className="text-text-secondary mb-4">Please select a book using the floating button to start the quiz.</p>
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
              <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-2 rounded-lg">
                <Brain className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-slate-800">Answer Questions</h1>
                <p className="text-sm text-slate-600">Test your knowledge with AI evaluation</p>
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
              <FileText className="h-5 w-5 text-blue-600" />
              <div>
                <p className="font-medium text-slate-800">{pdfInfo.filename}</p>
                <div className="flex items-center space-x-4 text-sm text-slate-600">
                  <span className="flex items-center space-x-1">
                    <Hash className="h-3 w-3" />
                    <span>{pdfInfo.pages} pages</span>
                  </span>
                  <span className="flex items-center space-x-1">
                    <HardDrive className="h-3 w-3" />
                    <span>{(pdfInfo.file_size / 1024).toFixed(1)} KB</span>
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
                onClick={() => router.push('/notes')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
              >
                <StickyNote className="h-4 w-4" />
                <span>Notes</span>
              </button>
              <button
                onClick={() => router.push('/qa')}
                className="flex items-center space-x-2 text-slate-600 hover:text-slate-800 transition-colors text-sm"
              >
                <MessageSquare className="h-4 w-4" />
                <span>Q&A Mode</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        {currentStep === 'setup' && (
          <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-8">
            <div className="text-center mb-8">
              <div className="bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-500 p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg">
                <Target className="h-8 w-8 text-white" />
              </div>
              <h2 className="text-2xl font-bold text-slate-800 mb-2">Setup Your Quiz</h2>
              <p className="text-slate-600">Configure your learning session</p>
            </div>

            <div className="space-y-6">
              {/* Topic Input */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Specific Topic (Optional)
                </label>
                <input
                  type="text"
                  value={questionTopic}
                  onChange={(e) => setQuestionTopic(e.target.value)}
                  placeholder="e.g., Machine Learning, Chapter 3, Data Structures..."
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-sm text-slate-500 mt-1">
                  Leave empty to generate questions from the entire document
                </p>
              </div>

              {/* Question Count */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Number of Questions
                </label>
                <select
                  value={questionCount}
                  onChange={(e) => setQuestionCount(Number(e.target.value))}
                  className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value={5}>5 Questions</option>
                  <option value={10}>10 Questions</option>
                  <option value={15}>15 Questions</option>
                  <option value={20}>20 Questions</option>
                  <option value={25}>25 Questions</option>
                </select>
              </div>

              {/* Mode Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Learning Mode
                </label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <button
                    onClick={() => setQuestionMode('quiz')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      questionMode === 'quiz'
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <Award className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Quiz Mode</h3>
                    <p className="text-sm text-slate-600">
                      Answer all questions, then get comprehensive evaluation
                    </p>
                  </button>

                  <button
                    onClick={() => setQuestionMode('practice')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      questionMode === 'practice'
                        ? 'border-purple-500 bg-purple-50 text-purple-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <TrendingUp className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Practice Mode</h3>
                    <p className="text-sm text-slate-600">
                      Get immediate feedback after each answer
                    </p>
                  </button>
                </div>
              </div>

              {/* Evaluation Level Selection */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-3">
                  Evaluation Level
                </label>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <button
                    onClick={() => setEvaluationLevel('easy')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      evaluationLevel === 'easy'
                        ? 'border-green-500 bg-green-50 text-green-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <CheckCircle className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Easy</h3>
                    <p className="text-sm text-slate-600">
                      Lenient evaluation, focuses on basic understanding
                    </p>
                  </button>

                  <button
                    onClick={() => setEvaluationLevel('medium')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      evaluationLevel === 'medium'
                        ? 'border-yellow-500 bg-yellow-50 text-yellow-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <Target className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Medium</h3>
                    <p className="text-sm text-slate-600">
                      Balanced evaluation with moderate expectations
                    </p>
                  </button>

                  <button
                    onClick={() => setEvaluationLevel('strict')}
                    className={`p-4 rounded-lg border-2 transition-all ${
                      evaluationLevel === 'strict'
                        ? 'border-red-500 bg-red-50 text-red-700'
                        : 'border-slate-200 hover:border-slate-300'
                    }`}
                  >
                    <AlertCircle className="h-6 w-6 mx-auto mb-2" />
                    <h3 className="font-medium mb-1">Strict</h3>
                    <p className="text-sm text-slate-600">
                      Rigorous evaluation requiring detailed answers
                    </p>
                  </button>
                </div>
              </div>

              {/* Generate Button */}
              <div className="text-center pt-4">
                <button
                  onClick={generateQuestions}
                  disabled={generatingQuestions}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-8 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {generatingQuestions ? (
                    <>
                      <Clock className="h-5 w-5 inline mr-2 animate-spin" />
                      Generating Questions...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 inline mr-2" />
                      Generate {questionCount} Questions
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {currentStep === 'answering' && (
          <div className="space-y-6">
            {/* Progress Bar */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-slate-800">
                  {questionMode === 'quiz' ? 'Quiz' : 'Practice'} Session
                </h2>
                <div className="text-sm text-slate-600">
                  {questions.filter(q => q.isAnswered).length} / {questions.length} answered
                </div>
              </div>

              <div className="w-full bg-slate-200 rounded-full h-2 mb-4">
                <div
                  className="bg-gradient-to-r from-blue-500 to-purple-500 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(questions.filter(q => q.isAnswered).length / questions.length) * 100}%` }}
                ></div>
              </div>

              <div className="flex items-center justify-between text-sm">
                <span className="text-slate-600">
                  Topic: {questionTopic.trim() || 'General'}
                </span>
                <div className="flex items-center space-x-4">
                  <span className="text-slate-600">
                    Mode: {questionMode === 'quiz' ? 'Quiz' : 'Practice'}
                  </span>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    evaluationLevel === 'easy'
                      ? 'bg-green-100 text-green-700'
                      : evaluationLevel === 'strict'
                      ? 'bg-red-100 text-red-700'
                      : 'bg-yellow-100 text-yellow-700'
                  }`}>
                    {evaluationLevel.charAt(0).toUpperCase() + evaluationLevel.slice(1)} Level
                  </span>
                </div>
              </div>
            </div>

            {/* Questions */}
            <div className="space-y-4">
              {questions.map((question, index) => (
                <div key={question.id} className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6">
                  <div className="flex items-start space-x-4">
                    <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium flex-shrink-0">
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-slate-800 mb-4">
                        {question.question}
                      </h3>

                      <textarea
                        value={question.userAnswer}
                        onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                        placeholder="Type your answer here..."
                        className="w-full px-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                        rows={4}
                      />

                      {question.isAnswered && (
                        <div className="mt-2 flex items-center text-sm text-green-600">
                          <CheckCircle className="h-4 w-4 mr-1" />
                          Answer provided
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Submit Button */}
            <div className="text-center pt-6">
              <button
                onClick={evaluateAnswers}
                disabled={evaluatingAnswers || questions.filter(q => q.isAnswered).length === 0}
                className="bg-gradient-to-r from-green-600 to-blue-600 text-white px-8 py-3 rounded-lg font-medium hover:from-green-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
              >
                {evaluatingAnswers ? (
                  <>
                    <Clock className="h-5 w-5 inline mr-2 animate-spin" />
                    Evaluating Answers...
                  </>
                ) : (
                  <>
                    <Award className="h-5 w-5 inline mr-2" />
                    Submit & Get Results
                  </>
                )}
              </button>

              {questions.filter(q => q.isAnswered).length === 0 && (
                <p className="text-sm text-slate-500 mt-2">
                  Please answer at least one question to submit
                </p>
              )}
            </div>
          </div>
        )}

        {currentStep === 'results' && quizResults && (
          <div className="space-y-6">
            {/* Overall Results */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-8">
              <div className="text-center mb-8">
                <div className={`p-4 rounded-2xl w-16 h-16 mx-auto mb-4 flex items-center justify-center shadow-lg ${
                  quizResults.percentage >= 80
                    ? 'bg-gradient-to-r from-green-500 to-emerald-500'
                    : quizResults.percentage >= 60
                    ? 'bg-gradient-to-r from-yellow-500 to-orange-500'
                    : 'bg-gradient-to-r from-red-500 to-pink-500'
                }`}>
                  <Award className="h-8 w-8 text-white" />
                </div>

                <h2 className="text-3xl font-bold text-slate-800 mb-2">
                  {quizResults.percentage}%
                </h2>
                <p className="text-xl text-slate-600 mb-1">
                  Grade: {quizResults.grade}
                </p>
                <p className="text-slate-500">
                  {quizResults.overall_score} / {quizResults.max_score} points
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="text-center p-4 bg-green-50 rounded-lg">
                  <h3 className="font-medium text-green-800 mb-2">Strengths</h3>
                  <ul className="text-sm text-green-700 space-y-1">
                    {quizResults.strengths.map((strength, index) => (
                      <li key={index}>• {strength}</li>
                    ))}
                  </ul>
                </div>

                <div className="text-center p-4 bg-blue-50 rounded-lg">
                  <h3 className="font-medium text-blue-800 mb-2">Study Suggestions</h3>
                  <ul className="text-sm text-blue-700 space-y-1">
                    {quizResults.study_suggestions.map((suggestion, index) => (
                      <li key={index}>• {suggestion}</li>
                    ))}
                  </ul>
                </div>

                <div className="text-center p-4 bg-orange-50 rounded-lg">
                  <h3 className="font-medium text-orange-800 mb-2">Areas to Improve</h3>
                  <ul className="text-sm text-orange-700 space-y-1">
                    {quizResults.areas_for_improvement.map((area, index) => (
                      <li key={index}>• {area}</li>
                    ))}
                  </ul>
                </div>
              </div>

              <div className="bg-slate-50 rounded-lg p-6 mb-6">
                <h3 className="font-medium text-slate-800 mb-2">Overall Feedback</h3>
                <p className="text-slate-700">{quizResults.overall_feedback}</p>
              </div>
            </div>

            {/* Individual Question Results */}
            <div className="bg-white/80 backdrop-blur-sm rounded-xl shadow-lg border border-white/20 p-6">
              <h3 className="text-xl font-bold text-slate-800 mb-6">Question-by-Question Results</h3>

              <div className="space-y-6">
                {questions.map((question, index) => (
                  <div key={question.id} className="border-b border-slate-200 pb-6 last:border-b-0">
                    <div className="flex items-start space-x-4">
                      <div className="bg-gradient-to-r from-blue-500 to-purple-500 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-medium flex-shrink-0">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h4 className="font-medium text-slate-800 mb-3">
                          {question.question}
                        </h4>

                        <div className="bg-slate-50 rounded-lg p-4 mb-4">
                          <h5 className="text-sm font-medium text-slate-700 mb-2">Your Answer:</h5>
                          <p className="text-slate-600">{question.userAnswer || 'No answer provided'}</p>
                        </div>

                        {question.evaluation && (
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="text-sm font-medium text-slate-700">Score:</span>
                              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                                question.evaluation.score >= 8
                                  ? 'bg-green-100 text-green-800'
                                  : question.evaluation.score >= 6
                                  ? 'bg-yellow-100 text-yellow-800'
                                  : 'bg-red-100 text-red-800'
                              }`}>
                                {question.evaluation.score}/10
                              </span>
                            </div>

                            <div>
                              <h5 className="text-sm font-medium text-slate-700 mb-2">Feedback:</h5>
                              <p className="text-sm text-slate-600">{question.evaluation.feedback}</p>
                            </div>

                            <div>
                              <h5 className="text-sm font-medium text-slate-700 mb-2">Suggestions:</h5>
                              <p className="text-sm text-slate-600">{question.evaluation.suggestions}</p>
                            </div>

                            {question.evaluation.correct_answer_hint && (
                              <div>
                                <h5 className="text-sm font-medium text-slate-700 mb-2">Hint:</h5>
                                <p className="text-sm text-slate-600">{question.evaluation.correct_answer_hint}</p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="text-center space-x-4">
              <button
                onClick={resetQuiz}
                className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Sparkles className="h-5 w-5 inline mr-2" />
                New Quiz
              </button>

              <button
                onClick={() => router.push('/notes')}
                className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <StickyNote className="h-5 w-5 inline mr-2" />
                Notes
              </button>

              <button
                onClick={() => router.push('/qa')}
                className="bg-slate-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-slate-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <MessageSquare className="h-5 w-5 inline mr-2" />
                Q&A Mode
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
