import subprocess
import requests
import re
from state import AgentState
from langgraph.types import interrupt

def extract_diff(state: AgentState):
    print("--- [NODE: Extracting Git Diff] ---")
    result = subprocess.run(['git', 'diff', 'HEAD'], capture_output=True, text=True)
    diff_content = result.stdout
    
    if not diff_content.strip():
        return {"git_diff": "No changes detected."}
    return {"git_diff": diff_content}

import json # Add this at the top of nodes.py if it isn't there

def generate_tests(state: AgentState):
    print("--- [NODE: Generating Tests via Local LLM] ---")
    diff = state.get("git_diff")
    if diff == "No changes detected.":
        return {"generated_tests": "Skipped"}
        
    prompt = f"""
    Act as an expert Python engineer. Write a pytest suite for this git diff. 
    Rules:
    1. Return ONLY valid Python code. No markdown, no backticks, no explanations.
    2. Use standard 'import pytest'. Do not write 'from pytest import pytest'.
    3. Write actual test cases for the functions added in the diff.
    
    Diff:
    {diff}
    """
    
    try:
        print("\n🤖 AI is typing (this may be slow on limited RAM)...\n")
        
        # We set stream=True in both the JSON payload and the requests call
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b", 
            "prompt": prompt,
            "stream": True 
        }, stream=True)
        
        tests = ""
        # Read the response word-by-word as it generates
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line).get("response", "")
                print(chunk, end="", flush=True) # Print to terminal instantly
                tests += chunk
                
        print("\n\n--- [Finished Typing] ---")
        
        # Strip markdown if the AI disobeys the prompt rules
        import re
        match = re.search(r'```python(.*?)```', tests, re.DOTALL)
        clean_code = match.group(1).strip() if match else tests.replace('```python', '').replace('```', '').strip()
        
        return {"generated_tests": clean_code}
    except Exception as e:
        return {"generated_tests": f"Error connecting to local LLM: {str(e)}"}

def human_gate(state: AgentState):
    print("--- [NODE: Human Gate Paused] ---")
    if state.get("generated_tests") == "Skipped" or "Error" in state.get("generated_tests"):
         return {"user_approved": False}
         
    # This completely halts execution and surfaces data to the user
    user_decision = interrupt({
        "message": "Review the generated tests. Proceed with execution?",
        "tests": state["generated_tests"]
    })
    
    return {"user_approved": user_decision == "approve"}

def execute_tests(state: AgentState):
    print("--- [NODE: Executing Tests] ---")
    if not state.get("user_approved"):
        return {"test_execution_logs": "Execution aborted."}
        
    # Write AI code to file
    with open("test_ai_generated.py", "w") as f:
        f.write(state["generated_tests"])
        
    # Run the tests
    result = subprocess.run(['pytest', 'test_ai_generated.py'], capture_output=True, text=True)
    return {"test_execution_logs": result.stdout + result.stderr}