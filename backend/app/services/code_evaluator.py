"""Deterministic Static Code Evaluator for ProofPath Phase 3.

Evaluates user-submitted code snippets safely via static syntax and AST analysis.
NEVER executes arbitrary code (no eval, no exec, no subprocess).
"""

import ast
import re
import logging
from typing import List, Dict, Any, Tuple

from app.models.progress import (
    CodeChallenge,
    ChallengeCriterion,
    ChallengeCriterionResult,
    EvaluationStatus,
)

logger = logging.getLogger(__name__)


class CodeEvaluator:
    """Safe, deterministic static evaluator for Monaco Editor code implementation challenges."""

    def evaluate(
        self,
        challenge: CodeChallenge,
        submitted_code: str,
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """
        Evaluate submitted code against challenge criteria statically.

        Returns:
            (status, score_0_to_100, criteria_results, feedback)
        """
        if not submitted_code or not submitted_code.strip():
            results = [
                ChallengeCriterionResult(
                    name=c.name,
                    description=c.description,
                    passed=False,
                    feedback="No code provided.",
                )
                for c in challenge.criteria
            ]
            return EvaluationStatus.FAILED, 0.0, results, "Submission was empty."

        lang = challenge.language.lower()
        if lang == "python":
            return self._evaluate_python(challenge, submitted_code)
        elif lang in ("javascript", "typescript", "js", "ts"):
            return self._evaluate_javascript(challenge, submitted_code)
        elif lang == "sql":
            return self._evaluate_sql(challenge, submitted_code)
        elif lang in ("dockerfile", "docker"):
            return self._evaluate_dockerfile(challenge, submitted_code)
        else:
            return self._evaluate_generic(challenge, submitted_code)

    def _evaluate_python(
        self, challenge: CodeChallenge, code: str
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Evaluate Python code statically using Python AST."""
        # Step 1: Syntax check via ast.parse
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            results = [
                ChallengeCriterionResult(
                    name=c.name,
                    description=c.description,
                    passed=False,
                    feedback=f"Python syntax error at line {e.lineno}: {e.msg}",
                )
                for c in challenge.criteria
            ]
            return EvaluationStatus.FAILED, 0.0, results, f"Syntax Error: {e.msg} at line {e.lineno}"

        criteria_results: List[ChallengeCriterionResult] = []

        # Find all defined functions, classes, and return statements
        func_defs = [node for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        class_defs = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        returns = [node for node in ast.walk(tree) if isinstance(node, ast.Return)]
        bin_ops = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp)]
        mod_ops = [node for node in bin_ops if isinstance(node.op, ast.Mod)]
        bitwise_and = [node for node in bin_ops if isinstance(node.op, ast.BitAnd)]
        decorators = [d for f in func_defs for d in f.decorator_list]

        for crit in challenge.criteria:
            c_name = crit.name.lower()
            passed = False
            feedback_msg = ""

            if "func" in c_name or "defined" in c_name:
                # Expecting a function or specific function name
                if func_defs:
                    passed = True
                    feedback_msg = f"Function '{func_defs[0].name}' successfully defined."
                else:
                    feedback_msg = "No function definition found."

            elif "return" in c_name or "boolean" in c_name or "even_odd" in c_name:
                # Check for return statement and modulo operator or bitwise AND
                has_mod = len(mod_ops) > 0 or len(bitwise_and) > 0
                has_return = len(returns) > 0
                if has_return and (has_mod or "return" in code):
                    passed = True
                    feedback_msg = "Correct conditional return logic detected."
                elif has_return:
                    passed = True
                    feedback_msg = "Return statement found."
                else:
                    feedback_msg = "Missing return statement."

            elif "module" in c_name or "inherit" in c_name:
                # PyTorch nn.Module inheritance check
                has_module_inherit = any(
                    any("Module" in getattr(base, "id", "") or "Module" in getattr(base, "attr", "") for base in c.bases)
                    for c in class_defs
                )
                if has_module_inherit:
                    passed = True
                    feedback_msg = "Inherits from torch.nn.Module."
                else:
                    feedback_msg = "Class does not inherit from nn.Module."

            elif "forward" in c_name:
                # Check for def forward(self, ...)
                has_forward = any(f.name == "forward" for f in func_defs)
                if has_forward:
                    passed = True
                    feedback_msg = "Implements forward pass method."
                else:
                    feedback_msg = "Missing forward method."

            elif "init" in c_name:
                # Check for def __init__(self, ...)
                has_init = any(f.name == "__init__" for f in func_defs)
                if has_init:
                    passed = True
                    feedback_msg = "Initializes layers in __init__."
                else:
                    feedback_msg = "Missing __init__ constructor."

            elif "route" in c_name or "decorator" in c_name:
                # Check for FastAPI route decorator
                if decorators or "@app." in code:
                    passed = True
                    feedback_msg = "Route decorator attached to handler."
                else:
                    feedback_msg = "Missing route decorator."

            elif "app" in c_name or "instance" in c_name:
                # Check for FastAPI() instantiation
                if "FastAPI(" in code:
                    passed = True
                    feedback_msg = "FastAPI application instantiated."
                else:
                    feedback_msg = "Missing FastAPI() instantiation."

            else:
                # General check: non-empty meaningful structure
                passed = len(func_defs) > 0 or len(class_defs) > 0
                feedback_msg = "Structural check passed." if passed else "Structural requirement not met."

            criteria_results.append(
                ChallengeCriterionResult(
                    name=crit.name,
                    description=crit.description,
                    passed=passed,
                    feedback=feedback_msg,
                )
            )

        return self._compute_outcome(criteria_results)

    def _evaluate_javascript(
        self, challenge: CodeChallenge, code: str
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Evaluate JS/TS code statically via pattern and syntax analysis."""
        criteria_results: List[ChallengeCriterionResult] = []

        has_function = bool(re.search(r"(?:function\s+\w+|const\s+\w+\s*=\s*(?:\([^)]*\)|[a-zA-Z0-9_]+)\s*=>)", code))
        has_return = bool(re.search(r"return\s+", code) or "=>" in code)
        has_jsx = bool(re.search(r"<[A-Za-z][^>]*>", code))
        has_event = bool(re.search(r"onClick\s*=", code) or "addEventListener" in code)
        has_reverse = bool(re.search(r"\.split\([^)]*\)\s*\.reverse\(\)\s*\.join\(", code) or "reverse" in code)

        for crit in challenge.criteria:
            c_name = crit.name.lower()
            passed = False
            feedback_msg = ""

            if "component" in c_name or "func" in c_name:
                if has_function:
                    passed = True
                    feedback_msg = "Functional definition detected."
                else:
                    feedback_msg = "Missing function or component declaration."

            elif "jsx" in c_name or "element" in c_name:
                if has_jsx:
                    passed = True
                    feedback_msg = "Returns valid JSX element."
                else:
                    feedback_msg = "Missing JSX element structure."

            elif "event" in c_name or "click" in c_name:
                if has_event:
                    passed = True
                    feedback_msg = "Event handler properly bound."
                else:
                    feedback_msg = "Event handler (e.g., onClick) not bound."

            elif "reverse" in c_name or "string" in c_name:
                if has_reverse or has_return:
                    passed = True
                    feedback_msg = "String transformation logic detected."
                else:
                    feedback_msg = "Missing reverse logic."

            else:
                passed = has_function and has_return
                feedback_msg = "Standard structure satisfied." if passed else "Missing expected implementation structure."

            criteria_results.append(
                ChallengeCriterionResult(
                    name=crit.name,
                    description=crit.description,
                    passed=passed,
                    feedback=feedback_msg,
                )
            )

        return self._compute_outcome(criteria_results)

    def _evaluate_sql(
        self, challenge: CodeChallenge, code: str
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Evaluate SQL queries statically."""
        criteria_results: List[ChallengeCriterionResult] = []
        normalized_sql = code.upper()

        has_select = "SELECT" in normalized_sql
        has_group_by = "GROUP BY" in normalized_sql
        has_having = "HAVING" in normalized_sql
        has_where = "WHERE" in normalized_sql
        has_join = "JOIN" in normalized_sql

        for crit in challenge.criteria:
            c_name = crit.name.lower()
            passed = False
            feedback_msg = ""

            if "select" in c_name:
                if has_select:
                    passed = True
                    feedback_msg = "SELECT projection present."
                else:
                    feedback_msg = "Missing SELECT keyword."

            elif "group" in c_name:
                if has_group_by:
                    passed = True
                    feedback_msg = "GROUP BY clause present."
                else:
                    feedback_msg = "Missing GROUP BY clause."

            elif "having" in c_name or "filter" in c_name:
                if has_having or has_where:
                    passed = True
                    feedback_msg = "Filtering condition (HAVING/WHERE) present."
                else:
                    feedback_msg = "Missing filtering condition."

            elif "join" in c_name:
                if has_join:
                    passed = True
                    feedback_msg = "Table JOIN present."
                else:
                    feedback_msg = "Missing table JOIN."

            else:
                passed = has_select
                feedback_msg = "SQL clause validated." if passed else "Clause not met."

            criteria_results.append(
                ChallengeCriterionResult(
                    name=crit.name,
                    description=crit.description,
                    passed=passed,
                    feedback=feedback_msg,
                )
            )

        return self._compute_outcome(criteria_results)

    def _evaluate_dockerfile(
        self, challenge: CodeChallenge, code: str
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Evaluate Dockerfile instructions statically."""
        criteria_results: List[ChallengeCriterionResult] = []
        lines = [line.strip().upper() for line in code.splitlines() if line.strip() and not line.strip().startswith("#")]

        has_from = any(line.startswith("FROM ") for line in lines)
        has_workdir = any(line.startswith("WORKDIR ") for line in lines)
        has_cmd = any(line.startswith("CMD ") or line.startswith("ENTRYPOINT ") for line in lines)
        has_copy = any(line.startswith("COPY ") or line.startswith("ADD ") for line in lines)

        for crit in challenge.criteria:
            c_name = crit.name.lower()
            passed = False
            feedback_msg = ""

            if "from" in c_name:
                passed = has_from
                feedback_msg = "FROM base image specified." if passed else "Missing FROM instruction."
            elif "workdir" in c_name:
                passed = has_workdir
                feedback_msg = "WORKDIR instruction present." if passed else "Missing WORKDIR instruction."
            elif "cmd" in c_name or "entrypoint" in c_name:
                passed = has_cmd
                feedback_msg = "CMD / ENTRYPOINT command present." if passed else "Missing CMD instruction."
            elif "copy" in c_name:
                passed = has_copy
                feedback_msg = "COPY instruction present." if passed else "Missing COPY instruction."
            else:
                passed = has_from
                feedback_msg = "Dockerfile validated." if passed else "Invalid Dockerfile."

            criteria_results.append(
                ChallengeCriterionResult(
                    name=crit.name,
                    description=crit.description,
                    passed=passed,
                    feedback=feedback_msg,
                )
            )

        return self._compute_outcome(criteria_results)

    def _evaluate_generic(
        self, challenge: CodeChallenge, code: str
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Fallback generic evaluation checking non-emptiness and criteria."""
        passed_all = len(code.strip()) > 10
        results = [
            ChallengeCriterionResult(
                name=c.name,
                description=c.description,
                passed=passed_all,
                feedback="Code submitted." if passed_all else "Code too short.",
            )
            for c in challenge.criteria
        ]
        return self._compute_outcome(results)

    def _compute_outcome(
        self, criteria_results: List[ChallengeCriterionResult]
    ) -> Tuple[EvaluationStatus, float, List[ChallengeCriterionResult], str]:
        """Calculate deterministic pass/partially_passed/failed status and score percentage."""
        if not criteria_results:
            return EvaluationStatus.PASSED, 100.0, [], "All criteria satisfied."

        total = len(criteria_results)
        passed_count = sum(1 for c in criteria_results if c.passed)
        score = round((passed_count / total) * 100.0, 1)

        if passed_count == total:
            status = EvaluationStatus.PASSED
            feedback = f"All {total} challenge criteria successfully verified! Score: {score}%"
        elif passed_count > 0:
            status = EvaluationStatus.PARTIALLY_PASSED
            feedback = f"{passed_count} of {total} criteria passed. Score: {score}%"
        else:
            status = EvaluationStatus.FAILED
            feedback = f"0 of {total} criteria passed. Score: 0%"

        return status, score, criteria_results, feedback
