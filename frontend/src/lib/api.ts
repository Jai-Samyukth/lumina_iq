import axios from 'axios';
import { authService } from './auth';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE_URL,
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = authService.getToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export interface ChatMessage {
  message: string;
}

export interface ChatResponse {
  response: string;
  timestamp: string;
}

export interface ChatHistoryItem {
  user: string;
  assistant: string;
  timestamp: string;
}

export interface AnswerEvaluationRequest {
  question: string;
  user_answer: string;
  question_id?: string;
  evaluation_level?: 'easy' | 'medium' | 'strict';
}

export interface AnswerEvaluationResponse {
  question_id?: string;
  score: number;
  max_score: number;
  feedback: string;
  suggestions: string;
  correct_answer_hint?: string;
}

export interface QuizAnswer {
  question_id: string;
  question: string;
  user_answer: string;
}

export interface QuizSubmissionRequest {
  answers: QuizAnswer[];
  topic?: string;
  evaluation_level?: 'easy' | 'medium' | 'strict';
}

export interface QuizSubmissionResponse {
  overall_score: number;
  max_score: number;
  percentage: number;
  grade: string;
  individual_results: AnswerEvaluationResponse[];
  overall_feedback: string;
  study_suggestions: string[];
  strengths: string[];
  areas_for_improvement: string[];
}

export interface PDFMetadata {
  title: string;
  author: string;
  subject: string;
  creator: string;
  producer: string;
  creation_date: string;
  modification_date: string;
  pages: number;
  file_size: number;
}

export interface PDFInfo {
  filename: string;
  title: string;
  author: string;
  pages: number;
  file_size: number;
  file_path: string;
}

export interface PDFSessionInfo {
  filename: string;
  selected_at?: string;
  uploaded_at?: string;
  text_length: number;
  metadata: PDFMetadata;
}

export const pdfApi = {
  async listPDFs(): Promise<{ pdfs: PDFInfo[] }> {
    const response = await api.get('/pdf/list');
    return response.data;
  },

  async selectPDF(filename: string) {
    const response = await api.post('/pdf/select', { filename });
    return response.data;
  },

  async uploadPDF(file: File) {
    const formData = new FormData();
    formData.append('file', file);

    const response = await api.post('/pdf/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getPDFInfo(): Promise<PDFSessionInfo> {
    const response = await api.get('/pdf/info');
    return response.data;
  },

  async getPDFMetadata(): Promise<PDFMetadata> {
    const response = await api.get('/pdf/metadata');
    return response.data;
  },
};

export const chatApi = {
  async sendMessage(message: string): Promise<ChatResponse> {
    const response = await api.post('/chat', { message });
    return response.data;
  },

  async getChatHistory(): Promise<{ history: ChatHistoryItem[] }> {
    const response = await api.get('/chat/history');
    return response.data;
  },

  async generateQuestions(topic?: string, count?: number): Promise<ChatResponse> {
    const response = await api.post('/chat/generate-questions', { topic, count });
    return response.data;
  },

  async evaluateAnswer(request: AnswerEvaluationRequest): Promise<AnswerEvaluationResponse> {
    const response = await api.post('/chat/evaluate-answer', request);
    return response.data;
  },

  async evaluateQuiz(request: QuizSubmissionRequest): Promise<QuizSubmissionResponse> {
    const response = await api.post('/chat/evaluate-quiz', request);
    return response.data;
  },
};

export default api;
