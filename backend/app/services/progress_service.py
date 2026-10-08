"""Progress Tracking and Next Best Action Service for ProofPath Phase 3.

Calculates composite Skill Confidence:
    skill_confidence = (code_score * 0.40) + (quiz_score * 0.30) + (practical_score * 0.30)
Manages progression states and generates data-driven Next Best Actions.
"""

import logging
from typing import List, Dict, Any, Optional
from sqlalchemy import select

from app.models.progress import SkillConfidence, NextBestAction
from app.schemas.progress import UserProgressResponse
from app.db.database import SessionLocal
from app.db.models import (
    SkillProgressRecord,
    QuizAttemptRecord,
    CodeChallengeAttemptRecord,
    TaskAttemptRecord,
    UserProfileRecord,
)
from app.services.career_service import CareerService

logger = logging.getLogger(__name__)

# Configurable weights for ProofPath's three pillars
WEIGHT_CODE = 0.40
WEIGHT_QUIZ = 0.30
WEIGHT_PRACTICAL = 0.30


class ProgressService:
    """Manages skill confidence calculations, persistence, and next best action logic."""

    def __init__(self, career_service: Optional[CareerService] = None):
        self.career_service = career_service or CareerService()

    def update_skill_progress(
        self,
        username: str,
        skill: str,
        code_score: Optional[float] = None,
        quiz_score: Optional[float] = None,
        practical_score: Optional[float] = None,
        initial_status: Optional[str] = None,
    ) -> SkillConfidence:
        """
        Update and persist skill confidence in SQLite database.
        Formula: (code * 0.40) + (quiz * 0.30) + (practical * 0.30)
        """
        with SessionLocal() as db:
            record = (
                db.query(SkillProgressRecord)
                .filter_by(username=username, skill=skill)
                .first()
            )

            if not record:
                record = SkillProgressRecord(
                    username=username,
                    skill=skill,
                    initial_status=initial_status or "missing",
                    current_status=initial_status or "missing",
                    code_score=code_score if code_score is not None else 0.0,
                    quiz_score=quiz_score if quiz_score is not None else 0.0,
                    practical_score=practical_score if practical_score is not None else 0.0,
                )
                db.add(record)
            else:
                if code_score is not None:
                    record.code_score = code_score
                if quiz_score is not None:
                    record.quiz_score = max(record.quiz_score, quiz_score)
                if practical_score is not None:
                    record.practical_score = max(record.practical_score, practical_score)

            # Compute composite confidence
            c_score = record.code_score or 0.0
            q_score = record.quiz_score or 0.0
            p_score = record.practical_score or 0.0

            confidence = round(
                (c_score * WEIGHT_CODE) + (q_score * WEIGHT_QUIZ) + (p_score * WEIGHT_PRACTICAL),
                1,
            )
            record.confidence = min(100.0, max(0.0, confidence))

            # Determine progression state
            if confidence >= 80.0 or (c_score >= 80.0 and (q_score >= 70.0 or p_score >= 70.0)):
                record.current_status = "proven"
            elif p_score >= 80.0 or confidence >= 60.0:
                record.current_status = "verified"
            elif q_score >= 50.0 or p_score >= 50.0 or confidence >= 30.0:
                record.current_status = "partial"
            elif q_score > 0.0 or p_score > 0.0:
                record.current_status = "learning"
            else:
                record.current_status = record.initial_status or "missing"

            db.commit()
            db.refresh(record)

            return SkillConfidence(
                skill=record.skill,
                code_score=record.code_score,
                quiz_score=record.quiz_score,
                practical_score=record.practical_score,
                confidence=record.confidence,
                status=record.current_status,
            )

    def get_user_progress(self, username: str, target_role: Optional[str] = None) -> UserProgressResponse:
        """Fetch all tracked skills for a user and compute next best action."""
        with SessionLocal() as db:
            records = (
                db.query(SkillProgressRecord)
                .filter_by(username=username)
                .all()
            )

            # Check user target role
            user_prof = db.query(UserProfileRecord).filter_by(username=username).first()
            active_role = target_role or (user_prof.target_role if user_prof else None) or "ml_engineer"

            skills_list: List[SkillConfidence] = [
                SkillConfidence(
                    skill=r.skill,
                    code_score=r.code_score,
                    quiz_score=r.quiz_score,
                    practical_score=r.practical_score,
                    confidence=r.confidence,
                    status=r.current_status,
                )
                for r in records
            ]

        overall_conf = (
            round(sum(s.confidence for s in skills_list) / len(skills_list), 1)
            if skills_list
            else 0.0
        )

        next_action = self.get_next_best_action(username, active_role, skills_list)

        return UserProgressResponse(
            username=username,
            target_role=active_role,
            overall_confidence=overall_conf,
            skills=skills_list,
            next_best_action=next_action,
        )

    def get_next_best_action(
        self,
        username: str,
        role_id: str,
        current_skills: Optional[List[SkillConfidence]] = None,
    ) -> NextBestAction:
        """
        Deterministic Next Best Action recommendation hierarchy:
        1. Missing Core skill -> Take knowledge quiz or learn
        2. Partial Core skill -> Complete Monaco code challenge
        3. Missing practical verification -> Submit GitHub practical mission
        4. Supporting skills
        """
        role = self.career_service.get_role_by_id(role_id)
        if not role:
            roles = self.career_service.get_all_roles()
            role = roles[0] if roles else None

        skill_map = {s.skill: s for s in (current_skills or [])}
        core_skills = role.core_skills if role else []

        # 1. Search for missing core skills with 0 quiz score
        for req in core_skills:
            s_conf = skill_map.get(req.skill)
            if not s_conf or s_conf.quiz_score == 0.0:
                return NextBestAction(
                    skill=req.skill,
                    action_type="quiz",
                    title=f"Take the {req.skill} Assessment",
                    reason=f"{req.skill} is a core requirement for {role.title} with no verified score.",
                    priority=1,
                    target_role=role_id,
                )

        # 2. Core skills with quiz score but incomplete code challenge
        for req in core_skills:
            s_conf = skill_map.get(req.skill)
            if s_conf and s_conf.practical_score < 50.0:
                return NextBestAction(
                    skill=req.skill,
                    action_type="code_challenge",
                    title=f"Complete {req.skill} Code Implementation Challenge",
                    reason=f"Prove implementation mastery of {req.skill} in the Monaco editor.",
                    priority=2,
                    target_role=role_id,
                )

        # 3. Core skills ready for GitHub mission verification
        for req in core_skills:
            s_conf = skill_map.get(req.skill)
            if s_conf and s_conf.status != "proven" and s_conf.practical_score < 100.0:
                return NextBestAction(
                    skill=req.skill,
                    action_type="practical_mission",
                    title=f"Deploy & Verify {req.skill} Mission Repository",
                    reason=f"Earn 100% Practical verification for {req.skill} via static GitHub inspection.",
                    priority=3,
                    target_role=role_id,
                )

        # 4. Default next best action
        top_skill = core_skills[0].skill if core_skills else "Python"
        return NextBestAction(
            skill=top_skill,
            action_type="quiz",
            title=f"Reinforce {top_skill} Knowledge",
            reason=f"Maintain peak readiness for {role.title if role else 'your target role'}.",
            priority=4,
            target_role=role_id,
        )
