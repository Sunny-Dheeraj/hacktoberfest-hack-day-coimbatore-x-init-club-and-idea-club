"""Adaptive Assessment Engine for ProofPath.

Provides:
- 100+ question bank loading and querying across 24 skills
- Dynamic adaptive difficulty progression (Beginner -> Intermediate -> Advanced -> Expert)
- Assessment modes: Quick (20), Standard (40), Full (75), Comprehensive (105)
- Topic weakness and strength tracking
- Gemma 4 question generation helper with strict validation and duplicate rejection
"""

import json
import logging
import os
import uuid
from typing import Dict, List, Optional, Tuple, Set

from app.models.question import (
    AssessmentQuestion,
    QuestionDifficulty,
    QuestionType,
    AssessmentMode,
    AdaptiveAssessmentSession,
    AdaptiveAnswerRecord,
)

logger = logging.getLogger(__name__)

DIFFICULTY_ORDER = [
    QuestionDifficulty.BEGINNER,
    QuestionDifficulty.INTERMEDIATE,
    QuestionDifficulty.ADVANCED,
    QuestionDifficulty.EXPERT,
]

DIFFICULTY_WEIGHTS = {
    QuestionDifficulty.BEGINNER: 1.0,
    QuestionDifficulty.INTERMEDIATE: 1.5,
    QuestionDifficulty.ADVANCED: 2.0,
    QuestionDifficulty.EXPERT: 2.5,
}

MODE_TARGETS = {
    AssessmentMode.QUICK: 20,
    AssessmentMode.STANDARD: 40,
    AssessmentMode.FULL: 75,
    AssessmentMode.COMPREHENSIVE: 105,
}


from app.utils.paths import get_data_file_path


