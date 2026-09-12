import subprocess
from state import AgentState

def extract_diff(state: AgentState):
    print("--- [NODE: Extracting Git Diff] ---")
    
    result = subprocess.run(
        ['git', 'diff', 'HEAD'], 
        capture_output=True, 
        text=True
    )
    diff_content = result.stdout
    
    if not diff_content.strip():
        return {"git_diff": "No changes detected."}
        
    return {"git_diff": diff_content}