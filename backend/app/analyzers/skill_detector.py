"""Skill Detection Engine for ProofPath."""

import os
import json
import logging
from typing import List, Dict, Any, Optional, Set

from app.models.evidence import (
    CodeSignal,
    EvidenceItem,
    SkillSummary,
    EvidenceStatus,
    EvidenceType,
)

logger = logging.getLogger(__name__)


class SkillDetector:
    """Evaluates collected code signals against the data-driven skill taxonomy."""

    def __init__(self, skills_json_path: Optional[str] = None):
        from app.utils.paths import get_data_file_path

        self.skills_json_path = skills_json_path or get_data_file_path("skills.json")
        self.taxonomy = self._load_taxonomy()

    def _load_taxonomy(self) -> List[Dict[str, Any]]:
        """Load skills from skills.json data file."""
        if not os.path.exists(self.skills_json_path):
            logger.error(f"Taxonomy file not found at {self.skills_json_path}")
            return []

        try:
            with open(self.skills_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("skills", [])
        except Exception as e:
            logger.error(f"Error loading taxonomy: {e}")
            return []

    def detect_skills(
        self,
        signals: List[CodeSignal],
        all_file_paths: Optional[List[str]] = None,
    ) -> List[SkillSummary]:
        """
        Evaluate all signals and return SkillSummary for every skill in taxonomy.
        Traceable, deterministic, and deduplicated.
        """
        all_file_paths = all_file_paths or []
        has_tests = any("test" in p.lower() for p in all_file_paths)
        has_docker = any("docker" in p.lower() for p in all_file_paths)
        has_ci = any(".github" in p.lower() or "workflow" in p.lower() for p in all_file_paths)

        skill_summaries: List[SkillSummary] = []

        # Index signals by technology and signal name
        for skill_def in self.taxonomy:
            skill_name = skill_def.get("name", "")
            category = skill_def.get("category", "General")
            declared_signals = set(skill_def.get("signals", []))
            declared_deps = set(d.lower() for d in skill_def.get("dependencies", []))
            parent_skills = set(skill_def.get("parent_skills", []))

            # Match signals belonging to this skill
            matched_signals: List[CodeSignal] = []
            for s in signals:
                # Direct technology match
                if s.technology.lower() == skill_name.lower():
                    matched_signals.append(s)
                # Direct signal name match
                elif s.name in declared_signals or any(sig.lower() in s.name.lower() for sig in declared_signals):
                    matched_signals.append(s)
                # Dependency match
                elif s.type.startswith("dependency") and s.name.lower() in declared_deps:
                    matched_signals.append(s)

            # Build evidence items
            evidence_items = self._synthesize_evidence(
                skill_name=skill_name,
                matched_signals=matched_signals,
                has_tests=has_tests,
                has_docker=has_docker,
                has_ci=has_ci,
            )

            # Determine overall strength
            if evidence_items:
                max_strength = max(item.strength for item in evidence_items)
            else:
                max_strength = 0

            # Determine status according to ProofPath rules:
            # Strength 4-5: proven
            # Strength 2-3: partial
            # Strength 0-1: missing
            if max_strength >= 4:
                status = EvidenceStatus.PROVEN
            elif max_strength >= 2:
                status = EvidenceStatus.PARTIAL
            else:
                status = EvidenceStatus.MISSING

            summary = SkillSummary(
                skill=skill_name,
                category=category,
                status=status,
                strength=max_strength,
                evidence=evidence_items,
            )
            skill_summaries.append(summary)

        # Propagate child skill evidence to parent skills if parent skill has lower evidence
        self._propagate_parent_evidence(skill_summaries)

        return skill_summaries

    def _synthesize_evidence(
        self,
        skill_name: str,
        matched_signals: List[CodeSignal],
        has_tests: bool,
        has_docker: bool,
        has_ci: bool,
    ) -> List[EvidenceItem]:
        """Group matched signals by file/repository and build representative EvidenceItems."""
        if not matched_signals:
            return []

        # Group signals by (repository, file)
        grouped: Dict[tuple, List[CodeSignal]] = {}
        for sig in matched_signals:
            key = (sig.repository or "unknown", sig.file or "unknown")
            grouped.setdefault(key, []).append(sig)

        evidence_items: List[EvidenceItem] = []

        for (repo, file_path), sig_list in grouped.items():
            # Classify signal types in this file
            has_mention_only = all(s.type == "readme_mention" for s in sig_list)
            has_dep_only = all(s.type.startswith("dependency") for s in sig_list)
            code_signals = [s for s in sig_list if not s.type.startswith("dependency") and s.type != "readme_mention"]

            # Distinct signal names for traceability
            distinct_names = list(dict.fromkeys(s.name for s in sig_list))

            # Calculate line range
            line_starts = [s.line_start for s in sig_list if s.line_start is not None]
            line_ends = [s.line_end for s in sig_list if s.line_end is not None]
            line_start = min(line_starts) if line_starts else None
            line_end = max(line_ends) if line_ends else None

            # Case 1: README Mention
            if has_mention_only:
                evidence_items.append(
                    EvidenceItem(
                        skill=skill_name,
                        status=EvidenceStatus.MISSING,
                        repository=repo,
                        file=file_path,
                        line_start=line_start,
                        line_end=line_end,
                        signals=distinct_names,
                        evidence_type=EvidenceType.MENTIONED,
                        strength=1,
                        explanation=f"{skill_name} is mentioned in documentation ({file_path}), but no implementation was found.",
                    )
                )
                continue

            # Case 2: Dependency manifest only
            if has_dep_only or not code_signals:
                evidence_items.append(
                    EvidenceItem(
                        skill=skill_name,
                        status=EvidenceStatus.PARTIAL,
                        repository=repo,
                        file=file_path,
                        line_start=line_start,
                        line_end=line_end,
                        signals=distinct_names,
                        evidence_type=EvidenceType.DEPENDENCY,
                        strength=2,
                        explanation=f"{skill_name} is declared as a project dependency in {file_path}.",
                    )
                )
                continue

            # Case 3: Code implementation
            # Determine depth of implementation
            patterns = [s.name for s in code_signals if s.type in {"pattern", "class_inheritance", "route", "component"}]
            calls = [s.name for s in code_signals if s.type in {"call", "instantiation"}]
            imports = [s.name for s in code_signals if s.type in {"import", "import_from"}]

            # Applied implementation (Level 4): training loop, route handlers, class inheritance, multiple calls
            is_applied = (
                len(patterns) > 0
                or len(calls) >= 2
                or (len(imports) >= 1 and len(calls) >= 1)
                or (skill_name in {"Python", "JavaScript", "TypeScript"} and len(code_signals) >= 3)
                or (skill_name == "Docker" and any("FROM" in s.name for s in code_signals))
                or (skill_name == "SQL" and any("SQL_" in s.name for s in code_signals))
            )

            # Production (Level 5): Applied + project tests / CI / Docker
            is_production = is_applied and (has_tests and (has_docker or has_ci))

            if is_production:
                evidence_type = EvidenceType.PRODUCTION
                strength = 5
                status = EvidenceStatus.PROVEN
                explanation = (
                    f"{skill_name} is implemented with production indicators (testing and containerization/CI) "
                    f"in {file_path} using {', '.join(distinct_names[:5])}."
                )
            elif is_applied:
                evidence_type = EvidenceType.APPLIED
                strength = 4
                status = EvidenceStatus.PROVEN
                explanation = (
                    f"{skill_name} is applied meaningfully in {file_path} "
                    f"via {', '.join(distinct_names[:5])}."
                )
            else:
                evidence_type = EvidenceType.IMPLEMENTATION
                strength = 3
                status = EvidenceStatus.PARTIAL
                explanation = (
                    f"{skill_name} implementation signals detected in {file_path} "
                    f"({', '.join(distinct_names[:4])})."
                )

            evidence_items.append(
                EvidenceItem(
                    skill=skill_name,
                    status=status,
                    repository=repo,
                    file=file_path,
                    line_start=line_start,
                    line_end=line_end,
                    signals=distinct_names[:8],  # limit per file to avoid bloat
                    evidence_type=evidence_type,
                    strength=strength,
                    explanation=explanation,
                )
            )

        # Sort evidence items descending by strength
        evidence_items.sort(key=lambda item: item.strength, reverse=True)
        # Limit to top 5 most representative evidence items per skill
        return evidence_items[:5]

    def _propagate_parent_evidence(self, summaries: List[SkillSummary]):
        """Ensure parent skills (e.g. Machine Learning, Deep Learning, REST API) reflect strong child evidence."""
        skill_map = {s.skill: s for s in summaries}

        # Parent mappings based on proven child technologies
        parent_rules = {
            "PyTorch": ["Python", "Deep Learning", "Machine Learning"],
            "TensorFlow": ["Python", "Deep Learning", "Machine Learning"],
            "Scikit-learn": ["Python", "Machine Learning", "Data Analysis"],
            "Pandas": ["Python", "Data Analysis"],
            "NumPy": ["Python", "Data Analysis"],
            "FastAPI": ["Python", "REST API"],
            "Flask": ["Python", "REST API"],
            "Django": ["Python", "REST API"],
            "React": ["JavaScript"],
            "TypeScript": ["JavaScript"],
            "OpenCV": ["Python", "Machine Learning"],
            "Transformers": ["Python", "Deep Learning", "Machine Learning"],
        }

        for child_name, parents in parent_rules.items():
            child = skill_map.get(child_name)
            if not child or child.strength < 3:
                continue

            for parent_name in parents:
                parent = skill_map.get(parent_name)
                if not parent:
                    continue

                # If parent has weaker strength than child, elevate parent to child strength
                # with representative evidence from child
                if child.strength > parent.strength:
                    parent.strength = child.strength
                    parent.status = child.status
                    if child.evidence and not any(e.file == child.evidence[0].file for e in parent.evidence):
                        # Inherit top evidence reference
                        top_child_ev = child.evidence[0]
                        parent.evidence.insert(
                            0,
                            EvidenceItem(
                                skill=parent_name,
                                status=child.status,
                                repository=top_child_ev.repository,
                                file=top_child_ev.file,
                                line_start=top_child_ev.line_start,
                                line_end=top_child_ev.line_end,
                                signals=top_child_ev.signals,
                                evidence_type=top_child_ev.evidence_type,
                                strength=child.strength,
                                explanation=f"{parent_name} demonstrated through applied {child_name} in {top_child_ev.file}.",
                            ),
                        )
