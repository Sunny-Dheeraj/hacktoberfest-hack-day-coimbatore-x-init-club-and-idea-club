"""Path utilities for locating data files in all runtime environments."""

import os
import logging

logger = logging.getLogger(__name__)


def get_data_file_path(filename: str) -> str:
    """Find a data file whether running locally, in Docker, or on Vercel Serverless."""
    candidates = [
        # Inside backend/data (direct sibling of backend/app)
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", filename)),
        # Inside repo-root/data
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", filename)),
        # Current working directory / data
        os.path.abspath(os.path.join(os.getcwd(), "data", filename)),
        # Current working directory / backend / data
        os.path.abspath(os.path.join(os.getcwd(), "backend", "data", filename)),
    ]
    for path in candidates:
        if os.path.exists(path):
            return path
    return candidates[0]
