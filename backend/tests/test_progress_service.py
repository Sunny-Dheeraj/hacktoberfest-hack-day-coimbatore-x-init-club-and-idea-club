"""Tests for ProgressService confidence calculations and next best actions."""

import pytest
from app.services.progress_service import ProgressService, WEIGHT_CODE, WEIGHT_QUIZ, WEIGHT_PRACTICAL


@pytest.fixture
def progress_service():
    return ProgressService()


def test_confidence_formula_weights():
    """Verify ProofPath's 40/30/30 weighting rule."""
    assert WEIGHT_CODE == 0.40
    assert WEIGHT_QUIZ == 0.30
    assert WEIGHT_PRACTICAL == 0.30


def test_update_skill_progress_calculation(progress_service):
    """Verify composite confidence calculation and progression state."""
    # code = 80.0, quiz = 100.0, practical = 100.0
    # confidence = 80 * 0.40 + 100 * 0.30 + 100 * 0.30 = 32 + 30 + 30 = 92.0
    res = progress_service.update_skill_progress(
        username="dev_test",
        skill="Python",
        code_score=80.0,
        quiz_score=100.0,
        practical_score=100.0,
        initial_status="partial",
    )

    assert res.confidence == 92.0
    assert res.status == "proven"


def test_next_best_action_prioritization(progress_service):
    """Verify missing core skill is prioritized as next best action."""
    action = progress_service.get_next_best_action(
        username="newbie",
        role_id="ml_engineer",
        current_skills=[],
    )

    assert action.target_role == "ml_engineer"
    assert action.priority == 1
    assert action.action_type == "quiz"
