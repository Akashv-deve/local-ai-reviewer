import ast
from state import AgentState

def validate_code(state: AgentState):
    print("--- [NODE: Validating AI Code via AST] ---")
    code = state.get("generated_tests", "")
    errors = []

    try:
        # 1. Check for basic Python syntax errors
        tree = ast.parse(code)
        
        # 2. Traverse the tree looking for dangerous imports/calls
        for node in ast.walk(tree):
            if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name in ['os', 'subprocess', 'sys', 'shutil']:
                        errors.append(f"Security Violation: Import of '{alias.name}' is blocked.")
            
            elif isinstance(node, ast.Call):
                if hasattr(node.func, 'id') and node.func.id in ['eval', 'exec', 'open']:
                    errors.append(f"Security Violation: Built-in function '{node.func.id}' is blocked.")

    except SyntaxError as e:
        errors.append(f"Syntax Error: {str(e)}")

    status = "FAIL" if errors else "PASS"
    return {"validation_status": status, "validation_errors": errors}