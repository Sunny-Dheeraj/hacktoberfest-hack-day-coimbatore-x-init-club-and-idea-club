"""Unit tests for RepositoryService file filtering and prioritization."""

import pytest
from app.services.repository_service import RepositoryService


def test_ignored_paths():
    service = RepositoryService()

    # Ignored directories
    assert service.should_ignore_path(".git/config") is True
    assert service.should_ignore_path("node_modules/react/index.js") is True
    assert service.should_ignore_path("venv/lib/python3.10/site-packages/pkg.py") is True
    assert service.should_ignore_path(".venv/bin/activate") is True
    assert service.should_ignore_path("backend/__pycache__/main.cpython-310.pyc") is True
    assert service.should_ignore_path("dist/bundle.js") is True
    assert service.should_ignore_path("build/static/app.js") is True
    assert service.should_ignore_path(".idea/workspace.xml") is True
    assert service.should_ignore_path(".vscode/settings.json") is True

    # Ignored binary and media files
    assert service.should_ignore_path("assets/logo.png") is True
    assert service.should_ignore_path("images/hero.jpg") is True
    assert service.should_ignore_path("docs/manual.pdf") is True
    assert service.should_ignore_path("bin/server.exe") is True
    assert service.should_ignore_path("archive.zip") is True
    assert service.should_ignore_path("static/main.min.js") is True

    # Valid files that should NOT be ignored
    assert service.should_ignore_path("src/index.ts") is False
    assert service.should_ignore_path("app/main.py") is False
    assert service.should_ignore_path("requirements.txt") is False
    assert service.should_ignore_path("package.json") is False
    assert service.should_ignore_path("Dockerfile") is False
    assert service.should_ignore_path("README.md") is False


def test_file_prioritization():
    service = RepositoryService()

    # Priority rank: lower is higher priority
    dep_rank = service.get_file_priority("requirements.txt")
    key_src_rank = service.get_file_priority("train.py")
    other_src_rank = service.get_file_priority("utils/helpers.py")
    readme_rank = service.get_file_priority("README.md")

    assert dep_rank == 1
    assert key_src_rank == 2
    assert other_src_rank == 3
    assert readme_rank == 4
    assert dep_rank < key_src_rank < other_src_rank < readme_rank


def test_filter_and_prioritize_tree():
    service = RepositoryService(max_files_per_repo=3, max_file_size=5000)

    raw_tree = [
        {"path": "node_modules/react.js", "type": "blob", "size": 100},  # should be ignored
        {"path": "large_dataset.csv", "type": "blob", "size": 999999},  # oversized
        {"path": "folder", "type": "tree"},  # directory
        {"path": "README.md", "type": "blob", "size": 200},
        {"path": "requirements.txt", "type": "blob", "size": 50},
        {"path": "main.py", "type": "blob", "size": 300},
        {"path": "extra.py", "type": "blob", "size": 400},
    ]

    filtered = service.filter_and_prioritize_tree(raw_tree)

    # Should take at most 3 files, sorted by priority: requirements.txt, main.py, extra.py
    assert len(filtered) == 3
    paths = [f["path"] for f in filtered]
    assert "requirements.txt" in paths
    assert "main.py" in paths
    assert "node_modules/react.js" not in paths
    assert "large_dataset.csv" not in paths
