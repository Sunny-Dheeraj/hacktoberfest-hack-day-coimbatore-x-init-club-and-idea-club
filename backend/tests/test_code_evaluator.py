"""Tests for Safe Static Code Evaluator (ProofPath Phase 3)."""

import pytest
from app.services.code_evaluator import CodeEvaluator
from app.models.progress import CodeChallenge, ChallengeCriterion, ChallengeDifficulty, EvaluationStatus


@pytest.fixture
def evaluator():
    return CodeEvaluator()


def test_python_is_even_correct(evaluator):
    """Verify correct Python implementation passes all criteria."""
    challenge = CodeChallenge(
        id="py-even",
        skill="Python",
        language="python",
        title="Even checker",
        difficulty=ChallengeDifficulty.BEGINNER,
        description="Return True when n is even",
        starter_code="def is_even(n):\n    pass\n",
        criteria=[
            ChallengeCriterion(name="function_defined", description="Defines is_even"),
            ChallengeCriterion(name="returns_boolean_condition", description="Uses modulo or remainder check"),
        ],
    )

    code = "def is_even(n):\n    return n % 2 == 0\n"
    status, score, criteria, feedback = evaluator.evaluate(challenge, code)

    assert status == EvaluationStatus.PASSED
    assert score == 100.0
    assert all(c.passed for c in criteria)


def test_python_syntax_error_handled_safely(evaluator):
    """Verify syntax error is caught safely without crashing."""
    challenge = CodeChallenge(
        id="py-even",
        skill="Python",
        language="python",
        title="Even checker",
        difficulty=ChallengeDifficulty.BEGINNER,
        description="Return True when n is even",
        starter_code="def is_even(n):\n    pass\n",
        criteria=[ChallengeCriterion(name="function_defined", description="Defines is_even")],
    )

    invalid_code = "def is_even(n):\n    return n % 2 == "  # Incomplete syntax
    status, score, criteria, feedback = evaluator.evaluate(challenge, invalid_code)

    assert status == EvaluationStatus.FAILED
    assert score == 0.0
    assert "Syntax Error" in feedback


def test_javascript_reverse_string(evaluator):
    """Verify JavaScript string reverse implementation."""
    challenge = CodeChallenge(
        id="js-reverse",
        skill="JavaScript",
        language="javascript",
        title="Reverse string",
        difficulty=ChallengeDifficulty.BEGINNER,
        description="Reverse given string",
        starter_code="function reverseString(s) {}\n",
        criteria=[
            ChallengeCriterion(name="function_defined", description="Defines function"),
            ChallengeCriterion(name="reverse_logic", description="Uses reverse method or loop"),
        ],
    )

    code = "function reverseString(s) {\n  return s.split('').reverse().join('');\n}\n"
    status, score, criteria, feedback = evaluator.evaluate(challenge, code)

    assert status == EvaluationStatus.PASSED
    assert score == 100.0


def test_sql_query_evaluation(evaluator):
    """Verify SQL query criteria evaluation."""
    challenge = CodeChallenge(
        id="sql-orders",
        skill="SQL",
        language="sql",
        title="Orders count",
        difficulty=ChallengeDifficulty.BEGINNER,
        description="Group by department",
        starter_code="SELECT ...",
        criteria=[
            ChallengeCriterion(name="select_clause", description="Contains SELECT"),
            ChallengeCriterion(name="group_by", description="Contains GROUP BY"),
            ChallengeCriterion(name="having_clause", description="Contains HAVING"),
        ],
    )

    query = "SELECT department, COUNT(*) FROM employees GROUP BY department HAVING COUNT(*) > 5;"
    status, score, criteria, feedback = evaluator.evaluate(challenge, query)

    assert status == EvaluationStatus.PASSED
    assert score == 100.0


def test_dockerfile_evaluation(evaluator):
    """Verify Dockerfile instructions evaluation."""
    challenge = CodeChallenge(
        id="dock-base",
        skill="Docker",
        language="dockerfile",
        title="Base Dockerfile",
        difficulty=ChallengeDifficulty.BEGINNER,
        description="Create basic Dockerfile",
        starter_code="FROM ...",
        criteria=[
            ChallengeCriterion(name="has_from", description="Includes FROM"),
            ChallengeCriterion(name="has_workdir", description="Includes WORKDIR"),
            ChallengeCriterion(name="has_cmd", description="Includes CMD"),
        ],
    )

    dockerfile = "FROM python:3.10-slim\nWORKDIR /app\nCOPY . .\nCMD [\"python\", \"main.py\"]\n"
    status, score, criteria, feedback = evaluator.evaluate(challenge, dockerfile)

    assert status == EvaluationStatus.PASSED
    assert score == 100.0
