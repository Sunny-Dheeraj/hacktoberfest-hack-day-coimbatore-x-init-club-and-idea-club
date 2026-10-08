"""API schemas package for ProofPath."""

from app.schemas.evidence import (
    AnalyzeRequest,
    AnalyzeResponse,
    ProfileResponse,
)
from app.schemas.career import (
    CareerAnalysisRequest,
    CareerAnalysisResponse,
    RoleSummaryResponse,
    RolesListResponse,
)
from app.schemas.progress import (
    FullSkillAssessment,
    QuizSubmissionRequest,
    QuizQuestionResult,
    QuizResultResponse,
    CodeChallengeSubmissionRequest,
    CodeChallengeResultResponse,
    TaskVerificationRequest,
    TaskCriterionResult,
    TaskVerificationResponse,
    LearningPathResponse,
    UserProgressResponse,
)

__all__ = [
    "AnalyzeRequest",
    "AnalyzeResponse",
    "ProfileResponse",
    "CareerAnalysisRequest",
    "CareerAnalysisResponse",
    "RoleSummaryResponse",
    "RolesListResponse",
    "FullSkillAssessment",
    "QuizSubmissionRequest",
    "QuizQuestionResult",
    "QuizResultResponse",
    "CodeChallengeSubmissionRequest",
    "CodeChallengeResultResponse",
    "TaskVerificationRequest",
    "TaskCriterionResult",
    "TaskVerificationResponse",
    "LearningPathResponse",
    "UserProgressResponse",
]
