"""Evidence Orchestration Service for ProofPath Phase 1."""

import logging
from typing import List, Dict, Any, Optional

from app.models.evidence import (
    GitHubProfile,
    GitHubRepository,
    CodeSignal,
    EvidenceItem,
    SkillSummary,
    EvidenceStatus,
)
from app.schemas.evidence import AnalyzeResponse
from app.services.github_service import GitHubService
from app.services.repository_service import RepositoryService
from app.analyzers.python_analyzer import PythonAnalyzer
from app.analyzers.javascript_analyzer import JavaScriptAnalyzer
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.framework_analyzer import FrameworkAnalyzer
from app.analyzers.skill_detector import SkillDetector

logger = logging.getLogger(__name__)


class EvidenceService:
    """
    Main Phase-1 Orchestrator implementing the complete 14-step Proof Extraction pipeline:
    GitHub User -> Profile -> Repositories -> Trees -> Prioritization ->
    Analyzers (Python, JS/TS, Dependency, Framework) -> Signals ->
    Skill Detector -> Evidence Strength & Traceability -> Unified JSON.
    """

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        repository_service: Optional[RepositoryService] = None,
        skill_detector: Optional[SkillDetector] = None,
    ):
        self.github_service = github_service or GitHubService()
        self.repository_service = repository_service or RepositoryService(github_service=self.github_service)
        self.skill_detector = skill_detector or SkillDetector()

        # Registered analyzers
        self.analyzers = [
            PythonAnalyzer(),
            JavaScriptAnalyzer(),
            DependencyAnalyzer(),
            FrameworkAnalyzer(),
        ]

    async def analyze_user(
        self, username: str, max_repos: Optional[int] = None
    ) -> AnalyzeResponse:
        """Execute complete deterministic proof extraction for a GitHub user."""
        logger.info(f"Starting ProofPath Phase 1 analysis for user: {username}")

        # 1 & 2: Retrieve public user profile
        profile = await self.github_service.get_user_profile(username)

        # 3 & 4: Retrieve and select repositories
        effective_max_repos = max_repos or self.repository_service.max_repositories
        repositories = await self.github_service.get_user_repositories(
            username=username, max_repos=effective_max_repos
        )

        all_signals: List[CodeSignal] = []
        all_collected_paths: List[str] = []
        updated_repositories: List[GitHubRepository] = []

        # 5 through 10: For each repository, collect files and extract signals
        for repo in repositories:
            logger.info(f"Analyzing repository: {repo.full_name}")
            try:
                collected_files = await self.repository_service.collect_repository_files(
                    owner=username, repo=repo.name, default_branch=repo.default_branch
                )
            except Exception as e:
                logger.warning(f"Error collecting files from {repo.name}: {e}")
                collected_files = []

            repo_files_count = len(collected_files)
            repo_copy = repo.model_copy(update={"files_analyzed": repo_files_count})
            updated_repositories.append(repo_copy)

            for file_item in collected_files:
                all_collected_paths.append(file_item.path)
                file_analyzed = False

                for analyzer in self.analyzers:
                    if analyzer.can_analyze(file_item.path):
                        try:
                            result = analyzer.analyze(
                                file_path=file_item.path,
                                content=file_item.content,
                                repository=repo.name,
                            )
                            if result.signals:
                                all_signals.extend(result.signals)
                            file_analyzed = True
                        except Exception as e:
                            logger.error(
                                f"Analyzer {analyzer.__class__.__name__} failed on {file_item.path}: {e}"
                            )

        # 11, 12, 13: Detect skills and calculate evidence strength & traceability
        skill_summaries = self.skill_detector.detect_skills(
            signals=all_signals, all_file_paths=all_collected_paths
        )

        # Categorize into proven, partial, missing
        proven_skills: List[str] = []
        partial_skills: List[str] = []
        missing_skills: List[str] = []
        all_evidence_items: List[EvidenceItem] = []

        for summary in skill_summaries:
            if summary.status == EvidenceStatus.PROVEN:
                proven_skills.append(summary.skill)
            elif summary.status == EvidenceStatus.PARTIAL:
                partial_skills.append(summary.skill)
            else:
                missing_skills.append(summary.skill)

            all_evidence_items.extend(summary.evidence)

        # 14: Construct and return Unified Response
        return AnalyzeResponse(
            username=username,
            profile=profile,
            repositories_analyzed=len(updated_repositories),
            repositories=updated_repositories,
            skills=skill_summaries,
            proven=proven_skills,
            partial=partial_skills,
            missing=missing_skills,
            evidence=all_evidence_items,
        )
