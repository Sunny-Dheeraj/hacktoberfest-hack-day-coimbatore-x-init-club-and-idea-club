"""API schemas for ProofPath Question Bank and Adaptive Assessments."""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.question import (
    QuestionDifficulty,
    QuestionType,
    AssessmentMode,
    AssessmentQuestion,
    AdaptiveAssessmentSession,
)


class StartAdaptiveAssessmentRequest(BaseModel):
    """Payload to start or configure an adaptive assessment."""
    username: str = Field(..., min_length=1, description="GitHub username")
    skill: str = Field(..., min_length=1, description="Skill to assess")
    mode: AssessmentMode = Field(default=AssessmentMode.QUICK, description="Assessment length/mode")
    role_id: Optional[str] = Field(None, description="Optional target role for contextual weighting")


class AdaptiveQuestionOut(BaseModel):
    """Clean question presentation without exposing the answer."""
    session_id: str
    question_id: str
    skill: str
    topic: str
    difficulty: QuestionDifficulty
    question_type: QuestionType
    question_text: str
    code_snippet: Optional[str] = None
    options: List[str]
    question_number: int
    total_questions: int


class SubmitAdaptiveAnswerRequest(BaseModel):
    """Payload when answering an adaptive question."""
    session_id: str
    question_id: str
    selected_answer: str
    time_taken_seconds: Optional[int] = None


class AdaptiveAnswerResult(BaseModel):
    """Immediate feedback on the answered question."""
    is_correct: bool
    correct_answer: str
    explanation: str
    next_difficulty: QuestionDifficulty
    streak: int
    session_completed: bool
    current_score: float
    next_question: Optional[AdaptiveQuestionOut] = None
    session_summary: Optional[AdaptiveAssessmentSession] = None


class QuestionBankSummary(BaseModel):
    """Summary of available questions per skill and difficulty."""
    skill: str
    total_questions: int
    by_difficulty: dict
    by_type: dict
    topics: List[str]
