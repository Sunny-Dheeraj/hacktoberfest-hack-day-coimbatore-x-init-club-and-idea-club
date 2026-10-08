"""Domain models and Pydantic validation for ProofPath Question Bank and Adaptive Assessments."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, model_validator


class QuestionDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"


class QuestionType(str, Enum):
    CONCEPTUAL = "conceptual"
    MCQ = "mcq"
    CODE_READING = "code_reading"
    PREDICT_OUTPUT = "predict_output"
    DEBUGGING = "debugging"
    ERROR_DIAGNOSIS = "error_diagnosis"
    CODE_COMPLETION = "code_completion"
    IMPLEMENTATION = "implementation"
    BEST_PRACTICE = "best_practice"
    SCENARIO = "scenario"
    ARCHITECTURE = "architecture"
    TRADE_OFF = "trade_off"


class AssessmentMode(str, Enum):
    QUICK = "quick"              # ~20 questions
    STANDARD = "standard"        # ~40 questions
    FULL = "full"                # ~75 questions
    COMPREHENSIVE = "comprehensive"  # 100+ questions


class AssessmentQuestion(BaseModel):
    """Structured question with strict validation for quality and consistency."""
    id: str = Field(..., description="Unique question identifier")
    skill: str = Field(..., min_length=1, description="Target technical skill")
    topic: str = Field(..., min_length=1, description="Broad knowledge domain or category")
    subtopic: Optional[str] = Field(None, description="Granular technical topic")
    difficulty: QuestionDifficulty = Field(..., description="Calibrated difficulty tier")
    question_type: QuestionType = Field(..., description="Pedagogical type of question")
    question_text: str = Field(..., min_length=10, description="The complete question statement")
    code_snippet: Optional[str] = Field(None, description="Optional code snippet for reasoning")
    options: List[str] = Field(default_factory=list, description="Selectable answers for choice-based questions")
    correct_answer: str = Field(..., min_length=1, description="The correct answer string")
    explanation: str = Field(..., min_length=10, description="Detailed explanation of the correct answer")
    expected_reasoning: Optional[str] = Field(None, description="Underlying thought process / steps")
    tags: List[str] = Field(default_factory=list, description="Categorization tags")
    estimated_time: str = Field(default="60s", description="Estimated completion time")
    source: str = Field(default="ProofPath Bank", description="Source or generation model")
    version: str = Field(default="1.0", description="Schema version")

    @field_validator("options")
    @classmethod
    def validate_unique_options(cls, v: List[str]) -> List[str]:
        if v:
            stripped = [opt.strip() for opt in v]
            if len(set(stripped)) != len(stripped):
                raise ValueError("Options must be unique; duplicates detected.")
            if any(len(opt) == 0 for opt in stripped):
                raise ValueError("Options cannot contain empty strings.")
        return v

    @model_validator(mode="after")
    def validate_answer_in_options(self) -> "AssessmentQuestion":
        if self.options and len(self.options) > 0:
            if self.correct_answer.strip() not in [o.strip() for o in self.options]:
                raise ValueError(
                    f"Correct answer '{self.correct_answer}' must be present in the provided options: {self.options}"
                )
        return self


class AdaptiveAnswerRecord(BaseModel):
    """Records a single answered question in an adaptive session."""
    question_id: str
    selected_answer: str
    is_correct: bool
    difficulty: QuestionDifficulty
    topic: str
    time_taken_seconds: Optional[int] = None


class AdaptiveAssessmentSession(BaseModel):
    """Tracks state and progression of an adaptive skill assessment."""
    session_id: str
    username: str
    skill: str
    mode: AssessmentMode
    target_count: int
    current_difficulty: QuestionDifficulty = QuestionDifficulty.INTERMEDIATE
    questions_answered: int = 0
    correct_streak: int = 0
    incorrect_streak: int = 0
    records: List[AdaptiveAnswerRecord] = Field(default_factory=list)
    score: float = 0.0
    status: str = "in_progress"  # in_progress, completed
    weak_topics: List[str] = Field(default_factory=list)
    strong_topics: List[str] = Field(default_factory=list)
    estimated_knowledge_level: str = "Intermediate"
    recommended_next_level: str = "Intermediate"
    confidence_score: float = 0.0
