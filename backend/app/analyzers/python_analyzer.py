"""Python AST Source Code Analyzer for ProofPath."""

import ast
import json
import logging
from typing import List, Optional, Set, Dict, Any

from app.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from app.models.evidence import CodeSignal

logger = logging.getLogger(__name__)


# Mapping of module/name roots to canonical technology names
KNOWN_TECH_MODULES = {
    "torch": "PyTorch",
    "torchvision": "PyTorch",
    "torchaudio": "PyTorch",
    "tensorflow": "TensorFlow",
    "keras": "TensorFlow",
    "tf": "TensorFlow",
    "sklearn": "Scikit-learn",
    "pandas": "Pandas",
    "pd": "Pandas",
    "numpy": "NumPy",
    "np": "NumPy",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "cv2": "OpenCV",
    "transformers": "Transformers",
    "sqlalchemy": "SQL",
    "sqlite3": "SQL",
    "psycopg2": "SQL",
}


def get_call_name(node: ast.AST) -> str:
    """Helper to reconstruct dotted call name from an AST call or attribute node."""
    if isinstance(node, ast.Call):
        return get_call_name(node.func)
    elif isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        parent = get_call_name(node.value)
        return f"{parent}.{node.attr}" if parent else node.attr
    return ""


class PythonASTVisitor(ast.NodeVisitor):
    """Visits Python AST nodes to extract structural code signals."""

    def __init__(self, repository: Optional[str] = None, file_path: Optional[str] = None):
        self.repository = repository
        self.file_path = file_path
        self.signals: List[CodeSignal] = []
        self.imported_aliases: Dict[str, str] = {}  # alias -> original module/symbol
        self.has_backward = False
        self.has_optim_step = False

    def _infer_tech(self, name: str) -> str:
        """Infer technology name from symbol or module name."""
        root = name.split(".")[0]
        mapped = self.imported_aliases.get(root, root)
        mapped_root = mapped.split(".")[0]
        return KNOWN_TECH_MODULES.get(mapped_root, KNOWN_TECH_MODULES.get(root, "Python"))

    def visit_Import(self, node: ast.Import):
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", node.lineno)
        for alias in node.names:
            mod_name = alias.name
            as_name = alias.asname or mod_name
            self.imported_aliases[as_name] = mod_name

            tech = self._infer_tech(mod_name)
            self.signals.append(
                CodeSignal(
                    type="import",
                    name=mod_name,
                    technology=tech,
                    repository=self.repository,
                    file=self.file_path,
                    line_start=line_start,
                    line_end=line_end,
                )
            )
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom):
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", node.lineno)
        module = node.module or ""
        tech = self._infer_tech(module)

        for alias in node.names:
            full_name = f"{module}.{alias.name}" if module else alias.name
            as_name = alias.asname or alias.name
            self.imported_aliases[as_name] = full_name

            # If symbol matches known tech pattern
            symbol_tech = tech
            if alias.name in {"DataLoader", "Dataset", "Adam", "SGD", "Module"}:
                symbol_tech = "PyTorch"
            elif alias.name in {"FastAPI", "APIRouter", "Depends", "HTTPException"}:
                symbol_tech = "FastAPI"
            elif alias.name in {"Flask", "render_template", "jsonify"}:
                symbol_tech = "Flask"
            elif alias.name in {"train_test_split", "StandardScaler", "GridSearchCV"}:
                symbol_tech = "Scikit-learn"
            elif alias.name in {"AutoModel", "AutoTokenizer", "Trainer"}:
                symbol_tech = "Transformers"

            self.signals.append(
                CodeSignal(
                    type="import_from",
                    name=full_name,
                    technology=symbol_tech,
                    repository=self.repository,
                    file=self.file_path,
                    line_start=line_start,
                    line_end=line_end,
                )
            )

            # Also emit short symbol name if different from full name
            if alias.name != full_name:
                self.signals.append(
                    CodeSignal(
                        type="imported_symbol",
                        name=alias.name,
                        technology=symbol_tech,
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef):
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", node.lineno)

        # Inspect base classes for inheritance patterns
        bases_names = []
        for base in node.bases:
            base_str = get_call_name(base)
            if base_str:
                bases_names.append(base_str)
                # Check for PyTorch nn.Module or similar
                resolved_base = self.imported_aliases.get(base_str, base_str)
                if "nn.Module" in base_str or "Module" in base_str or "torch.nn.Module" in resolved_base:
                    self.signals.append(
                        CodeSignal(
                            type="class_inheritance",
                            name="torch.nn.Module",
                            technology="PyTorch",
                            repository=self.repository,
                            file=self.file_path,
                            line_start=line_start,
                            line_end=line_end,
                            details={"class_name": node.name, "base": base_str},
                        )
                    )
                elif "Dataset" in base_str:
                    self.signals.append(
                        CodeSignal(
                            type="class_inheritance",
                            name="Dataset",
                            technology="PyTorch",
                            repository=self.repository,
                            file=self.file_path,
                            line_start=line_start,
                            line_end=line_end,
                            details={"class_name": node.name, "base": base_str},
                        )
                    )
                elif "models.Model" in base_str or "django" in resolved_base:
                    self.signals.append(
                        CodeSignal(
                            type="class_inheritance",
                            name="django.db.models",
                            technology="Django",
                            repository=self.repository,
                            file=self.file_path,
                            line_start=line_start,
                            line_end=line_end,
                            details={"class_name": node.name, "base": base_str},
                        )
                    )

        # Record class definition signal
        self.signals.append(
            CodeSignal(
                type="class",
                name=node.name,
                technology="Python",
                repository=self.repository,
                file=self.file_path,
                line_start=line_start,
                line_end=line_end,
                details={"bases": bases_names},
            )
        )
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef):
        self._inspect_function(node, is_async=False)
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self._inspect_function(node, is_async=True)
        self.generic_visit(node)

    def _inspect_function(self, node: ast.AST, is_async: bool):
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", node.lineno)
        func_name = getattr(node, "name", "")

        # Inspect decorators for routes / frameworks
        for dec in getattr(node, "decorator_list", []):
            dec_name = get_call_name(dec)
            if any(dec_name.endswith(f".{method}") for method in ["get", "post", "put", "delete", "patch"]):
                # Route decorator: FastAPI or Flask
                if "app.route" in dec_name:
                    self.signals.append(
                        CodeSignal(
                            type="route",
                            name="flask_route_decorator",
                            technology="Flask",
                            repository=self.repository,
                            file=self.file_path,
                            line_start=line_start,
                            line_end=line_end,
                            details={"function": func_name, "decorator": dec_name},
                        )
                    )
                else:
                    self.signals.append(
                        CodeSignal(
                            type="route",
                            name="fastapi_route_decorator",
                            technology="FastAPI",
                            repository=self.repository,
                            file=self.file_path,
                            line_start=line_start,
                            line_end=line_end,
                            details={"function": func_name, "decorator": dec_name},
                        )
                    )

        self.signals.append(
            CodeSignal(
                type="async_function" if is_async else "function",
                name=func_name,
                technology="Python",
                repository=self.repository,
                file=self.file_path,
                line_start=line_start,
                line_end=line_end,
            )
        )

    def visit_Call(self, node: ast.Call):
        line_start = node.lineno
        line_end = getattr(node, "end_lineno", node.lineno)
        call_name = get_call_name(node.func)

        if call_name:
            # Check training loop indicators
            if call_name.endswith("backward"):
                self.has_backward = True
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="loss.backward",
                        technology="PyTorch",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif call_name.endswith("step") and ("optimizer" in call_name or "optim" in call_name):
                self.has_optim_step = True
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="optimizer.step",
                        technology="PyTorch",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "DataLoader" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="DataLoader",
                        technology="PyTorch",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "optim.Adam" in call_name or "Adam" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="torch.optim.Adam",
                        technology="PyTorch",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "optim.SGD" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="torch.optim.SGD",
                        technology="PyTorch",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "cv2." in call_name:
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name=call_name,
                        technology="OpenCV",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif any(call_name.endswith(k) for k in [".fit", ".predict", ".score", ".transform"]):
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name=call_name,
                        technology="Scikit-learn",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "read_csv" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="call",
                        name="pd.read_csv",
                        technology="Pandas",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "FastAPI" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="instantiation",
                        name="FastAPI",
                        technology="FastAPI",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )
            elif "Flask" in call_name:
                self.signals.append(
                    CodeSignal(
                        type="instantiation",
                        name="Flask",
                        technology="Flask",
                        repository=self.repository,
                        file=self.file_path,
                        line_start=line_start,
                        line_end=line_end,
                    )
                )

        self.generic_visit(node)


