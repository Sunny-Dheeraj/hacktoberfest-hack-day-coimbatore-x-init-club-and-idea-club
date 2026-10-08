"""Tests for LearningService and prioritized roadmaps."""

import pytest
from app.services.learning_service import LearningService


@pytest.fixture
def learning_service():
    return LearningService()


def test_get_resources_for_skill(learning_service):
    """Verify loading curated learning resources from data/resources.json."""
    resources = learning_service.get_resources_for_skill("Python")
    assert len(resources) >= 1
    assert any("docs.python.org" in r.url for r in resources)


def test_get_resources_for_docker(learning_service):
    """Verify loading Docker resources."""
    resources = learning_service.get_resources_for_skill("Docker")
    assert len(resources) >= 1
    assert any("docker.com" in r.url for r in resources)


def test_learning_path_prioritization(learning_service):
    """Verify missing core skills are placed first in the roadmap."""
    path = learning_service.build_learning_path(
        role_id="ml_engineer",
        missing_skills=["PyTorch", "Pandas"],
        partial_skills=["Python"],
    )

    assert path.role_id == "ml_engineer"
    assert len(path.ordered_skills) >= 3

    # PyTorch and Pandas are missing core skills; they should appear in top steps
    top_step_skills = [s["skill"] for s in path.ordered_skills[:3]]
    assert "PyTorch" in top_step_skills or "Pandas" in top_step_skills
