from typing import TypedDict, List

class AgentState(TypedDict):
    git_diff: str
    generated_tests: str
    validation_status: str
    validation_errors: List[str]
    human_action: str
    test_execution_logs: str
    # New reporting fields
    tests_passed: int
    tests_failed: int