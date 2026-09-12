from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from state import AgentState
from nodes import extract_diff, generate_tests, human_gate, execute_tests

workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("extract", extract_diff)
workflow.add_node("generate", generate_tests)
workflow.add_node("gate", human_gate)
workflow.add_node("execute", execute_tests)

# Define Logic Flow
workflow.add_edge(START, "extract")
workflow.add_edge("extract", "generate")
workflow.add_edge("generate", "gate")
workflow.add_edge("gate", "execute")
workflow.add_edge("execute", END)

# Compile with memory persistence
memory = MemorySaver()
agent = workflow.compile(checkpointer=memory)