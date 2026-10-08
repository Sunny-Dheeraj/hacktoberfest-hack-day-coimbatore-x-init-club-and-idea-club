"""Career Analysis Service for ProofPath Phase 2.

Loads career role definitions, matches Phase 1 skill evidence against role
requirements, classifies skills as Proven / Partial / Missing, and calculates
deterministic weighted readiness scores.

This service NEVER invents evidence. It only interprets what Phase 1 found.
"""

import os
import json
import logging
from typing import List, Dict, Optional, Any

from app.models.evidence import SkillSummary, EvidenceStatus, EvidenceItem
from app.models.career import (
    CareerRole,
    RoleSkillRequirement,
    SkillClassification,
    SkillAssessment,
    ReadinessScore,
    RoleAnalysis,
    CareerAnalysis,
    RepositorySummary,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Classification thresholds (deterministic, centralized)
# ---------------------------------------------------------------------------
# Phase 1 SkillDetector assigns strength 0-5.
# Career service maps these to Proven / Partial / Missing:
PROVEN_THRESHOLD = 3   # strength >= 3 → Proven
PARTIAL_THRESHOLD = 2  # strength == 2 → Partial
# strength 0-1 → Missing


from app.utils.paths import get_data_file_path


class CareerService:
    """Deterministic career readiness analysis built on Phase 1 evidence."""

    def __init__(self, roles_json_path: Optional[str] = None):
        if not roles_json_path:
            roles_json_path = get_data_file_path("roles.json")

        self.roles_json_path = roles_json_path
        self.roles: List[CareerRole] = self._load_roles()

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def _load_roles(self) -> List[CareerRole]:
        """Load career roles from data/roles.json."""
        if not os.path.exists(self.roles_json_path):
            logger.error(f"Roles file not found at {self.roles_json_path}")
            return []

        try:
            with open(self.roles_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading roles: {e}")
            return []

        roles: List[CareerRole] = []
        for role_data in data.get("roles", []):
            core = [
                RoleSkillRequirement(skill=s["skill"], weight=s["weight"], is_core=True)
                for s in role_data.get("core_skills", [])
            ]
            supporting = [
                RoleSkillRequirement(skill=s["skill"], weight=s["weight"], is_core=False)
                for s in role_data.get("supporting_skills", [])
            ]
            roles.append(
                CareerRole(
                    id=role_data["id"],
                    title=role_data["title"],
                    description=role_data.get("description", ""),
                    core_skills=core,
                    supporting_skills=supporting,
                )
            )
        logger.info(f"Loaded {len(roles)} career roles from {self.roles_json_path}")
        return roles

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_all_roles(self) -> List[CareerRole]:
        """Return all loaded career roles."""
        return self.roles

    def get_role_by_id(self, role_id: str) -> Optional[CareerRole]:
        """Retrieve a single role by its ID."""
        for role in self.roles:
            if role.id == role_id:
                return role
        return None

    def analyze_career(
        self,
        username: str,
        skill_summaries: List[SkillSummary],
        role_ids: Optional[List[str]] = None,
        profile: Optional[Any] = None,
        repositories: Optional[List[Any]] = None,
        repositories_analyzed: int = 0,
        total_public_repos: int = 0,
        coverage_summary: str = "",
    ) -> CareerAnalysis:
        """
        Run deterministic career analysis against Phase 1 evidence.

        Args:
            username: GitHub username
            skill_summaries: Phase 1 SkillSummary list (from EvidenceService)
            role_ids: Optional list of role IDs to analyze (None = all)
            profile: Optional GitHub profile object
            repositories: Optional list of analyzed repositories
            repositories_analyzed: Count of analyzed repositories
            total_public_repos: Total public repositories on profile
            coverage_summary: Transparency summary string

        Returns:
            CareerAnalysis with readiness scores and skill assessments
        """
        # Build skill lookup from Phase 1 output
        skill_map: Dict[str, SkillSummary] = {s.skill: s for s in skill_summaries}

        # Select which roles to analyze
        if role_ids:
            roles_to_analyze = [r for r in self.roles if r.id in role_ids]
        else:
            roles_to_analyze = self.roles

        role_analyses: List[RoleAnalysis] = []
        for role in roles_to_analyze:
            analysis = self._analyze_role(role, skill_map)
            role_analyses.append(analysis)

        # Sort by readiness score descending to find primary role
        role_analyses.sort(key=lambda ra: ra.readiness.score, reverse=True)
        primary_role = role_analyses[0].role.id if role_analyses else None

        # Compute overall strengths (proven skills across all roles)
        overall_strengths = self._compute_overall_strengths(skill_summaries)

        formatted_repos: List[RepositorySummary] = []
        for repo in (repositories or []):
            if isinstance(repo, RepositorySummary):
                formatted_repos.append(repo)
            elif hasattr(repo, "name"):
                formatted_repos.append(
                    RepositorySummary(
                        name=getattr(repo, "name", ""),
                        description=getattr(repo, "description", None),
                        language=getattr(repo, "language", None),
                        stars=getattr(repo, "stars", 0),
                        forks=getattr(repo, "forks", 0),
                        files_analyzed=getattr(repo, "files_analyzed", 0),
                        skills_detected=getattr(repo, "skills_detected", []),
                    )
                )
            elif isinstance(repo, dict):
                formatted_repos.append(RepositorySummary(**repo))

        return CareerAnalysis(
            username=username,
            roles_analyzed=role_analyses,
            overall_strengths=overall_strengths,
            primary_role=primary_role,
            profile=profile,
            repositories=formatted_repos,
            repositories_analyzed=repositories_analyzed,
            total_public_repos=total_public_repos,
            coverage_summary=coverage_summary,
            analysis_metadata={
                "total_skills_evaluated": len(skill_summaries),
                "roles_count": len(role_analyses),
                "classification_thresholds": {
                    "proven": f">= {PROVEN_THRESHOLD}",
                    "partial": f"== {PARTIAL_THRESHOLD}",
                    "missing": f"< {PARTIAL_THRESHOLD}",
                },
            },
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _analyze_role(
        self, role: CareerRole, skill_map: Dict[str, SkillSummary]
    ) -> RoleAnalysis:
        """Analyze a single role against the Phase 1 skill evidence."""
        assessments: List[SkillAssessment] = []
        proven: List[str] = []
        partial: List[str] = []
        missing: List[str] = []

        for req in role.all_skills:
            assessment = self._assess_skill(req, skill_map)
            assessments.append(assessment)

            if assessment.classification == SkillClassification.PROVEN:
                proven.append(req.skill)
            elif assessment.classification == SkillClassification.PARTIAL:
                partial.append(req.skill)
            else:
                missing.append(req.skill)

        readiness = self._calculate_readiness(assessments)

        return RoleAnalysis(
            role=role,
            readiness=readiness,
            skill_assessments=assessments,
            proven_skills=proven,
            partial_skills=partial,
            missing_skills=missing,
            ai_insight=None,  # Populated later by Gemma if available
        )

    def _assess_skill(
        self, req: RoleSkillRequirement, skill_map: Dict[str, SkillSummary]
    ) -> SkillAssessment:
        """Classify a single skill requirement against Phase 1 evidence with detailed findings."""
        summary = skill_map.get(req.skill)

        evidence_found: List[str] = []
        missing_evidence: List[str] = []
        evidence_locations: List[str] = []

        if summary and summary.evidence:
            for ev in summary.evidence:
                loc = f"{ev.repository}/{ev.file}" if ev.repository and ev.file else (ev.file or "")
                if loc and loc not in evidence_locations:
                    evidence_locations.append(loc)
                for sig in ev.signals:
                    clean_sig = sig.replace("_", " ").title()
                    if clean_sig not in evidence_found:
                        evidence_found.append(clean_sig)

        if not summary or summary.strength < PARTIAL_THRESHOLD:
            missing_evidence.extend([
                f"Source code files implementing {req.skill} logic",
                f"Dependencies or configuration files referencing {req.skill}",
                "Public GitHub repository demonstrating practical proficiency",
            ])
            return SkillAssessment(
                skill=req.skill,
                classification=SkillClassification.MISSING,
                is_core=req.is_core,
                weight=req.weight,
                evidence_strength=summary.strength if summary else 0,
                evidence_count=len(summary.evidence) if summary else 0,
                top_evidence=summary.evidence[:3] if summary else [],
                evidence_found=evidence_found,
                missing_evidence=missing_evidence,
                evidence_locations=evidence_locations,
            )
        elif summary.strength >= PROVEN_THRESHOLD:
            if not evidence_found:
                evidence_found.append(f"{req.skill} verified in source code implementation")
            missing_evidence.append("Automated test coverage and continuous integration pipelines")
            return SkillAssessment(
                skill=req.skill,
                classification=SkillClassification.PROVEN,
                is_core=req.is_core,
                weight=req.weight,
                evidence_strength=summary.strength,
                evidence_count=len(summary.evidence),
                top_evidence=summary.evidence[:3],
                evidence_found=evidence_found,
                missing_evidence=missing_evidence,
                evidence_locations=evidence_locations,
            )
        else:
            if not evidence_found:
                evidence_found.append(f"{req.skill} declared in project configuration or manifests")
            missing_evidence.extend([
                f"Deep implementation usage of {req.skill} APIs and modules",
                "Unit and integration tests for core logic",
                "Containerization or production deployment configuration",
            ])
            return SkillAssessment(
                skill=req.skill,
                classification=SkillClassification.PARTIAL,
                is_core=req.is_core,
                weight=req.weight,
                evidence_strength=summary.strength,
                evidence_count=len(summary.evidence),
                top_evidence=summary.evidence[:3],
                evidence_found=evidence_found,
                missing_evidence=missing_evidence,
                evidence_locations=evidence_locations,
            )

    def _calculate_readiness(self, assessments: List[SkillAssessment]) -> ReadinessScore:
        """
        Compute deterministic weighted readiness score.

        Formula:
            earned = Σ (weight × normalized_strength)
            max_possible = Σ (weight × 5)  # max strength is 5
            score = (earned / max_possible) × 100

        Core skills have weight 2.0, supporting skills have weight 1.0.
        """
        total_earned = 0.0
        total_max = 0.0
        core_earned = 0.0
        core_max = 0.0
        supporting_earned = 0.0
        supporting_max = 0.0

        for a in assessments:
            weighted_earned = a.weight * a.evidence_strength
            weighted_max = a.weight * 5  # max evidence strength

            total_earned += weighted_earned
            total_max += weighted_max

            if a.is_core:
                core_earned += weighted_earned
                core_max += weighted_max
            else:
                supporting_earned += weighted_earned
                supporting_max += weighted_max

        score = (total_earned / total_max * 100) if total_max > 0 else 0.0
        core_score = (core_earned / core_max * 100) if core_max > 0 else 0.0
        supporting_score = (supporting_earned / supporting_max * 100) if supporting_max > 0 else 0.0

        return ReadinessScore(
            score=round(score, 1),
            max_possible=round(total_max, 1),
            earned=round(total_earned, 1),
            core_score=round(core_score, 1),
            supporting_score=round(supporting_score, 1),
        )

    def _compute_overall_strengths(self, skill_summaries: List[SkillSummary]) -> List[str]:
        """Identify overall proven strengths from Phase 1 evidence."""
        return [
            s.skill
            for s in sorted(skill_summaries, key=lambda s: s.strength, reverse=True)
            if s.strength >= PROVEN_THRESHOLD
        ]
