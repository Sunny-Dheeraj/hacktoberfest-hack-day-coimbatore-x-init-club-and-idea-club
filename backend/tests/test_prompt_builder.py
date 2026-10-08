"""Tests for Phase 2 Evidence-Grounded Prompt Construction."""

from app.ai.prompt_builder import build_role_assessment_prompt, SYSTEM_INSTRUCTION
from app.models.career import CareerRole, RoleSkillRequirement, ReadinessScore, SkillAssessment, SkillClassification
from app.models.evidence import EvidenceItem, EvidenceStatus, EvidenceType


def test_prompt_builder_contains_critical_grounding():
    """Verify prompt builder embeds core grounding rules and candidate data."""
    role = CareerRole(
        id="backend_engineer",
        title="Backend Engineer",
        description="Builds APIs and databases",
        core_skills=[RoleSkillRequirement(skill="Python", weight=2.0, is_core=True)],
        supporting_skills=[RoleSkillRequirement(skill="Docker", weight=1.0, is_core=False)],
    )

    readiness = ReadinessScore(
        score=75.0,
        max_possible=15.0,
        earned=11.25,
        core_score=80.0,
        supporting_score=70.0,
    )

    assessments = [
        SkillAssessment(
            skill="Python",
            classification=SkillClassification.PROVEN,
            is_core=True,
            weight=2.0,
            evidence_strength=4,
            evidence_count=1,
            top_evidence=[
                EvidenceItem(
                    skill="Python",
                    status=EvidenceStatus.PROVEN,
                    repository="api-server",
                    file="main.py",
                    evidence_type=EvidenceType.APPLIED,
                    strength=4,
                    signals=["FastAPI", "def", "async_def"],
                    explanation="Applied FastAPI route handlers",
                )
            ],
        )
    ]

    prompt = build_role_assessment_prompt(
        username="dev_alice",
        role=role,
        readiness=readiness,
        assessments=assessments,
        proven_skills=["Python"],
        partial_skills=[],
        missing_skills=["Docker"],
    )

    # Assert critical grounding rules are present
    assert "NO EVIDENCE -> NO CLAIM" in prompt
    assert "dev_alice" in prompt
    assert "Backend Engineer" in prompt
    assert "75.0%" in prompt
    assert "api-server" in prompt
    assert "main.py" in prompt
    assert "FastAPI" in prompt
    assert "required_output_schema" in prompt
