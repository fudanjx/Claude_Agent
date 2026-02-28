# Phase 2 Feature Guide

Phase 2 adds advanced capabilities for infinite sessions, async operations, and multi-agent coordination.

## 🎯 New Features

### 1. Three-Layer Compression Strategy

Enables infinite sessions without losing context:

**Layer 1: Working Set** (< 2000 chars)
- Current goal, active plan, immediate context
- Updated every event
- Auto-compresses when threshold exceeded

**Layer 2: Rolling Summary** (< 5000 chars)
- What's been done, key facts, decisions made
- Compressed from working set
- Includes pointers to artifacts

**Layer 3: Archive** (chunked files)
- Older details stored as numbered chunks
- Retrieved on-demand (lazy loading)
- Lossless history

**Usage:**
```python
from compression import CompressionManager

# Initialize for a task
compression = CompressionManager(task_dir)

# Create initial working set
compression.create_initial_working_set(goal="...", plan="...")

# Check if compression needed
if compression.should_compress(messages):
    summary = compression.compress_messages_to_summary(...)
    compression.update_rolling_summary(summary)

# Get context for injection
context = compression.get_context_for_injection()
```

### 2. Background Job System

Run long-running commands without blocking:

**Features:**
- Async execution in separate threads
- Output capture (stdout/stderr)
- Job status tracking
- Callback support

**Usage:**
```python
from background_jobs import BackgroundJobManager

job_mgr = BackgroundJobManager(state_dir)

# Spawn a job
job = job_mgr.spawn_job("sleep 10 && echo done")
print(f"Job {job.job_id} started")

# Check status later
job = job_mgr.get_job(job.job_id)
print(f"Status: {job.status}")

# Get output
if job.status == "COMPLETED":
    output = job_mgr.get_job_output(job.job_id)
    print(output["stdout"])
```

**Lead Agent Tools:**
- `spawn_job(command)` - Start background job
- `get_job_status(job_id)` - Check job status
- `get_job_output(job_id)` - Get job output
- `list_jobs()` - List all jobs

### 3. Worker Teammate Agents

Autonomous agents that claim and execute tasks:

**Features:**
- Self-scan task board for claimable tasks
- Atomic task claiming
- Isolated execution context
- Mailbox-based reporting

**Starting a Worker:**
```bash
# Terminal 1 - Lead agent
source .venv/bin/activate
python lead_agent.py

# Terminal 2 - Worker
source .venv/bin/activate
python worker_agent.py Worker_alpha

# Terminal 3 - Another worker
python worker_agent.py Worker_beta
```

**Worker Behavior:**
1. Scans task board every N seconds
2. Finds OPEN tasks with no owner
3. Checks dependencies are satisfied
4. Claims task atomically
5. Executes in isolated context
6. Reports progress/completion via mailbox

### 4. Mailbox Communication Protocol

Structured agent-to-agent messaging:

**Message Types:**
- `REQUEST` - Lead asks worker to do something
- `RESPONSE` - Worker accepts/declines/clarifies
- `CLAIM` - Worker claims a task
- `PROGRESS` - Worker reports progress
- `COMPLETE` - Worker reports completion
- `BLOCKED` - Worker reports blockage

**Usage:**
```python
from mailbox import MailboxManager

mailbox = MailboxManager(state_dir)

# Send a message
msg = mailbox.create_request_message(
    from_agent="Lead",
    to_agent="Worker_alpha",
    task_id="T-xxx",
    intent="research",
    goal="Research Python frameworks",
    priority="high"
)

# Read inbox
messages = mailbox.read_inbox("Lead", mark_read=False)
for msg in messages:
    print(f"From {msg.from_agent}: {msg.type}")
```

**Lead Agent Tools:**
- `read_inbox()` - Check messages from workers
- `send_message(to_agent, msg_type, task_id, body)` - Send message

## 🚀 Quick Start

### Example 1: Background Job

```bash
source .venv/bin/activate
python lead_agent.py

# Then type:
Create a task that spawns a background job to download something
```

The agent will use `spawn_job` tool and continue planning while the job runs.

### Example 2: Multi-Agent Task Execution

```bash
# Terminal 1 - Create tasks
python phase2_examples.py 2

# Terminal 2 - Start worker
python worker_agent.py Worker_alpha

# Terminal 3 - Start another worker
python worker_agent.py Worker_beta

# Watch workers claim and execute tasks autonomously
```

### Example 3: Compression Demo

```bash
python phase2_examples.py 4
```

Shows how compression layers work and persist state.

## 📋 Interactive Mode Commands

New commands in Phase 2:

```
/tasks   - List all tasks (shows owner now)
/jobs    - List background jobs
/inbox   - Check messages from workers
/workers - Show how to start workers
/quit    - Exit
```

## 🔧 Architecture

```
Lead Agent
├── Compression Manager (per task)
├── Background Job Manager
├── Mailbox Manager
└── Task Manager

Worker Agents (autonomous)
├── Scan task board
├── Claim tasks
├── Execute in isolation
└── Report via mailbox
```

## 📁 Directory Structure

```
.agent_state/
├── board/
│   └── tasks.jsonl
├── tasks/
│   └── T-xxx/
│       ├── task.json
│       ├── context/
│       │   ├── working_set.md      [Layer 1]
│       │   ├── rolling_summary.md  [Layer 2]
│       │   └── archive/            [Layer 3]
│       │       ├── chunk_0001.md
│       │       └── chunk_0002.md
│       ├── mail/
│       │   ├── inbox/
│       │   └── outbox/
│       └── logs/
├── jobs/
│   ├── job_xxx.json
│   ├── job_xxx.stdout
│   └── job_xxx.stderr
├── mailboxes/
│   ├── Lead/
│   │   ├── inbox/
│   │   └── outbox/
│   └── Worker_alpha/
│       ├── inbox/
│       └── outbox/
└── worktrees/
    └── T-xxx/
```

## 🎓 Best Practices

1. **Use Background Jobs** for:
   - Downloads
   - Long computations
   - External API calls with retries
   - File processing

2. **Use Workers** for:
   - Parallel research tasks
   - Independent analysis
   - Data processing pipelines
   - Multi-step workflows

3. **Use Compression** for:
   - Long conversations (> 10 iterations)
   - Complex multi-task projects
   - Resumable sessions

4. **Use Mailbox** for:
   - Worker coordination
   - Status updates
   - Error reporting
   - Progress tracking

## 🐛 Troubleshooting

**Workers not claiming tasks:**
- Check task status: `python lead_agent.py` > `/tasks`
- Ensure task status is "OPEN" with no owner
- Check dependencies are satisfied

**Background jobs stuck:**
- List jobs: `/jobs` in interactive mode
- Check job output: agent can use `get_job_output` tool
- Jobs timeout after subprocess completion

**Compression not triggering:**
- Compression checks every 5 iterations
- Manual trigger: call `_check_and_compress()`
- Check threshold in `config.py`

## 📚 Next: Phase 3

Phase 3 will add:
- Advanced worker coordination strategies
- Resource management and prioritization
- Performance optimizations
- Enhanced error recovery
- Metrics and observability

Stay tuned!
