"""Unit tests for DependencyAnalyzer parsing manifests."""

import pytest
import json
from app.analyzers.dependency_analyzer import DependencyAnalyzer


def test_requirements_txt_parsing():
    analyzer = DependencyAnalyzer()
    content = """# Machine Learning Dependencies
torch>=2.1.0
pandas==2.2.0
numpy>=1.26.0
scikit-learn
fastapi[all]>=0.110.0
# Comments and invalid lines
-r other.txt
"""
    result = analyzer.analyze("requirements.txt", content, repository="ml-service")

    assert result.error is None
    signal_techs = {s.technology for s in result.signals}

    assert "PyTorch" in signal_techs
    assert "Pandas" in signal_techs
    assert "NumPy" in signal_techs
    assert "Scikit-learn" in signal_techs
    assert "FastAPI" in signal_techs

    # Verify every signal is marked as dependency type
    for s in result.signals:
        assert s.type == "dependency"
        assert s.line_start is not None


def test_package_json_parsing():
    analyzer = DependencyAnalyzer()
    pkg_data = {
        "name": "react-frontend",
        "dependencies": {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "express": "^4.18.2"
        },
        "devDependencies": {
            "typescript": "^5.3.3",
            "@types/react": "^18.2.48"
        }
    }
    content = json.dumps(pkg_data)

    result = analyzer.analyze("package.json", content, repository="web-app")

    assert result.error is None
    signal_techs = {s.technology for s in result.signals}

    assert "React" in signal_techs
    assert "TypeScript" in signal_techs
    assert "Express" in signal_techs
    assert "Node.js" in signal_techs


def test_dockerfile_parsing():
    analyzer = DependencyAnalyzer()
    content = """FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "main.py"]
"""
    result = analyzer.analyze("Dockerfile", content, repository="dockerized-app")

    assert result.error is None
    docker_signals = [s for s in result.signals if s.technology == "Docker"]
    assert len(docker_signals) >= 2
    names = [s.name for s in docker_signals]
    assert "docker_instruction_FROM" in names
    assert "docker_instruction_CMD" in names


def test_pyproject_toml_parsing():
    analyzer = DependencyAnalyzer()
    content = """[project]
name = "backend-api"
dependencies = [
    "fastapi>=0.100.0",
    "uvicorn",
    "sqlalchemy",
]
"""
    result = analyzer.analyze("pyproject.toml", content, repository="python-api")
    signal_techs = {s.technology for s in result.signals}

    assert "FastAPI" in signal_techs
    assert "SQL" in signal_techs
