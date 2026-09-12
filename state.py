from typing import TypedDict

class AgentState(TypedDict):
    git_diff: str
    generated_tests: str
    user_approved: bool
    test_execution_logs: str