import ast
from state import AgentState
from langgraph.types import interrupt

def validate_code(state: AgentState):
    print("\n--- [NODE: AST Security Validation] ---")
    code = state.get("generated_tests", "")
    if code == "Skipped" or code.startswith("Error") or code.startswith("HTTP Error"):
        return {"validation_status": "FAIL", "validation_errors": ["No tests were generated."], "feedback": "Code generation failed."}
        
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
            # POINT 5: Check attributes like os.system()
            elif isinstance(node, ast.Attribute):
                if hasattr(node.value, 'id') and node.value.id in ['os', 'subprocess', 'sys']:
                    errors.append(f"Security: Blocked attribute access '{node.value.id}.{node.attr}'.")
    except SyntaxError as e:
        errors.append(f"Syntax Error: {str(e)}")

    if errors:
        print(f"❌ Static Security Check Failed: {errors}")
        return {"validation_status": "FAIL", "validation_errors": errors, "feedback": str(errors)}
        
    print("✅ Static Security Check Passed (Syntax & Policy only).")
    return {"validation_status": "PASS", "validation_errors": [], "feedback": ""}

def human_gate(state: AgentState):
    print("\n--- [NODE: Human Gate Paused] ---")
    regen_count = state.get("regeneration_count", 0)
    
    # POINT 1: Enforce absolute maximum of 3 regenerations
    if regen_count >= 3:
        print("\n" + "!"*50)
        print("🛑 MAXIMUM REGENERATIONS (3) REACHED. FORCING REJECTION.")
        print("!"*50)
        return {"human_action": "reject"}
    
    payload = {
        "review": state.get("code_review", []), "tests": state.get("generated_tests", ""),
        "validation_status": state.get("validation_status"), "validation_errors": state.get("validation_errors", []),
        "regen_count": regen_count
    }

    msg = "Code failed static security validation." if state.get("validation_status") == "FAIL" else "Review generated tests."
    user_decision = interrupt({"message": msg, "payload": payload})
    
    if isinstance(user_decision, str):
        if user_decision.startswith("regenerate"):
            # POINT 7: Max regenerations check
            if regen_count >= 3:
                print("\n⚠️ Maximum regeneration attempts (3) reached. Forcing rejection.")
                return {"human_action": "reject"}
                
            reason = user_decision.split(":", 1)[1].strip() if ":" in user_decision else "Human requested regeneration."
            # POINT 4: Auto-append AST failures to the feedback
            if state.get("validation_status") == "FAIL":
                reason += f" | Static Validation Failed Because: {state.get('validation_errors')}"
                
            return {"human_action": "regenerate", "feedback": reason, "regeneration_count": regen_count + 1}
            
        elif user_decision == "approve":
            if state.get("validation_status") == "FAIL":
                return {"human_action": "reject"}
            return {"human_action": "approve"}
            
    return {"human_action": "reject"}