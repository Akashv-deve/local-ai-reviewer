import json
import requests
from state import AgentState

def review_code(state: AgentState):
    print("\n--- [NODE: AI Code Review] ---")
    diff = state.get("git_diff", "")
    
    # FIXED: Explicitly check if it starts with Error, rather than just containing it
    if diff == "No changes detected." or not diff or diff.startswith("Error:"):
        return {"code_review": []}

    prompt = f"""
    Perform a code review on this Git diff.
    Output ONLY a raw JSON array of objects. No markdown. No conversational text.
    Structure exactly like this:
    [
      {{
        "severity": "HIGH",
        "category": "Bug",
        "file": "calculator.py",
        "line": "10",
        "issue": "Brief description",
        "recommendation": "How to fix it"
      }}
    ]
    
    Diff:
    {diff}
    """
    
    try:
        print("🤖 AI is reviewing code (Strict JSON Array mode - this may take 3-4 mins on local hardware)...")
        response = requests.post('http://localhost:11434/api/generate', json={
            "model": "qwen2.5:3b",
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }, timeout=300) # FIXED: Increased to 300 seconds for laptop hardware
        response.raise_for_status()
        
        raw_output = response.json().get("response", "[]").strip()
        review_data = json.loads(raw_output)
        
        if isinstance(review_data, dict):
            review_data = [review_data]
            
        print(f"✅ Review Complete: {len(review_data)} issue(s) found.")
        return {"code_review": review_data}
        
    except requests.exceptions.Timeout:
        print("⚠️ Review Error: Hardware Timeout (Exceeded 5 minutes).")
        return {"code_review": [{"severity": "ERROR", "issue": "LLM Inference timed out due to hardware constraints."}]}
    except Exception as e:
        print(f"⚠️ Review Error: {e}")
        return {"code_review": [{"severity": "ERROR", "issue": str(e)}]}