class PythonAnalyzer(BaseAnalyzer):
    """Parses and extracts signals from Python files (.py) and Jupyter Notebooks (.ipynb)."""

    def can_analyze(self, file_path: str) -> bool:
        lower = file_path.lower()
        return lower.endswith(".py") or lower.endswith(".ipynb")

    def _extract_ipynb_code(self, content: str) -> str:
        """Extract all code cells from a Jupyter notebook JSON structure."""
        try:
            nb = json.loads(content)
            code_lines: List[str] = []
            cells = nb.get("cells", [])
            for cell in cells:
                if cell.get("cell_type") == "code":
                    source = cell.get("source", [])
                    if isinstance(source, list):
                        code_lines.extend(source)
                        code_lines.append("\n")
                    elif isinstance(source, str):
                        code_lines.append(source)
                        code_lines.append("\n")
            return "".join(code_lines)
        except Exception as e:
            logger.debug(f"Failed to parse ipynb JSON: {e}")
            return ""

    def analyze(self, file_path: str, content: str, repository: Optional[str] = None) -> AnalysisResult:
        result = AnalysisResult(file=file_path, language="python")

        code_to_parse = content
        if file_path.lower().endswith(".ipynb"):
            code_to_parse = self._extract_ipynb_code(content)
            if not code_to_parse:
                return result

        try:
            tree = ast.parse(code_to_parse, filename=file_path)
        except SyntaxError as e:
            logger.debug(f"SyntaxError parsing {file_path}: {e}")
            result.error = f"SyntaxError at line {e.lineno}: {e.msg}"
            return result
        except Exception as e:
            logger.debug(f"Unexpected AST error in {file_path}: {e}")
            result.error = f"AST parse error: {str(e)}"
            return result

        visitor = PythonASTVisitor(repository=repository, file_path=file_path)
        visitor.visit(tree)

        # Check for composite training loop pattern
        if visitor.has_backward and visitor.has_optim_step:
            visitor.signals.append(
                CodeSignal(
                    type="pattern",
                    name="model_training_loop",
                    technology="PyTorch",
                    repository=repository,
                    file=file_path,
                    line_start=1,
                    line_end=len(code_to_parse.splitlines()),
                    details={"description": "Composite PyTorch training loop with backward pass and optimizer step"},
                )
            )

        result.signals = visitor.signals
        return result
