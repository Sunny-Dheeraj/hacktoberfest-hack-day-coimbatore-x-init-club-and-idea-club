"""Quiz Assessment and Grading Service for ProofPath Phase 3.

Handles generation, evaluation, and persistence of the 3 assessment dimensions:
1. Knowledge Questions (conceptual multiple choice)
2. Code Reasoning Questions (snippet analysis)
3. Code Implementation Challenges (evaluated via CodeEvaluator)
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from app.models.progress import (
    KnowledgeQuestion,
    CodeReasoningQuestion,
    CodeChallenge,
    ChallengeCriterion,
    ChallengeDifficulty,
)
from app.schemas.progress import (
    FullSkillAssessment,
    QuizSubmissionRequest,
    QuizResultResponse,
    QuizQuestionResult,
    CodeChallengeSubmissionRequest,
    CodeChallengeResultResponse,
)
from app.services.code_evaluator import CodeEvaluator
from app.db.database import SessionLocal
from app.db.models import QuizAttemptRecord, CodeChallengeAttemptRecord

logger = logging.getLogger(__name__)


class QuizService:
    """Manages 3-dimension assessments and deterministic grading."""

    def __init__(
        self,
        challenges_json_path: Optional[str] = None,
        code_evaluator: Optional[CodeEvaluator] = None,
    ):
        if not challenges_json_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            challenges_json_path = os.path.join(base_dir, "data", "challenges.json")

        self.challenges_json_path = challenges_json_path
        self.code_evaluator = code_evaluator or CodeEvaluator()
        self.catalog = self._load_catalog()

    def _load_catalog(self) -> Dict[str, Any]:
        """Load assessment challenges and questions from data/challenges.json."""
        if not os.path.exists(self.challenges_json_path):
            logger.warning(f"Challenges file not found at {self.challenges_json_path}")
            return {}
        try:
            with open(self.challenges_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("skills_assessment_data", {})
        except Exception as e:
            logger.error(f"Error loading challenges data: {e}")
            return {}

    def get_skill_assessment(self, skill: str) -> FullSkillAssessment:
        """Retrieve complete 3-dimension assessment for a given skill."""
        skill_data = self.catalog.get(skill)
        if not skill_data:
            # Generate default fallback assessment for skills not explicitly cataloged
            return self._build_default_assessment(skill)

        # 1. Knowledge Questions
        knowledge_list = [
            KnowledgeQuestion(
                id=q["id"],
                question=q["question"],
                options=q["options"],
                correct_index=q["correct_index"],
                explanation=q["explanation"],
            )
            for q in skill_data.get("knowledge", [])
        ]

        # 2. Code Reasoning Questions
        reasoning_list = [
            CodeReasoningQuestion(
                id=q["id"],
                language=q["language"],
                snippet=q["snippet"],
                question=q["question"],
                options=q["options"],
                correct_index=q["correct_index"],
                explanation=q["explanation"],
            )
            for q in skill_data.get("code_reasoning", [])
        ]

        # 3. Code Challenge
        challenge_data = skill_data.get("code_challenge")
        challenge_obj = None
        if challenge_data:
            criteria = [
                ChallengeCriterion(name=c["name"], description=c["description"])
                for c in challenge_data.get("criteria", [])
            ]
            challenge_obj = CodeChallenge(
                id=challenge_data["id"],
                skill=skill,
                language=challenge_data.get("language", "python"),
                title=challenge_data["title"],
                difficulty=ChallengeDifficulty(challenge_data.get("difficulty", "beginner")),
                description=challenge_data["description"],
                starter_code=challenge_data["starter_code"],
                expected_behavior=challenge_data.get("expected_behavior", []),
                criteria=criteria,
            )

        return FullSkillAssessment(
            skill=skill,
            knowledge_questions=knowledge_list,
            code_reasoning_questions=reasoning_list,
            code_challenge=challenge_obj,
        )

    def grade_quiz(self, submission: QuizSubmissionRequest) -> QuizResultResponse:
        """
        Deterministically grade multiple choice questions (knowledge + code reasoning).
        Formula: (correct_answers / total_questions) * 100
        """
        assessment = self.get_skill_assessment(submission.skill)
        all_questions = {q.id: q for q in assessment.knowledge_questions}
        all_questions.update({q.id: q for q in assessment.code_reasoning_questions})

        total = len(all_questions)
        if total == 0:
            return QuizResultResponse(
                username=submission.username,
                skill=submission.skill,
                score=100.0,
                total_questions=0,
                correct_answers=0,
                question_results=[],
                updated_confidence=100.0,
                feedback="No questions evaluated for this skill.",
            )

        correct_count = 0
        results: List[QuizQuestionResult] = []

        for q_id, q in all_questions.items():
            selected = submission.answers.get(q_id, -1)
            is_correct = (selected == q.correct_index)
            if is_correct:
                correct_count += 1

            results.append(
                QuizQuestionResult(
                    question_id=q_id,
                    selected_index=selected,
                    correct_index=q.correct_index,
                    is_correct=is_correct,
                    explanation=q.explanation,
                )
            )

        score = round((correct_count / total) * 100.0, 1)

        # Persist attempt to SQLite
        try:
            with SessionLocal() as db:
                attempt = QuizAttemptRecord(
                    username=submission.username,
                    skill=submission.skill,
                    score=score,
                    total_questions=total,
                    correct_answers=correct_count,
                    details_json=json.dumps([r.model_dump() for r in results]),
                )
                db.add(attempt)
                db.commit()
        except Exception as e:
            logger.warning(f"Could not persist quiz attempt: {e}")

        feedback = (
            f"Scored {score}% ({correct_count}/{total} correct). Excellent conceptual mastery!"
            if score >= 80.0
            else f"Scored {score}% ({correct_count}/{total} correct). Review the explanations to reinforce knowledge gaps."
        )

        return QuizResultResponse(
            username=submission.username,
            skill=submission.skill,
            score=score,
            total_questions=total,
            correct_answers=correct_count,
            question_results=results,
            updated_confidence=score,
            feedback=feedback,
        )

    def evaluate_code_challenge(
        self, submission: CodeChallengeSubmissionRequest
    ) -> CodeChallengeResultResponse:
        """Evaluate Monaco Editor implementation code submission."""
        assessment = self.get_skill_assessment(submission.skill)
        challenge = assessment.code_challenge

        if not challenge or challenge.id != submission.challenge_id:
            # Create challenge on the fly if needed
            challenge = CodeChallenge(
                id=submission.challenge_id,
                skill=submission.skill,
                language=submission.language,
                title=f"{submission.skill} Implementation Challenge",
                difficulty=ChallengeDifficulty.BEGINNER,
                description=f"Implement a verified {submission.skill} snippet.",
                starter_code=submission.code,
                criteria=[
                    ChallengeCriterion(name="syntax_valid", description="Code parses without syntax errors"),
                    ChallengeCriterion(name="logic_implemented", description="Implements meaningful logic"),
                ],
            )

        status, score, criteria_results, feedback = self.code_evaluator.evaluate(
            challenge=challenge, submitted_code=submission.code
        )

        # Persist challenge attempt
        try:
            with SessionLocal() as db:
                attempt = CodeChallengeAttemptRecord(
                    username=submission.username,
                    challenge_id=submission.challenge_id,
                    skill=submission.skill,
                    language=submission.language,
                    code=submission.code,
                    status=status.value,
                    score=score,
                    criteria_json=json.dumps([c.model_dump() for c in criteria_results]),
                    feedback=feedback,
                )
                db.add(attempt)
                db.commit()
        except Exception as e:
            logger.warning(f"Could not persist code challenge attempt: {e}")

        return CodeChallengeResultResponse(
            challenge_id=submission.challenge_id,
            skill=submission.skill,
            language=submission.language,
            status=status,
            score=score,
            criteria=criteria_results,
            feedback=feedback,
            updated_confidence=score,
        )

    def _build_default_assessment(self, skill: str) -> FullSkillAssessment:
        """Construct fallback assessment for skills without explicit catalog entry."""
        k_q = KnowledgeQuestion(
            id=f"{skill.lower()}-k-gen",
            question=f"What is the core architectural purpose of using {skill} in modern software engineering?",
            options=[
                f"To provide low-level hardware interrupt handling for {skill}",
                f"To standardize scalable design and implementation for {skill} workflows",
                f"To replace relational database schemas with binary logs",
                f"To bypass HTTP transport protocols entirely",
            ],
            correct_index=1,
            explanation=f"{skill} provides industry-standard structures for maintainable software development.",
        )
        r_q = CodeReasoningQuestion(
            id=f"{skill.lower()}-r-gen",
            language="python",
            snippet=f"# Example {skill} usage\ndef process_data(items):\n    return [item for item in items if item is not None]\nprint(len(process_data([1, None, 2])))",
            question="What is the output of the code snippet above?",
            options=["1", "2", "3", "None"],
            correct_index=1,
            explanation="The list comprehension removes None elements, leaving [1, 2] with length 2.",
        )
        challenge = CodeChallenge(
            id=f"{skill.lower()}-c-gen",
            skill=skill,
            language="python",
            title=f"Implement a {skill} Utility Function",
            difficulty=ChallengeDifficulty.BEGINNER,
            description=f"Write a Python utility function `solution()` returning True.",
            starter_code="def solution():\n    return True\n",
            expected_behavior=["solution() == True"],
            criteria=[
                ChallengeCriterion(name="function_defined", description="Defines function 'solution'"),
                ChallengeCriterion(name="returns_value", description="Returns boolean True"),
            ],
        )
        return FullSkillAssessment(
            skill=skill,
            knowledge_questions=[k_q],
            code_reasoning_questions=[r_q],
            code_challenge=challenge,
        )
