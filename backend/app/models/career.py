"""Domain models for ProofPath Phase 2 Career Intelligence."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.evidence import EvidenceStatus, EvidenceItem, SkillSummary, GitHubProfile


class RepositorySummary(BaseModel):
    """Summary of an analyzed repository."""
    name: str
    description: Optional[str] = None
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    files_analyzed: int = 0
    skills_detected: List[str] = Field(default_factory=list)


class SkillClassification(str, Enum):
    """How a skill maps to a career role requirement."""
    PROVEN = "proven"
    PARTIAL = "partial"
    MISSING = "missing"


class RoleSkillRequirement(BaseModel):
    """A skill required for a career role with its weight."""
    skill: str
    weight: float = Field(ge=0.0, description="Weight for readiness scoring (core=2.0, supporting=1.0)")
    is_core: bool = Field(default=False, description="Whether this is a core requirement")


class CareerRole(BaseModel):
    """A career role definition loaded from data/roles.json."""
    id: str
    title: str
    description: str
    core_skills: List[RoleSkillRequirement] = Field(default_factory=list)
    supporting_skills: List[RoleSkillRequirement] = Field(default_factory=list)

    @property
    def all_skills(self) -> List[RoleSkillRequirement]:
        """All skills (core + supporting) for this role."""
        return self.core_skills + self.supporting_skills


class SkillAssessment(BaseModel):
    """Assessment of a single skill against a career role requirement."""
    skill: str
    classification: SkillClassification
    is_core: bool
    weight: float
    evidence_strength: int = Field(ge=0, le=5)
    evidence_count: int = 0
    top_evidence: List[EvidenceItem] = Field(default_factory=list, description="Top evidence items for this skill")
    evidence_found: List[str] = Field(default_factory=list, description="Positive evidence signals discovered")
    missing_evidence: List[str] = Field(default_factory=list, description="Evidence needed to advance to higher tier")
    evidence_locations: List[str] = Field(default_factory=list, description="Physical repository file paths")


class ReadinessScore(BaseModel):
    """Deterministic career readiness score for a role."""
    score: float = Field(ge=0.0, le=100.0, description="Weighted readiness percentage 0-100")
    max_possible: float = Field(description="Maximum possible weighted score")
    earned: float = Field(description="Earned weighted score")
    core_score: float = Field(ge=0.0, le=100.0, description="Core skills readiness percentage")
    supporting_score: float = Field(ge=0.0, le=100.0, description="Supporting skills readiness percentage")


class AIInsight(BaseModel):
    """Structured AI-generated insight from Gemma, grounded in evidence."""
    summary: str = Field(description="Overall career readiness summary")
    strengths: List[str] = Field(default_factory=list, description="Key strengths identified from evidence")
    gaps: List[str] = Field(default_factory=list, description="Skill gaps that need attention")
    recommendations: List[str] = Field(default_factory=list, description="Actionable recommendations")
    confidence: float = Field(ge=0.0, le=1.0, default=0.0, description="AI confidence in assessment")
    grounded: bool = Field(default=True, description="Whether the insight is grounded in evidence")
    model_used: Optional[str] = None
    fallback_used: bool = Field(default=False, description="Whether deterministic fallback was used instead of AI")


class RoleAnalysis(BaseModel):
    """Complete analysis of a user's readiness for a specific career role."""
    role: CareerRole
    readiness: ReadinessScore
    skill_assessments: List[SkillAssessment] = Field(default_factory=list)
    proven_skills: List[str] = Field(default_factory=list)
    partial_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    ai_insight: Optional[AIInsight] = None


class CareerAnalysis(BaseModel):
    """Full career analysis result combining Phase 1 evidence with Phase 2 intelligence."""
    username: str
    roles_analyzed: List[RoleAnalysis] = Field(default_factory=list)
    overall_strengths: List[str] = Field(default_factory=list)
    primary_role: Optional[str] = Field(None, description="Best-matching role ID")
    analysis_metadata: Dict[str, Any] = Field(default_factory=dict)
    profile: Optional[GitHubProfile] = None
    repositories: List[RepositorySummary] = Field(default_factory=list)
    repositories_analyzed: int = 0
    total_public_repos: int = 0
    coverage_summary: str = ""
