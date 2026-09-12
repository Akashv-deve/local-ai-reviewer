import json
import requests
from state import AgentState

def review_code(state: AgentState):
    print("\n--- [NODE: AI Code Review] ---")
    diff = state.get("git_diff", "")
    
    if diff == "No changes detected." or not diff:
        return {"code_review": {"status": "skipped"}}

    prompt = f"""
    Perform a code review on this Git diff.
    Output ONLY a raw JSON object with this exact structure:
    {{
        "severity": "HIGH, MEDIUM, or LOW",
        "category": "Bug, Security, Performance, or Style",
        "issue": "Brief description of the main issue",
        "recommendation": "How to fix it"
    }}
    Do not include markdown backticks. Return ONLY the JSON object.
    
    Diff:
    {diff}
    """
    
    try:
        print("🤖 AI is reviewing code (Strict JSON mode)...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "format": "json" # Forces Ollama to return valid JSON
        })
        
        raw_output = response.json().get("response", "{}").strip()
        review_data = json.loads(raw_output)
        print(f"✅ Review Complete: {review_data.get('severity', 'UNKNOWN')} Severity Issue Found.")
        return {"code_review": review_data}
        
    except Exception as e:
        print(f"⚠️ Review Error: {e}")
        return {"code_review": {"error": str(e)}}