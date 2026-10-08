"""Framework & Domain Pattern Analyzer for ProofPath."""

import os
import re
import logging
from typing import List, Optional

from app.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from app.models.evidence import CodeSignal

logger = logging.getLogger(__name__)

# SQL statement patterns
SQL_KEYWORDS_PATTERN = re.compile(
    r"\b(SELECT\s+.*?\s+FROM|INSERT\s+INTO|UPDATE\s+\w+\s+SET|DELETE\s+FROM|CREATE\s+TABLE|ALTER\s+TABLE|DROP\s+TABLE|JOIN\s+\w+)\b",
    re.IGNORECASE
)

# Mention patterns in README
TECH_MENTION_PATTERNS = {
    "PyTorch": re.compile(r"\b(pytorch|torch)\b", re.IGNORECASE),
    "TensorFlow": re.compile(r"\b(tensorflow|tf|keras)\b", re.IGNORECASE),
    "React": re.compile(r"\b(react|react\.js|reactjs)\b", re.IGNORECASE),
    "FastAPI": re.compile(r"\b(fastapi)\b", re.IGNORECASE),
    "Flask": re.compile(r"\b(flask)\b", re.IGNORECASE),
    "Django": re.compile(r"\b(django)\b", re.IGNORECASE),
    "Docker": re.compile(r"\b(docker|docker-compose)\b", re.IGNORECASE),
    "TypeScript": re.compile(r"\b(typescript)\b", re.IGNORECASE),
    "Scikit-learn": re.compile(r"\b(scikit-learn|sklearn)\b", re.IGNORECASE),
    "Pandas": re.compile(r"\b(pandas)\b", re.IGNORECASE),
    "NumPy": re.compile(r"\b(numpy)\b", re.IGNORECASE),
    "OpenCV": re.compile(r"\b(opencv|cv2)\b", re.IGNORECASE),
    "Transformers": re.compile(r"\b(transformers|huggingface)\b", re.IGNORECASE),
}


class FrameworkAnalyzer(BaseAnalyzer):
    """Detects framework workflows, SQL scripts, and README declared mentions."""

    def can_analyze(self, file_path: str) -> bool:
        lower = file_path.lower()
        filename = os.path.basename(lower)
        return lower.endswith(".sql") or filename.startswith("readme")

    def analyze(self, file_path: str, content: str, repository: Optional[str] = None) -> AnalysisResult:
        lower = file_path.lower()
        filename = os.path.basename(lower)

        if lower.endswith(".sql"):
            return self._analyze_sql(file_path, content, repository)
        elif filename.startswith("readme"):
            return self._analyze_readme(file_path, content, repository)

        return AnalysisResult(file=file_path, language="unknown")

    def _analyze_sql(self, file_path: str, content: str, repository: Optional[str]) -> AnalysisResult:
        result = AnalysisResult(file=file_path, language="sql")
        signals: List[CodeSignal] = []

        lines = content.splitlines()
        for line_no, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith("--") or line_str.startswith("/*"):
                continue

            match = SQL_KEYWORDS_PATTERN.search(line_str)
            if match:
                keyword = match.group(1).split()[0].upper()
                signals.append(
                    CodeSignal(
                        type="sql_statement",
                        name=f"SQL_{keyword}",
                        technology="SQL",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                        details={"statement": match.group(0)},
                    )
                )

        if signals:
            signals.insert(
                0,
                CodeSignal(
                    type="source_file",
                    name="sql_file",
                    technology="SQL",
                    repository=repository,
                    file=file_path,
                    line_start=1,
                    line_end=len(lines) if lines else 1,
                )
            )

        result.signals = signals
        return result

    def _analyze_readme(self, file_path: str, content: str, repository: Optional[str]) -> AnalysisResult:
        result = AnalysisResult(file=file_path, language="markdown")
        signals: List[CodeSignal] = []
        lines = content.splitlines()

        for tech, pattern in TECH_MENTION_PATTERNS.items():
            for line_no, line in enumerate(lines, start=1):
                if pattern.search(line):
                    signals.append(
                        CodeSignal(
                            type="readme_mention",
                            name=f"mentioned_{tech}",
                            technology=tech,
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                            details={"text": line.strip()[:100]},
                        )
                    )
                    # One mention per tech in README is sufficient
                    break

        result.signals = signals
        return result
