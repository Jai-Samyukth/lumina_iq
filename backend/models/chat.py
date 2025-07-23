from pydantic import BaseModel
from typing import List, Optional

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    timestamp: str

class AnswerEvaluationRequest(BaseModel):
    question: str
    user_answer: str
    question_id: Optional[str] = None
    evaluation_level: Optional[str] = "medium"  # easy, medium, strict

class AnswerEvaluationResponse(BaseModel):
    question_id: Optional[str] = None
    score: int  # 0-10
    max_score: int = 10
    feedback: str
    suggestions: str
    correct_answer_hint: Optional[str] = None

class QuizAnswer(BaseModel):
    question_id: str
    question: str
    user_answer: str

class QuizSubmissionRequest(BaseModel):
    answers: List[QuizAnswer]
    topic: Optional[str] = None
    evaluation_level: Optional[str] = "medium"  # easy, medium, strict

class QuizSubmissionResponse(BaseModel):
    overall_score: int
    max_score: int
    percentage: float
    grade: str  # A, B, C, D, F
    individual_results: List[AnswerEvaluationResponse]
    overall_feedback: str
    study_suggestions: List[str]
    strengths: List[str]
    areas_for_improvement: List[str]
