"""API tests for ProofPath Phase 2 Career Analysis endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.evidence import AnalyzeResponse
from app.models.evidence import GitHubProfile, GitHubRepository, SkillSummary, EvidenceStatus, EvidenceItem, EvidenceType

client = TestClient(app)


def test_list_roles_endpoint():
    """Verify GET /api/analysis/roles returns available career roles."""
    response = client.get("/api/analysis/roles")
    assert response.status_code == 200
    data = response.json()
    assert "roles" in data
    assert data["total"] >= 3
    role_ids = [r["id"] for r in data["roles"]]
    assert "ml_engineer" in role_ids
    assert "full_stack_developer" in role_ids


def test_get_role_details_endpoint():
    """Verify GET /api/analysis/roles/{role_id} returns single role specification."""
    response = client.get("/api/analysis/roles/ml_engineer")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "ml_engineer"
    assert "core_skills" in data
    assert "supporting_skills" in data


def test_get_nonexistent_role_returns_404():
    """Verify GET /api/analysis/roles/invalid_id returns 404."""
    response = client.get("/api/analysis/roles/unknown_role_xyz")
    assert response.status_code == 404


def test_career_analysis_endpoint_with_mocked_pipeline():
    """Verify POST /api/analysis/career end-to-end with mocked Phase 1 evidence."""
    mock_analyze_response = AnalyzeResponse(
        username="octocat",
        profile=GitHubProfile(login="octocat", html_url="https://github.com/octocat"),
        repositories_analyzed=1,
        repositories=[
            GitHubRepository(
                name="ml-pipeline",
                full_name="octocat/ml-pipeline",
                html_url="https://github.com/octocat/ml-pipeline",
            )
        ],
        skills=[
            SkillSummary(
                skill="Python",
                category="Programming Languages",
                status=EvidenceStatus.PROVEN,
                strength=4,
                evidence=[
                    EvidenceItem(
                        skill="Python",
                        status=EvidenceStatus.PROVEN,
                        repository="ml-pipeline",
                        file="train.py",
                        evidence_type=EvidenceType.APPLIED,
                        strength=4,
                        signals=["torch.nn.Module"],
                        explanation="Applied training script",
                    )
                ],
            ),
            SkillSummary(
                skill="PyTorch",
                category="Machine Learning",
                status=EvidenceStatus.PROVEN,
                strength=4,
                evidence=[],
            ),
            SkillSummary(
                skill="Machine Learning",
                category="Data Science",
                status=EvidenceStatus.PROVEN,
                strength=4,
                evidence=[],
            ),
        ],
        proven=["Python", "PyTorch", "Machine Learning"],
        partial=[],
        missing=[],
        evidence=[],
    )

    with patch(
        "app.api.analysis.evidence_service.analyze_user",
        new_callable=AsyncMock,
        return_value=mock_analyze_response,
    ):
        payload = {
            "username": "octocat",
            "role_ids": ["ml_engineer"],
            "include_ai": True,
        }
        response = client.post("/api/analysis/career", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "octocat"
        assert data["roles_analyzed"] == 1
        assert len(data["analyses"]) == 1

        analysis = data["analyses"][0]
        assert analysis["role"]["id"] == "ml_engineer"
        assert analysis["readiness"]["score"] > 0
        assert "Python" in analysis["proven_skills"]
        # AI insight should be present (either parsed or fallback)
        assert analysis["ai_insight"] is not None
        assert "summary" in analysis["ai_insight"]
        assert len(analysis["ai_insight"]["strengths"]) > 0


def test_career_analysis_without_ai():
    """Verify POST /api/analysis/career when include_ai=False."""
    mock_analyze_response = AnalyzeResponse(
        username="octocat",
        profile=GitHubProfile(login="octocat", html_url="https://github.com/octocat"),
        repositories_analyzed=1,
        repositories=[],
        skills=[],
        proven=[],
        partial=[],
        missing=[],
        evidence=[],
    )

    with patch(
        "app.api.analysis.evidence_service.analyze_user",
        new_callable=AsyncMock,
        return_value=mock_analyze_response,
    ):
        payload = {
            "username": "octocat",
            "role_ids": ["ml_engineer"],
            "include_ai": False,
        }
        response = client.post("/api/analysis/career", json=payload)
        assert response.status_code == 200
        data = response.json()
        # ai_insight should be null when include_ai=False
        assert data["analyses"][0]["ai_insight"] is None
