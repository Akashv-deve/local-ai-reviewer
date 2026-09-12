import pytest

def test_calculator_divide():
    from calculator import divide
    assert divide(10, 5) == 2.0

def test_calculator_unsafe_divide():
    from calculator import unsafe_divide
    assert unsafe_divide(10, 5) == 2.0

def test_graph_imports():
    from graph import workflow, AgentState
    from nodes.git import extract_diff
    from nodes.review import review_code
    from nodes.generation import generate_tests
    from nodes.validation import validate_code, human_gate
    from nodes.execution import execute_tests

def test_main_script():
    from main import thread
    assert thread["configurable"]["thread_id"] == "portfolio-demo-1"

def test_validation_node():
    from nodes.validation import validate_code, human_gate
    from ast import parse
    code = "print('Hello, world!')"
    tree = parse(code)
    errors = validate_code({"generated_tests": code})
    assert errors["validation_status"] == "PASS"
    assert "validation_errors" in errors
    assert "feedback" in errors

    code_with_violation = "import os; print(os.listdir('.'))"
    errors_with_violation = validate_code({"generated_tests": code_with_violation})
    assert errors_with_violation["validation_status"] == "FAIL"
    assert "Security: Blocked import 'os'" in errors_with_violation["validation_errors"]
    assert "feedback" in errors_with_violation

def test_human_gate():
    from nodes.validation import human_gate
    state = {"code_review": {"severity": "high", "category": "security", "issue": "unquoted string", "recommendation": "quote all strings"}, "generated_tests": "def test_foo(): assert True"}
    decision = human_gate(state)
    assert "human_action" in decision
    assert decision["human_action"] in ["approve", "regenerate", "reject"]
    if decision["human_action"] == "regenerate":
        assert "feedback" in decision and decision["feedback"] == "Human reviewer requested regeneration. Improve the logic and test coverage."