from graph import agent
from langgraph.types import Command

if __name__ == "__main__":
    thread = {"configurable": {"thread_id": "review-session-2"}}
    print("\n🚀 Starting Upgraded Agent Pipeline...")
    
    for event in agent.stream({}, config=thread):
        pass 
        
    state = agent.get_state(thread)
    pending_interrupts = state.tasks[0].interrupts if state.tasks else []
    
    if pending_interrupts:
        payload = pending_interrupts[0].value
        print("\n" + "="*50)
        print("🛑 AGENT PAUSED: HUMAN APPROVAL REQUIRED")
        print("="*50)
        if "errors" in payload:
            print(f"VALIDATION ERRORS: {payload['errors']}")
        else:
            print(payload["tests"])
        print("="*50)
        
        user_input = input("\nCommands -> 'approve', 'regenerate', 'reject': ").strip().lower()
        
        print(f"\nExecuting command: {user_input}...")
        for event in agent.stream(Command(resume=user_input), config=thread):
            pass
            
        final_state = agent.get_state(thread).values
        if final_state.get("test_execution_logs"):
            print("\n" + "="*50)
            print("📊 FINAL EXECUTION REPORT")
            print("="*50)
            print(f"✅ Tests Passed: {final_state.get('tests_passed', 0)}")
            print(f"❌ Tests Failed: {final_state.get('tests_failed', 0)}")
            print("-" * 50)
            print("RAW LOGS:")
            print(final_state["test_execution_logs"])
            print("="*50)