# Subagent Quick Start Guide

## What Are Subagents?

Subagents are specialized agents that run in **isolated context windows** with **restricted tool access**. They're perfect for focused tasks that you want to delegate without polluting your main conversation context.

## Quick Examples

### Example 1: Research Task
```python
# Use researcher subagent to find information
Agent(
    subagent_type="researcher",
    prompt="Research AWS Bedrock pricing for Claude models and provide a summary with key points",
    description="Research Bedrock pricing"
)
```

**What happens:**
1. Researcher spawns in isolated context
2. Uses web_search and web_fetch to find information
3. Cannot write files (restricted)
4. Returns summary to lead agent
5. Context stays clean!

### Example 2: Code Implementation
```python
# Use developer subagent to write code
Agent(
    subagent_type="developer",
    prompt="Add error handling to the bedrock_client.py for connection errors",
    description="Add error handling"
)
```

**What happens:**
1. Developer spawns with code tools
2. Reads existing code
3. Writes improved version
4. Tests changes with bash
5. Returns summary of changes

### Example 3: Data Analysis
```python
# Use analyst subagent to find patterns
Agent(
    subagent_type="analyst",
    prompt="Analyze error logs in .agent_state/logs/ and identify the top 3 most common errors",
    description="Analyze error logs"
)
```

**What happens:**
1. Analyst spawns read-only
2. Reads log files
3. Uses bash for processing (grep, awk, etc.)
4. Cannot modify files
5. Returns findings with evidence

### Example 4: Multi-turn Work
```python
# First call - initial research
result = Agent(
    subagent_type="researcher",
    prompt="Research best practices for Python error handling",
    description="Research error handling"
)

# Second call - continue with same context
Agent(
    subagent_type="researcher",
    prompt="Now find examples of retry mechanisms with exponential backoff",
    description="Continue research",
    resume=result['agent_id']  # Preserves full context!
)
```

### Example 5: Background Execution
```python
# Long-running task in background
Agent(
    subagent_type="general",
    prompt="Run comprehensive test suite and generate coverage report",
    description="Run tests",
    run_in_background=True  # Non-blocking!
)

# Lead agent continues working immediately
# Check status later or wait for completion
```

## When to Use Each Subagent

### 🔍 Researcher
**Use when:** Need to find information online or in documentation
**Tools:** web_search, web_fetch, read_file, list_dir, bash
**Cannot:** Write files, create tasks
**Example tasks:**
- Research API documentation
- Find code examples
- Compare technology options
- Gather requirements

### 💻 Developer
**Use when:** Need to write or modify code
**Tools:** read_file, write_file, list_dir, bash
**Cannot:** Search web, create tasks
**Example tasks:**
- Implement new features
- Fix bugs
- Refactor code
- Add tests

### 📊 Analyst
**Use when:** Need to understand data or find patterns
**Tools:** read_file, list_dir, bash
**Cannot:** Write files, search web
**Example tasks:**
- Analyze logs
- Find patterns in data
- Review metrics
- Identify issues

### 🎯 General
**Use when:** Complex tasks needing multiple capabilities
**Tools:** All tools available
**Cannot:** Nothing (full access)
**Example tasks:**
- End-to-end features
- Complex investigations
- Mixed research + implementation

## Benefits

### 1. Context Isolation
```
Without subagents:
Lead Context: 10,000 tokens
├── User request
├── Lead thinking
├── 50 tool uses from research  ← Clutters context!
├── All web search results
└── Final response

With subagents:
Lead Context: 500 tokens
├── User request
├── Lead spawns researcher
└── Researcher summary only  ← Clean!

Researcher Context (isolated):
├── Research task
├── 50 tool uses
└── Return summary
```

### 2. Tool Restrictions
```python
# Researcher CANNOT write files (enforced)
Agent(
    subagent_type="researcher",
    prompt="Write a file with results"  # Will fail!
)

# Developer CANNOT search web (enforced)
Agent(
    subagent_type="developer",
    prompt="Search for examples online"  # Will fail!
)
```

### 3. Focused Work
Each subagent has a specific role and prompt optimized for that role:
- Researchers cite sources
- Developers follow code patterns
- Analysts provide evidence
- General purpose is flexible

## Subagent vs Worker: When to Use Which?

### Use Subagents When:
- ✅ Task is focused and well-defined
- ✅ Want immediate result (blocking OK)
- ✅ Need tool restrictions for safety
- ✅ Want clean context (avoid pollution)
- ✅ Short to medium duration (< 5 minutes)

