"""JavaScript and TypeScript Analyzer for ProofPath."""

import re
import logging
from typing import List, Optional

from app.analyzers.base_analyzer import BaseAnalyzer, AnalysisResult
from app.models.evidence import CodeSignal

logger = logging.getLogger(__name__)


# Precompiled regex patterns for JS/TS detection
REACT_HOOKS = ["useState", "useEffect", "useContext", "useReducer", "useCallback", "useMemo", "useRef"]
HOOK_PATTERN = re.compile(rf"\b({'|'.join(REACT_HOOKS)})\s*(?:<[^>]+>)?\s*\(")

REACT_IMPORT_PATTERN = re.compile(r"""(?:import\s+.*?\s+from\s+['"]react['"]|require\s*\(\s*['"]react['"]\s*\))""")
REACT_COMPONENT_PATTERN = re.compile(
    r"""(?:(?:export\s+(?:default\s+)?)?function\s+([A-Z]\w+)\s*\(|"""
    r"""(?:export\s+)?(?:const|let|var)\s+([A-Z]\w+)(?:\s*:\s*[^=]+)?\s*=\s*(?:React\.)?(?:memo|forwardRef)?\s*\(?.*?\)?\s*=>|"""
    r"""(?:export\s+(?:default\s+)?)?class\s+([A-Z]\w+)\s+extends\s+(?:React\.)?Component)"""
)
JSX_TAG_PATTERN = re.compile(r"""<([A-Z]\w+|div|span|button|input|form|header|footer|section|main|nav)\b[^>]*>""")

EXPRESS_IMPORT_PATTERN = re.compile(r"""(?:import\s+express\s+from\s+['"]express['"]|require\s*\(\s*['"]express['"]\s*\))""")
EXPRESS_ROUTE_PATTERN = re.compile(r"""(?:app|router)\.(get|post|put|delete|patch|use)\s*\(\s*['"`]([^'"`]+)['"`]""")

NODE_API_PATTERN = re.compile(r"""(?:require\s*\(\s*['"](fs|path|http|https|crypto|os|events|stream)['"]\s*\)|process\.env|http\.createServer)""")

TS_INTERFACE_PATTERN = re.compile(r"""\binterface\s+([A-Z]\w+)""")
TS_TYPE_ALIAS_PATTERN = re.compile(r"""\btype\s+([A-Z]\w+)\s*=""")
TS_ENUM_PATTERN = re.compile(r"""\benum\s+([A-Z]\w+)""")
TS_TYPE_ANNOTATION_PATTERN = re.compile(r""":\s*(?:string|number|boolean|any|unknown|void|Promise<[^>]+>|Array<[^>]+>|Record<[^>]+>|{\s*\w+:\s*\w+\s*})""")

ASYNC_AWAIT_PATTERN = re.compile(r"""\b(async\s+function|async\s*\(|await\s+)""")
FETCH_AXIOS_PATTERN = re.compile(r"""\b(fetch\s*\(|axios\.(get|post|put|delete)\s*\()""")


