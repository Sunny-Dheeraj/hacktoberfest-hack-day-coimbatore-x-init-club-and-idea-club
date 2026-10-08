"""ProofPath Backend Application Entrypoint."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.github import router as github_router
from app.api.analysis import router as analysis_router

# Load environment variables from .env file if available
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="ProofPath API",
    description="Deterministic Technical Skill Proof Extraction Engine and Career Intelligence powered by Google Cloud Gemma 4.",
    version="2.0.0",
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


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": "ProofPath Backend",
        "phase": "Proof Extraction & Career Intelligence (Phase 2)",
        "core_principle": "NO EVIDENCE -> NO CLAIM",
        "motto": "Code proves. AI interprets.",
    }


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint pointing to documentation and health check."""
    return {
        "message": "Welcome to ProofPath Career Intelligence Engine (Phase 2)",
        "docs_url": "/docs",
        "health_url": "/health",
        "endpoints": {
            "github_analyze": "/api/github/analyze",
            "career_analyze": "/api/analysis/career",
            "roles_list": "/api/analysis/roles",
        },
    }
