"""SQLAlchemy ORM models for ProofPath Phase 3 persistence."""

import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, UniqueConstraint
from app.db.database import Base


class UserProfileRecord(Base):
    """User profile record storing target career role and state."""
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    target_role = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class SkillProgressRecord(Base):
    """Tracks composite skill confidence (40% code, 30% quiz, 30% practical)."""
    __tablename__ = "skill_progress"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, nullable=False)
    skill = Column(String(100), index=True, nullable=False)
    initial_status = Column(String(50), default="missing")
    current_status = Column(String(50), default="missing")
    code_score = Column(Float, default=0.0)       # 0-100 from Phase 1 evidence
    quiz_score = Column(Float, default=0.0)       # 0-100 from knowledge/reasoning
    practical_score = Column(Float, default=0.0)  # 0-100 from challenge / GitHub mission
    confidence = Column(Float, default=0.0)       # 0-100 composite confidence
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("username", "skill", name="uix_user_skill"),
    )


class QuizAttemptRecord(Base):
    """Records quiz submissions (knowledge & code reasoning)."""
    __tablename__ = "quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, nullable=False)
    skill = Column(String(100), index=True, nullable=False)
    score = Column(Float, nullable=False)
    total_questions = Column(Integer, nullable=False)
    correct_answers = Column(Integer, nullable=False)
    details_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class CodeChallengeAttemptRecord(Base):
    """Records Monaco editor code implementation attempts."""
    __tablename__ = "code_challenge_attempts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, nullable=False)
    challenge_id = Column(String(100), nullable=False)
    skill = Column(String(100), index=True, nullable=False)
    language = Column(String(50), nullable=False)
    code = Column(Text, nullable=False)
    status = Column(String(50), nullable=False)  # passed, partially_passed, failed
    score = Column(Float, nullable=False)
    criteria_json = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class TaskAttemptRecord(Base):
    """Records practical mission GitHub static verification submissions."""
    __tablename__ = "task_attempts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), index=True, nullable=False)
    task_id = Column(String(100), nullable=False)
    skill = Column(String(100), index=True, nullable=False)
    repo_url = Column(String(255), nullable=False)
    branch = Column(String(100), default="main")
    status = Column(String(50), nullable=False)  # verified, partially_verified, not_verified
    score = Column(Float, nullable=False)
    criteria_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
