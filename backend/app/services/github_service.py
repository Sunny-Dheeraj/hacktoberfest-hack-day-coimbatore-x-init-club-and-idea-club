"""GitHub REST API Service for ProofPath."""

import os
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.models.evidence import GitHubProfile, GitHubRepository

logger = logging.getLogger(__name__)


class GitHubAPIError(Exception):
    """Base exception for GitHub API errors."""
    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class GitHubUserNotFoundError(GitHubAPIError):
    """Raised when GitHub username does not exist."""
    pass


class GitHubRateLimitError(GitHubAPIError):
    """Raised when GitHub API rate limit is exceeded."""
    pass


class GitHubService:
    """Service wrapping GitHub REST API with rate-limit and error resilience."""

    BASE_URL = "https://api.github.com"
    RAW_BASE_URL = "https://raw.githubusercontent.com"

    def __init__(self, token: Optional[str] = None, timeout: float = 15.0):
        # Allow passing token or reading from environment
        self.token = token or os.getenv("GITHUB_TOKEN", "").strip() or None
        self.timeout = timeout

    def _get_headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "ProofPath-Phase1-ProofExtractor/1.0",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def get_user_profile(self, username: str) -> GitHubProfile:
        """Fetch public profile for a GitHub user."""
        url = f"{self.BASE_URL}/users/{username}"
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers)
            except httpx.RequestError as exc:
                logger.error(f"Network error requesting GitHub profile for {username}: {exc}")
                raise GitHubAPIError(f"Network connection to GitHub failed: {str(exc)}")

            if response.status_code == 404:
                raise GitHubUserNotFoundError(f"GitHub user '{username}' was not found.", status_code=404)
            if response.status_code == 403:
                fallback_profile = await self._fallback_scrape_profile(username)
                if fallback_profile:
                    return fallback_profile
                rate_limit_reset = response.headers.get("x-ratelimit-reset", "unknown")
                msg = f"GitHub API rate limit exceeded. Reset at {rate_limit_reset}."
                if not self.token:
                    msg += " Configure GITHUB_TOKEN in .env to increase rate limits."
                raise GitHubRateLimitError(msg, status_code=403)
            if response.status_code != 200:
                raise GitHubAPIError(
                    f"GitHub API error {response.status_code}: {response.text}",
                    status_code=response.status_code
                )

            data = response.json()
            return GitHubProfile(
                login=data.get("login", username),
                name=data.get("name"),
                bio=data.get("bio"),
                avatar_url=data.get("avatar_url"),
                public_repositories=data.get("public_repos", 0),
                html_url=data.get("html_url", f"https://github.com/{username}"),
            )

    async def get_user_repositories(
        self, username: str, max_repos: int = 10, include_forks: bool = False
    ) -> List[GitHubRepository]:
        """Fetch publicly accessible repositories for a user, sorted by recent activity."""
        url = f"{self.BASE_URL}/users/{username}/repos"
        params = {
            "type": "owner",
            "sort": "updated",
            "direction": "desc",
            "per_page": min(max_repos * 2, 50),
        }
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
            except httpx.RequestError as exc:
                logger.error(f"Network error requesting repos for {username}: {exc}")
                raise GitHubAPIError(f"Failed to fetch repositories: {str(exc)}")

            if response.status_code == 404:
                raise GitHubUserNotFoundError(f"GitHub user '{username}' was not found.", status_code=404)
            if response.status_code == 403:
                fallback_repos = await self._fallback_scrape_repos(username, max_repos)
                if fallback_repos:
                    return fallback_repos
                raise GitHubRateLimitError("GitHub API rate limit exceeded while fetching repositories.", status_code=403)
            if response.status_code != 200:
                raise GitHubAPIError(f"GitHub API error {response.status_code}: {response.text}", status_code=response.status_code)

            repos_raw = response.json()
            if not isinstance(repos_raw, list):
                return []

            filtered_repos: List[GitHubRepository] = []
            for r in repos_raw:
                if not include_forks and r.get("fork", False):
                    continue
                # Verify repository is public and not disabled
                if r.get("private", False) or r.get("disabled", False):
                    continue

                repo_obj = GitHubRepository(
                    name=r.get("name", ""),
                    full_name=r.get("full_name", ""),
                    description=r.get("description"),
                    html_url=r.get("html_url", ""),
                    language=r.get("language"),
                    stars=r.get("stargazers_count", 0),
                    forks=r.get("forks_count", 0),
                    default_branch=r.get("default_branch", "main"),
                    visibility=r.get("visibility", "public"),
                    updated_at=r.get("updated_at"),
                )
                filtered_repos.append(repo_obj)
                if len(filtered_repos) >= max_repos:
                    break

            return filtered_repos

    async def get_repository_tree(
        self, owner: str, repo: str, default_branch: str = "main"
    ) -> List[Dict[str, Any]]:
        """Fetch the full recursive Git tree for a repository."""
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/git/trees/{default_branch}"
        params = {"recursive": "1"}
        headers = self._get_headers()

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                response = await client.get(url, headers=headers, params=params)
            except httpx.RequestError as exc:
                logger.warning(f"Error fetching tree for {owner}/{repo}: {exc}")
                return await self._probe_common_files(owner, repo, default_branch)

            if response.status_code == 403:
                logger.warning(f"Rate limited on tree for {owner}/{repo}, using raw probe fallback")
                return await self._probe_common_files(owner, repo, default_branch)

            if response.status_code != 200:
                logger.warning(f"Unexpected tree status {response.status_code} for {owner}/{repo}")
                return await self._probe_common_files(owner, repo, default_branch)

            data = response.json()
            tree = data.get("tree", [])
            return tree if tree else await self._probe_common_files(owner, repo, default_branch)

    async def _fallback_scrape_profile(self, username: str) -> Optional[GitHubProfile]:
        """Fallback to parsing public GitHub user page when REST API is rate-limited."""
        url = f"https://github.com/{username}"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code != 200:
                    return None
                import re
                name_match = re.search(r'<span class="p-name vcard-fullname[^"]*"[^>]*>([^<]+)</span>', res.text)
                name = name_match.group(1).strip() if name_match else username
                bio_match = re.search(r'<div class="p-note user-profile-bio[^"]*"[^>]*>(?:<div>)?([^<]+)', res.text)
                bio = bio_match.group(1).strip() if bio_match else None
                avatar_match = re.search(r'<img[^>]+class="[^"]*avatar-user[^"]*"[^>]+src="([^"]+)"', res.text)
                avatar_url = avatar_match.group(1) if avatar_match else None
                return GitHubProfile(
                    login=username,
                    name=name,
                    bio=bio,
                    avatar_url=avatar_url,
                    public_repositories=10,
                    html_url=url,
                )
            except Exception:
                return None

    async def _fallback_scrape_repos(self, username: str, max_repos: int = 10) -> List[GitHubRepository]:
        """Fallback to parsing public GitHub user repository listing when REST API is rate-limited."""
        url = f"https://github.com/{username}?tab=repositories"
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                res = await client.get(url, headers=headers)
                if res.status_code != 200:
                    return []
                import re
                repo_names = re.findall(r'itemprop="name codeRepository"[^>]*>\s*([a-zA-Z0-9_\-\.]+)', res.text)
                results = []
                for name in list(dict.fromkeys(repo_names))[:max_repos]:
                    results.append(
                        GitHubRepository(
                            name=name,
                            full_name=f"{username}/{name}",
                            description=None,
                            html_url=f"https://github.com/{username}/{name}",
                            default_branch="main",
                            visibility="public",
                        )
                    )
                return results
            except Exception:
                return []

    async def _probe_common_files(self, owner: str, repo: str, default_branch: str) -> List[Dict[str, Any]]:
        """Probe standard priority files via raw Fastly CDN when Git Trees API is restricted."""
        import asyncio
        candidate_paths = [
            "requirements.txt", "pyproject.toml", "package.json", "Dockerfile", "docker-compose.yml",
            "main.py", "app.py", "app/main.py", "train.py", "model.py", "server.js", "index.js",
            "index.ts", "src/App.tsx", "src/index.tsx", "README.md"
        ]

        async def _check_path(client: httpx.AsyncClient, branch: str, path: str):
            raw_url = f"{self.RAW_BASE_URL}/{owner}/{repo}/{branch}/{path}"
            try:
                res = await client.head(raw_url, headers=self._get_headers())
                if res.status_code == 200:
                    content_len = int(res.headers.get("content-length", 500))
                    return {"path": path, "type": "blob", "size": content_len}
            except Exception:
                pass
            return None

        found_entries = []
        async with httpx.AsyncClient(timeout=min(self.timeout, 5.0)) as client:
            for branch in list(dict.fromkeys([default_branch, "main", "master"])):
                tasks = [_check_path(client, branch, path) for path in candidate_paths]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                for r in results:
                    if isinstance(r, dict):
                        found_entries.append(r)
                if found_entries:
                    break
        return found_entries

    async def get_file_content(
        self, owner: str, repo: str, file_path: str, default_branch: str = "main", max_bytes: int = 100000
    ) -> Optional[str]:
        """Fetch raw content of a specific source or dependency file."""
        # When unauthenticated or falling back, raw.githubusercontent.com is much faster and bypasses rate limits
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if not self.token:
                for branch in list(dict.fromkeys([default_branch, "main", "master"])):
                    raw_url = f"{self.RAW_BASE_URL}/{owner}/{repo}/{branch}/{file_path}"
                    try:
                        raw_res = await client.get(raw_url, headers=self._get_headers())
                        if raw_res.status_code == 200:
                            content = raw_res.text
                            if len(content.encode("utf-8")) > max_bytes:
                                logger.info(f"Skipping oversized file {file_path} ({len(content)} bytes)")
                                return None
                            return content
                    except Exception:
                        pass

            # Try GitHub API directly
            url = f"{self.BASE_URL}/repos/{owner}/{repo}/contents/{file_path}"
            params = {"ref": default_branch}
            headers = self._get_headers()
            headers["Accept"] = "application/vnd.github.raw+json"

            try:
                response = await client.get(url, headers=headers, params=params)
                if response.status_code == 200:
                    content = response.text
                    if len(content.encode("utf-8")) > max_bytes:
                        logger.info(f"Skipping oversized file {file_path} (> {max_bytes} bytes)")
                        return None
                    return content
            except Exception:
                pass

            # Fallback for authenticated mode
            raw_url = f"{self.RAW_BASE_URL}/{owner}/{repo}/{default_branch}/{file_path}"
            try:
                raw_res = await client.get(raw_url, headers=self._get_headers())
                if raw_res.status_code == 200:
                    content = raw_res.text
                    if len(content.encode("utf-8")) > max_bytes:
                        return None
                    return content
            except Exception:
                pass
            return None
