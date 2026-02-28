# Quick Start Guide

## Installation

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Verify AWS credentials:**
   ```bash
   aws sts get-caller-identity --profile work
   ```

   If this fails, configure your AWS profile:
   ```bash
   aws configure --profile work
   ```

## Running Your First Agent

### Option 1: Interactive Mode

```bash
python lead_agent.py
```

Then enter your goal when prompted. Examples:
- "Research the top 3 Python web frameworks and create a comparison table"
- "Analyze the files in the current directory and create a summary"
- "Create a task breakdown for building a REST API"

### Option 2: Command Line

```bash
python lead_agent.py "Your goal here"
```

Example:
```bash
python lead_agent.py "List all files in the current directory and categorize them by type"
```

## Example Session

```
🎯 You: Research Python async frameworks and create a summary

💬 Lead:
Goal: Research Python async frameworks and create a summary

Assumptions:
- Focus on popular, actively maintained frameworks
- Include asyncio, Trio, and Curio

Plan:
1. Use bash to search for information about async frameworks
2. Create a task for this research
3. Gather key information about each framework
4. Write summary to a file

[Agent executes tools...]

Deliverable:
Summary written to .agent_state/worktrees/T-20260228-0001/async_frameworks_summary.md

Next Actions:
1. Review the summary file
2. Add more frameworks if needed
3. Create comparison table
```

## Understanding the Output

The agent creates a structured state directory:

```
.agent_state/
├── board/
│   └── tasks.jsonl         # All tasks (append-only log)
├── tasks/
│   └── T-20260228-0001/    # Each task gets a directory
│       ├── task.json       # Current task state
│       ├── context/        # Memory layers
│       ├── mail/           # Communications
│       └── logs/           # Tool call logs
├── logs/
│   ├── events.jsonl        # All events
│   └── tool_calls.jsonl    # All tool calls
└── worktrees/
    └── T-20260228-0001/    # Task working directory
        └── ...             # Generated files
```

## Commands in Interactive Mode

- `/tasks` - List all tasks and their status
- `/quit` - Exit the agent
- Any other text - Send as a goal to the agent

## Tips

1. **Be Specific**: The clearer your goal, the better the agent performs
2. **Check Tasks**: Use `/tasks` to see what the agent is working on
3. **Review Outputs**: Check `.agent_state/worktrees/<task_id>/` for generated files
4. **Logs**: Check `.agent_state/logs/` if you need to debug

## What's Next?

- Phase 1 ✅: Basic Lead agent with task management
- Phase 2 🚧: 3-layer compression, background jobs
- Phase 3 📋: Worker teammates, self-claim system

The current implementation gives you a working Lead agent that can:
- Plan and execute multi-step tasks
- Use bash, file operations, and task management
- Maintain persistent state across runs
- Log all operations for debugging

More features will be added progressively!
