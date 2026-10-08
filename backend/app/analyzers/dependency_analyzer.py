"""Dependency and Manifest Analyzer for ProofPath."""

import os
import re
import json
import logging
from typing import List, Optional, Dict, Set

from app.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from app.models.evidence import CodeSignal

logger = logging.getLogger(__name__)

# Map package name (lowercase) to canonical technology name
PACKAGE_TECH_MAP: Dict[str, str] = {
    # Python Data / ML
    "torch": "PyTorch",
    "torchvision": "PyTorch",
    "torchaudio": "PyTorch",
    "pytorch-lightning": "PyTorch",
    "tensorflow": "TensorFlow",
    "tensorflow-gpu": "TensorFlow",
    "keras": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "numpy": "NumPy",
    "opencv-python": "OpenCV",
    "opencv-python-headless": "OpenCV",
    "transformers": "Transformers",
    "datasets": "Transformers",
    "xgboost": "Machine Learning",
    "lightgbm": "Machine Learning",
    # Python Web & API
    "fastapi": "FastAPI",
    "uvicorn": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "djangorestframework": "Django",
    # Databases / SQL
    "sqlalchemy": "SQL",
    "psycopg2": "SQL",
    "psycopg2-binary": "SQL",
    "asyncpg": "SQL",
    "pymysql": "SQL",
    "mysqlclient": "SQL",
    "pg": "SQL",
    "mysql2": "SQL",
    "prisma": "SQL",
    "typeorm": "SQL",
    # JS / TS / Web
    "react": "React",
    "react-dom": "React",
    "@types/react": "React",
    "next": "React",
    "typescript": "TypeScript",
    "ts-node": "TypeScript",
    "express": "Express",
    "@types/node": "Node.js",
    "axios": "REST API",
}


class DependencyAnalyzer(BaseAnalyzer):
    """Analyzes package manifests to extract declared library dependencies."""

    TARGET_FILES = {
        "requirements.txt",
        "pyproject.toml",
        "pipfile",
        "package.json",
        "package-lock.json",
        "yarn.lock",
        "pnpm-lock.yaml",
        "dockerfile",
        "docker-compose.yml",
        "docker-compose.yaml",
    }

    def can_analyze(self, file_path: str) -> bool:
        filename = os.path.basename(file_path).lower()
        return filename in self.TARGET_FILES or filename.startswith("requirements")

    def analyze(self, file_path: str, content: str, repository: Optional[str] = None) -> AnalysisResult:
        filename = os.path.basename(file_path).lower()
        result = AnalysisResult(file=file_path, language="manifest")
        signals: List[CodeSignal] = []

        if filename.startswith("requirements") or filename.endswith(".txt"):
            signals.extend(self._parse_requirements_txt(content, file_path, repository))
        elif filename == "package.json":
            signals.extend(self._parse_package_json(content, file_path, repository))
        elif filename == "pyproject.toml":
            signals.extend(self._parse_pyproject_toml(content, file_path, repository))
        elif filename == "pipfile":
            signals.extend(self._parse_pipfile(content, file_path, repository))
        elif filename in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
            signals.extend(self._parse_lockfile(content, file_path, repository, filename))
        elif "docker" in filename:
            signals.extend(self._parse_docker(content, file_path, repository, filename))

        result.signals = signals
        return result

    def _parse_requirements_txt(self, content: str, file_path: str, repository: Optional[str]) -> List[CodeSignal]:
        signals = []
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("-r") or line.startswith("-i"):
                continue

            # Strip version specifiers: ==, >=, <=, ~=, !=, <, >
            clean_pkg = re.split(r"[><=~!@;]", line)[0].strip().lower()
            clean_pkg = re.sub(r"\[.*?\]", "", clean_pkg)  # remove extras like [all]

            tech = PACKAGE_TECH_MAP.get(clean_pkg)
            if tech:
                signals.append(
                    CodeSignal(
                        type="dependency",
                        name=clean_pkg,
                        technology=tech,
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                        details={"raw": line},
                    )
                )
        return signals

    def _parse_package_json(self, content: str, file_path: str, repository: Optional[str]) -> List[CodeSignal]:
        signals = []
        try:
            data = json.loads(content)
        except Exception:
            return signals

        dep_sections = ["dependencies", "devDependencies", "peerDependencies"]
        seen_packages = set()

        for section in dep_sections:
            deps = data.get(section, {})
            if isinstance(deps, dict):
                for pkg in deps.keys():
                    pkg_clean = pkg.lower().strip()
                    if pkg_clean in seen_packages:
                        continue
                    seen_packages.add(pkg_clean)
                    tech = PACKAGE_TECH_MAP.get(pkg_clean)
                    if tech:
                        signals.append(
                            CodeSignal(
                                type="dependency",
                                name=pkg_clean,
                                technology=tech,
                                repository=repository,
                                file=file_path,
                                line_start=1,
                                line_end=1,
                                details={"section": section},
                            )
                        )

        # Baseline Node.js signal from existence of package.json
        signals.append(
            CodeSignal(
                type="dependency_manifest",
                name="package.json",
                technology="Node.js",
                repository=repository,
                file=file_path,
                line_start=1,
                line_end=1,
            )
        )
        return signals

    def _parse_pyproject_toml(self, content: str, file_path: str, repository: Optional[str]) -> List[CodeSignal]:
        signals = []
        # Basic line-by-line parsing to avoid strict toml library variations
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            for pkg, tech in PACKAGE_TECH_MAP.items():
                pattern = rf"""(?:['"]{re.escape(pkg)}['"]|['"]{re.escape(pkg)}[><=~!^@;\s])"""
                if re.search(pattern, line, re.IGNORECASE):
                    signals.append(
                        CodeSignal(
                            type="dependency",
                            name=pkg,
                            technology=tech,
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
        return signals

    def _parse_pipfile(self, content: str, file_path: str, repository: Optional[str]) -> List[CodeSignal]:
        signals = []
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            for pkg, tech in PACKAGE_TECH_MAP.items():
                if line.lower().startswith(pkg):
                    signals.append(
                        CodeSignal(
                            type="dependency",
                            name=pkg,
                            technology=tech,
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
        return signals

    def _parse_lockfile(self, content: str, file_path: str, repository: Optional[str], filename: str) -> List[CodeSignal]:
        signals = []
        for pkg, tech in PACKAGE_TECH_MAP.items():
            if f'"{pkg}"' in content or f"/{pkg}@" in content or f"/{pkg}/" in content:
                signals.append(
                    CodeSignal(
                        type="dependency_locked",
                        name=pkg,
                        technology=tech,
                        repository=repository,
                        file=file_path,
                        line_start=1,
                        line_end=1,
                        details={"lockfile": filename},
                    )
                )
        return signals

    def _parse_docker(self, content: str, file_path: str, repository: Optional[str], filename: str) -> List[CodeSignal]:
        signals = []
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if filename.lower() == "dockerfile" or "dockerfile" in filename.lower():
                if line.upper().startswith("FROM "):
                    signals.append(
                        CodeSignal(
                            type="docker_instruction",
                            name="docker_instruction_FROM",
                            technology="Docker",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                            details={"instruction": line},
                        )
                    )
                elif line.upper().startswith("CMD ") or line.upper().startswith("ENTRYPOINT "):
                    signals.append(
                        CodeSignal(
                            type="docker_instruction",
                            name="docker_instruction_CMD",
                            technology="Docker",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
            elif "docker-compose" in filename.lower():
                if "services:" in line or "image:" in line:
                    signals.append(
                        CodeSignal(
                            type="docker_instruction",
                            name="docker_compose_services",
                            technology="Docker",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
        return signals
