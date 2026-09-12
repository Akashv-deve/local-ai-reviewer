from graph import agent
from langgraph.types import Command

def run_agent():
    thread = {"configurable": {"thread_id": "portfolio-demo-3"}}
    print("\n🚀 Starting Upgraded Agent Pipeline...")
    
    # 1. Initial run of the graph
    for event in agent.stream({}, config=thread):
        pass 
        
    # 2. Main loop to handle multiple interrupts (e.g., during regeneration loops)
    while True:
        state = agent.get_state(thread)
        
        # If there are no next tasks, the graph has reached the END node
        if not state.next:
            break
            
        pending_interrupts = state.tasks[0].interrupts if state.tasks else []
        
        if pending_interrupts:
            data = pending_interrupts[0].value
            payload = data.get("payload", {})
            
            print("\n" + "="*50)
            print("🛑 AGENT PAUSED: HUMAN APPROVAL REQUIRED")
            print("="*50)
            
            # Print structured JSON Review Array or Review Error
            reviews = payload.get("review", [])
            metrics = payload.get("review_metrics", {})
            review_error = payload.get("review_error")
            
            if review_error:
                print(f"\n⚠️ AI Code Review failed")
                print(f"Reason: {review_error}")
            else:
                print(f"\n📊 AI CODE REVIEW (Total: {metrics.get('total', 0)} | Valid: {metrics.get('valid', 0)} | Rejected: {metrics.get('invalid', 0)})")
                if reviews:
                    for rev in reviews:
                        print(f"[{rev.get('severity', 'INFO')}] {rev.get('file', 'Unknown')}:{rev.get('line', '?')} - {rev.get('issue', '')}")
                        print(f"   ↳ Fix: {rev.get('recommendation', '')}")
                else:
                    print("No valid issues found.")
                 
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
            # Resume the graph with the user's command
            for event in agent.stream(Command(resume=resume_command), config=thread):
                pass
        else:
            # If there are next tasks but no interrupts, something unexpected happened
            break
            
    # 3. Final Execution Report
    final_state = agent.get_state(thread).values
    if final_state.get("test_execution_logs"):
        print("\n" + "="*50)
        print("📊 FINAL EXECUTION REPORT (Subprocess Mode)")
        print("="*50)
        print(f"Status: {final_state.get('execution_status', 'N/A')}")
        print(f"✅ Passed: {final_state.get('tests_passed', 0)}")
        print(f"❌ Failed: {final_state.get('tests_failed', 0)}")
        print(f"⚠️ Errors: {final_state.get('tests_errors', 0)}")
        print("-" * 50)
        print("RAW LOGS (Truncated):")
        print(final_state["test_execution_logs"][-1500:]) 
        print("="*50)
    elif final_state.get("human_action") == "reject":
        print("\nWorkflow aborted by human.")

if __name__ == "__main__":
    run_agent()