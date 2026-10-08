"""ProofPath Backend Application Entrypoint."""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.api.github import router as github_router

# Load environment variables from .env file if available
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

app = FastAPI(
    title="ProofPath API",
    description="Deterministic Technical Skill Proof Extraction Engine from GitHub repositories.",
    version="1.0.0",
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


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint to verify backend service readiness."""
    return {
        "status": "healthy",
        "service": "ProofPath Backend",
        "phase": "Phase 1 - Proof Extraction",
        "core_principle": "NO EVIDENCE -> NO CLAIM",
    }


@app.get("/", tags=["Root"])
async def root():
    """Welcome endpoint pointing to documentation and health check."""
    return {
        "message": "Welcome to ProofPath Proof Extraction Engine (Phase 1)",
        "docs_url": "/docs",
        "health_url": "/health",
        "analyze_endpoint": "/api/github/analyze",
    }
