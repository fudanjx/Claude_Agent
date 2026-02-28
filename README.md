# Claude Agent SDK

A production-ready, general-purpose multi-agent system built with Claude Sonnet 4.6 via AWS Bedrock.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure AWS
Ensure your AWS profile "work" is configured:
```bash
aws configure --profile work
```

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
│   └── worker_agent.py    # Worker teammates
│
├── Infrastructure
│   ├── config.py          # Configuration
│   ├── prompts.py         # System prompts
│   ├── tools.py           # Tool handlers (8 tools)
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

- **Plan-First Execution** - Always plans before acting
- **Web Search** - Internet access via DuckDuckGo
- **Worker Specialization** - Skill-based task matching
- **Error Recovery** - Automatic retry with backoff
- **Infinite Sessions** - 3-layer compression
- **Background Jobs** - Async command execution
- **Multi-Agent** - Autonomous coordination

## 📚 Documentation

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
