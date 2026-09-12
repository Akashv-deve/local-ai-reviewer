from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import extract_diff, generate_tests, validate_code, human_gate, execute_tests

workflow = StateGraph(AgentState)

workflow.add_node("extract", extract_diff)
workflow.add_node("generate", generate_tests)
workflow.add_node("validate", validate_code)
workflow.add_node("gate", human_gate)
workflow.add_node("execute", execute_tests)

# This function controls where the graph goes after the human pauses
def route_after_gate(state: AgentState):
    action = state.get("human_action")
    if action == "approve":
        return "execute"
    elif action == "regenerate":
        return "generate"  # Loops backward to the AI
    else:
        return END         # Aborts the process

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "generate")
workflow.add_edge("generate", "validate")
workflow.add_edge("validate", "gate")

# Attach the conditional router
workflow.add_conditional_edges("gate", route_after_gate)
workflow.add_edge("execute", END)

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)