from state import AgentState
from nodes import extract_diff

# Temporary test to verify our modular imports work
if __name__ == "__main__":
    dummy_state = AgentState()
    result = extract_diff(dummy_state)
    print("EXTRACTED DIFF FROM MODULAR ARCHITECTURE:\n", result["git_diff"])