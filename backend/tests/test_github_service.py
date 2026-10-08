"""Unit tests for GitHubService with mock HTTP responses."""

import pytest
import httpx
from unittest.mock import AsyncMock, patch, MagicMock

from app.services.github_service import (
    GitHubService,
    GitHubUserNotFoundError,
    GitHubRateLimitError,
    GitHubAPIError,
)
from app.models.evidence import GitHubProfile, GitHubRepository


@pytest.mark.asyncio
async def test_get_user_profile_success():
    service = GitHubService(token="test-token")
    mock_data = {
        "login": "octocat",
        "name": "The Octocat",
        "bio": "Building open source",
        "avatar_url": "https://github.com/images/error/octocat_happy.gif",
        "public_repos": 8,
        "html_url": "https://github.com/octocat",
    }

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        profile = await service.get_user_profile("octocat")

        assert isinstance(profile, GitHubProfile)
        assert profile.login == "octocat"
        assert profile.name == "The Octocat"
        assert profile.public_repositories == 8
        assert profile.html_url == "https://github.com/octocat"


@pytest.mark.asyncio
async def test_get_user_profile_not_found():
    service = GitHubService()
    mock_resp = MagicMock()
    mock_resp.status_code = 404
    mock_resp.text = "Not Found"

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        with pytest.raises(GitHubUserNotFoundError):
            await service.get_user_profile("nonexistent-user-123456")


@pytest.mark.asyncio
async def test_get_user_profile_rate_limited():
    service = GitHubService()
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_resp.headers = {"x-ratelimit-reset": "1700000000"}

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        with pytest.raises(GitHubRateLimitError):
            await service.get_user_profile("octocat")


@pytest.mark.asyncio
async def test_get_user_repositories_filtering():
    service = GitHubService()
    mock_repos = [
        {
            "name": "public-repo",
            "full_name": "octocat/public-repo",
            "description": "A public repo",
            "html_url": "https://github.com/octocat/public-repo",
            "language": "Python",
            "stargazers_count": 10,
            "forks_count": 2,
            "default_branch": "main",
            "fork": False,
            "private": False,
        },
        {
            "name": "forked-repo",
            "full_name": "octocat/forked-repo",
            "fork": True,
            "private": False,
        },
        {
            "name": "private-repo",
            "full_name": "octocat/private-repo",
            "fork": False,
            "private": True,
        },
    ]

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_repos

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        repos = await service.get_user_repositories("octocat", include_forks=False)

        assert len(repos) == 1
        assert repos[0].name == "public-repo"
        assert repos[0].language == "Python"
        assert repos[0].stars == 10


@pytest.mark.asyncio
async def test_get_repository_tree():
    service = GitHubService()
    mock_tree = {
        "tree": [
            {"path": "main.py", "type": "blob", "size": 120},
            {"path": "docs", "type": "tree"},
        ]
    }
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_tree

    with patch("httpx.AsyncClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_resp
        tree = await service.get_repository_tree("octocat", "hello-world")
        assert len(tree) == 2
        assert tree[0]["path"] == "main.py"
