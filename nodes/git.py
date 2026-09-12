import subprocess
import re
from state import AgentState

def extract_diff(state: AgentState):
    print("\n--- [NODE: Extracting Git Diff] ---")
    try:
        # Check if Git exists and we are in a repo
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True, capture_output=True)
        
        result = subprocess.run(
            ['git', 'diff', 'HEAD'], 
            capture_output=True, text=True, encoding='utf-8', errors='replace', check=True
        )
        diff = result.stdout
        
        if not diff.strip():
            return {"git_diff": "No changes detected.", "target_files": []}
            
        # Extract changed files: matches 'diff --git a/file b/file'
        all_files = re.findall(r'^diff --git a/.*? b/(.*?)$', diff, re.MULTILINE)
        # CRITICAL: Filter out the agent's own infrastructure
        target_files = [f for f in all_files if not f.startswith('nodes/') and f not in ['main.py', 'graph.py', 'state.py', 'database.py']]
        
        return {"git_diff": diff, "target_files": target_files}
        
    except FileNotFoundError:
        return {"git_diff": "Error: Git is not installed.", "target_files": []}
    except subprocess.CalledProcessError:
        return {"git_diff": "Error: Not a Git repository or Git command failed.", "target_files": []}