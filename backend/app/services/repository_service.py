"""Repository Collection and File Filtering Service."""

import os
import logging
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass

from app.services.github_service import GitHubService
from app.models.evidence import GitHubRepository

logger = logging.getLogger(__name__)


# Ignored directory names (any path containing one of these segments will be ignored)
IGNORED_DIRECTORIES: Set[str] = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "env",
    "__pycache__",
    "dist",
    "build",
    "coverage",
    ".next",
    "target",
    "vendor",
    ".idea",
    ".vscode",
    ".pytest_cache",
    ".mypy_cache",
    ".tox",
    "out",
    "bin",
    "obj",
}

# Binary and non-source extensions to strictly ignore
IGNORED_EXTENSIONS: Set[str] = {
    # Images & Media
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".ico",
    ".mp3", ".mp4", ".mov", ".wav", ".avi", ".mkv",
    # Archives & Binaries
    ".zip", ".tar", ".gz", ".7z", ".rar", ".exe", ".dll", ".so",
    ".bin", ".dylib", ".class", ".jar", ".war", ".pyc", ".pyd",
    # Documents & Fonts
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    ".woff", ".woff2", ".ttf", ".eot", ".otf",
    # Maps & Minified
    ".map",
}

# Source code extensions prioritized for deep code analysis
SOURCE_EXTENSIONS: Set[str] = {
    ".py", ".ipynb", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".c", ".h", ".cpp", ".hpp", ".go", ".rs", ".sql"
}

# Dependency and deployment manifests
DEPENDENCY_FILENAMES: Set[str] = {
    "requirements.txt",
    "pyproject.toml",
    "pipfile",
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
}


@dataclass
class CollectedFile:
    path: str
    content: str
    size: int
    is_dependency: bool
    is_source: bool
    language: Optional[str] = None


class RepositoryService:
    """Collects repository file trees, applies security filtering, and retrieves priority files."""

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        max_repositories: Optional[int] = None,
        max_files_per_repo: Optional[int] = None,
        max_file_size: Optional[int] = None,
        max_total_source_size: Optional[int] = None,
    ):
        self.github_service = github_service or GitHubService()
        self.max_repositories = max_repositories or int(os.getenv("MAX_REPOSITORIES", "5"))
        self.max_files_per_repo = max_files_per_repo or int(os.getenv("MAX_FILES_PER_REPOSITORY", "40"))
        self.max_file_size = max_file_size or int(os.getenv("MAX_FILE_SIZE", "100000"))
        self.max_total_source_size = max_total_source_size or int(os.getenv("MAX_TOTAL_SOURCE_SIZE", "1000000"))

    def should_ignore_path(self, path: str) -> bool:
        """Determines if a file path belongs to an ignored directory or extension."""
        path_lower = path.lower()
        parts = path_lower.replace("\\", "/").split("/")

        # Check ignored directory segments
        for part in parts[:-1]:
            if part in IGNORED_DIRECTORIES:
                return True
            # Ignore hidden directories like .hidden
            if part.startswith(".") and part not in {".", ".."}:
                return True

        filename = parts[-1]
        # Ignore minified files
        if filename.endswith(".min.js") or filename.endswith(".min.css") or filename == "bundle.js":
            return True

        # Check ignored file extension
        _, ext = os.path.splitext(filename)
        if ext in IGNORED_EXTENSIONS:
            return True

        return False

    def get_file_priority(self, path: str) -> int:
        """
        Calculates priority rank for a file (lower number = higher priority).
        1: Core dependency manifests (requirements.txt, package.json, Dockerfile)
        2: Source code files (.py, .ts, .tsx, .js, .jsx, .ipynb, .sql)
        3: Secondary config / documentation (README.md, compose files)
        4: Other source files
        99: Lowest priority
        """
        filename = os.path.basename(path).lower()
        _, ext = os.path.splitext(filename)

        if filename in DEPENDENCY_FILENAMES:
            return 1
        if ext in SOURCE_EXTENSIONS:
            # Entry points or key code files get slight priority boost
            if filename in {"main.py", "app.py", "index.ts", "index.js", "app.tsx", "train.py"}:
                return 2
            return 3
        if filename.startswith("readme"):
            return 4
        if ext in {".yml", ".yaml", ".json"}:
            return 5
        return 99

    def filter_and_prioritize_tree(self, tree_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter out ignored paths and return prioritized list of file entries."""
        valid_files: List[Dict[str, Any]] = []

        for entry in tree_entries:
            if entry.get("type") != "blob":
                continue
            path = entry.get("path", "")
            if not path or self.should_ignore_path(path):
                continue

            size = entry.get("size", 0)
            if size > self.max_file_size:
                logger.debug(f"Skipping {path}: size {size} exceeds max {self.max_file_size}")
                continue

            valid_files.append(entry)

        # Sort by priority rank ascending, then by size ascending
        valid_files.sort(key=lambda item: (self.get_file_priority(item["path"]), item.get("size", 0)))
        return valid_files[: self.max_files_per_repo]

    async def collect_repository_files(
        self, owner: str, repo: str, default_branch: str = "main"
    ) -> List[CollectedFile]:
        """Fetch file tree, filter priority files, and retrieve their contents."""
        tree = await self.github_service.get_repository_tree(owner, repo, default_branch)
        if not tree:
            logger.info(f"Empty or unreachable tree for {owner}/{repo}")
            return []

        priority_files = self.filter_and_prioritize_tree(tree)
        collected: List[CollectedFile] = []
        total_bytes = 0

        for entry in priority_files:
            if total_bytes >= self.max_total_source_size:
                logger.info(f"Reached max total source size limit ({total_bytes} bytes) for {owner}/{repo}")
                break

            path = entry["path"]
            content = await self.github_service.get_file_content(
                owner=owner,
                repo=repo,
                file_path=path,
                default_branch=default_branch,
                max_bytes=self.max_file_size,
            )

            if content is None:
                continue

            content_bytes = len(content.encode("utf-8"))
            total_bytes += content_bytes

            filename_lower = os.path.basename(path).lower()
            _, ext = os.path.splitext(filename_lower)

            is_dep = filename_lower in DEPENDENCY_FILENAMES or ext in {".txt", ".toml", ".json", ".lock"}
            is_src = ext in SOURCE_EXTENSIONS

            collected.append(
                CollectedFile(
                    path=path,
                    content=content,
                    size=content_bytes,
                    is_dependency=is_dep,
                    is_source=is_src,
                    language=ext.lstrip(".") if ext else None,
                )
            )

        return collected
