import subprocess
import re
import os
from state import AgentState

# Configurable exclusions for enterprise deployment
IGNORE_DIRS = os.getenv("AGENT_IGNORE_DIRS", "nodes/,tests/").split(",")
IGNORE_FILES = os.getenv("AGENT_IGNORE_FILES", "main.py,graph.py,state.py,database.py").split(",")

def extract_diff(state: AgentState):
    print("\n--- [NODE: Extracting Git Diff] ---")
    try:
        subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], check=True, capture_output=True)
        result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True, encoding='utf-8', errors='replace', check=True)
        diff = result.stdout
        
        if not diff.strip():
            return {"git_diff": "No changes detected.", "target_files": [], "filtered_diff": ""}
            
        chunks = re.split(r'(?=^diff --git )', diff, flags=re.MULTILINE)
        target_files = []
        filtered_diff = ""
        
        for chunk in chunks:
            if not chunk.strip(): continue
            match = re.search(r'^diff --git a/.*? b/(.*?)$', chunk, re.MULTILINE)
            if match:
                filename = match.group(1)
                if filename.endswith('.py') and not any(filename.startswith(d) for d in IGNORE_DIRS) and filename not in IGNORE_FILES:
                    target_files.append(filename)
                    filtered_diff += chunk + "\n"
        
        return {"git_diff": diff, "target_files": target_files, "filtered_diff": filtered_diff.strip()}
        
    except FileNotFoundError:
        return {"git_diff": "Error: Git is not installed.", "target_files": [], "filtered_diff": ""}
    except subprocess.CalledProcessError:
        return {"git_diff": "Error: Not a Git repo or command failed.", "target_files": [], "filtered_diff": ""}