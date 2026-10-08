"""Domain models for ProofPath Phase 3 Proof & Progress."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChallengeDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class EvaluationStatus(str, Enum):
    PASSED = "passed"
    PARTIALLY_PASSED = "partially_passed"
    FAILED = "failed"


class VerificationStatus(str, Enum):
    VERIFIED = "verified"
    PARTIALLY_VERIFIED = "partially_verified"
    NOT_VERIFIED = "not_verified"


class LearningResourceType(str, Enum):
    DOCUMENTATION = "documentation"
    TUTORIAL = "tutorial"
    COURSE = "course"
    GUIDE = "guide"
    EXAMPLE = "example"


class LearningResource(BaseModel):
    """Curated learning resource for bridging skill gaps."""
    id: str
    skill: str
    title: str
    description: str
    type: LearningResourceType
    url: str
    difficulty: ChallengeDifficulty
    estimated_time: str


class KnowledgeQuestion(BaseModel):
    """Conceptual multiple-choice question testing theoretical understanding."""
    id: str
    question: str
    options: List[str]
    correct_index: int = Field(ge=0, le=3)
    explanation: str


class CodeReasoningQuestion(BaseModel):
    """Snippet-based question testing code comprehension and reasoning."""
    id: str
    language: str
    snippet: str
    question: str
    options: List[str]
    correct_index: int = Field(ge=0, le=3)
    explanation: str


class ChallengeCriterion(BaseModel):
    name: str
    description: str


class ChallengeCriterionResult(BaseModel):
    name: str
    description: str
    passed: bool
    feedback: Optional[str] = None


class CodeChallenge(BaseModel):
    """Monaco Editor implementation challenge evaluated deterministically."""
    id: str
    skill: str
    language: str
    title: str
    difficulty: ChallengeDifficulty
    description: str
    starter_code: str
    expected_behavior: List[str] = Field(default_factory=list)
    criteria: List[ChallengeCriterion] = Field(default_factory=list)


class PracticalTask(BaseModel):
    """Measurable real-world mission verified via GitHub repository."""
    id: str
    skill: str
    title: str
    difficulty: ChallengeDifficulty
    description: str
    requirements: List[str] = Field(default_factory=list)
    expected_artifacts: List[str] = Field(default_factory=list)
    verification_rules: Dict[str, Any] = Field(default_factory=dict)


class SkillConfidence(BaseModel):
    """
    Composite skill confidence based on ProofPath's three pillars:
    Code Evidence (40%) + Knowledge Quiz (30%) + Practical Ability (30%)
    """
    skill: str
    code_score: float = Field(ge=0.0, le=100.0, description="Score from Phase 1 code evidence (strength/5 * 100)")
    quiz_score: float = Field(ge=0.0, le=100.0, description="Score from knowledge and code reasoning quiz")
    practical_score: float = Field(ge=0.0, le=100.0, description="Score from code challenge or GitHub mission")
    confidence: float = Field(ge=0.0, le=100.0, description="Weighted composite score")
    status: str = Field(description="missing, learning, partial, verified, proven")


class NextBestAction(BaseModel):
    """Prioritized next recommended action to bridge gaps."""
    skill: str
    action_type: str  # "learn", "quiz", "code_challenge", "practical_mission"
    title: str
    reason: str
    priority: int  # 1 (highest) to 5
    target_role: Optional[str] = None
