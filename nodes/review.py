import json
import requests
from state import AgentState

def review_code(state: AgentState):
    print("\n--- [NODE: AI Code Review] ---")
    diff = state.get("filtered_diff", "")
    
    if not diff or diff.startswith("Error:"):
        return {"code_review": []}

    prompt = f"""
    Perform a code review on this Git diff.
    Return 0 to 10 findings. If no issues exist, return an empty array [].
    Output ONLY a raw JSON array. No conversational text.
    Structure exactly like this:
    [
      {{
        "severity": "HIGH", "category": "Bug", "file": "calculator.py", "line": "10",
        "issue": "Brief description", "recommendation": "How to fix it"
      }}
    ]
    Diff:
    {diff}
    """
    
    try:
        print("🤖 AI is reviewing code...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:3b", "prompt": prompt, "stream": False, "format": "json"
        }, timeout=300)
        response.raise_for_status()
        
        raw_output = response.json().get("response", "[]").strip()
        review_data = json.loads(raw_output)
        if isinstance(review_data, dict): review_data = [review_data]
        
        # Point 1: Schema Validation
        valid_reviews = []
        for item in review_data:
            if isinstance(item, dict) and all(k in item for k in ("severity", "category", "file", "line", "issue", "recommendation")):
                valid_reviews.append(item)
                
        print(f"✅ Review Complete: {len(valid_reviews)} valid issue(s) found.")
        return {"code_review": valid_reviews}
        
    except Exception as e:
        print(f"⚠️ Review Error: {e}")
        return {"code_review": [{"severity": "ERROR", "file": "System", "line": "0", "category": "System", "issue": str(e), "recommendation": "Check API connection."}]}