### Use Workers When:
- ✅ Task is long-running (> 5 minutes)
- ✅ Want async execution (don't block)
- ✅ Need persistent daemon
- ✅ Task board coordination
- ✅ Mailbox communication needed

### Examples

**Subagent (sync, focused):**
```python
# Quick research - blocks for result
Agent(subagent_type="researcher", prompt="Research X")
```

**Worker (async, long-running):**
```python
# Long processing - continues in background
create_task(goal="Process 10,000 files")
```

## Common Patterns

### Pattern 1: Sequential Research
```python
# Step 1: Research topic
research = Agent(
    subagent_type="researcher",
    prompt="Research AWS Lambda pricing",
    description="Research Lambda pricing"
)

# Step 2: Continue research with context
Agent(
    subagent_type="researcher",
    prompt="Compare with AWS Fargate pricing",
    description="Compare pricing",
    resume=research['agent_id']
)
```

### Pattern 2: Research Then Implement
```python
# Step 1: Research best practices
research_result = Agent(
    subagent_type="researcher",
    prompt="Research Python async best practices",
    description="Research async"
)

# Step 2: Implement based on findings
Agent(
    subagent_type="developer",
    prompt=f"Implement async handler following these practices: {research_result['output']}",
    description="Implement async"
)
```

### Pattern 3: Analyze Then Act
```python
# Step 1: Analyze logs
analysis = Agent(
    subagent_type="analyst",
    prompt="Analyze error logs and identify root causes",
    description="Analyze errors"
)

# Step 2: Fix identified issues
Agent(
    subagent_type="developer",
    prompt=f"Fix these issues: {analysis['output']}",
    description="Fix errors"
)
```

### Pattern 4: Parallel Execution
```python
# Start multiple subagents in background
Agent(
    subagent_type="researcher",
    prompt="Research AWS pricing",
    description="Research AWS",
    run_in_background=True
)

Agent(
    subagent_type="researcher",
    prompt="Research GCP pricing",
    description="Research GCP",
    run_in_background=True
)

# Both run in parallel!
```

## Creating Custom Subagents

Just drop in a markdown file!

```bash
# Create custom subagent
$ cat > subagents/tester.md << 'EOF'
---
name: tester
description: Test execution and quality assurance specialist
tools: [bash, read_file, list_dir]
disallowedTools: [write_file, web_search]
maxTurns: 20
---

You are a QA specialist focused on testing.

When invoked:
1. Identify test requirements
2. Run tests using bash
3. Analyze results
4. Report findings

Present results as:
- **Tests Run**: Count
- **Passed**: Count
- **Failed**: List with details
- **Coverage**: Percentage if available
EOF

# Automatically available!
$ python lead_agent.py
Features: ... Subagents (5)
```

## Tips & Best Practices

### 1. Be Specific in Prompts
```python
# ❌ Too vague
Agent(subagent_type="researcher", prompt="Research AWS")

# ✅ Clear and specific
Agent(
    subagent_type="researcher",
    prompt="Research AWS Bedrock pricing for Claude Sonnet 4.6 in us-east-1, focusing on input/output token costs"
)
```

### 2. Use Descriptions
```python
# ❌ Generic description
Agent(..., description="Do task")

# ✅ Clear summary (shows in logs)
Agent(..., description="Research Bedrock pricing")
```

### 3. Resume for Multi-turn
```python
# ✅ Save agent_id for continuation
result = Agent(...)
agent_id = result['agent_id']

# Later...
Agent(..., resume=agent_id)
```

### 4. Choose Right Subagent
```python
# ❌ Using general for everything
Agent(subagent_type="general", prompt="Research topic")

# ✅ Use specialized subagents
Agent(subagent_type="researcher", prompt="Research topic")
```

### 5. Check Results
```python
result = Agent(...)

if result['success']:
    print(f"Output: {result['output']}")
    print(f"Turns: {result['turns']}")
    print(f"Tool uses: {result['tool_uses']}")
else:
    print(f"Error: {result['error']}")
```

## Troubleshooting

### Subagent not found
```python
# Error: Unknown subagent type: xyz
# Solution: Check available types
```

Available: `researcher`, `developer`, `analyst`, `general`

### Tool restrictions
```python
# Researcher tries to write file
# Error: Tool not available: write_file
# Solution: Use appropriate subagent (developer)
```

### Grandchild prevention
```python
# Subagent tries to spawn another subagent
# Error: Tool not available: Agent
# Solution: This is by design - no nesting allowed
```

## Summary

Subagents are perfect for:
- 🎯 **Focused tasks** with clear deliverables
- 🔒 **Tool restrictions** for safety
- 🧹 **Context cleanliness** in lead agent
- 🔄 **Resume capability** for multi-turn work
- ⚡ **Sync or async** execution

Just use the `Agent` tool and let subagents handle specialized work!

**See full documentation:** [`SUBAGENTS.md`](SUBAGENTS.md)
