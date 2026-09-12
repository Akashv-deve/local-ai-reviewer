import subprocess
import requests
import re
import ast
import json
from state import AgentState
from langgraph.types import interrupt

def extract_diff(state: AgentState):
    print("\n--- [NODE: Extracting Git Diff] ---")
    
    # ADDED: encoding='utf-8' and errors='replace' to safely handle Windows terminal outputs
    result = subprocess.run(
        ['git', 'diff', 'HEAD'], 
        capture_output=True, 
        text=True,
        encoding='utf-8', 
        errors='replace' 
    )
    diff_content = result.stdout
    
    # ADDED: Fallback check in case diff_content is None
    if not diff_content or not diff_content.strip():
        return {"git_diff": "No changes detected."}
        
    return {"git_diff": diff_content}

def generate_tests(state: AgentState):
    print("\n--- [NODE: Generating Tests via Local LLM] ---")
    diff = state.get("git_diff")
    if diff == "No changes detected.":
        return {"generated_tests": "Skipped"}
        
    prompt = f"""
    Act as an expert Python engineer. Write a pytest suite for this git diff. 
    Rules:
    1. Return ONLY valid Python code. No markdown.
    2. Use standard 'import pytest'.
    3. CRITICAL: Look at the file path in the git diff and write the correct import statement.
    4. Write actual test cases for the functions.
    
    Diff:
    {diff}
    """
    
    try:
        print("\n🤖 AI is typing...\n")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b", 
            "prompt": prompt,
            "stream": True 
        }, stream=True)
        
        tests = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line).get("response", "")
                print(chunk, end="", flush=True)
                tests += chunk
                
        print("\n\n--- [Finished Typing] ---")
        
        match = re.search(r'```python(.*?)```', tests, re.DOTALL)
        clean_code = match.group(1).strip() if match else tests.replace('```python', '').replace('```', '').strip()
        
        return {"generated_tests": clean_code}
    except Exception as e:
        return {"generated_tests": f"Error: {str(e)}"}

def validate_code(state: AgentState):
    print("\n--- [NODE: AST Security Validation] ---")
    code = state.get("generated_tests", "")
    if code == "Skipped" or "Error:" in code:
        return {"validation_status": "FAIL", "validation_errors": ["No valid code to check."]}
        
    errors = []
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    # Block dangerous system libraries
                    if alias.name in ['os', 'subprocess', 'sys', 'shutil']:
                        errors.append(f"Security Violation: Import of '{alias.name}' is blocked.")
    except SyntaxError as e:
        errors.append(f"Syntax Error: {str(e)}")

    if errors:
        print(f"❌ Validation Failed: {errors}")
        return {"validation_status": "FAIL", "validation_errors": errors}
    
    print("✅ AST Validation Passed. No malicious imports detected.")
    return {"validation_status": "PASS", "validation_errors": []}

def human_gate(state: AgentState):
    print("\n--- [NODE: Human Gate Paused] ---")
    if state.get("validation_status") == "FAIL":
         user_decision = interrupt({
            "message": "Code failed security/syntax validation. Type 'regenerate' to try again, or 'reject' to abort.",
            "errors": state["validation_errors"]
        })
         return {"human_action": user_decision}
         
    user_decision = interrupt({
        "message": "Review the generated tests. Options: 'approve', 'reject', 'regenerate'.",
        "tests": state["generated_tests"]
    })
    return {"human_action": user_decision}

def execute_tests(state: AgentState):
    print("\n--- [NODE: Sandboxed Execution] ---")
    with open("test_ai_generated.py", "w") as f:
        f.write(state["generated_tests"])
        
    try:
        result = subprocess.run(['pytest', 'test_ai_generated.py'], capture_output=True, text=True, timeout=30)
        logs = result.stdout + result.stderr
        
        # Parse pass/fail counts from pytest logs
        passed_match = re.search(r'(\d+) passed', logs)
        failed_match = re.search(r'(\d+) failed', logs)
        
        passed_count = int(passed_match.group(1)) if passed_match else 0
        failed_count = int(failed_match.group(1)) if failed_match else 0
        
        return {
            "test_execution_logs": logs,
            "tests_passed": passed_count,
            "tests_failed": failed_count
        }
    except subprocess.TimeoutExpired:
        return {
            "test_execution_logs": "Execution aborted: Sandbox Timeout (30s exceeded).",
            "tests_passed": 0,
            "tests_failed": 0
        }