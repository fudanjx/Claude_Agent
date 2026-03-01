# Subagent Architecture

This SDK now implements Claude Code's subagent architecture, where subagents are specialized agents that run in isolated context windows with restricted tool access.

## Overview

**Key Features:**
- ✅ Isolated context windows per subagent
- ✅ Markdown + YAML frontmatter configuration
- ✅ Per-subagent tool restrictions (allowlist/denylist)
- ✅ Synchronous and asynchronous execution
- ✅ Resume capability with full context preservation
- ✅ Grandchild prevention (subagents cannot spawn subagents)
- ✅ Model selection (sonnet/opus/haiku/inherit)
- ✅ Backward compatible with existing worker system

## Architecture

### Subagent vs Worker

| Feature | Subagent (New) | Worker (Existing) |
|---------|----------------|-------------------|
| Context | Isolated per invocation | Persistent across tasks |
| Spawning | Via Agent tool (sync) | Manual CLI startup (async) |
| Communication | Synchronous return | File-based mailbox |
| Lifetime | Single task | Long-running daemon |
| Tool Access | Per-definition restrictions | Profile-based |
| Use Case | Focused subtasks | Background work |

**Both systems coexist** - use subagents for focused, synchronous work and workers for long-running background tasks.

## Built-in Subagents

### 1. Researcher
- **Description:** Expert at web search, research, and data gathering
- **Tools:** web_search, web_fetch, read_file, list_dir, bash
- **Cannot:** Write files, create tasks
- **Max Turns:** 20
- **Use When:** Need to find information, research documentation, gather data

### 2. Developer
- **Description:** Expert at writing code, debugging, and implementing features
- **Tools:** read_file, write_file, list_dir, bash
- **Cannot:** Web search, create tasks
- **Max Turns:** 30
- **Use When:** Need to write or modify code, implement features

### 3. Analyst
- **Description:** Expert at analyzing data, logs, and patterns
- **Tools:** read_file, list_dir, bash
- **Cannot:** Write files, web search, create tasks
- **Max Turns:** 15
- **Use When:** Need to analyze data, find patterns, review logs

### 4. General
- **Description:** General-purpose agent for complex, multi-step tasks
- **Tools:** All tools available
- **Cannot:** Nothing (has full access)
- **Max Turns:** 50
- **Use When:** Complex tasks requiring multiple capabilities

## Usage

### Using the Agent Tool

From the lead agent, use the `Agent` tool to spawn a subagent:

```python
# Example: Research task
Agent(
    subagent_type="researcher",
    prompt="Research AWS Bedrock pricing for Claude models and summarize key points",
    description="Research Bedrock pricing"
)

# Example: Code implementation
Agent(
    subagent_type="developer",
    prompt="Implement a retry mechanism for the Bedrock client with exponential backoff",
    description="Implement retry logic"
)

# Example: Log analysis
Agent(
    subagent_type="analyst",
    prompt="Analyze error logs in .agent_state/logs/ and identify common patterns",
    description="Analyze error logs"
)

# Example: Background execution
Agent(
    subagent_type="general",
    prompt="Run comprehensive tests and generate a report",
    description="Run test suite",
    run_in_background=True
)

# Example: Resume previous work
Agent(
    subagent_type="researcher",
    prompt="Now also research the cost comparison with OpenAI",
    description="Continue research",
    resume="agent-0001"  # Resume from previous agent
)
```

### When to Use Subagents

**Use subagents when:**
- ✅ Task produces verbose output you don't need in main context
- ✅ Want to enforce specific tool restrictions (security/safety)
- ✅ Work is self-contained with clear deliverable
- ✅ Need specialized focus (research vs coding vs analysis)
- ✅ Want to isolate exploration from main conversation

**Don't use subagents when:**
- ❌ Task requires back-and-forth with lead agent
- ❌ Need to maintain context across multiple related subtasks
- ❌ Task is simple enough to handle directly

## Creating Custom Subagents

### Directory Structure

Custom subagents can be placed in:
1. **Built-in:** `subagents/*.md` (SDK level, version controlled)
2. **User-level:** `~/.claude/agents/*.md` (global, all projects)
3. **Project-level:** `.claude/agents/*.md` (project-specific)

Priority: Built-in < User < Project (higher priority overrides lower)

### Subagent Definition Format

Create a markdown file with YAML frontmatter:

```markdown
---
name: my_specialist
description: Short description for tool definition
tools: [read_file, bash, web_search]  # Optional: allowlist
disallowedTools: [write_file]  # Optional: denylist
model: inherit  # inherit, sonnet, opus, haiku
maxTurns: 25
memory: project  # Optional: user, project, local
---

You are a specialist in [domain].

## Your Role

When invoked, you should:
1. Step 1
2. Step 2

## Guidelines

- Guideline 1
- Guideline 2

## Output Format

Present results as:
- Section 1
- Section 2
```

### Example: Custom Security Auditor

