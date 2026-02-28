# Python Module Summary
> Generated: 2026-02-28 20:17:45

This document summarizes all Python modules found in the project root. The codebase implements a **Claude-powered Lead Agent** that runs on AWS Bedrock, manages tasks via a file-based task board, and dispatches tool calls in an agentic loop.

---

## 📦 Module Index

| File | Purpose |
|---|---|
| `config.py` | Global configuration & directory initialization |
| `prompts.py` | System prompt definitions for Lead and Worker agents |
| `task_manager.py` | File-based task lifecycle and persistence |
| `tools.py` | Tool handler implementations and dispatcher |
| `lead_agent.py` | Core agent orchestration loop (Claude ↔ Bedrock) |
| `example.py` | Runnable usage examples |
| `test_agent.py` | Quick smoke-test for the agent setup |
| `verify_setup.py` | Environment and dependency verification checks |

---

## 🔍 Detailed Summaries

### `config.py`
**Purpose:** Central configuration hub for the entire project.

- Defines **AWS settings**: profile name (`work`), region (`us-east-1`), and Bedrock model ID (`global.anthropic.claude-sonnet-4-6`).
- Declares **path constants** for the agent state directory tree: `.agent_state/board/`, `.agent_state/tasks/`, `.agent_state/mailboxes/`, `.agent_state/worktrees/`.
- Sets **agent tuning constants**: `MAX_ITERATIONS=50`, `TEMPERATURE=1.0`, `MAX_TOKENS=4096`, compression thresholds.
- Provides `init_directories()` — creates all required state directories and the `tasks.jsonl` board file on first run.

---

### `prompts.py`
**Purpose:** Stores the system prompt strings injected into Claude at runtime.

- `LEAD_AGENT_PROMPT` — The full system prompt for the orchestrator agent ("Lead"). Defines its core principles (plan-first, lazy knowledge, grounded claims, etc.), response format, available tools, and safety rules.
- `WORKER_AGENT_PROMPT` — System prompt for a future collaborator agent ("Worker"). Specifies that workers scan the task board, claim tasks, work in isolated directories, and report back to Lead via mailboxes.

---

### `task_manager.py`
**Purpose:** Implements the file-based task graph and full task lifecycle management.

- **`Task` (dataclass):** Data model for a task, holding `task_id`, `goal`, `status` (`OPEN → CLAIMED → IN_PROGRESS → BLOCKED → DONE`), `owner`, `deps`, `priority`, `workdir`, `inputs`, `outputs`, and `acceptance_criteria`.
- **`TaskManager` class:**
  - `create_task()` — Generates a unique dated ID (e.g. `T-20260228-0001`), writes the task to an append-only `tasks.jsonl` log, and scaffolds a full directory tree (`context/`, `mail/`, `logs/`, `outputs/`, `worktrees/`) with a `task.json` and `README.md`.
  - `get_task()` / `update_task()` — Reads/writes the canonical `task.json` per task and appends an update record to the log.
  - `list_tasks()` — Scans task directories for latest state; supports filtering by `status` or `owner`.
  - `get_task_summary()` — Returns a count of tasks in each status bucket.

---

### `tools.py`
**Purpose:** Implements all agent tool handlers and the central dispatcher.

- **`ToolHandler` (base class):** Provides `log_tool_call()` — persists every tool invocation (name, params, result, timestamp) to `.agent_state/logs/tool_calls.jsonl`.
- **`BashTool`:** Runs arbitrary shell commands via `subprocess.run` with configurable timeout; returns `stdout`, `stderr`, and `exit_code`.
- **`ReadFileTool`:** Reads and returns file contents; validates existence and file-vs-directory.
- **`WriteFileTool`:** Writes text to a path, creating parent directories as needed.
- **`ListDirTool`:** Lists a directory's contents with name, type, and file size.
- **`ToolDispatcher`:** Holds a `handlers` dispatch map keyed by tool name; `dispatch()` routes calls to the correct handler. Also exposes `get_tool_definitions()` which returns the full Claude API-compatible JSON schema for all tools (bash, read_file, write_file, list_dir, create_task, update_task, list_tasks).

---

### `lead_agent.py`
**Purpose:** The main agent orchestration engine — the agentic event loop.

- **`LeadAgent` class:**
  - `__init__()` — Initializes AWS Bedrock client (via `boto3`), `ToolDispatcher`, `TaskManager`, and an event log at `.agent_state/logs/events.jsonl`.
  - `_call_claude()` — Sends the current `messages[]` conversation history plus tool definitions to Claude via `bedrock.invoke_model`; handles the full Bedrock request/response lifecycle.
  - `_handle_tool_use()` — Handles tool-use blocks from Claude: routes `create_task`/`update_task`/`list_tasks` to `TaskManager`, all other tools to `ToolDispatcher`; returns structured `tool_result` blocks.
  - `_process_response()` — Parses Claude's response content, prints text blocks, collects tool results, and decides whether to continue the loop.
  - `run(goal)` — Entry point for a single goal: logs the event, calls Claude, and runs the loop up to `MAX_ITERATIONS`.
  - `run_interactive()` — REPL mode with `/tasks` and `/quit` commands for interactive use.

---

### `example.py`
**Purpose:** Provides three ready-to-run demonstrations of the `LeadAgent`.

- `example_1_simple_research()` — Asks the agent to check the Python version and produce a brief report.
- `example_2_task_breakdown()` — Asks the agent to decompose building a TODO app into sub-tasks (design, backend, frontend, testing).
- `example_3_file_analysis()` — Asks the agent to analyze all Python files and write a module summary (i.e., the task currently being performed).
- Can be invoked with `python example.py [1|2|3]` or run without arguments to see the menu.

---

### `test_agent.py`
**Purpose:** Minimal smoke test to verify the agent pipeline is functional end-to-end.

- Imports `LeadAgent`, instantiates it, and runs a trivial goal (`"What is 2+2?"`).
- Prints success or full traceback on failure.
- Intended for quick post-setup verification.

---

### `verify_setup.py`
**Purpose:** Pre-flight environment verification tool — run this before using the agent.

Runs 5 checks in sequence:
1. **Python Version** — Requires Python 3.8+.
2. **Dependencies** — Checks that `boto3`, `anthropic`, and `pydantic` are importable.
3. **AWS Credentials** — Validates the `work` AWS profile via `sts.get_caller_identity()`.
4. **Project Structure** — Confirms all required project files exist on disk.
5. **Bedrock Access** (optional, only if all above pass) — Makes a minimal live API call to verify Claude model access.

Exits with code `0` on full success, `1` on any failure, with actionable remediation guidance printed to stdout.

---

## 🗺️ Architecture Overview

```
User / CLI
    │
    ▼
lead_agent.py  ──────────────────────────── AWS Bedrock (Claude)
  │  LeadAgent                                   ▲
  │  ├── _call_claude()  ──────────────────────►│
  │  ├── _handle_tool_use()                      │
  │  └── run() / run_interactive()               │
  │                                              │
  ├── tools.py (ToolDispatcher)                  │
  │   ├── BashTool        → subprocess           │
  │   ├── ReadFileTool    → filesystem           │
  │   ├── WriteFileTool   → filesystem           │
  │   └── ListDirTool     → filesystem           │
  │                                              │
  ├── task_manager.py (TaskManager)              │
  │   ├── tasks.jsonl (append-only log)          │
  │   └── .agent_state/tasks/<id>/task.json      │
  │                                              │
  ├── config.py  (constants & init_directories)  │
  └── prompts.py (LEAD_AGENT_PROMPT) ───────────►│
```
