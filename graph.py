from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState

# Clean, professional imports from our nodes package
from nodes.git import extract_diff
from nodes.review import review_code
from nodes.generation import generate_tests
from nodes.validation import validate_code, human_gate
from nodes.execution import execute_tests

workflow = StateGraph(AgentState)

workflow.add_node("extract", extract_diff)
workflow.add_node("review", review_code)
workflow.add_node("generate", generate_tests)
workflow.add_node("validate", validate_code)
workflow.add_node("gate", human_gate)
workflow.add_node("execute", execute_tests)

def route_after_gate(state: AgentState):
    action = state.get("human_action")
    if action == "approve":
        return "execute"
    elif action == "regenerate":
        return "generate"
    return END

workflow.add_edge(START, "extract")
workflow.add_edge("extract", "review")
workflow.add_edge("review", "generate")
workflow.add_edge("generate", "validate")
workflow.add_edge("validate", "gate")
workflow.add_conditional_edges("gate", route_after_gate)
workflow.add_edge("execute", END)

memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)