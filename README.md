# Local AI Code Reviewer

A privacy-first, resource-efficient AI developer agent that runs locally and reviews Git code changes, generates targeted tests, validates AI-generated code, and executes approved tests.

Built with **LangGraph + Ollama + Qwen2.5:3b + Python AST + pytest**.

## Demo

**[▶ Watch the full project demo](./demo/local-ai-reviewer-demo.mp4)**

## Human-in-the-Loop Recovery

During the demo, the local LLM initially generates an incorrect test suite.
The human reviewer rejects the result and provides feedback.
The agent then regenerates the tests, validates the new code, and the corrected
test suite passes execution.

This demonstrates that the system is designed to handle imperfect LLM output
rather than blindly executing generated code.

The demo shows the complete workflow:

```text
Git Change
    ↓
Application File Filtering
    ↓
AI Code Review
    ↓
Targeted Test Generation
    ↓
AST Validation
    ↓
Human Approval
    ├── Approve ──→ Test Execution
    ├── Regenerate → Generate Again
    └── Reject ───→ Stop
    ↓
Execution Report
```

## Why I Built This

AI coding tools can generate useful code and tests, but their output should not automatically be trusted or executed.

This project explores a safer developer workflow where AI-generated tests pass through:

* targeted code selection
* structured AI review
* static AST validation
* human approval
* controlled subprocess execution
* execution-result analysis

The entire workflow runs locally using a local LLM through Ollama.

## Key Features

### 🔍 Git-Aware Code Analysis

The agent detects changes using:

```bash
git diff HEAD
```

Only relevant Python application files are passed to the AI pipeline.

Project infrastructure such as the agent's own nodes, graph, and state files is excluded from analysis.

### 🤖 Local AI Code Review

A local Qwen2.5:3b model reviews the changed application code and returns structured findings containing:

* severity
* category
* file
* line
* issue
* recommendation

Review results are validated before being shown to the user.

### 🧪 Targeted Test Generation

The AI generates pytest tests specifically for the changed application files.

Human feedback can be supplied when regeneration is requested, allowing the agent to iterate on its previous output.

### 🛡️ AST Validation

Generated Python code is parsed using Python's `ast` module before execution.

The validation layer checks for:

* syntax errors
* restricted imports
* dangerous function calls
* restricted system attribute access

This is a **static policy check**, not a complete security system.

### 👤 Human-in-the-Loop

The agent pauses using LangGraph's `interrupt()` before executing generated tests.

The developer can:

```text
approve
regenerate
reject
```

Regeneration can include a reason that is passed back to the AI.

A maximum of three regeneration attempts is enforced.

### ⚙️ Controlled Test Execution

Approved tests are executed through a subprocess with a 30-second timeout.

The agent captures pytest output and reports:

* passed tests
* failed tests
* errors
* timeout status
* raw execution logs

Generated test files are temporary and removed after execution.

> **Important:** This project uses controlled subprocess execution. It is **not a security sandbox** and should not be treated as a safe environment for arbitrary untrusted code.

## Architecture

```text
                    ┌─────────────────┐
                    │   Git Diff      │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ File Filtering  │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │  AI Code Review │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ Test Generation │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │ AST Validation │
                    └────────┬────────┘
                             ↓
                    ┌─────────────────┐
                    │  Human Gate     │
                    └───────┬─┬───────┘
                            │ │
                 regenerate │ │ approve
                            │ ↓
                            │ ┌─────────────────┐
                            │ │ Test Execution  │
                            │ └────────┬────────┘
                            │          ↓
                            │ ┌─────────────────┐
                            │ │ Execution Report│
                            │ └─────────────────┘
                            ↓
                    Test Generation
```

The workflow is implemented as a LangGraph `StateGraph`.

## Project Structure

```text
local-ai-reviewer/
│
├── calculator.py
├── graph.py
├── main.py
├── state.py
│
├── nodes/
│   ├── git.py
│   ├── review.py
│   ├── generation.py
│   ├── validation.py
│   └── execution.py
│
├── tests/
├── requirements.txt
└── .gitignore
```

