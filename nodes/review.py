import json
import requests
from state import AgentState

def review_code(state: AgentState):
    print("\n--- [NODE: AI Code Review] ---")
    diff = state.get("git_diff", "")
    
    if diff == "No changes detected." or not diff:
        return {"code_review": []}

    prompt = f"""
    Perform a code review on this Git diff.
    Output ONLY a raw JSON array of objects. If no issues are found, output an empty array [].
    Structure each object exactly like this:
    [
      {{
        "severity": "HIGH, MEDIUM, or LOW",
        "category": "Bug, Security, Performance, or Style",
        "file": "filename",
        "line": "line number or general location",
        "issue": "Brief description",
        "recommendation": "How to fix it"
      }}
    ]
    
    Diff:
    {diff}
    """
    
    try:
        print("🤖 AI is reviewing code (Strict JSON Array mode)...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:7b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=120)
        response.raise_for_status()
        
        raw_output = response.json().get("response", "[]").strip()
        review_data = json.loads(raw_output)
        
        # Ensure it's a list
        if isinstance(review_data, dict):
            review_data = [review_data]
            
        print(f"✅ Review Complete: {len(review_data)} issue(s) found.")
        return {"code_review": review_data}
        
    except Exception as e:
        print(f"⚠️ Review Error: {e}")
        return {"code_review": [{"severity": "ERROR", "issue": str(e)}]}