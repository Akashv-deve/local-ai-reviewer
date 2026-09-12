import subprocess
import re
from state import AgentState

def execute_tests(state: AgentState):
    print("\n--- [NODE: Sandboxed Execution] ---")
    
    # Failsafe: Ensure it only runs if explicitly approved
    if state.get("human_action") != "approve":
        return {"test_execution_logs": "Execution aborted by user.", "tests_passed": 0, "tests_failed": 0}

    with open("test_ai_generated.py", "w") as f:
        f.write(state["generated_tests"])
        
    try:
        result = subprocess.run(['pytest', 'test_ai_generated.py'], capture_output=True, text=True, timeout=30)
        logs = result.stdout + result.stderr
        
        # Parse advanced analytics
        passed_match = re.search(r'(\d+) passed', logs)
        failed_match = re.search(r'(\d+) failed', logs)
        error_match = re.search(r'(\d+) error', logs)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        return {
            "test_execution_logs": logs,
            "tests_passed": passed,
            "tests_failed": failed + errors
        }
    except subprocess.TimeoutExpired:
        return {
            "test_execution_logs": "Execution aborted: Sandbox Timeout (30s exceeded).",
            "tests_passed": 0,
            "tests_failed": 0
        }