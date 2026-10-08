"""Learning Resources and Learning Path Service for ProofPath Phase 3.

Provides curated educational resources from data/resources.json and builds
prioritized learning roadmaps tailored to a developer's specific role gaps.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

from app.models.progress import LearningResource, LearningResourceType, ChallengeDifficulty
from app.schemas.progress import LearningPathResponse
from app.services.career_service import CareerService

logger = logging.getLogger(__name__)


from app.utils.paths import get_data_file_path


class LearningService:
    """Manages learning resources and builds gap-prioritized learning paths."""

    def __init__(
        self,
        resources_json_path: Optional[str] = None,
        career_service: Optional[CareerService] = None,
    ):
        self.resources_json_path = resources_json_path or get_data_file_path("resources.json")
        self.career_service = career_service or CareerService()
        self.resources = self._load_resources()

    def _load_resources(self) -> List[LearningResource]:
        """Load curated resources from data/resources.json."""
        if not os.path.exists(self.resources_json_path):
            logger.warning(f"Resources file not found at {self.resources_json_path}")
            return []
        try:
            with open(self.resources_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [
                    LearningResource(
                        id=r["id"],
                        skill=r["skill"],
                        title=r["title"],
                        description=r["description"],
                        type=LearningResourceType(r["type"]),
                        url=r["url"],
                        difficulty=ChallengeDifficulty(r["difficulty"]),
                        estimated_time=r["estimated_time"],
                    )
                    for r in data.get("resources", [])
                ]
        except Exception as e:
            logger.error(f"Error loading resources: {e}")
            return []

    def get_resources_for_skill(self, skill: str) -> List[LearningResource]:
        """Return all curated learning resources for a given skill."""
        matched = [r for r in self.resources if r.skill.lower() == skill.lower()]
        if not matched:
            # Fallback generic documentation pointer if not specifically listed
            matched.append(
                LearningResource(
                    id=f"{skill.lower()}-official-doc",
                    skill=skill,
                    title=f"Official {skill} Documentation",
                    description=f"Core technical guides and API references for {skill}.",
                    type=LearningResourceType.DOCUMENTATION,
                    url=f"https://www.google.com/search?q={skill}+official+documentation",
                    difficulty=ChallengeDifficulty.BEGINNER,
                    estimated_time="3 hours",
                )
            )
        return matched

    def build_learning_path(
        self,
        role_id: str,
        missing_skills: Optional[List[str]] = None,
        partial_skills: Optional[List[str]] = None,
    ) -> LearningPathResponse:
        """
        Build an ordered roadmap for a target career role, prioritizing:
        1. Missing Core skills (Highest priority)
        2. Partial Core skills
        3. Missing Supporting skills
        4. Partial Supporting skills
        """
        role = self.career_service.get_role_by_id(role_id)
        if not role:
            # Default to first role if not found
            roles = self.career_service.get_all_roles()
            role = roles[0] if roles else None

        role_title = role.title if role else role_id
        core_names = {s.skill for s in (role.core_skills if role else [])}
        supporting_names = {s.skill for s in (role.supporting_skills if role else [])}

        missing_set = set(missing_skills or [])
        partial_set = set(partial_skills or [])

        # Priority 1: Missing core
        p1 = [s for s in core_names if s in missing_set]
        # Priority 2: Partial core
        p2 = [s for s in core_names if s in partial_set]
        # Priority 3: Missing supporting
        p3 = [s for s in supporting_names if s in missing_set]
        # Priority 4: Partial supporting
        p4 = [s for s in supporting_names if s in partial_set]
        # Priority 5: Remaining skills in role
        p5 = [s for s in (core_names | supporting_names) if s not in (missing_set | partial_set)]

        ordered_names = []
        for group in (p1, p2, p3, p4, p5):
            for skill_name in sorted(group):
                if skill_name not in ordered_names:
                    ordered_names.append(skill_name)

        ordered_skills = []
        step = 1
        for name in ordered_names:
            is_core = name in core_names
            status = "missing" if name in missing_set else ("partial" if name in partial_set else "proven")
            res_list = self.get_resources_for_skill(name)
            guidance = self.generate_personalized_guidance(name, role_title, status)
            ordered_skills.append({
                "step": step,
                "skill": name,
                "is_core": is_core,
                "status": status,
                "priority_label": "High Priority" if (is_core and status != "proven") else "Medium Priority",
                "resources_count": len(res_list),
                "primary_resource": res_list[0].model_dump() if res_list else None,
                "guidance": guidance,
            })
            step += 1

        return LearningPathResponse(
            role_id=role.id if role else role_id,
            role_title=role_title,
            readiness_score=0.0,
            ordered_skills=ordered_skills,
            total_estimated_time=f"{len(ordered_skills) * 3} hours",
        )

    def generate_personalized_guidance(self, skill: str, role_title: str, status: str) -> dict:
        """Generates structured 9-point career guidance for bridging skill gaps."""
        if status == "missing":
            return {
                "why": f"{skill} is a critical core competency for {role_title}.",
                "current_proof": "No physical code evidence detected in analyzed public repositories.",
                "gap": f"Missing source files, imports, and practical tests implementing {skill}.",
                "learn": f"Start with official {skill} documentation and structured tutorials.",
                "build": f"Construct a clean, modular repository implementing {skill} features.",
                "test": f"Complete the {skill} conceptual and reasoning assessment.",
                "verify": f"Submit your GitHub repository for automated AST verification.",
                "next": f"Advance {skill} from Missing to Proven to significantly boost role readiness.",
            }
        elif status == "partial":
            return {
                "why": f"{skill} is required at production-grade depth for {role_title}.",
                "current_proof": f"Detected configuration, package manifest, or shallow usage of {skill}.",
                "gap": "Lacks comprehensive test suites, advanced API integration, or Docker containerization.",
                "learn": f"Review intermediate architecture and best practices for {skill}.",
                "build": f"Containerize your project and add automated unit tests.",
                "test": f"Solve the interactive {skill} code challenge in the Monaco editor.",
                "verify": "Re-analyze your updated repository to verify new AST signals.",
                "next": f"Achieve Level 4/5 production-grade evidence in {skill}.",
            }
        else:
            return {
                "why": f"{skill} is a foundational pillar for {role_title}.",
                "current_proof": f"Verified physical source code implementation detected in repository.",
                "gap": "Core evidence verified; ready for advanced production hardening.",
                "learn": f"Explore high-throughput optimization and distributed systems with {skill}.",
                "build": "Contribute to open-source libraries or author production templates.",
                "test": f"Challenge yourself with Expert-level {skill} assessments.",
                "verify": "Ensure continuous testing and documentation in your public repository.",
                "next": "Focus on remaining partial/missing skills in your career matrix.",
            }
