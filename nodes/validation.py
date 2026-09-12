import ast
from state import AgentState
from langgraph.types import interrupt

def validate_code(state: AgentState):
    print("\n--- [NODE: AST Security Validation] ---")
    code = state.get("generated_tests", "")
    
    # FIXED: Explicitly block non-code states
    if code == "Skipped" or code.startswith("Error") or code.startswith("HTTP Error"):
        return {"validation_status": "FAIL", "validation_errors": ["No tests were generated. Validation bypassed."], "feedback": "Code generation failed or was skipped."}
        
    errors = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys', 'shutil']:
                        errors.append(f"Security: Blocked import '{alias.name}'.")
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec', 'open', '__import__', 'compile']:
                    errors.append(f"Security: Blocked dangerous function '{node.func.id}()'.")
    except SyntaxError as e:
        errors.append(f"Syntax Error: {str(e)}")

    if errors:
        print(f"❌ Static Security Check Failed: {errors}")
        return {"validation_status": "FAIL", "validation_errors": errors, "feedback": str(errors)}
        
    print("✅ Static Security Check Passed (Syntax & Policy only).")
    return {"validation_status": "PASS", "validation_errors": [], "feedback": ""}

def human_gate(state: AgentState):
    print("\n--- [NODE: Human Gate Paused] ---")
    
    payload = {
        "review": state.get("code_review", []),
        "tests": state.get("generated_tests", ""),
        "validation_status": state.get("validation_status"),
        "validation_errors": state.get("validation_errors", [])
    }

    # Pause based on validation status
    if state.get("validation_status") == "FAIL":
         user_decision = interrupt({"message": "Code failed static security validation.", "payload": payload})
    else:
         user_decision = interrupt({"message": "Review generated tests.", "payload": payload})
    
    # FIXED: Robust parsing for all decisions
    if isinstance(user_decision, str):
        if user_decision.startswith("regenerate"):
            reason = user_decision.split(":", 1)[1].strip() if ":" in user_decision else "Human requested regeneration."
            return {"human_action": "regenerate", "feedback": reason}
        elif user_decision == "approve":
            if state.get("validation_status") == "FAIL":
                print("\n⚠️ Cannot approve code that failed security validation. Forcing rejection.")
                return {"human_action": "reject"}
            return {"human_action": "approve"}
            
    return {"human_action": "reject"}
    if state.get("validation_status") == "FAIL":
         user_decision = interrupt({"message": "Code failed static security validation.", "payload": payload})
         return {"human_action": "regenerate" if user_decision == "regenerate" else "reject"}
         
    user_decision = interrupt({"message": "Review generated tests.", "payload": payload})
    
    if isinstance(user_decision, str) and user_decision.startswith("regenerate:"):
        reason = user_decision.split(":", 1)[1].strip()
        return {"human_action": "regenerate", "feedback": reason}
        
    return {"human_action": user_decision}