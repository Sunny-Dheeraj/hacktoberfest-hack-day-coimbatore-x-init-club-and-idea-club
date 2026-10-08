"""ProofPath Backend Application Entrypoint."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.github import router as github_router
from app.api.analysis import router as analysis_router
from app.api.progress import router as progress_router
from app.db.database import init_db

# Load environment variables from .env file if available
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

# Initialize database schema
try:
    init_db()
except Exception as e:
    logging.getLogger(__name__).warning(f"Database initialization deferred: {e}")

app = FastAPI(
    title="ProofPath API",
    description="Deterministic Technical Skill Proof Extraction Engine, Career Intelligence, and Proof & Progress Platform.",
    version="3.0.0",
)

# CORS middleware to allow development clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(github_router)
app.include_router(analysis_router)
app.include_router(progress_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": "ProofPath Backend",
        "phase": "Proof Extraction & Career Intelligence (Phase 2 & 3)",
        "core_principle": "NO EVIDENCE -> NO CLAIM",
        "motto": "Code proves. AI interprets. GitHub verifies.",
    }


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint pointing to documentation and health check."""
    return {
        "message": "Welcome to ProofPath Platform (Phase 3 & 4)",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "github_analyze": "/api/github/analyze",
            "career_analyze": "/api/analysis/career",
            "roles_list": "/api/analysis/roles",
            "quiz_generate": "/api/quiz/generate",
            "quiz_submit": "/api/quiz/submit",
            "code_challenge_submit": "/api/code-challenges/submit",
            "task_verify": "/api/tasks/verify",
            "progress": "/api/progress/{username}",
        },
    }
