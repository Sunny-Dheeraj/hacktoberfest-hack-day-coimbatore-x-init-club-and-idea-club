"""API integration tests for ProofPath Phase 3 endpoints."""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.models.progress import VerificationStatus

client = TestClient(app)


def test_generate_quiz_endpoint():
    """Verify POST /api/quiz/generate returns 3-dimension assessment."""
    res = client.post("/api/quiz/generate?skill=Python")
    assert res.status_code == 200
    data = res.json()
    assert data["skill"] == "Python"
    assert len(data["knowledge_questions"]) >= 1
    assert len(data["code_reasoning_questions"]) >= 1
    assert data["code_challenge"] is not None


def test_submit_quiz_endpoint():
    """Verify POST /api/quiz/submit returns deterministic grading."""
    res = client.post(
        "/api/quiz/submit",
        json={
            "username": "tester",
            "skill": "Python",
            "answers": {"py-k-1": 1, "py-r-1": 1},
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert "score" in data
    assert "updated_confidence" in data
    assert data["total_questions"] >= 1


def test_submit_code_challenge_endpoint():
    """Verify POST /api/code-challenges/submit runs static evaluation."""
    res = client.post(
        "/api/code-challenges/submit",
        json={
            "username": "tester",
            "challenge_id": "py-c-is-even",
            "skill": "Python",
            "language": "python",
            "code": "def is_even(n):\n    return n % 2 == 0\n",
        },
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "passed"
    assert data["score"] == 100.0


def test_get_learning_resources_endpoint():
    """Verify GET /api/learning/{skill} returns curated resources."""
    res = client.get("/api/learning/Docker")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert data[0]["skill"] == "Docker"


def test_get_learning_path_endpoint():
    """Verify GET /api/learning-path/{role_id} returns roadmap."""
    res = client.get("/api/learning-path/full_stack_developer")
    assert res.status_code == 200
    data = res.json()
    assert data["role_id"] == "full_stack_developer"
    assert len(data["ordered_skills"]) >= 1


def test_get_progress_endpoint():
    """Verify GET /api/progress/{username} returns tracking data."""
    res = client.get("/api/progress/tester")
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == "tester"
    assert "skills" in data
    assert "overall_confidence" in data


def test_get_recommendations_endpoint():
    """Verify GET /api/progress/{username}/recommendations."""
    res = client.get("/api/progress/tester/recommendations?role=ml_engineer")
    assert res.status_code == 200
    data = res.json()
    assert "skill" in data
    assert "action_type" in data
    assert "title" in data
