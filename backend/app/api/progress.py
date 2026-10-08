"""API routes for ProofPath Phase 3 & 4 Proof & Progress and Adaptive Assessments."""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, status, Query

from app.models.progress import (
    LearningResource,
    CodeChallenge,
    PracticalTask,
    NextBestAction,
)
from app.models.question import (
    QuestionDifficulty,
    AssessmentMode,
)
from app.schemas.progress import (
    FullSkillAssessment,
    QuizSubmissionRequest,
    QuizResultResponse,
    CodeChallengeSubmissionRequest,
    CodeChallengeResultResponse,
    TaskVerificationRequest,
    TaskVerificationResponse,
    LearningPathResponse,
    UserProgressResponse,
)
from app.schemas.question import (
    StartAdaptiveAssessmentRequest,
    AdaptiveQuestionOut,
    SubmitAdaptiveAnswerRequest,
    AdaptiveAnswerResult,
    QuestionBankSummary,
)
from app.services.quiz_service import QuizService
from app.services.learning_service import LearningService
from app.services.verification_service import VerificationService
from app.services.progress_service import ProgressService
from app.services.adaptive_assessment_service import AdaptiveAssessmentService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Proof & Progress"])

# Singletons
quiz_service = QuizService()
learning_service = LearningService()
verification_service = VerificationService()
progress_service = ProgressService()
adaptive_service = AdaptiveAssessmentService()


# ---------------------------------------------------------------------------
# Adaptive Assessment Endpoints (100+ Question Bank)
# ---------------------------------------------------------------------------

@router.post(
    "/assessment/start",
    response_model=dict,
    summary="Start an adaptive skill assessment session (Quick/Standard/Full/Comprehensive)",
)
async def start_adaptive_assessment(request: StartAdaptiveAssessmentRequest):
    """Initializes an adaptive testing session spanning Beginner to Expert."""
    session, first_q = adaptive_service.start_session(
        username=request.username,
        skill=request.skill,
        mode=request.mode,
    )
    q_out = None
    if first_q:
        q_out = AdaptiveQuestionOut(
            session_id=session.session_id,
            question_id=first_q.id,
            skill=first_q.skill,
            topic=first_q.topic,
            difficulty=first_q.difficulty,
            question_type=first_q.question_type,
            question_text=first_q.question_text,
            code_snippet=first_q.code_snippet,
            options=first_q.options,
            question_number=1,
            total_questions=session.target_count,
        ).model_dump()

    return {
        "session_id": session.session_id,
        "username": session.username,
        "skill": session.skill,
        "mode": session.mode.value,
        "target_questions": session.target_count,
        "current_difficulty": session.current_difficulty.value,
        "first_question": q_out,
    }


@router.post(
    "/assessment/answer",
    response_model=AdaptiveAnswerResult,
    summary="Submit answer for an adaptive question; adapts difficulty and tracks performance",
)
async def submit_adaptive_answer(request: SubmitAdaptiveAnswerRequest):
    """Submits answer, grades deterministically, adapts difficulty, and tracks strong/weak topics."""
    try:
        (
            is_correct,
            correct_ans,
            explanation,
            next_diff,
            is_completed,
            next_q,
            session,
        ) = adaptive_service.submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            selected_answer=request.selected_answer,
            time_taken_seconds=request.time_taken_seconds,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    next_q_out = None
    if next_q:
        next_q_out = AdaptiveQuestionOut(
            session_id=session.session_id,
            question_id=next_q.id,
            skill=next_q.skill,
            topic=next_q.topic,
            difficulty=next_q.difficulty,
            question_type=next_q.question_type,
            question_text=next_q.question_text,
            code_snippet=next_q.code_snippet,
            options=next_q.options,
            question_number=session.questions_answered + 1,
            total_questions=session.target_count,
        )

    # If completed, sync score to composite progress
    if is_completed:
        progress_service.update_skill_progress(
            username=session.username,
            skill=session.skill,
            quiz_score=session.score,
        )

    return AdaptiveAnswerResult(
        is_correct=is_correct,
        correct_answer=correct_ans,
        explanation=explanation,
        next_difficulty=next_diff,
        streak=session.correct_streak,
        session_completed=is_completed,
        current_score=session.score,
        next_question=next_q_out,
        session_summary=session if is_completed else None,
    )


@router.get(
    "/assessment/summary/{skill}",
    response_model=QuestionBankSummary,
    summary="Get question bank statistics for a skill",
)
async def get_question_bank_summary(skill: str):
    """Provides breakdown of 100+ questions across difficulty tiers and topics."""
    return adaptive_service.get_skill_bank_summary(skill)


# ---------------------------------------------------------------------------
# Quiz & Code Challenge Endpoints (Compatible with GET & POST)
# ---------------------------------------------------------------------------

@router.get(
    "/quiz/generate",
    response_model=FullSkillAssessment,
    summary="Generate 3-dimension assessment (Knowledge, Code Reasoning, Implementation)",
    operation_id="generate_skill_quiz_get",
)
@router.post(
    "/quiz/generate",
    response_model=FullSkillAssessment,
    summary="Generate 3-dimension assessment (Knowledge, Code Reasoning, Implementation)",
    operation_id="generate_skill_quiz_post",
)
async def generate_skill_quiz(skill: str = Query(..., description="Target skill name")):
    """Generates 3-dimension assessment testing conceptual knowledge, snippet reasoning, and coding."""
    assessment = quiz_service.get_skill_assessment(skill)
    return assessment


