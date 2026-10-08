"""Career Analysis API routes for ProofPath Phase 2."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from app.schemas.career import (
    CareerAnalysisRequest,
    CareerAnalysisResponse,
    RolesListResponse,
    RoleSummaryResponse,
)
from app.models.career import CareerRole, RoleAnalysis
from app.services.github_service import (
    GitHubService,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)
from app.services.evidence_service import EvidenceService
from app.services.career_service import CareerService
from app.ai.gemma_service import GemmaService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analysis", tags=["Career Intelligence"])

# Service singletons
github_service = GitHubService()
evidence_service = EvidenceService(github_service=github_service)
career_service = CareerService()
gemma_service = GemmaService()


@router.get(
    "/roles",
    response_model=RolesListResponse,
    summary="List all available career roles and requirement summaries",
)
async def list_career_roles():
    """Returns all supported career roles with core and supporting skill breakdowns."""
    roles = career_service.get_all_roles()
    summaries = [
        RoleSummaryResponse(
            id=r.id,
            title=r.title,
            description=r.description,
            core_skill_count=len(r.core_skills),
            supporting_skill_count=len(r.supporting_skills),
        )
        for r in roles
    ]
    return RolesListResponse(roles=summaries, total=len(summaries))


@router.get(
    "/roles/{role_id}",
    response_model=CareerRole,
    summary="Get full details for a specific career role",
)
async def get_role_details(role_id: str):
    """Retrieve complete role definition including core and supporting skill weights."""
    role = career_service.get_role_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Career role with id '{role_id}' not found.",
        )
    return role


@router.post(
    "/career",
    response_model=CareerAnalysisResponse,
    summary="Analyze candidate career readiness using code evidence + Gemma 4",
)
async def analyze_career_readiness(request: CareerAnalysisRequest):
    """
    Executes the complete ProofPath pipeline:
    1. Deterministic Proof Extraction (Phase 1)
    2. Deterministic Career Role Matching & Readiness Scoring (Phase 2)
    3. Evidence-Grounded AI Career Interpretation (Gemma 4 with automatic fallback)
    """
    logger.info(f"Received career analysis request for user: {request.username}")

    # Step 1: Execute Phase 1 Evidence Extraction
    try:
        phase1_result = await evidence_service.analyze_user(
            username=request.username, max_repos=request.max_repos
        )
    except GitHubUserNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except GitHubRateLimitError as e:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=str(e))
    except GitHubAPIError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except Exception as e:
        logger.exception(f"Error during Phase 1 evidence extraction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Evidence extraction failed: {str(e)}",
        )

    # Step 2: Execute Deterministic Career Role Matching
    career_result = career_service.analyze_career(
        username=request.username,
        skill_summaries=phase1_result.skills,
        role_ids=request.role_ids,
    )

    # Step 3: AI Interpretation via Gemma 4 (or deterministic fallback)
    if request.include_ai:
        for role_analysis in career_result.roles_analyzed:
            try:
                ai_insight = await gemma_service.generate_role_insight(
                    username=request.username,
                    role=role_analysis.role,
                    readiness=role_analysis.readiness,
                    assessments=role_analysis.skill_assessments,
                    proven_skills=role_analysis.proven_skills,
                    partial_skills=role_analysis.partial_skills,
                    missing_skills=role_analysis.missing_skills,
                )
                role_analysis.ai_insight = ai_insight
            except Exception as e:
                logger.warning(f"Error generating AI insight for role {role_analysis.role.id}: {e}")
                # Generate fallback directly
                fallback = gemma_service._generate_deterministic_fallback(
                    role=role_analysis.role,
                    readiness=role_analysis.readiness,
                    assessments=role_analysis.skill_assessments,
                    proven_skills=role_analysis.proven_skills,
                    partial_skills=role_analysis.partial_skills,
                    missing_skills=role_analysis.missing_skills,
                )
                role_analysis.ai_insight = fallback

    # Step 4: Assemble response
    return CareerAnalysisResponse(
        username=request.username,
        roles_analyzed=len(career_result.roles_analyzed),
        primary_role=career_result.primary_role,
        analyses=career_result.roles_analyzed,
        overall_strengths=career_result.overall_strengths,
        phase1_evidence_count=len(phase1_result.evidence),
        ai_available=gemma_service.is_configured(),
        metadata=career_result.analysis_metadata,
    )
