import json, requests, re
from state import AgentState

def generate_tests(state: AgentState):
    print("\n--- [NODE: Generating Tests via Local LLM] ---")
    diff = state.get("git_diff", "")
    feedback = state.get("feedback", "")
    
    if diff == "No changes detected.":
         return {"generated_tests": "Skipped"}
         
    prompt = f"""
    Write a pytest suite for this git diff. 
    CRITICAL RULES:
    1. ONLY generate tests for the business logic and application files changed.
    2. DO NOT write tests for the AI agent itself, LangGraph, node orchestration, or CLI files.
    3. Return ONLY valid Python code. No markdown.
    
    Diff:
    {diff}
    """
    
    if feedback:
        print(f"⚠️ Applying human feedback to next generation...")
        prompt += f"\n\nCRITICAL FIX REQUIRED: The human reviewer rejected your previous attempt with this reason: '{feedback}'. Fix the code to address this."
        
    try:
        print("🤖 AI is typing...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b", "prompt": prompt, "stream": True 
        }, stream=True)
        response.raise_for_status()
        
        tests = ""
        for line in response.iter_lines():
            if line:
                chunk = json.loads(line).get("response", "")
                print(chunk, end="", flush=True)
                tests += chunk
                
        print("\n\n--- [Finished Typing] ---")
        match = re.search(r'```python(.*?)```', tests, re.DOTALL)
        clean_code = match.group(1).strip() if match else tests.replace('```python', '').replace('```', '').strip()
        
        return {"generated_tests": clean_code, "feedback": ""}
    except Exception as e:
        return {"generated_tests": f"Error: {str(e)}"}