"""Static GitHub Repository Verification Service for ProofPath Phase 3.

Verifies completion of practical missions by statically inspecting submitted GitHub
repositories using Phase 1 analyzers and file collection infrastructure.
NEVER executes submitted code.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from app.models.progress import (
    PracticalTask,
    ChallengeDifficulty,
    VerificationStatus,
)
from app.schemas.progress import (
    TaskVerificationRequest,
    TaskVerificationResponse,
    TaskCriterionResult,
)
from app.services.github_service import GitHubService
from app.services.repository_service import RepositoryService
from app.analyzers.python_analyzer import PythonAnalyzer
from app.analyzers.javascript_analyzer import JavaScriptAnalyzer
from app.analyzers.dependency_analyzer import DependencyAnalyzer
from app.analyzers.framework_analyzer import FrameworkAnalyzer
from app.db.database import SessionLocal
from app.db.models import TaskAttemptRecord

logger = logging.getLogger(__name__)


class VerificationService:
    """Statically verifies practical mission completion against public GitHub repositories."""

    def __init__(
        self,
        github_service: Optional[GitHubService] = None,
        repository_service: Optional[RepositoryService] = None,
        challenges_json_path: Optional[str] = None,
    ):
        self.github_service = github_service or GitHubService()
        self.repository_service = repository_service or RepositoryService(github_service=self.github_service)

        if not challenges_json_path:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
            challenges_json_path = os.path.join(base_dir, "data", "challenges.json")

        self.challenges_json_path = challenges_json_path
        self.analyzers = [
            PythonAnalyzer(),
            JavaScriptAnalyzer(),
            DependencyAnalyzer(),
            FrameworkAnalyzer(),
        ]
        self.missions = self._load_missions()

    def _load_missions(self) -> Dict[str, PracticalTask]:
        """Load practical missions from data/challenges.json."""
        if not os.path.exists(self.challenges_json_path):
            return {}
        try:
            with open(self.challenges_json_path, "r", encoding="utf-8") as f:
                data = json.load(f).get("skills_assessment_data", {})
                missions = {}
                for skill_name, s_data in data.items():
                    m = s_data.get("mission")
                    if m:
                        missions[m["id"]] = PracticalTask(
                            id=m["id"],
                            skill=skill_name,
                            title=m["title"],
                            difficulty=ChallengeDifficulty(m.get("difficulty", "intermediate")),
                            description=m["description"],
                            requirements=m.get("requirements", []),
                            expected_artifacts=m.get("expected_artifacts", []),
                            verification_rules=m.get("verification_rules", {}),
                        )
                return missions
        except Exception as e:
            logger.error(f"Error loading missions: {e}")
            return {}

    def get_mission_for_skill(self, skill: str) -> PracticalTask:
        """Retrieve practical mission for a given skill."""
        for m in self.missions.values():
            if m.skill.lower() == skill.lower():
                return m

        # Fallback practical mission
        return PracticalTask(
            id=f"{skill.lower()}-m-practical",
            skill=skill,
            title=f"Build and Showcase a {skill} Project",
            difficulty=ChallengeDifficulty.INTERMEDIATE,
            description=f"Create a GitHub repository demonstrating functional {skill} code with unit tests.",
            requirements=[
                f"Implement core logic applying {skill}",
                "Include clean project structure and README",
                "Ensure source files are present in the repository",
            ],
            expected_artifacts=["README.md"],
            verification_rules={
                "required_files": ["*.py", "*.js", "*.ts", "Dockerfile"],
                "required_signals": [],
                "min_files": 1,
            },
        )

    async def verify_task(self, req: TaskVerificationRequest) -> TaskVerificationResponse:
        """
        Statically verify submitted GitHub repository against practical mission criteria.
        Extracts repository tree and inspects file presence and signals.
        """
        # Parse owner and repo from URL or string
        owner, repo_name = self._parse_repo_target(req.repo_url)
        mission = self.missions.get(req.task_id) or self.get_mission_for_skill(req.skill)

        # Collect files using Phase 1 repository service
        try:
            collected_files = await self.repository_service.collect_repository_files(
                owner=owner, repo=repo_name, default_branch=req.branch or "main"
            )
        except Exception as e:
            logger.warning(f"Failed to fetch files from {owner}/{repo_name}: {e}")
            collected_files = []

        file_paths = [f.path for f in collected_files]
        all_signals: List[str] = []

        # Run Phase 1 static analyzers over collected files
        for f in collected_files:
            for analyzer in self.analyzers:
                if analyzer.can_analyze(f.path):
                    try:
                        res = analyzer.analyze(file_path=f.path, content=f.content, repository=repo_name)
                        for sig in res.signals:
                            all_signals.append(sig.name)
                    except Exception as e:
                        logger.debug(f"Analyzer error during verification: {e}")

        # Deterministic criteria verification
        criteria_results: List[TaskCriterionResult] = []
        rules = mission.verification_rules
        required_files_patterns = rules.get("required_files", [])
        required_signals = rules.get("required_signals", [])
        min_files = rules.get("min_files", 1)

        # 1. Criterion: Minimum files present
        file_count_passed = len(collected_files) >= min_files
        criteria_results.append(
            TaskCriterionResult(
                name="repository_structure",
                description=f"Repository contains at least {min_files} relevant source file(s)",
                passed=file_count_passed,
                details=f"Found {len(collected_files)} source files in tree.",
            )
        )

        # 2. Criterion: Expected file pattern matches
        if required_files_patterns:
            files_matched = False
            for pat in required_files_patterns:
                pat_clean = pat.replace("*", "").lower()
                if any(pat_clean in p.lower() for p in file_paths):
                    files_matched = True
                    break

            criteria_results.append(
                TaskCriterionResult(
                    name="expected_artifacts",
                    description=f"Expected artifacts present ({', '.join(required_files_patterns)})",
                    passed=files_matched,
                    details=f"Matched artifacts in collected paths." if files_matched else "Expected artifact files not detected.",
                )
            )

        # 3. Criterion: Technical signal detection
        if required_signals:
            matched_sigs = [s for s in required_signals if any(s.lower() in sig.lower() for sig in all_signals)]
            signals_passed = len(matched_sigs) > 0
            criteria_results.append(
                TaskCriterionResult(
                    name="code_signals_verified",
                    description=f"Code implementation signals found ({', '.join(required_signals)})",
                    passed=signals_passed,
                    details=f"Detected signals: {', '.join(matched_sigs)}" if signals_passed else "No matching signals detected.",
                )
            )

        total_crit = len(criteria_results)
        passed_crit = sum(1 for c in criteria_results if c.passed)

        if passed_crit == total_crit and total_crit > 0:
            status = VerificationStatus.VERIFIED
            score = 100.0
            feedback = f"Mission Verified! All {total_crit} verification criteria satisfied."
        elif passed_crit > 0:
            status = VerificationStatus.PARTIALLY_VERIFIED
            score = round((passed_crit / total_crit) * 100.0, 1)
            feedback = f"Partially Verified ({passed_crit}/{total_crit} criteria met). Implement missing requirements to reach full verification."
        else:
            status = VerificationStatus.NOT_VERIFIED
            score = 0.0
            feedback = "Not Verified. No required artifacts or signals detected in target repository."

        # Persist task verification result
        try:
            with SessionLocal() as db:
                attempt = TaskAttemptRecord(
                    username=req.username,
                    task_id=req.task_id,
                    skill=req.skill,
                    repo_url=req.repo_url,
                    branch=req.branch or "main",
                    status=status.value,
                    score=score,
                    criteria_json=json.dumps([c.model_dump() for c in criteria_results]),
                )
                db.add(attempt)
                db.commit()
        except Exception as e:
            logger.warning(f"Could not persist task verification attempt: {e}")

        return TaskVerificationResponse(
            username=req.username,
            task_id=req.task_id,
            skill=req.skill,
            repo_url=req.repo_url,
            status=status,
            score=score,
            criteria=criteria_results,
            signals_detected=list(set(all_signals))[:10],
            files_checked=file_paths[:10],
            updated_confidence=score,
            feedback=feedback,
        )

    def _parse_repo_target(self, target: str) -> tuple:
        """Parse owner and repo name from GitHub URL or 'owner/repo' format."""
        clean = target.strip().rstrip("/")
        if "github.com/" in clean:
            parts = clean.split("github.com/")[1].split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        elif "/" in clean:
            parts = clean.split("/")
            if len(parts) >= 2:
                return parts[0], parts[1]
        return clean, clean
