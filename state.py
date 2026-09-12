from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    git_diff: str
    target_files: List[str]      # Explicit list of files the AI is allowed to test
    code_review: List[Dict[str, Any]]
    generated_tests: str
    validation_status: str
    validation_errors: List[str]
    human_action: str
    feedback: Optional[str]
    test_execution_logs: str
    tests_passed: int
    tests_failed: int
    tests_errors: int            # Separated from failures
    execution_status: str        # PASS, FAIL, ERROR, or TIMEOUT