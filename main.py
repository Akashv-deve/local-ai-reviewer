from graph import agent
from langgraph.types import Command

if __name__ == "__main__":
    thread = {"configurable": {"thread_id": "portfolio-demo-2"}}
    print("\n🚀 Starting Upgraded Agent Pipeline...")
    
    for event in agent.stream({}, config=thread):
        pass 
        
    state = agent.get_state(thread)
    pending_interrupts = state.tasks[0].interrupts if state.tasks else []
    
    if pending_interrupts:
        data = pending_interrupts[0].value
        payload = data.get("payload", {})
        
        print("\n" + "="*50)
        print("🛑 AGENT PAUSED: HUMAN APPROVAL REQUIRED")
        print("="*50)
        
        # Print structured JSON Review Array
        reviews = payload.get("review", [])
        if reviews:
            print("\n📊 AI CODE REVIEW FINDINGS:")
            for rev in reviews:
                print(f"[{rev.get('severity', 'INFO')}] {rev.get('file', 'Unknown')}:{rev.get('line', '?')} - {rev.get('issue', '')}")
                print(f"   ↳ Fix: {rev.get('recommendation', '')}")
        else:
             print("\n📊 AI CODE REVIEW: No issues found.")
             
        print("\n🧪 GENERATED TESTS:")
        print(payload.get("tests", ""))
        print("="*50)
        
        user_input = input("\nCommands -> 'approve', 'regenerate', 'reject': ").strip().lower()
        
        if user_input == "regenerate":
            reason = input("Reason for regeneration (this will be fed to the AI): ")
            resume_command = f"regenerate:{reason}"
        else:
            resume_command = user_input
            
        print(f"\nExecuting command...")
        for event in agent.stream(Command(resume=resume_command), config=thread):
            pass
            
        final_state = agent.get_state(thread).values
        if final_state.get("test_execution_logs"):
            print("\n" + "="*50)
            print("📊 FINAL EXECUTION REPORT (Subprocess Mode)")
            print("="*50)
            print(f"Static Validation: {final_state.get('validation_status', 'UNKNOWN')}")
            print(f"✅ Tests Passed: {final_state.get('tests_passed', 0)}")
            print(f"❌ Tests Failed/Errors: {final_state.get('tests_failed', 0)}")
            print("-" * 50)
            print("RAW LOGS (Truncated):")
            print(final_state["test_execution_logs"][-1500:]) 
            print("="*50)