## Tech Stack

| Technology | Purpose                  |
| ---------- | ------------------------ |
| Python     | Core implementation      |
| LangGraph  | Stateful agent workflow  |
| Ollama     | Local LLM runtime        |
| Qwen2.5:3b | Local AI model           |
| Python AST | Static validation        |
| pytest     | Generated test execution |
| Git        | Change detection         |

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/Akashv-deve/local-ai-reviewer.git
cd local-ai-reviewer
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Windows:

```bash
venv\Scripts\activate
```

Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Ollama

Install Ollama and make sure it is running locally.

Then pull the model:

```bash
ollama pull qwen2.5:3b
```

Verify that Ollama is available before starting the agent.

## Running the Agent

Make a change to an application Python file.

For example, modify:

```text
calculator.py
```

Then run:

```bash
python main.py
```

The agent will:

1. Detect the Git diff.
2. Filter relevant application files.
3. Review the changed code.
4. Generate targeted pytest tests.
5. Validate the generated Python using AST checks.
6. Pause for human approval.
7. Regenerate if requested.
8. Execute approved tests.
9. Display a structured execution report.

## Example Interaction

```text
🚀 Starting Upgraded Agent Pipeline...

--- [NODE: Extracting Git Diff] ---

--- [NODE: AI Code Review] ---
🤖 AI is reviewing code...

--- [NODE: Generating Tests via Local LLM] ---
🤖 AI is typing...

--- [NODE: AST Security Validation] ---
✅ Static Security Check Passed

==================================================
🛑 AGENT PAUSED: HUMAN APPROVAL REQUIRED
==================================================

📊 AI CODE REVIEW
[HIGH] calculator.py:10 - Potential division by zero
   ↳ Fix: Add appropriate input handling.

🧪 GENERATED TESTS:
...

Commands -> 'approve', 'regenerate', 'reject':
```

After approval:

```text
==================================================
📊 FINAL EXECUTION REPORT (Subprocess Mode)
==================================================
Status: PASS
✅ Passed: 5
❌ Failed: 0
⚠️ Errors: 0
==================================================
```

## Design Decisions

### Why Local AI?

The project uses Ollama with a small local model so source code can remain on the developer's machine.

This avoids requiring source code to be sent to an external AI API for the core workflow.

The smaller Qwen2.5:3b model also keeps local resource requirements more practical for development on a typical laptop.

### Why LangGraph?

The workflow is not simply a sequence of LLM calls.

It requires:

* persistent state
* conditional routing
* human interruption
* regeneration loops
* controlled progression between stages

LangGraph provides these workflow primitives directly.

### Why AST Validation?

The AI-generated output is treated as untrusted Python code.

AST analysis allows the project to inspect the structure of generated code before execution and reject selected dangerous constructs.

### Why Human Approval?

AI-generated tests should not automatically execute simply because an LLM produced them.

The human gate provides an explicit approval point between generation and execution.

## Limitations

This project intentionally remains lightweight.

* The AI review depends on the capabilities of the local model.
* AST validation only checks defined policies and is not comprehensive security protection.
* Subprocess execution is not a true sandbox.
* The project is designed for local developer workflows rather than arbitrary public code execution.
* Ollama and the selected model must be installed locally.

## What This Project Demonstrates

This project focuses on practical AI engineering rather than a simple chatbot.

It demonstrates:

* agentic workflow design
* stateful AI orchestration
* local LLM integration
* structured LLM output validation
* prompt engineering
* AI-generated test creation
* static code analysis
* human-in-the-loop systems
* conditional agent routing
* feedback-driven regeneration
* controlled subprocess execution
* error handling and result reporting

## Future Improvements

Possible future improvements include:

* richer static analysis
* broader language support
* stronger execution isolation
* additional local models
* IDE integration
* GitHub pull-request integration

These are intentionally outside the current lightweight implementation.

## Author

**Akash V**

Built as a portfolio project to explore practical local AI agents and developer tooling.
