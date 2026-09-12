import json
import requests
from state import AgentState

ALLOWED_SEVERITY = {"HIGH", "MEDIUM", "LOW"}
ALLOWED_CATEGORY = {"Bug", "Security", "Performance", "Style"}

def review_code(state: AgentState):
    print("\n--- [NODE: AI Code Review] ---")
    diff = state.get("filtered_diff", "")
    
    if not diff or diff.startswith("Error:"):
        return {"code_review": []}

    prompt = f"""
    Perform a Python code review on this Git diff.
    Return 0 to 10 findings. If no issues exist, return an empty array [].
    Output ONLY a raw JSON array.
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
        
        valid_reviews = []
        invalid_count = 0
        
        for item in review_data:
            if isinstance(item, dict) and all(k in item for k in ("severity", "category", "file", "line", "issue", "recommendation")):
                if item["severity"].upper() in ALLOWED_SEVERITY and item["category"] in ALLOWED_CATEGORY:
                    valid_reviews.append(item)
                else:
                    invalid_count += 1
            else:
                invalid_count += 1
                    
        metrics = {"total": len(review_data), "valid": len(valid_reviews), "invalid": invalid_count}
        print(f"✅ Review Complete: {len(valid_reviews)} valid, {invalid_count} rejected.")
        return {"code_review": valid_reviews, "review_metrics": metrics}
        
    except Exception as e:
        return {"code_review": [], "review_metrics": {"total": 0, "valid": 0, "invalid": 1}}