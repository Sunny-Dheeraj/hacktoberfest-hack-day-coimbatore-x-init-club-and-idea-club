"""API schemas for ProofPath Phase 3 endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.progress import (
    LearningResource,
    KnowledgeQuestion,
    CodeReasoningQuestion,
    CodeChallenge,
    ChallengeCriterionResult,
    PracticalTask,
    SkillConfidence,
    NextBestAction,
    EvaluationStatus,
    VerificationStatus,
)


class FullSkillAssessment(BaseModel):
    """Unified 3-dimension assessment for a skill."""
    skill: str
    knowledge_questions: List[KnowledgeQuestion] = Field(default_factory=list)
    code_reasoning_questions: List[CodeReasoningQuestion] = Field(default_factory=list)
    code_challenge: Optional[CodeChallenge] = None


class QuizSubmissionRequest(BaseModel):
    """Payload for submitting knowledge & code reasoning answers."""
    username: str = Field(..., min_length=1)
    skill: str
    answers: Dict[str, int] = Field(..., description="Map of question_id to selected_option_index")


class QuizQuestionResult(BaseModel):
    question_id: str
    selected_index: int
    correct_index: int
    is_correct: bool
    explanation: str


class QuizResultResponse(BaseModel):
    """Deterministic grading result for quiz."""
    username: str
    skill: str
    score: float
    total_questions: int
    correct_answers: int
    question_results: List[QuizQuestionResult]
    updated_confidence: float
    feedback: str


class CodeChallengeSubmissionRequest(BaseModel):
    """Payload for submitting Monaco Editor code implementation."""
    username: str = Field(..., min_length=1)
    challenge_id: str
    skill: str
    language: str
    code: str = Field(..., min_length=1, description="Source code written in editor")


class CodeChallengeResultResponse(BaseModel):
    """Deterministic static evaluation of code implementation."""
    challenge_id: str
    skill: str
    language: str
    status: EvaluationStatus
    score: float
    criteria: List[ChallengeCriterionResult]
    feedback: str
    updated_confidence: float


class TaskVerificationRequest(BaseModel):
    """Payload for submitting practical mission repository for static verification."""
    username: str = Field(..., min_length=1)
    task_id: str
    skill: str
    repo_url: str = Field(..., description="GitHub repository URL or owner/repo format")
    branch: Optional[str] = Field("main", description="Target git branch")


class TaskCriterionResult(BaseModel):
    name: str
    description: str
    passed: bool
    details: Optional[str] = None


class TaskVerificationResponse(BaseModel):
    """Static verification outcome for GitHub mission."""
    username: str
    task_id: str
    skill: str
    repo_url: str
    status: VerificationStatus
    score: float
    criteria: List[TaskCriterionResult]
    signals_detected: List[str] = Field(default_factory=list)
    files_checked: List[str] = Field(default_factory=list)
    updated_confidence: float
    feedback: str


class LearningPathResponse(BaseModel):
    """Ordered learning path for target career role."""
    role_id: str
    role_title: str
    readiness_score: float
    ordered_skills: List[Dict[str, Any]]
    total_estimated_time: str


class UserProgressResponse(BaseModel):
    """Unified user progress overview."""
    username: str
    target_role: Optional[str] = None
    overall_confidence: float
    skills: List[SkillConfidence]
    next_best_action: Optional[NextBestAction] = None
