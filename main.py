from graph import agent
from langgraph.types import Command

if __name__ == "__main__":
    # A unique thread ID is required so LangGraph knows which session to pause/resume
    thread = {"configurable": {"thread_id": "review-session-1"}}
    
    print("\n🚀 Starting Agent Pipeline...")
    
    # 1. Pass {} instead of None to start the graph
    for event in agent.stream({}, config=thread):
        pass 
        
    # 2. Extract the paused state data
    state = agent.get_state(thread)
    pending_interrupts = state.tasks[0].interrupts if state.tasks else []
    
    if pending_interrupts:
        payload = pending_interrupts[0].value
        print("\n" + "="*40)
        print("🛑 AGENT PAUSED: HUMAN APPROVAL REQUIRED")
        print("="*40)
        print(payload["tests"])
        print("="*40)
        
        # 3. Wait for human command
        user_input = input("\nType 'approve' to execute tests, or anything else to abort: ")
        
        print("\nResuming graph execution...")
        # 4. Resume the graph with the command
        for event in agent.stream(Command(resume=user_input), config=thread):
            pass
            
        final_state = agent.get_state(thread).values
        print("\n--- FINAL TEST LOGS ---")
        print(final_state.get("test_execution_logs", ""))