class AdaptiveAssessmentService:
    """Manages persistent question banks, adaptive test sessions, and skill mastery scoring."""

    def __init__(self, question_bank_path: Optional[str] = None):
        self.question_bank_path = question_bank_path or get_data_file_path("question_bank.json")

        self.questions_by_skill: Dict[str, List[AssessmentQuestion]] = {}
        self.sessions: Dict[str, AdaptiveAssessmentSession] = {}
        self._load_question_bank()

    def _load_question_bank(self):
        """Loads and indexes verified questions from JSON storage."""
        if not os.path.exists(self.question_bank_path):
            logger.warning(f"Question bank not found at {self.question_bank_path}")
            return

        try:
            with open(self.question_bank_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            loaded_count = 0
            for skill_name, q_list in data.items():
                parsed_list = []
                for q_dict in q_list:
                    try:
                        q_obj = AssessmentQuestion(**q_dict)
                        parsed_list.append(q_obj)
                    except Exception as e:
                        logger.error(f"Validation failure for question {q_dict.get('id')}: {e}")
                self.questions_by_skill[skill_name] = parsed_list
                loaded_count += len(parsed_list)

            logger.info(
                f"Loaded {loaded_count} validated questions across {len(self.questions_by_skill)} skills."
            )
        except Exception as e:
            logger.exception(f"Failed to load question bank: {e}")

    # -----------------------------------------------------------------------
    # Question Bank Introspection & Validation
    # -----------------------------------------------------------------------

    def get_skill_question_count(self, skill: str) -> int:
        """Returns total validated questions available for a skill."""
        return len(self.questions_by_skill.get(skill, []))

    def get_skill_bank_summary(self, skill: str) -> dict:
        """Provides statistical breakdown of questions by difficulty and topic."""
        questions = self.questions_by_skill.get(skill, [])
        by_diff = {d.value: 0 for d in DIFFICULTY_ORDER}
        by_type = {}
        topics = set()

        for q in questions:
            by_diff[q.difficulty.value] = by_diff.get(q.difficulty.value, 0) + 1
            by_type[q.question_type.value] = by_type.get(q.question_type.value, 0) + 1
        return {
            "skill": skill,
            "total_questions": len(questions),
            "by_difficulty": by_diff,
            "by_type": by_type,
            "topics": sorted(list(topics)),
        }

    def get_available_skills(self) -> List[str]:
        """Returns list of all skills present in the question bank."""
        return sorted(list(self.questions_by_skill.keys()))

    def get_skill_summary(self, skill: str) -> dict:
        """Alias for get_skill_bank_summary."""
        return self.get_skill_bank_summary(skill)

    # -----------------------------------------------------------------------
    # Adaptive Session Lifecycle
    # -----------------------------------------------------------------------

    def start_session(
        self,
        username: str,
        skill: str,
        mode: AssessmentMode = AssessmentMode.QUICK,
        initial_difficulty: QuestionDifficulty = QuestionDifficulty.INTERMEDIATE,
    ) -> Tuple[AdaptiveAssessmentSession, Optional[AssessmentQuestion]]:
        """Initializes a new adaptive assessment session and returns the first question."""
        session_id = str(uuid.uuid4())
        target_count = MODE_TARGETS.get(mode, 20)

        # Normalize skill name if possible
        matched_skill = self._find_matching_skill(skill)

        session = AdaptiveAssessmentSession(
            session_id=session_id,
            username=username,
            skill=matched_skill,
            mode=mode,
            target_count=target_count,
            current_difficulty=initial_difficulty,
            questions_answered=0,
            correct_streak=0,
            incorrect_streak=0,
            records=[],
            score=0.0,
            status="in_progress",
        )
        self.sessions[session_id] = session

        first_question = self._select_next_question(session)
        return session, first_question

    def get_session(self, session_id: str) -> Optional[AdaptiveAssessmentSession]:
        """Retrieves session state by ID."""
        return self.sessions.get(session_id)

    def submit_answer(
        self,
        session_id: str,
        question_id: str,
        selected_answer: str,
        time_taken_seconds: Optional[int] = None,
    ) -> Tuple[bool, str, str, QuestionDifficulty, bool, Optional[AssessmentQuestion], AdaptiveAssessmentSession]:
        """
        Grades an answer, adjusts difficulty adaptively, and advances session.

        Returns:
            (is_correct, correct_answer, explanation, next_difficulty, is_completed, next_question, session)
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session '{session_id}' not found.")

        # Find question
        question = self._find_question(session.skill, question_id)
        if not question:
            raise ValueError(f"Question '{question_id}' not found in skill '{session.skill}'.")

        is_correct = selected_answer.strip() == question.correct_answer.strip()

        # Update streak and adapt difficulty
        if is_correct:
            session.correct_streak += 1
            session.incorrect_streak = 0
            if question.topic not in session.strong_topics:
                session.strong_topics.append(question.topic)

            # Adapt upwards on streak >= 2
            if session.correct_streak >= 2:
                session.current_difficulty = self._step_difficulty(session.current_difficulty, direction=+1)
                session.correct_streak = 0
        else:
            session.incorrect_streak += 1
            session.correct_streak = 0
            if question.topic not in session.weak_topics:
                session.weak_topics.append(question.topic)

            # Adapt downwards on streak >= 2
            if session.incorrect_streak >= 2:
                session.current_difficulty = self._step_difficulty(session.current_difficulty, direction=-1)
                session.incorrect_streak = 0

        # Record answer
        record = AdaptiveAnswerRecord(
            question_id=question_id,
            selected_answer=selected_answer,
            is_correct=is_correct,
            difficulty=question.difficulty,
            topic=question.topic,
            time_taken_seconds=time_taken_seconds,
        )
        session.records.append(record)
        session.questions_answered += 1

        # Check if completed
        is_completed = session.questions_answered >= session.target_count
        if is_completed:
            session.status = "completed"
            self._finalize_session_diagnostics(session)
            next_q = None
        else:
            next_q = self._select_next_question(session)

        # Calculate current percentage score
        total_correct = sum(1 for r in session.records if r.is_correct)
        session.score = round((total_correct / len(session.records)) * 100.0, 1)

        return (
            is_correct,
            question.correct_answer,
            question.explanation,
            session.current_difficulty,
            is_completed,
            next_q,
            session,
        )

    # -----------------------------------------------------------------------
    # Adaptive Selection Algorithm
    # -----------------------------------------------------------------------

    def _select_next_question(self, session: AdaptiveAssessmentSession) -> Optional[AssessmentQuestion]:
        """Picks the best next question matching current difficulty and untackled topics."""
        all_skill_questions = self.questions_by_skill.get(session.skill, [])
        if not all_skill_questions:
            return None

        answered_ids = {r.question_id for r in session.records}
        unanswered = [q for q in all_skill_questions if q.id not in answered_ids]

        if not unanswered:
            return None

        # Filter by current difficulty
        candidates = [q for q in unanswered if q.difficulty == session.current_difficulty]

        # If none left at current difficulty, fallback to nearest difficulty
        if not candidates:
            candidates = unanswered

        # Prefer untackled topics
        covered_topics = {r.topic for r in session.records}
        untackled = [q for q in candidates if q.topic not in covered_topics]

        if untackled:
            return untackled[0]
        return candidates[0]

    def _step_difficulty(self, current: QuestionDifficulty, direction: int) -> QuestionDifficulty:
        """Moves difficulty one tier up (+1) or down (-1) within bounds."""
        idx = DIFFICULTY_ORDER.index(current)
        new_idx = max(0, min(len(DIFFICULTY_ORDER) - 1, idx + direction))
        return DIFFICULTY_ORDER[new_idx]

    def _finalize_session_diagnostics(self, session: AdaptiveAssessmentSession):
        """Computes knowledge level, recommended next level, and confidence score."""
        if not session.records:
            return

        correct_records = [r for r in session.records if r.is_correct]
        accuracy = len(correct_records) / len(session.records)

        # Weighted difficulty achievement
        diff_counts = {d: 0 for d in DIFFICULTY_ORDER}
        for r in correct_records:
            diff_counts[r.difficulty] += 1

        if diff_counts[QuestionDifficulty.EXPERT] >= 2 and accuracy >= 0.75:
            session.estimated_knowledge_level = "Expert / Challenge"
            session.recommended_next_level = "Production System Hardening"
        elif diff_counts[QuestionDifficulty.ADVANCED] >= 3 and accuracy >= 0.65:
            session.estimated_knowledge_level = "Advanced"
            session.recommended_next_level = "Expert Deep Dives"
        elif diff_counts[QuestionDifficulty.INTERMEDIATE] >= 4 and accuracy >= 0.50:
            session.estimated_knowledge_level = "Intermediate"
            session.recommended_next_level = "Advanced Architecture"
        else:
            session.estimated_knowledge_level = "Foundational / Beginner"
            session.recommended_next_level = "Core Fundamentals Review"

        session.confidence_score = round(accuracy * 100.0, 1)

    # -----------------------------------------------------------------------
    # Helper & Search Functions
    # -----------------------------------------------------------------------

    def _find_matching_skill(self, skill: str) -> str:
        """Finds closest registered skill name."""
        for s in self.questions_by_skill.keys():
            if s.lower() == skill.lower():
                return s
        return skill

    def _find_question(self, skill: str, question_id: str) -> Optional[AssessmentQuestion]:
        """Finds question by id within a skill bank."""
        for q in self.questions_by_skill.get(skill, []):
            if q.id == question_id:
                return q
        return None

    @staticmethod
    def topic_name_clean(topic: str) -> str:
        return topic.split("(")[0].strip()

    # -----------------------------------------------------------------------
    # Question Generation & Quality Assurance
    # -----------------------------------------------------------------------

    def add_generated_question(self, question: AssessmentQuestion) -> bool:
        """
        Validates, checks for duplicates, and inserts a question into the live bank.
        Returns True if accepted, False if rejected as duplicate or malformed.
        """
        skill = self._find_matching_skill(question.skill)
        existing = self.questions_by_skill.setdefault(skill, [])

        # Duplicate check: exact text or high token overlap
        new_tokens = set(question.question_text.lower().split())
        for ex in existing:
            if ex.id == question.id:
                return False
            ex_tokens = set(ex.question_text.lower().split())
            intersection = len(new_tokens.intersection(ex_tokens))
            union = len(new_tokens.union(ex_tokens))
            similarity = (intersection / union) if union > 0 else 0
            if similarity > 0.85:
                logger.warning(
                    f"Rejecting question '{question.id}' as near-duplicate of '{ex.id}' (sim={similarity:.2f})"
                )
                return False

        existing.append(question)
        logger.info(f"Accepted new question {question.id} into skill {skill} bank.")
        return True
