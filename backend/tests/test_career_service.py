"""Tests for Phase 2 Career Service and Deterministic Readiness Scoring."""

import pytest
from app.services.career_service import CareerService, PROVEN_THRESHOLD, PARTIAL_THRESHOLD
from app.models.evidence import SkillSummary, EvidenceStatus, EvidenceItem, EvidenceType
from app.models.career import SkillClassification, RoleSkillRequirement, CareerRole


@pytest.fixture
def career_service():
    return CareerService()


def test_roles_loaded(career_service):
    """Verify career roles are loaded from data/roles.json."""
    roles = career_service.get_all_roles()
    assert len(roles) >= 3
    role_ids = [r.id for r in roles]
    assert "ml_engineer" in role_ids
    assert "full_stack_developer" in role_ids
    assert "data_scientist" in role_ids


def test_role_skill_weights(career_service):
    """Verify core skills have weight 2.0 and supporting skills have weight 1.0."""
    ml_role = career_service.get_role_by_id("ml_engineer")
    assert ml_role is not None
    assert len(ml_role.core_skills) > 0
    assert len(ml_role.supporting_skills) > 0

    for core in ml_role.core_skills:
        assert core.weight == 2.0
        assert core.is_core is True

    for sup in ml_role.supporting_skills:
        assert sup.weight == 1.0
        assert sup.is_core is False


def test_skill_classification(career_service):
    """Verify deterministic classification policy: >=3 Proven, ==2 Partial, <=1 Missing."""
    skill_map = {
        "Python": SkillSummary(
            skill="Python",
            category="Programming Languages",
            status=EvidenceStatus.PROVEN,
            strength=4,
            evidence=[
                EvidenceItem(
                    skill="Python",
                    status=EvidenceStatus.PROVEN,
                    repository="repo1",
                    file="main.py",
                    evidence_type=EvidenceType.APPLIED,
                    strength=4,
                    explanation="Applied Python code",
                )
            ],
        ),
        "Docker": SkillSummary(
            skill="Docker",
            category="DevOps",
            status=EvidenceStatus.PARTIAL,
            strength=2,
            evidence=[],
        ),
        "PyTorch": SkillSummary(
            skill="PyTorch",
            category="Machine Learning",
            status=EvidenceStatus.MISSING,
            strength=1,
            evidence=[],
        ),
    }

    req_proven = RoleSkillRequirement(skill="Python", weight=2.0, is_core=True)
    req_partial = RoleSkillRequirement(skill="Docker", weight=1.0, is_core=False)
    req_missing_strength1 = RoleSkillRequirement(skill="PyTorch", weight=2.0, is_core=True)
    req_missing_not_found = RoleSkillRequirement(skill="SQL", weight=1.0, is_core=False)

    assessment_proven = career_service._assess_skill(req_proven, skill_map)
    assert assessment_proven.classification == SkillClassification.PROVEN
    assert assessment_proven.evidence_strength == 4

    assessment_partial = career_service._assess_skill(req_partial, skill_map)
    assert assessment_partial.classification == SkillClassification.PARTIAL
    assert assessment_partial.evidence_strength == 2

    assessment_missing1 = career_service._assess_skill(req_missing_strength1, skill_map)
    assert assessment_missing1.classification == SkillClassification.MISSING

    assessment_missing2 = career_service._assess_skill(req_missing_not_found, skill_map)
    assert assessment_missing2.classification == SkillClassification.MISSING
    assert assessment_missing2.evidence_strength == 0


def test_readiness_score_calculation(career_service):
    """Test deterministic weighted readiness scoring math."""
    # 2 core skills (weight 2.0) and 1 supporting (weight 1.0)
    # Total max = 2.0*5 + 2.0*5 + 1.0*5 = 10 + 10 + 5 = 25
    # Skill 1 (core): strength 4 -> earned = 2.0*4 = 8
    # Skill 2 (core): strength 2 -> earned = 2.0*2 = 4
    # Skill 3 (sup): strength 5 -> earned = 1.0*5 = 5
    # Total earned = 8 + 4 + 5 = 17
    # Total score = 17 / 25 * 100 = 68.0%
    # Core score = (8 + 4) / (10 + 10) * 100 = 12 / 20 * 100 = 60.0%
    # Supporting score = 5 / 5 * 100 = 100.0%

    assessments = [
        career_service._assess_skill(
            RoleSkillRequirement(skill="Python", weight=2.0, is_core=True),
            {"Python": SkillSummary(skill="Python", category="Lang", status=EvidenceStatus.PROVEN, strength=4)},
        ),
        career_service._assess_skill(
            RoleSkillRequirement(skill="SQL", weight=2.0, is_core=True),
            {"SQL": SkillSummary(skill="SQL", category="DB", status=EvidenceStatus.PARTIAL, strength=2)},
        ),
        career_service._assess_skill(
            RoleSkillRequirement(skill="Docker", weight=1.0, is_core=False),
            {"Docker": SkillSummary(skill="Docker", category="DevOps", status=EvidenceStatus.PROVEN, strength=5)},
        ),
    ]

    readiness = career_service._calculate_readiness(assessments)
    assert readiness.score == 68.0
    assert readiness.core_score == 60.0
    assert readiness.supporting_score == 100.0
    assert readiness.max_possible == 25.0
    assert readiness.earned == 17.0


def test_analyze_career_end_to_end(career_service):
    """Test analyze_career with a populated list of skills."""
    skills = [
        SkillSummary(skill="Python", category="Lang", status=EvidenceStatus.PROVEN, strength=5),
        SkillSummary(skill="Pandas", category="DS", status=EvidenceStatus.PROVEN, strength=4),
        SkillSummary(skill="NumPy", category="DS", status=EvidenceStatus.PROVEN, strength=4),
        SkillSummary(skill="Data Analysis", category="DS", status=EvidenceStatus.PROVEN, strength=4),
        SkillSummary(skill="SQL", category="DB", status=EvidenceStatus.PROVEN, strength=3),
    ]

    result = career_service.analyze_career(
        username="testuser",
        skill_summaries=skills,
    )

    assert result.username == "testuser"
    assert len(result.roles_analyzed) >= 3
    assert result.primary_role is not None
    # Data scientist or ML should rank very high with these skills
    assert result.primary_role in ["data_scientist", "ml_engineer"]
    assert "Python" in result.overall_strengths


def test_filter_by_role_ids(career_service):
    """Test analyzing only a specific subset of roles."""
    skills = [
        SkillSummary(skill="JavaScript", category="Lang", status=EvidenceStatus.PROVEN, strength=4),
        SkillSummary(skill="React", category="Frontend", status=EvidenceStatus.PROVEN, strength=4),
    ]

    result = career_service.analyze_career(
        username="webdev",
        skill_summaries=skills,
        role_ids=["full_stack_developer"],
    )

    assert len(result.roles_analyzed) == 1
    assert result.roles_analyzed[0].role.id == "full_stack_developer"
