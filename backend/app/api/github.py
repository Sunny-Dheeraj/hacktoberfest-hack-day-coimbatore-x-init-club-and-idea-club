"""GitHub API routes for ProofPath."""

import logging
from fastapi import APIRouter, HTTPException, status

from app.schemas.evidence import AnalyzeRequest, AnalyzeResponse, ProfileResponse
from app.services.github_service import (
    GitHubService,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)
from app.services.evidence_service import EvidenceService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/github", tags=["GitHub"])

# Service singletons
github_service = GitHubService()
evidence_service = EvidenceService(github_service=github_service)


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
    summary="Analyze user GitHub repositories for deterministic skill evidence",
)
async def analyze_github_user(request: AnalyzeRequest):
    """
    Trigger full deterministic proof extraction pipeline for a public GitHub user.
    Evaluates source code and dependencies to produce verified skill evidence.
    """
    try:
        result = await evidence_service.analyze_user(
            username=request.username, max_repos=request.max_repos
        )
        return result
    except GitHubUserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except GitHubRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except GitHubAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error analyzing user {request.username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}",
        )


@router.get(
    "/profile/{username}",
    response_model=ProfileResponse,
    summary="Retrieve public profile and repository metadata",
)
async def get_github_profile(username: str):
    """
    Fetch profile metadata and public repositories for a GitHub user.
    """
    try:
        profile = await github_service.get_user_profile(username)
        repositories = await github_service.get_user_repositories(username)
        return ProfileResponse(profile=profile, repositories=repositories)
    except GitHubUserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except GitHubRateLimitError as e:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(e),
        )
    except GitHubAPIError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
    except Exception as e:
        logger.exception(f"Unexpected error fetching profile for {username}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch profile: {str(e)}",
        )
