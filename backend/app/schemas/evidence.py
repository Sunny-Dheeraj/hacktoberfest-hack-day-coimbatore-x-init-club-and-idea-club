"""API schemas for ProofPath Phase 1 endpoints."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.evidence import (
    EvidenceStatus,
    EvidenceType,
    CodeSignal,
    EvidenceItem,
    SkillSummary,
    GitHubProfile,
    GitHubRepository,
)


class AnalyzeRequest(BaseModel):
    """Payload for POST /api/github/analyze."""
    username: str = Field(..., min_length=1, max_length=100, description="Public GitHub username")
    max_repos: Optional[int] = Field(None, ge=1, le=20, description="Override maximum repositories to analyze")


class AnalyzeResponse(BaseModel):
    """Unified Phase 1 Proof Extraction response."""
    username: str
    profile: GitHubProfile
    repositories_analyzed: int
    repositories: List[GitHubRepository] = Field(default_factory=list)
    skills: List[SkillSummary] = Field(default_factory=list)
    proven: List[str] = Field(default_factory=list)
    partial: List[str] = Field(default_factory=list)
    missing: List[str] = Field(default_factory=list)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class ProfileResponse(BaseModel):
    """Response schema for GET /api/github/profile/{username}."""
    profile: GitHubProfile
    repositories: List[GitHubRepository] = Field(default_factory=list)
