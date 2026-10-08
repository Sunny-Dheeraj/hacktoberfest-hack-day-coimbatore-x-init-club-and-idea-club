"""API package for ProofPath."""

from app.api.github import router as github_router

__all__ = ["github_router"]
