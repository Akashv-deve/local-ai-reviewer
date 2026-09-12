# Local AI Code Review & Test Generation Agent

> **Demo:** [Insert link to 60-second Loom/YouTube video here]

A privacy-first, resource-efficient local AI developer agent. This project detects application code changes in a Git repository, performs a code review, generates targeted `pytest` tests, validates the generated tests using deterministic AST parsing, and executes them in a controlled subprocess—all coordinated via a LangGraph state machine.

Built to run entirely locally on limited hardware (e.g., an i5 laptop) without relying on Docker overhead or cloud API keys.

## Architecture & Workflow

The agent operates on a cyclic LangGraph state machine (`StateGraph`) using local LLM inference via Ollama. 

```text
Git Diff (HEAD)
   ↓
Filter Infrastructure (Target Application Files Only)
   ↓
AI Code Review (JSON Structured Output)
   ↓
Targeted Test Generation
   ↓
AST Static Validation (Block malicious imports/calls)
   ↓
Human-in-the-Loop (LangGraph interrupt)
   ├── Approve → Subprocess Execution (30s timeout) → Results Report
   ├── Regenerate (with human feedback) → Generate Again (Max 3 attempts)
   └── Reject → Abort Workflow