"""Unit and integration tests for EvidenceService and FastAPI endpoints."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.models.evidence import GitHubProfile, GitHubRepository
from app.services.evidence_service import EvidenceService
from app.services.repository_service import CollectedFile


@pytest.fixture
def mock_github_data():
    profile = GitHubProfile(
        login="coder",
        name="Test Coder",
        bio="Fullstack ML developer",
        avatar_url="https://example.com/avatar.png",
        public_repositories=2,
        html_url="https://github.com/coder",
    )
    repos = [
        GitHubRepository(
            name="ml-pipeline",
            full_name="coder/ml-pipeline",
            description="PyTorch Pipeline",
            html_url="https://github.com/coder/ml-pipeline",
            language="Python",
            stars=5,
            forks=1,
            default_branch="main",
        )
    ]
    return profile, repos


@pytest.mark.asyncio
async def test_evidence_service_orchestration(mock_github_data):
    profile, repos = mock_github_data

    mock_gh_service = MagicMock()
    mock_gh_service.get_user_profile = AsyncMock(return_value=profile)
    mock_gh_service.get_user_repositories = AsyncMock(return_value=repos)

    sample_train_py = """import torch
from torch import nn
from torch.utils.data import DataLoader

class Model(nn.Module):
    def __init__(self):
        super().__init__()

def train():
    loader = DataLoader([])
    opt = torch.optim.Adam()
    loss.backward()
    opt.step()
"""
    collected = [
        CollectedFile(
            path="train.py",
            content=sample_train_py,
            size=len(sample_train_py),
            is_dependency=False,
            is_source=True,
            language="py",
        ),
        CollectedFile(
            path="requirements.txt",
            content="torch\npandas\n",
            size=15,
            is_dependency=True,
            is_source=False,
            language="txt",
        ),
    ]

    mock_repo_service = MagicMock()
    mock_repo_service.max_repositories = 5
    mock_repo_service.collect_repository_files = AsyncMock(return_value=collected)

    service = EvidenceService(
        github_service=mock_gh_service,
        repository_service=mock_repo_service,
    )

    response = await service.analyze_user("coder")

    assert response.username == "coder"
    assert response.repositories_analyzed == 1
    assert "PyTorch" in response.proven
    assert "Python" in response.proven

    # Find PyTorch in skills
    pytorch_summary = next(s for s in response.skills if s.skill == "PyTorch")
    assert pytorch_summary.status.value == "proven"
    assert pytorch_summary.strength >= 4
    assert len(pytorch_summary.evidence) >= 1

    # Verify evidence traceability
    ev = pytorch_summary.evidence[0]
    assert ev.repository == "ml-pipeline"
    assert ev.file in {"train.py", "requirements.txt"}
    assert ev.strength >= 2


def test_api_health_endpoint():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Proof Extraction" in data["phase"]


def test_api_analyze_endpoint_mocked(mock_github_data):
    profile, repos = mock_github_data

    with patch("app.api.github.github_service.get_user_profile", new_callable=AsyncMock) as mock_p, \
         patch("app.api.github.github_service.get_user_repositories", new_callable=AsyncMock) as mock_r, \
         patch("app.api.github.evidence_service.repository_service.collect_repository_files", new_callable=AsyncMock) as mock_c:

        mock_p.return_value = profile
        mock_r.return_value = repos
        mock_c.return_value = [
            CollectedFile(
                path="requirements.txt",
                content="torch\nfastapi\n",
                size=20,
                is_dependency=True,
                is_source=False,
            )
        ]

        client = TestClient(app)
        res = client.post("/api/github/analyze", json={"username": "coder"})
        assert res.status_code == 200
        data = res.json()
        assert data["username"] == "coder"
        assert "repositories" in data
        assert "skills" in data
        assert "proven" in data
        assert "partial" in data
        assert "missing" in data
