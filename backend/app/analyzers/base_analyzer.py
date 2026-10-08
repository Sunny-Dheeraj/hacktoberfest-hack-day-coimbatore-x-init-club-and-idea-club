"""Base Analyzer interface for ProofPath."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

from app.models.evidence import CodeSignal


class AnalysisResult(BaseModel):
    """Normalized result returned by any code/manifest analyzer."""
    file: str
    language: str
    signals: List[CodeSignal] = Field(default_factory=list)
    error: Optional[str] = None


class BaseAnalyzer(ABC):
    """Abstract Base Class for all language and manifest analyzers."""

    @abstractmethod
    def can_analyze(self, file_path: str) -> bool:
        """Return True if this analyzer handles the given file path."""
        pass

    @abstractmethod
    def analyze(self, file_path: str, content: str, repository: Optional[str] = None) -> AnalysisResult:
        """Parse the content and extract structured code signals."""
        pass
