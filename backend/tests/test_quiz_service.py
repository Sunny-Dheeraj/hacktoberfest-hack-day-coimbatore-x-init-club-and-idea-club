"""Tests for QuizService and 3-dimension assessment engine."""

import pytest
from app.services.quiz_service import QuizService
from app.schemas.progress import QuizSubmissionRequest, CodeChallengeSubmissionRequest
from app.models.progress import EvaluationStatus


@pytest.fixture
def quiz_service():
    return QuizService()


def test_get_skill_assessment_cataloged(quiz_service):
    """Verify loading 3-dimension assessment for cataloged skill."""
    assessment = quiz_service.get_skill_assessment("Python")
    assert assessment.skill == "Python"
    assert len(assessment.knowledge_questions) >= 1
    assert len(assessment.code_reasoning_questions) >= 1
    assert assessment.code_challenge is not None
    assert assessment.code_challenge.language == "python"


def test_get_skill_assessment_fallback(quiz_service):
    """Verify fallback assessment generated for uncataloged skill."""
    assessment = quiz_service.get_skill_assessment("Kubernetes")
    assert assessment.skill == "Kubernetes"
    assert len(assessment.knowledge_questions) >= 1
    assert assessment.code_challenge is not None


def test_grade_quiz_all_correct(quiz_service):
    """Verify deterministic grading for 100% correct answers."""
    assessment = quiz_service.get_skill_assessment("Python")
    answers = {}
    for q in assessment.knowledge_questions:
        answers[q.id] = q.correct_index
    for q in assessment.code_reasoning_questions:
        answers[q.id] = q.correct_index

    sub = QuizSubmissionRequest(
        username="alice",
        skill="Python",
        answers=answers,
    )
    result = quiz_service.grade_quiz(sub)

    assert result.score == 100.0
    assert result.correct_answers == len(answers)
    assert result.total_questions == len(answers)


def test_grade_quiz_partial_correct(quiz_service):
    """Verify deterministic grading with mixed answers."""
    assessment = quiz_service.get_skill_assessment("Python")
    answers = {}
    for i, q in enumerate(assessment.knowledge_questions + assessment.code_reasoning_questions):
        answers[q.id] = q.correct_index if i == 0 else 99  # Only first correct

    sub = QuizSubmissionRequest(
        username="bob",
        skill="Python",
        answers=answers,
    )
    result = quiz_service.grade_quiz(sub)

    assert result.correct_answers == 1
    assert result.score < 100.0


def test_evaluate_code_challenge_via_service(quiz_service):
    """Verify code challenge submission integration in QuizService."""
    sub = CodeChallengeSubmissionRequest(
        username="alice",
        challenge_id="py-c-is-even",
        skill="Python",
        language="python",
        code="def is_even(n):\n    return n % 2 == 0\n",
    )
    result = quiz_service.evaluate_code_challenge(sub)

    assert result.status == EvaluationStatus.PASSED
    assert result.score == 100.0
