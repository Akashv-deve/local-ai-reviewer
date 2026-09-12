import json, requests, re
from state import AgentState

def generate_tests(state: AgentState):
    print("\n--- [NODE: Generating Tests via Local LLM] ---")
    diff = state.get("git_diff", "")
    feedback = state.get("feedback", "")
    
    if diff == "No changes detected.":
         return {"generated_tests": "Skipped"}
         
    prompt = f"""
    Write a pytest suite for this git diff. Return ONLY valid Python code. No markdown.
    Use standard 'import pytest'. Check the file path in the diff for correct imports.
    
    Diff:
    {diff}
    """
    
    # THE SMART REGENERATION LOOP: If the AI failed previously, tell it why!
    if feedback:
        print(f"⚠️ Feeding previous errors back to AI: {feedback}")
        prompt += f"\n\nCRITICAL FIX REQUIRED. Your previous attempt failed with this error: {feedback}. Fix the code so this error does not happen."
        
    try:
        print("🤖 AI is typing...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b", "prompt": prompt, "stream": True 
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
        
        return {"generated_tests": clean_code, "feedback": ""} # Clear feedback after generating
    except Exception as e:
        return {"generated_tests": f"Error: {str(e)}"}