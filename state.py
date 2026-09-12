from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    git_diff: str
    filtered_diff: str           # NEW: Only the target code hunks
    target_files: List[str]      
    code_review: List[Dict[str, Any]]
    generated_tests: str
    validation_status: str
    validation_errors: List[str]
    human_action: str
    feedback: Optional[str]
    regeneration_count: int      # NEW: Prevents infinite loops
    test_execution_logs: str
    tests_passed: int
    tests_failed: int
    tests_errors: int
    execution_status: str