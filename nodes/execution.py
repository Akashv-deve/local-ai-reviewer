import subprocess
import re
from state import AgentState

def execute_tests(state: AgentState):
    print("\n--- [NODE: Subprocess Execution] ---")
    
    if state.get("human_action") != "approve":
        return {"test_execution_logs": "Execution aborted by user.", "execution_status": "ABORTED"}

    with open("test_ai_generated.py", "w") as f:
        f.write(state["generated_tests"])
        
    try:
        result = subprocess.run(['pytest', 'test_ai_generated.py'], capture_output=True, text=True, timeout=30)
        logs = result.stdout + result.stderr
        
        passed_match = re.search(r'(\d+) passed', logs)
        failed_match = re.search(r'(\d+) failed', logs)
        error_match = re.search(r'(\d+) error', logs)
        
        passed = int(passed_match.group(1)) if passed_match else 0
        failed = int(failed_match.group(1)) if failed_match else 0
        errors = int(error_match.group(1)) if error_match else 0
        
        # Determine overall status
        if errors > 0: status = "ERROR"
        elif failed > 0: status = "FAIL"
        elif passed > 0: status = "PASS"
        else: status = "UNKNOWN"
        
        return {
            "test_execution_logs": logs,
            "tests_passed": passed,
            "tests_failed": failed,
            "tests_errors": errors,
            "execution_status": status
        }
    except subprocess.TimeoutExpired:
        return {
            "test_execution_logs": "Execution aborted: Subprocess Timeout (30s exceeded).",
            "tests_passed": 0, "tests_failed": 0, "tests_errors": 0,
            "execution_status": "TIMEOUT"
        }