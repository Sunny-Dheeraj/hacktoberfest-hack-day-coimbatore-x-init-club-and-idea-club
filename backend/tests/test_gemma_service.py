"""Tests for Google Cloud Gemma 4 Service and AI Fallback Mechanism."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock

from app.ai.gemma_service import GemmaService
from app.models.career import CareerRole, RoleSkillRequirement, ReadinessScore, SkillAssessment, SkillClassification
from app.models.evidence import EvidenceItem, EvidenceStatus, EvidenceType


@pytest.fixture
def mock_role():
    return CareerRole(
        id="ml_engineer",
        title="Machine Learning Engineer",
        description="Builds ML pipelines",
        core_skills=[RoleSkillRequirement(skill="Python", weight=2.0, is_core=True)],
        supporting_skills=[RoleSkillRequirement(skill="Docker", weight=1.0, is_core=False)],
    )


@pytest.fixture
def mock_readiness():
    return ReadinessScore(
        score=80.0,
        max_possible=15.0,
        earned=12.0,
        core_score=80.0,
        supporting_score=80.0,
    )


@pytest.fixture
def mock_assessments():
    return [
        SkillAssessment(
            skill="Python",
            classification=SkillClassification.PROVEN,
            is_core=True,
            weight=2.0,
            evidence_strength=4,
            evidence_count=1,
            top_evidence=[
                EvidenceItem(
                    skill="Python",
                    status=EvidenceStatus.PROVEN,
                    repository="ml-repo",
                    file="train.py",
                    evidence_type=EvidenceType.APPLIED,
                    strength=4,
                    signals=["torch.nn.Module"],
                    explanation="Applied PyTorch training loop",
                )
            ],
        )
    ]


@pytest.mark.asyncio
async def test_unconfigured_service_returns_deterministic_fallback(mock_role, mock_readiness, mock_assessments):
    """When credentials are not configured, GemmaService must immediately return deterministic fallback without failing."""
    service = GemmaService(project_id="", api_key="")
    assert not service.is_configured()

    insight = await service.generate_role_insight(
        username="testuser",
        role=mock_role,
        readiness=mock_readiness,
        assessments=mock_assessments,
        proven_skills=["Python"],
        partial_skills=[],
        missing_skills=["Docker"],
    )

    assert insight is not None
    assert insight.fallback_used is True
    assert insight.grounded is True
    assert "Machine Learning Engineer" in insight.summary
    assert len(insight.strengths) > 0
    assert "Python" in insight.strengths[0]
    assert len(insight.gaps) > 0
    assert len(insight.recommendations) > 0


@pytest.mark.asyncio
async def test_parse_clean_json_response():
    """Verify parser extracts clean JSON correctly."""
    service = GemmaService(api_key="mock_key")
    raw_json = """
    {
        "summary": "Candidate exhibits strong applied competencies in ML with demonstrated PyTorch pipelines.",
        "strengths": ["Verified PyTorch model definitions in ml-repo/train.py"],
        "gaps": ["Missing containerization evidence (Docker)"],
        "recommendations": ["Create Dockerfile for ML training script"],
        "confidence": 0.92
    }
    """
    insight = service._parse_and_validate_response(raw_json)
    assert insight is not None
    assert insight.fallback_used is False
    assert "PyTorch pipelines" in insight.summary
    assert len(insight.strengths) == 1
    assert insight.confidence == 0.92


@pytest.mark.asyncio
async def test_parse_markdown_code_fence_response():
    """Verify parser strips ```json code fences properly."""
    service = GemmaService(api_key="mock_key")
    fenced_response = """
    ```json
    {
        "summary": "Solid full-stack foundational proof.",
        "strengths": ["React components in web-app"],
        "gaps": ["No production CI/CD"],
        "recommendations": ["Add GitHub Actions workflow"],
        "confidence": 0.88
    }
    ```
    """
    insight = service._parse_and_validate_response(fenced_response)
    assert insight is not None
    assert insight.fallback_used is False
    assert "Solid full-stack" in insight.summary


@pytest.mark.asyncio
async def test_api_failure_triggers_fallback(mock_role, mock_readiness, mock_assessments):
    """When API call raises network error or timeout, fallback must be returned safely."""
    service = GemmaService(api_key="mock_key")
    assert service.is_configured()

    with patch.object(service, "_call_gemma_api", side_effect=Exception("API Connection timeout")):
        insight = await service.generate_role_insight(
            username="testuser",
            role=mock_role,
            readiness=mock_readiness,
            assessments=mock_assessments,
            proven_skills=["Python"],
            partial_skills=[],
            missing_skills=["Docker"],
        )

        assert insight is not None
        assert insight.fallback_used is True
        assert insight.grounded is True
        assert len(insight.strengths) > 0