@router.post(
    "/quiz/submit",
    response_model=QuizResultResponse,
    summary="Deterministically score multiple choice knowledge and code reasoning questions",
)
async def submit_quiz(request: QuizSubmissionRequest):
    """Scores quiz deterministically and updates composite skill confidence."""
    result = quiz_service.grade_quiz(request)

    # Update composite progress
    conf = progress_service.update_skill_progress(
        username=request.username,
        skill=request.skill,
        quiz_score=result.score,
    )
    result.updated_confidence = conf.confidence
    return result


@router.get(
    "/code-challenges/generate",
    response_model=CodeChallenge,
    summary="Retrieve coding challenge for Monaco editor",
    operation_id="generate_code_challenge_get",
)
@router.post(
    "/code-challenges/generate",
    response_model=CodeChallenge,
    summary="Retrieve coding challenge for Monaco editor",
    operation_id="generate_code_challenge_post",
)
async def generate_code_challenge(skill: str = Query(..., description="Target skill")):
    """Retrieves coding implementation challenge with starter code and criteria."""
    assessment = quiz_service.get_skill_assessment(skill)
    if not assessment.code_challenge:
        raise HTTPException(status_code=404, detail=f"No challenge found for {skill}")
    return assessment.code_challenge


@router.post(
    "/code-challenges/submit",
    response_model=CodeChallengeResultResponse,
    summary="Statically evaluate user code implementation in Monaco editor",
)
async def submit_code_challenge(request: CodeChallengeSubmissionRequest):
    """Statically validates user code syntax and AST criteria without arbitrary execution."""
    result = quiz_service.evaluate_code_challenge(request)

    # Update composite progress
    conf = progress_service.update_skill_progress(
        username=request.username,
        skill=request.skill,
        practical_score=result.score,
    )
    result.updated_confidence = conf.confidence
    return result


# ---------------------------------------------------------------------------
# Learning & Roadmap Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/learning/{skill}",
    response_model=List[LearningResource],
    summary="Get curated public learning resources for a skill",
)
async def get_skill_resources(skill: str):
    """Returns verified technical documentation and tutorials for the skill."""
    return learning_service.get_resources_for_skill(skill)


@router.get(
    "/learning-path/{role_id}",
    response_model=LearningPathResponse,
    summary="Build prioritized role roadmap based on missing/partial gaps",
)
async def get_role_learning_path(
    role_id: str,
    missing: Optional[List[str]] = Query(None),
    partial: Optional[List[str]] = Query(None),
):
    """Constructs prioritized sequence of skills to master for target career role."""
    return learning_service.build_learning_path(
        role_id=role_id,
        missing_skills=missing,
        partial_skills=partial,
    )


# ---------------------------------------------------------------------------
# Practical Missions & Verification Endpoints (Compatible with GET & POST)
# ---------------------------------------------------------------------------

@router.get(
    "/tasks/generate",
    response_model=PracticalTask,
    summary="Generate practical mission specifications for a skill",
    operation_id="generate_practical_task_get",
)
@router.post(
    "/tasks/generate",
    response_model=PracticalTask,
    summary="Generate practical mission specifications for a skill",
    operation_id="generate_practical_task_post",
)
async def generate_practical_task(skill: str = Query(..., description="Target skill")):
    """Generates measurable GitHub practical mission with verification criteria."""
    return verification_service.get_mission_for_skill(skill)


@router.post(
    "/tasks/verify",
    response_model=TaskVerificationResponse,
    summary="Statically verify practical mission against a public GitHub repository",
)
async def verify_task_repository(request: TaskVerificationRequest):
    """Inspects GitHub repository tree and code signals to statically verify mission completion."""
    result = await verification_service.verify_task(request)

    # Update composite progress
    conf = progress_service.update_skill_progress(
        username=request.username,
        skill=request.skill,
        practical_score=result.score,
    )
    result.updated_confidence = conf.confidence
    return result


# ---------------------------------------------------------------------------
# User Progress & Next Best Action Endpoints
# ---------------------------------------------------------------------------

@router.get(
    "/progress/{username}",
    response_model=UserProgressResponse,
    summary="Get full user progress across all tracked skills",
)
async def get_progress(username: str, role: Optional[str] = Query(None)):
    """Retrieves composite confidence across code evidence, quiz, and practical tasks."""
    return progress_service.get_user_progress(username=username, target_role=role)


@router.get(
    "/progress/{username}/recommendations",
    response_model=NextBestAction,
    summary="Get deterministic Next Best Action for user",
)
async def get_user_recommendations(username: str, role: Optional[str] = Query("ml_engineer")):
    """Returns prioritized next best action (missing core skill, quiz, challenge, mission)."""
    progress = progress_service.get_user_progress(username, target_role=role)
    if progress.next_best_action:
        return progress.next_best_action
    return progress_service.get_next_best_action(username, role or "ml_engineer")
