from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    git_diff: str
    code_review: List[Dict[str, Any]]  # Upgraded to a List of JSON objects
    generated_tests: str
    validation_status: str
    validation_errors: List[str]
    human_action: str
    feedback: Optional[str]
    test_execution_logs: str
    tests_passed: int
    tests_failed: int