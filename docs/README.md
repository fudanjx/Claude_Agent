# Claude Agent SDK - Multi-Agent System

A versatile, general-purpose agent system built with Claude Agent SDK and AWS Bedrock.

## Features

- **Lead Agent**: Orchestrates tasks with plan-first execution
- **Event-Driven Architecture**: Single event loop with dispatch map
- **File-Based Task Management**: Persistent task graph with dependencies
- **Web Search & Fetch**: Internet access for grounded fact-finding
- **Progressive Implementation**: Start simple, scale as needed

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure AWS:**
   Ensure your AWS profile "work" is configured with Bedrock access:
   ```bash
   aws configure --profile work
   ```

3. **Run the Lead Agent:**
   ```bash
   python lead_agent.py
   ```

## Architecture

```
.agent_state/
├── board/
│   └── tasks.jsonl         # Task board
├── tasks/
│   └── <task_id>/
│       ├── task.json       # Task state
│       ├── context/        # 3-layer compression
│       ├── mail/           # Mailboxes
│       └── logs/           # Event logs
├── mailboxes/              # Agent mailboxes
└── worktrees/              # Isolated work directories
```

## Usage

```python
from lead_agent import LeadAgent

# Create and start the agent
agent = LeadAgent()
agent.run("Your goal here")
```

## Progressive Roadmap

- [x] Phase 1: Foundation (Lead agent, event loop, basic tasks)
- [x] Phase 2: Enhanced (Compression, background jobs, workers)
- [x] Phase 3: Production (Worker skills, error recovery, optimization)

**🎉 ALL PHASES COMPLETE! Production-ready multi-agent system!**
