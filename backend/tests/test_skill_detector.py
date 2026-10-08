"""Unit tests for SkillDetector, evidence levels, and traceability."""

import pytest
from app.models.evidence import CodeSignal, EvidenceStatus, EvidenceType
from app.analyzers.skill_detector import SkillDetector


def test_taxonomy_loaded():
    detector = SkillDetector()
    assert len(detector.taxonomy) >= 20
    skill_names = [s["name"] for s in detector.taxonomy]
    assert "Python" in skill_names
    assert "PyTorch" in skill_names
    assert "FastAPI" in skill_names
    assert "React" in skill_names
    assert "TypeScript" in skill_names
    assert "SQL" in skill_names
    assert "Docker" in skill_names


def test_readme_mention_produces_level_1_missing():
    detector = SkillDetector()
    signals = [
        CodeSignal(
            type="readme_mention",
            name="mentioned_PyTorch",
            technology="PyTorch",
            repository="sample-repo",
            file="README.md",
            line_start=12,
            line_end=12,
        )
    ]

    summaries = detector.detect_skills(signals)
    pytorch_summary = next(s for s in summaries if s.skill == "PyTorch")

    assert pytorch_summary.strength == 1
    assert pytorch_summary.status == EvidenceStatus.MISSING
    assert len(pytorch_summary.evidence) == 1
    assert pytorch_summary.evidence[0].evidence_type == EvidenceType.MENTIONED
    assert pytorch_summary.evidence[0].file == "README.md"
    assert pytorch_summary.evidence[0].line_start == 12


def test_dependency_only_produces_level_2_partial():
    detector = SkillDetector()
    signals = [
        CodeSignal(
            type="dependency",
            name="torch",
            technology="PyTorch",
            repository="ml-repo",
            file="requirements.txt",
            line_start=3,
            line_end=3,
        )
    ]

    summaries = detector.detect_skills(signals)
    pytorch_summary = next(s for s in summaries if s.skill == "PyTorch")

    assert pytorch_summary.strength == 2
    assert pytorch_summary.status == EvidenceStatus.PARTIAL
    assert len(pytorch_summary.evidence) == 1
    assert pytorch_summary.evidence[0].evidence_type == EvidenceType.DEPENDENCY
    assert pytorch_summary.evidence[0].file == "requirements.txt"


def test_pytorch_applied_produces_level_4_proven():
    detector = SkillDetector()
    signals = [
        CodeSignal(type="import", name="torch", technology="PyTorch", repository="classifier", file="train.py", line_start=1, line_end=1),
        CodeSignal(type="import_from", name="torch.nn", technology="PyTorch", repository="classifier", file="train.py", line_start=2, line_end=2),
        CodeSignal(type="class_inheritance", name="torch.nn.Module", technology="PyTorch", repository="classifier", file="train.py", line_start=5, line_end=15),
        CodeSignal(type="call", name="DataLoader", technology="PyTorch", repository="classifier", file="train.py", line_start=20, line_end=20),
        CodeSignal(type="call", name="torch.optim.Adam", technology="PyTorch", repository="classifier", file="train.py", line_start=25, line_end=25),
        CodeSignal(type="call", name="loss.backward", technology="PyTorch", repository="classifier", file="train.py", line_start=30, line_end=30),
        CodeSignal(type="call", name="optimizer.step", technology="PyTorch", repository="classifier", file="train.py", line_start=31, line_end=31),
    ]

    summaries = detector.detect_skills(signals, all_file_paths=["train.py"])
    pytorch_summary = next(s for s in summaries if s.skill == "PyTorch")

    assert pytorch_summary.strength >= 4
    assert pytorch_summary.status == EvidenceStatus.PROVEN
    assert len(pytorch_summary.evidence) >= 1

    ev = pytorch_summary.evidence[0]
    assert ev.evidence_type == EvidenceType.APPLIED
    assert ev.repository == "classifier"
    assert ev.file == "train.py"
    assert ev.line_start == 1
    assert ev.line_end == 31
    assert "torch.nn.Module" in ev.signals
    assert "DataLoader" in ev.signals


def test_production_level_5_with_tests_and_docker():
    detector = SkillDetector()
    signals = [
        CodeSignal(type="import", name="FastAPI", technology="FastAPI", repository="api-prod", file="app/main.py", line_start=1, line_end=1),
        CodeSignal(type="route", name="fastapi_route_decorator", technology="FastAPI", repository="api-prod", file="app/main.py", line_start=10, line_end=15),
        CodeSignal(type="route", name="fastapi_route_decorator", technology="FastAPI", repository="api-prod", file="app/main.py", line_start=20, line_end=25),
    ]

    # File paths include tests and Dockerfile
    paths = ["app/main.py", "tests/test_api.py", "Dockerfile"]
    summaries = detector.detect_skills(signals, all_file_paths=paths)
    fastapi_summary = next(s for s in summaries if s.skill == "FastAPI")

    assert fastapi_summary.strength == 5
    assert fastapi_summary.status == EvidenceStatus.PROVEN
    assert fastapi_summary.evidence[0].evidence_type == EvidenceType.PRODUCTION


def test_no_evidence_no_claim():
    detector = SkillDetector()
    # Empty signals list
    summaries = detector.detect_skills([])

    for s in summaries:
        assert s.strength == 0
        assert s.status == EvidenceStatus.MISSING
        assert len(s.evidence) == 0
