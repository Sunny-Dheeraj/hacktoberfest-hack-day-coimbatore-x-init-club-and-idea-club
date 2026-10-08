"""Tests for ProofPath Adaptive Assessment Engine and 100+ Question Bank."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.adaptive_assessment_service import AdaptiveAssessmentService
from app.models.question import QuestionDifficulty, AssessmentMode


@pytest.fixture
def assessment_service():
    return AdaptiveAssessmentService()


@pytest.fixture
def client():
    return TestClient(app)


def test_question_bank_counts_and_validation(assessment_service):
    """Verify that every skill in taxonomy has >= 100 validated questions in the bank."""
    assert len(assessment_service.questions_by_skill) >= 24

    skills = assessment_service.get_available_skills()
    assert len(skills) >= 24
    assert "Mathematics" in skills
    assert "Statistics" in skills
    assert "Python" in skills
    assert "PyTorch" in skills

    for skill in skills:
        summary = assessment_service.get_skill_bank_summary(skill)
        assert summary["total_questions"] >= 100, f"Skill {skill} has only {summary['total_questions']} questions"

        # Verify difficulties coverage
        counts = summary["by_difficulty"]
        for diff in ["beginner", "intermediate", "advanced", "expert"]:
            assert counts.get(diff, 0) > 0, f"Skill {skill} missing {diff} questions"


def test_question_model_integrity(assessment_service):
    """Verify each question has unique options, non-empty explanation, and valid correct answer."""
    for skill, questions in assessment_service.questions_by_skill.items():
        for q in questions:
            assert len(q.options) >= 2, f"Insufficient options in {q.id}"
            assert len(q.options) == len(set(q.options)), f"Duplicate options in {q.id}"
            assert q.correct_answer in q.options, f"Correct answer not in options in {q.id}"
            assert len(q.explanation.strip()) > 0, f"Empty explanation in {q.id}"


def test_adaptive_session_start(assessment_service):
    """Verify starting an adaptive session initializes at Intermediate difficulty."""
    session, first_q = assessment_service.start_session(
        username="octocat", skill="Python", mode=AssessmentMode.QUICK
    )
    assert session.session_id is not None
    assert session.target_count == 20
    assert session.current_difficulty == QuestionDifficulty.INTERMEDIATE
    assert first_q is not None
    assert first_q.difficulty == QuestionDifficulty.INTERMEDIATE
    assert first_q.skill == "Python"


def test_adaptive_progression_streak_up(assessment_service):
    """Verify 2 consecutive correct answers elevate difficulty."""
    session, first_q = assessment_service.start_session(
        username="octocat", skill="Python", mode=AssessmentMode.QUICK
    )
    assert session.current_difficulty == QuestionDifficulty.INTERMEDIATE

    # Answer 1 correctly
    (
        is_correct1,
        _,
        _,
        next_diff1,
        _,
        next_q1,
        session1,
    ) = assessment_service.submit_answer(
        session_id=session.session_id,
        question_id=first_q.id,
        selected_answer=first_q.correct_answer,
    )
    assert is_correct1 is True
    assert next_diff1 == QuestionDifficulty.INTERMEDIATE

    # Answer 2 correctly -> streak reaches 2, should step up to ADVANCED
    assert next_q1 is not None
    (
        is_correct2,
        _,
        _,
        next_diff2,
        _,
        next_q2,
        session2,
    ) = assessment_service.submit_answer(
        session_id=session.session_id,
        question_id=next_q1.id,
        selected_answer=next_q1.correct_answer,
    )
    assert is_correct2 is True
    assert next_diff2 == QuestionDifficulty.ADVANCED
    assert session2.current_difficulty == QuestionDifficulty.ADVANCED


def test_adaptive_progression_streak_down(assessment_service):
    """Verify 2 consecutive incorrect answers step down difficulty."""
    session, first_q = assessment_service.start_session(
        username="octocat", skill="Python", mode=AssessmentMode.QUICK
    )
    # Start at ADVANCED
    session.current_difficulty = QuestionDifficulty.ADVANCED

    # Wrong answer 1
    wrong_opt1 = [o for o in first_q.options if o != first_q.correct_answer][0]
    (
        is_correct1,
        _,
        _,
        next_diff1,
        _,
        next_q1,
        session1,
    ) = assessment_service.submit_answer(
        session_id=session.session_id,
        question_id=first_q.id,
        selected_answer=wrong_opt1,
    )
    assert is_correct1 is False

    # Wrong answer 2 -> streak reaches 2, should step down to INTERMEDIATE
    assert next_q1 is not None
    wrong_opt2 = [o for o in next_q1.options if o != next_q1.correct_answer][0]
    (
        is_correct2,
        _,
        _,
        next_diff2,
        _,
        next_q2,
        session2,
    ) = assessment_service.submit_answer(
        session_id=session.session_id,
        question_id=next_q1.id,
        selected_answer=wrong_opt2,
    )
    assert is_correct2 is False
    assert next_diff2 == QuestionDifficulty.INTERMEDIATE
    assert session2.current_difficulty == QuestionDifficulty.INTERMEDIATE


def test_adaptive_session_completion(assessment_service):
    """Verify completing a session produces mastery score and diagnostic report."""
    session, current_q = assessment_service.start_session(
        username="testuser", skill="Docker", mode=AssessmentMode.QUICK
    )

    last_is_completed = False
    for _ in range(session.target_count):
        if not current_q:
            break
        (
            _,
            _,
            _,
            _,
            is_completed,
            current_q,
            session,
        ) = assessment_service.submit_answer(
            session_id=session.session_id,
            question_id=current_q.id,
            selected_answer=current_q.correct_answer,
        )
        last_is_completed = is_completed

    assert last_is_completed is True
    assert session.status == "completed"
    assert session.score >= 80.0
    assert len(session.strong_topics) > 0


def test_adaptive_api_flow(client):
    """Test start, submit answer, and summary API endpoints."""
    # 1. Summary endpoint
    res = client.get("/api/assessment/summary/Python")
    assert res.status_code == 200
    data = res.json()
    assert data["total_questions"] >= 100

    # 2. Start endpoint
    start_payload = {
        "skill": "Python",
        "username": "candidate_test",
        "mode": "quick",
    }
    start_res = client.post("/api/assessment/start", json=start_payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    assert "session_id" in start_data
    assert "first_question" in start_data
    session_id = start_data["session_id"]
    q_id = start_data["first_question"]["question_id"]
    opt = start_data["first_question"]["options"][0]

    # 3. Answer endpoint
    answer_payload = {
        "session_id": session_id,
        "question_id": q_id,
        "selected_answer": opt,
    }
    ans_res = client.post("/api/assessment/answer", json=answer_payload)
    assert ans_res.status_code == 200
    ans_data = ans_res.json()
    assert "is_correct" in ans_data
    assert "explanation" in ans_data
