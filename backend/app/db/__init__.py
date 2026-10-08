"""Database package for ProofPath."""

from app.db.database import get_db, init_db, SessionLocal, engine, Base
from app.db.models import (
    UserProfileRecord,
    SkillProgressRecord,
    QuizAttemptRecord,
    CodeChallengeAttemptRecord,
    TaskAttemptRecord,
)

__all__ = [
    "get_db",
    "init_db",
    "SessionLocal",
    "engine",
    "Base",
    "UserProfileRecord",
    "SkillProgressRecord",
    "QuizAttemptRecord",
    "CodeChallengeAttemptRecord",
    "TaskAttemptRecord",
]