class JavaScriptAnalyzer(BaseAnalyzer):
    """Parses JavaScript and TypeScript files using structured pattern and token extraction."""

    JS_EXTENSIONS = {".js", ".jsx", ".mjs", ".cjs"}
    TS_EXTENSIONS = {".ts", ".tsx"}

    def can_analyze(self, file_path: str) -> bool:
        lower = file_path.lower()
        return any(lower.endswith(ext) for ext in self.JS_EXTENSIONS | self.TS_EXTENSIONS)

    def analyze(self, file_path: str, content: str, repository: Optional[str] = None) -> AnalysisResult:
        lower_path = file_path.lower()
        is_ts = any(lower_path.endswith(ext) for ext in self.TS_EXTENSIONS)
        language = "typescript" if is_ts else "javascript"

        result = AnalysisResult(file=file_path, language=language)
        lines = content.splitlines()

        signals: List[CodeSignal] = []
        is_react_file = False

        # Per-line and multi-signal scanning
        for line_no, line in enumerate(lines, start=1):
            line_str = line.strip()
            if not line_str or line_str.startswith("//") or line_str.startswith("/*") or line_str.startswith("*"):
                continue

            # 1. React Imports
            if REACT_IMPORT_PATTERN.search(line_str):
                is_react_file = True
                signals.append(
                    CodeSignal(
                        type="import",
                        name="import_react",
                        technology="React",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            # 2. React Hooks
            hook_match = HOOK_PATTERN.search(line_str)
            if hook_match:
                hook_name = hook_match.group(1)
                signals.append(
                    CodeSignal(
                        type="call",
                        name=hook_name,
                        technology="React",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            # 3. React Components
            comp_match = REACT_COMPONENT_PATTERN.search(line_str)
            if comp_match:
                comp_name = next(g for g in comp_match.groups() if g is not None)
                signals.append(
                    CodeSignal(
                        type="component",
                        name=comp_name,
                        technology="React",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                        details={"component_name": comp_name},
                    )
                )

            # 4. Express Import & Routes
            if EXPRESS_IMPORT_PATTERN.search(line_str):
                signals.append(
                    CodeSignal(
                        type="import",
                        name="express",
                        technology="Express",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            route_match = EXPRESS_ROUTE_PATTERN.search(line_str)
            if route_match:
                method, path = route_match.groups()
                signals.append(
                    CodeSignal(
                        type="route",
                        name="express_route_handler",
                        technology="Express",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                        details={"method": method.upper(), "path": path},
                    )
                )

            # 5. Node.js built-ins & globals
            node_match = NODE_API_PATTERN.search(line_str)
            if node_match:
                signals.append(
                    CodeSignal(
                        type="api_call",
                        name="node_builtin",
                        technology="Node.js",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            # 6. TypeScript specific signals
            if is_ts:
                if TS_INTERFACE_PATTERN.search(line_str):
                    match = TS_INTERFACE_PATTERN.search(line_str)
                    signals.append(
                        CodeSignal(
                            type="ts_interface",
                            name=match.group(1),
                            technology="TypeScript",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
                elif TS_TYPE_ALIAS_PATTERN.search(line_str):
                    match = TS_TYPE_ALIAS_PATTERN.search(line_str)
                    signals.append(
                        CodeSignal(
                            type="ts_type_alias",
                            name=match.group(1),
                            technology="TypeScript",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
                elif TS_ENUM_PATTERN.search(line_str):
                    match = TS_ENUM_PATTERN.search(line_str)
                    signals.append(
                        CodeSignal(
                            type="ts_enum",
                            name=match.group(1),
                            technology="TypeScript",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )
                elif TS_TYPE_ANNOTATION_PATTERN.search(line_str):
                    signals.append(
                        CodeSignal(
                            type="ts_type_annotation",
                            name="type_annotation",
                            technology="TypeScript",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )

            # 7. Async/await & Fetch/Axios
            if ASYNC_AWAIT_PATTERN.search(line_str):
                signals.append(
                    CodeSignal(
                        type="syntax",
                        name="async_await",
                        technology="JavaScript",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            if FETCH_AXIOS_PATTERN.search(line_str):
                is_axios = "axios" in line_str
                signals.append(
                    CodeSignal(
                        type="call",
                        name="axios" if is_axios else "fetch",
                        technology="REST API",
                        repository=repository,
                        file=file_path,
                        line_start=line_no,
                        line_end=line_no,
                    )
                )

            # 8. JSX elements in .jsx / .tsx
            if lower_path.endswith(".jsx") or lower_path.endswith(".tsx"):
                if JSX_TAG_PATTERN.search(line_str):
                    signals.append(
                        CodeSignal(
                            type="syntax",
                            name="jsx_element",
                            technology="React",
                            repository=repository,
                            file=file_path,
                            line_start=line_no,
                            line_end=line_no,
                        )
                    )

        # Baseline language signal for existing files
        signals.append(
            CodeSignal(
                type="syntax",
                name="ts_code" if is_ts else "js_code",
                technology="TypeScript" if is_ts else "JavaScript",
                repository=repository,
                file=file_path,
                line_start=1,
                line_end=len(lines) if lines else 1,
            )
        )

        result.signals = signals
        return result
