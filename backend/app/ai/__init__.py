"""AI integration package for ProofPath Phase 2."""

from app.ai.gemma_service import GemmaService
from app.ai.prompt_builder import build_role_assessment_prompt

__all__ = [
    "GemmaService",
    "build_role_assessment_prompt",
]
