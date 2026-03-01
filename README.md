# Claude Agent SDK

A production-ready, general-purpose multi-agent system built with Claude Sonnet 4.6 via AWS Bedrock. Features Claude Code-style subagent architecture with isolated contexts and tool restrictions.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file with your AWS settings:
```bash
cp .env.example .env
# Edit .env with your AWS profile and region
```

Your `.env` should contain:
```env
AWS_PROFILE=your-aws-profile
AWS_REGION=us-east-1
MODEL_ID=global.anthropic.claude-sonnet-4-6
FALLBACK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
```

**Note:** Ensure your AWS profile is configured:
```bash
aws configure --profile your-aws-profile
```

For detailed configuration options, see [CONFIGURATION.md](CONFIGURATION.md).

### 3. Run the Agent
```bash
# Interactive mode
python lead_agent.py

# Command line
python lead_agent.py "Your goal here"

# Start a worker
python worker_agent.py Worker_alpha --profile researcher
```

## 📁 Project Structure

```
Claude_SDK/
├── Core Agents
│   ├── lead_agent.py      # Lead orchestrator
│   ├── worker_agent.py    # Worker teammates
│   ├── subagent_loader.py # Subagent registry (NEW!)
│   └── subagent_executor.py # Execution engine (NEW!)
│
├── Subagents (NEW!)
│   ├── researcher.md      # Research specialist
│   ├── developer.md       # Code specialist
│   ├── analyst.md         # Analysis specialist
│   └── general.md         # General-purpose
│
├── Infrastructure
│   ├── config.py          # Configuration
│   ├── prompts.py         # System prompts
│   ├── tools.py           # Tool handlers
│   ├── task_manager.py    # Task board
│   ├── compression.py     # 3-layer memory
│   ├── background_jobs.py # Async jobs
│   ├── mailbox.py         # Agent messaging
│   ├── worker_skills.py   # Skill system
│   └── error_recovery.py  # Retry logic
│
├── examples/              # Example scripts
├── tests/                 # Test suite
└── docs/                  # Documentation
```

## ✨ Features

- **Subagent Architecture** - Claude Code-style isolated contexts (NEW!)
- **Plan-First Execution** - Always plans before acting
- **Web Search** - Internet access via DuckDuckGo
- **Worker Specialization** - Skill-based task matching
- **Error Recovery** - Automatic retry with backoff
- **Infinite Sessions** - 3-layer compression
- **Background Jobs** - Async command execution
- **Multi-Agent** - Autonomous coordination
- **Skills System** - Pluggable domain expertise modules

### 🆕 Subagent System

The SDK now supports **Claude Code's subagent architecture**:

```python
# Spawn specialized subagents with isolated contexts
Agent(
    subagent_type="researcher",  # researcher, developer, analyst, general
    prompt="Research AWS Bedrock pricing and summarize",
    description="Research pricing"
)
```

**Features:**
- ✅ Isolated context per subagent (no context bleed)
- ✅ Tool restrictions (allowlist/denylist per subagent)
- ✅ Built-in specialists: Researcher, Developer, Analyst, General
- ✅ Sync/async execution with resume capability
- ✅ Easy to extend: Just drop in a markdown file

**See [`SUBAGENTS.md`](SUBAGENTS.md) for full documentation.**

## 📚 Documentation

- [**Subagent Guide**](SUBAGENTS.md) - Claude Code-style subagents (NEW!)
- [Implementation Summary](IMPLEMENTATION_SUMMARY.md) - What was built
- [Configuration Guide](CONFIGURATION.md) - Setup and config
- [Quick Start Guide](docs/QUICKSTART.md) - Getting started
- [Final Summary](docs/FINAL_SUMMARY.md) - Complete overview
- [Phase 2 Guide](docs/PHASE2_GUIDE.md) - Advanced features
- [Phase 3 Guide](docs/PHASE3_COMPLETE.md) - Production features
- [Web Search Guide](docs/WEB_SEARCH_GUIDE.md) - Internet access
- [PRD](docs/PRD.md) - Original requirements

## 🧪 Testing

```bash
# Run all tests
python tests/test_phase2.py  # Phase 2 features (6/6)
python tests/test_phase3.py  # Phase 3 features (5/5)
python tests/test_web_tools.py  # Web tools (2/2)

# Verify setup
python tests/verify_setup.py
```

## 💡 Examples

```bash
# Phase 1 examples
python examples/example.py 1

# Phase 2 examples
python examples/phase2_examples.py 1

# Phase 3 examples
python examples/phase3_examples.py 1

# Web search examples
python examples/example_web_search.py 1
```

## 🎯 Common Commands

### Interactive Mode
```bash
python lead_agent.py
```

**Commands:**
- `/tasks` - List all tasks
- `/jobs` - List background jobs
- `/inbox` - Check messages from workers
- `/workers` - Worker startup guide
- `/quit` - Exit

### Start Workers

**Specialized:**
```bash
python worker_agent.py Researcher --profile researcher
python worker_agent.py Developer --profile developer
python worker_agent.py Analyst --profile analyst
```

**General:**
```bash
python worker_agent.py Worker_A
```

## 📊 Status

**All 3 Phases Complete:**
- ✅ Phase 1: Foundation
- ✅ Phase 2: Enhanced Features
- ✅ Phase 3: Production Optimization

**Test Coverage:** 13/13 passing ✅

**PRD Coverage:** 100% ✅

## 🔧 Configuration

Edit `config.py` to customize:
- AWS profile and region
- Model ID
- Compression thresholds
- Max iterations

## 🎊 Built With

- Claude Sonnet 4.6 (AWS Bedrock)
- Python 3.8+
- Progressive implementation
- Production-ready practices

---

**For detailed documentation, see [docs/](docs/)**
