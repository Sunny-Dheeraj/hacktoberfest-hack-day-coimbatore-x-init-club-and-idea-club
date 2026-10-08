"""Database connection and session management for ProofPath persistence."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Default SQLite database path in data/ directory or /tmp for serverless
is_serverless = bool(os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"))
if is_serverless:
    DB_PATH = os.getenv("PROOFPATH_DB_PATH", "/tmp/proofpath.db")
else:
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    DATA_DIR = os.path.join(BASE_DIR, "data")
    try:
        os.makedirs(DATA_DIR, exist_ok=True)
        DB_PATH = os.getenv("PROOFPATH_DB_PATH", os.path.join(DATA_DIR, "proofpath.db"))
    except OSError:
        DB_PATH = os.getenv("PROOFPATH_DB_PATH", "/tmp/proofpath.db")

SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for obtaining database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables in SQLite database if they do not exist."""
    import app.db.models  # Ensure models are registered
    Base.metadata.create_all(bind=engine)
