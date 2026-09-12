import json, requests, re
from state import AgentState

def generate_tests(state: AgentState):
    print("\n--- [NODE: Generating Tests via Local LLM] ---")
    diff = state.get("filtered_diff", "")
    feedback = state.get("feedback", "")
    targets = state.get("target_files", [])
    
    if not diff or diff.startswith("Error:"): return {"generated_tests": "Skipped"}
         
    prompt = f"""
    Write a complete pytest suite for this git diff. 
    CRITICAL RULES:
    1. TARGET FILES: You may ONLY write tests for these specific files: {targets}
    2. DO NOT output conversational text, summaries, or explanations. 
    3. OUTPUT STRICTLY EXECUTABLE PYTHON CODE.
    4. Always start your response with 'import pytest'.
    
    TARGET DIFF (Only test the logic shown below):
    {diff}
    """
    
    if feedback:
        print(f"⚠️ Applying human/system feedback to next generation...")
        prompt += f"\n\nCRITICAL FIX REQUIRED: Your previous attempt was rejected. REASON: '{feedback}'. Fix the code."
        
    try:
        print("🤖 AI is typing...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:3b", "prompt": prompt, "stream": True 
        }, stream=True, timeout=300)
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
        return {"generated_tests": f"HTTP Error connecting to Ollama: {str(e)}"}