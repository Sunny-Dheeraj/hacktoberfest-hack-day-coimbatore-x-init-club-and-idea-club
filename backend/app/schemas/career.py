"""API schemas for ProofPath Phase 2 Career Analysis endpoints."""

from typing import List, Optional
from pydantic import BaseModel, Field

from app.models.career import (
    CareerRole,
    RoleAnalysis,
    CareerAnalysis,
    AIInsight,
    ReadinessScore,
    SkillAssessment,
)


class CareerAnalysisRequest(BaseModel):
    """Payload for POST /api/analysis/career."""
    username: str = Field(..., min_length=1, max_length=100, description="Public GitHub username")
    role_ids: Optional[List[str]] = Field(
        None,
        description="Specific role IDs to analyze. If None, all roles are analyzed."
    )
    max_repos: Optional[int] = Field(
        None, ge=1, le=20,
        description="Override maximum repositories to analyze"
    )
    include_ai: bool = Field(
        default=True,
        description="Whether to include Gemma AI interpretation"
    )


class RoleSummaryResponse(BaseModel):
    """Lightweight role info for listing."""
    id: str
    title: str
    description: str
    core_skill_count: int
    supporting_skill_count: int


class CareerAnalysisResponse(BaseModel):
    """Response for POST /api/analysis/career."""
    username: str
    roles_analyzed: int
    primary_role: Optional[str] = None
    analyses: List[RoleAnalysis] = Field(default_factory=list)
    overall_strengths: List[str] = Field(default_factory=list)
    phase1_evidence_count: int = 0
    ai_available: bool = False
    metadata: dict = Field(default_factory=dict)


class RolesListResponse(BaseModel):
    """Response for GET /api/analysis/roles."""
    roles: List[RoleSummaryResponse] = Field(default_factory=list)
    total: int = 0
