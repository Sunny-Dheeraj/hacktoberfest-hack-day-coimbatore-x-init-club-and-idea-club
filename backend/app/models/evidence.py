"""Domain models for ProofPath Phase 1 Evidence Extraction."""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class EvidenceStatus(str, Enum):
    PROVEN = "proven"
    PARTIAL = "partial"
    MISSING = "missing"


class EvidenceType(str, Enum):
    NONE = "none"
    MENTIONED = "mentioned"
    DEPENDENCY = "dependency"
    IMPLEMENTATION = "implementation"
    APPLIED = "applied"
    PRODUCTION = "production"


class CodeSignal(BaseModel):
    """Atomic signal identified in source code or project metadata."""
    type: str  # e.g., "import", "class", "function", "call", "decorator", "dependency", "syntax"
    name: str  # e.g., "torch.nn.Module", "FastAPI", "useState"
    technology: str  # e.g., "PyTorch", "FastAPI", "React"
    repository: Optional[str] = None
    file: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    details: Optional[Dict[str, Any]] = None


class EvidenceItem(BaseModel):
    """Deterministic trace linking a skill claim to physical repository code."""
    skill: str
    status: EvidenceStatus
    repository: Optional[str] = None
    file: Optional[str] = None
    line_start: Optional[int] = None
    line_end: Optional[int] = None
    signals: List[str] = Field(default_factory=list)
    evidence_type: EvidenceType
    strength: int = Field(ge=0, le=5)
    explanation: str
    snippet: Optional[str] = None


class SkillSummary(BaseModel):
    """Aggregated evaluation for a single skill in the taxonomy."""
    skill: str
    category: str
    status: EvidenceStatus
    strength: int = Field(ge=0, le=5)
    evidence: List[EvidenceItem] = Field(default_factory=list)


class GitHubProfile(BaseModel):
    """User profile data retrieved from GitHub REST API."""
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    public_repositories: int = 0
    html_url: str


class GitHubRepository(BaseModel):
    """Repository metadata retrieved from GitHub REST API."""
    name: str
    full_name: str
    description: Optional[str] = None
    html_url: str
    language: Optional[str] = None
    stars: int = 0
    forks: int = 0
    default_branch: str = "main"
    visibility: str = "public"
    updated_at: Optional[str] = None
    files_analyzed: int = 0