```markdown
---
name: security_auditor
description: Security audit specialist for code review
tools: [read_file, list_dir, bash]
disallowedTools: [write_file, web_search]
model: sonnet
maxTurns: 20
---

You are a security auditor specializing in finding vulnerabilities.

## Your Role

When auditing code:
1. Read all relevant source files
2. Identify security concerns (injection, XSS, auth issues)
3. Check for OWASP Top 10 vulnerabilities
4. Provide specific remediation recommendations

## Output Format

**Security Findings**:
- [HIGH] Finding 1: Description
- [MEDIUM] Finding 2: Description

**Recommendations**:
1. Fix for finding 1
2. Fix for finding 2
```

## Implementation Details

### Key Files

1. **`subagent_loader.py`** - Registry and loader for subagent definitions
2. **`subagent_executor.py`** - Execution engine with isolated context
3. **`subagents/*.md`** - Built-in subagent definitions
4. **`lead_agent.py`** - Integration of Agent tool

### How It Works

1. **Loading:** At startup, `SubagentRegistry` scans directories and loads all `.md` files
2. **Tool Definition:** Registry generates Agent tool definition with enum of available subagents
3. **Spawning:** When Lead calls Agent tool, `SubagentExecutor` is created
4. **Execution:** Executor runs agentic loop with isolated context and restricted tools
5. **Result:** Final output is extracted and returned to lead agent

### Isolated Context

Each subagent execution has:
- **Separate message history** - No context bleed
- **Restricted tool dispatcher** - Only allowed tools
- **Independent execution** - Cannot affect parent
- **Grandchild prevention** - Agent tool is removed from subagent's tools

### Resume Capability

Subagents return an `agent_id` which can be used to resume:

```python
# First call
result = Agent(
    subagent_type="researcher",
    prompt="Start researching topic X",
    description="Research X"
)
agent_id = result['agent_id']  # e.g., "agent-0001"

# Continue later
Agent(
    subagent_type="researcher",
    prompt="Now also research related topic Y",
    description="Continue research",
    resume=agent_id  # Full context preserved
)
```

## Testing

### Test Subagent Loading

```bash
source .venv/bin/activate
python test_subagents.py
```

### Test Lead Agent Integration

```bash
source .venv/bin/activate
python -c "from lead_agent import LeadAgent; LeadAgent()"
```

### Interactive Testing

```bash
source .venv/bin/activate
python lead_agent.py
```

Then use the Agent tool in conversation:
```
Use the researcher subagent to find information about AWS Bedrock
```

## Benefits of This Architecture

### 1. True Context Isolation
- Each subagent has completely isolated message history
- No context bleed between subagents
- Clean separation of concerns

### 2. Tool Restrictions
- Per-subagent allowlist/denylist
- Enforced at execution time
- Clear security model

### 3. Synchronous Results
- Results returned immediately to parent
- No async polling needed
- Simpler programming model

### 4. Resume Capability
- Full context preservation
- Continue previous work seamlessly
- Efficient multi-turn investigations

### 5. Markdown Configuration
- Easy to read and write
- Version controllable
- Shareable across team

### 6. Grandchild Prevention
- Enforced limitation prevents infinite nesting
- Clear execution model
- Predictable behavior

### 7. Backward Compatible
- Existing worker system still works
- Can use both approaches
- Gradual migration path

## Comparison: Subagent vs Worker System

### When to Use Subagents

```python
# Research task (focused, returns summary)
Agent(subagent_type="researcher", prompt="Research topic X")

# Code implementation (isolated, restricted tools)
Agent(subagent_type="developer", prompt="Implement feature Y")

# Quick analysis (read-only, focused output)
Agent(subagent_type="analyst", prompt="Analyze logs")
```

### When to Use Workers

```python
# Long-running background task
create_task(goal="Monitor system for 24 hours", priority="high")

# Persistent work queue
create_task(goal="Process batch of 1000 items", deps=[])

# Async work with mailbox communication
create_task(goal="Generate report and email results")
```

## Future Enhancements

Potential improvements:
- [ ] Memory persistence across invocations
- [ ] Streaming output for long-running subagents
- [ ] Subagent pools for parallel execution
- [ ] Custom hooks for pre/post execution
- [ ] Metrics and logging dashboard
- [ ] Subagent marketplace/registry

## Troubleshooting

### Subagent not found
- Check that `.md` file exists in one of the search directories
- Verify YAML frontmatter is valid
- Check that `name` field matches the file

### Tool restrictions not working
- Verify `tools` or `disallowedTools` in frontmatter
- Check that tool names match exactly
- Note: Agent tool is always removed for subagents

### Resume not working
- Ensure `agent_id` matches exactly
- Check that subagent type is the same
- Verify subagent is still in memory (not restarted)

### Import errors
- Run from SDK root directory
- Ensure virtual environment is activated
- Check that all dependencies are installed

## Summary

The subagent architecture brings Claude Code's powerful delegation model to the SDK:

✅ **Isolated contexts** - Clean separation and no context bleed
✅ **Tool restrictions** - Security and focus through allowlist/denylist
✅ **Easy to extend** - Just drop in a markdown file
✅ **Backward compatible** - Workers still available for async work
✅ **Production ready** - Tested and integrated with lead agent

Use subagents for focused, synchronous subtasks and workers for long-running background work!
