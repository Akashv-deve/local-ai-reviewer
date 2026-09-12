import subprocess
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

# 1. Define the State (Keeps memory lean for your laptop)
class AgentState(TypedDict):
    git_diff: str
    generated_tests: str
    user_approved: bool
    test_execution_logs: str

# 2. Node 1: Extract Local Git Changes
def extract_diff(state: AgentState):
    print("--- [NODE: Extracting Git Diff] ---")
    
    # Run local git diff command
    result = subprocess.run(
        ['git', 'diff', 'HEAD'], 
        capture_output=True, 
        text=True
    )
    diff_content = result.stdout
    
    # If there are no changes, return a placeholder
    if not diff_content.strip():
        return {"git_diff": "No changes detected."}
        
    return {"git_diff": diff_content}
# Temporary test to see if it works
if __name__ == "__main__":
    dummy_state = {}
    result = extract_diff(dummy_state)
    print("EXTRACTED DIFF:\n", result["git_diff"])