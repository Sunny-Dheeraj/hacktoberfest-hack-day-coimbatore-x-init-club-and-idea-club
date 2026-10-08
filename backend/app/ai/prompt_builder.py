"""Evidence-grounded Prompt Construction for Gemma 4."""

import json
from typing import List, Dict, Any, Optional

from app.models.career import CareerRole, RoleAnalysis, ReadinessScore, SkillAssessment


SYSTEM_INSTRUCTION = """You are ProofPath's Career Intelligence Engine powered by Gemma 4.
Your core principle is: NO EVIDENCE -> NO CLAIM. Code proves; AI interprets.

Rules you MUST strictly follow:
1. You are an interpreter of verified technical evidence, NOT an evidence generator.
2. Rely EXCLUSIVELY on the verified code evidence, signals, and deterministic scores provided in the prompt.
3. NEVER invent, hallucinate, or assume technologies, projects, or experience not present in the evidence.
4. You CANNOT override or alter deterministic readiness scores or skill classifications (Proven/Partial/Missing).
5. Ground every observation in the specific repositories, files, and signals cited in the evidence.
6. For missing or partial skills, highlight the gap clearly and provide actionable, practical next steps.
7. Return your response ONLY as valid, raw JSON conforming exactly to the requested schema. No conversational filler, no markdown wrappers, no backticks.
"""


def build_role_assessment_prompt(
    username: str,
    role: CareerRole,
    readiness: ReadinessScore,
    assessments: List[SkillAssessment],
    proven_skills: List[str],
    partial_skills: List[str],
    missing_skills: List[str],
) -> str:
    """
    Construct a dense, evidence-grounded prompt for Gemma 4 to interpret
    a developer's readiness for a specific career role.
    """
    # Compact evidence summary for each assessed skill
    evidence_payload = []
    for a in assessments:
        item = {
            "skill": a.skill,
            "type": "Core" if a.is_core else "Supporting",
            "classification": a.classification.value,
            "evidence_strength": f"{a.evidence_strength}/5",
            "evidence_traces": [
                {
                    "repo": ev.repository,
                    "file": ev.file,
                    "signals": ev.signals[:4] if ev.signals else [],
                    "finding": ev.explanation,
                }
                for ev in a.top_evidence[:2]
            ]
            if a.top_evidence
            else [],
        }
        evidence_payload.append(item)

    prompt_data = {
        "candidate": username,
        "target_role": {
            "id": role.id,
            "title": role.title,
            "description": role.description,
        },
        "deterministic_metrics": {
            "overall_readiness_score": f"{readiness.score}%",
            "core_skills_score": f"{readiness.core_score}%",
            "supporting_skills_score": f"{readiness.supporting_score}%",
            "proven_count": len(proven_skills),
            "partial_count": len(partial_skills),
            "missing_count": len(missing_skills),
        },
        "skill_breakdown": {
            "proven": proven_skills,
            "partial": partial_skills,
            "missing": missing_skills,
        },
        "verified_evidence": evidence_payload,
        "required_output_schema": {
            "summary": "Concise 2-3 sentence assessment of candidate's evidence-backed readiness for this role.",
            "strengths": [
                "Specific strength grounded in verified code signals and repositories."
            ],
            "gaps": [
                "Specific skill gap or partial implementation identified from missing/partial classifications."
            ],
            "recommendations": [
                "Actionable, concrete engineering project or practice to bridge identified gaps."
            ],
            "confidence": 0.95,
        },
    }

    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"Input Data:\n{json.dumps(prompt_data, indent=2)}\n\n"
        f"Generate the JSON assessment according to required_output_schema:"
    )
