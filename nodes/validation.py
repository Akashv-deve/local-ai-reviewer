import ast
from state import AgentState
from langgraph.types import interrupt

def validate_code(state: AgentState):
    print("\n--- [NODE: AST Security Validation] ---")
    code = state.get("generated_tests", "")
    errors = []
    
    try:
        tree = ast.parse(code)
        for node in ast.walk(tree):
            # 1. Catch malicious imports
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys', 'shutil']:
                        errors.append(f"Security: Blocked import '{alias.name}'.")
            
            # 2. Catch dangerous function calls
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec', 'open', '__import__']:
                    errors.append(f"Security: Blocked function call '{node.func.id}()'.")
                    
    except SyntaxError as e:
        errors.append(f"Syntax Error: {str(e)}")

    if errors:
        print(f"❌ Validation Failed: {errors}")
        return {"validation_status": "FAIL", "validation_errors": errors, "feedback": str(errors)}
        
    print("✅ AST Validation Passed.")
    return {"validation_status": "PASS", "validation_errors": [], "feedback": ""}

def human_gate(state: AgentState):
    print("\n--- [NODE: Human Gate Paused] ---")
    
    # Surface the JSON Code Review to the human
    review = state.get("code_review", {})
    if review and "error" not in review and "status" not in review:
        print(f"\n📊 AI REVIEW:\nSeverity: {review.get('severity')}\nCategory: {review.get('category')}\nIssue: {review.get('issue')}\nFix: {review.get('recommendation')}\n")

    if state.get("validation_status") == "FAIL":
         user_decision = interrupt({"message": "Code failed AST security validation.", "errors": state["validation_errors"]})
         # If rejected by AST, automatically feed it back to regeneration
         return {"human_action": user_decision if user_decision in ['reject', 'approve'] else 'regenerate'}
         
    user_decision = interrupt({"message": "Review generated tests.", "tests": state["generated_tests"]})
    
    # If the user manually types 'regenerate', set the feedback so the AI knows
    if user_decision == "regenerate":
        return {"human_action": "regenerate", "feedback": "Human reviewer requested regeneration. Improve the logic and test coverage."}
        
    return {"human_action": user_decision}