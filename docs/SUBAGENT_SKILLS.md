## Subagent Skill System

## Overview

Subagents in the Claude SDK can acquire skills in two ways, enabling both specialized and general-purpose capabilities.

## Two Types of Subagents

### Type 1: Specialized Subagents (Static Skills)

**Definition:** Subagents with pre-defined, always-loaded skills for specific domains.

**Use When:**
- You need guaranteed domain expertise
- The subagent should always have specific knowledge
- You want predictable, consistent behavior
- The skill is core to the subagent's purpose

**Configuration:**
```yaml
---
name: pdf-specialist
skillMode: static
skills: [pdf]  # These skills are ALWAYS loaded
---
```

**Behavior:**
1. **At initialization**: All specified skills are loaded
2. **During execution**: Skills remain active throughout
3. **System prompt**: Includes full skill content
4. **Predictable**: Always has the same capabilities

**Example:**
```python
# Spawn PDF specialist - PDF skill is already loaded
Agent(
    subagent_type="pdf-specialist",
    prompt="Extract text from document.pdf",
    description="Extract PDF text"
)

# The PDF skill is ALREADY loaded and available
```

### Type 2: Generic Subagents (Dynamic Skills)

**Definition:** Subagents that dynamically acquire skills based on task context.

**Use When:**
- Task requirements are varied
- You want automatic skill selection
- Need flexibility for diverse tasks
- Want skills loaded only when needed (token efficiency)

**Configuration:**
```yaml
---
name: general
skillMode: dynamic  # Can access ANY skill from /skills folder
---
```

**Behavior:**
1. **At initialization**: No skills loaded (clean state)
2. **Task analysis**: Checks task prompt for skill triggers
3. **Dynamic activation**: Loads matching skills automatically
4. **On-demand**: Only loads what's needed

**Example:**
```python
# Spawn general agent with PDF task
Agent(
    subagent_type="general",
    prompt="Extract data from invoice.pdf and analyze",
    description="Process PDF invoice"
)

# Behind the scenes:
# 1. Checks prompt: "invoice.pdf" contains "pdf"
# 2. Finds PDF skill trigger matches
# 3. Dynamically loads PDF skill
# 4. Subagent now has PDF expertise
```

## How It Works

### Static Skills (Type 1)

```
Initialization:
┌─────────────────────────────────────┐
│ 1. Parse subagent definition       │
│    skills: [pdf, docx]              │
│                                     │
│ 2. Load SkillLoader                │
│    - Scan /skills directory         │
│    - Find pdf.SKILL.md              │
│    - Find docx.SKILL.md             │
│                                     │
│ 3. Load skill content               │
│    - Read full skill files          │
│    - Store in active_skills dict    │
│                                     │
│ 4. Inject into system prompt       │
│    - Add skill content to prompt    │
│    - Wrap in <skill_content> tags   │
└─────────────────────────────────────┘

Execution:
┌─────────────────────────────────────┐
│ Skills remain loaded throughout     │
│ Subagent has persistent expertise   │
└─────────────────────────────────────┘
```

### Dynamic Skills (Type 2)

```
Initialization:
┌─────────────────────────────────────┐
│ 1. Parse subagent definition       │
│    skillMode: dynamic               │
│                                     │
│ 2. Initialize SkillLoader           │
│    - Scan /skills directory         │
│    - Load skill metadata ONLY       │
│    - Store triggers list            │
│                                     │
│ 3. No skills loaded yet             │
│    active_skills: {}  (empty)       │
└─────────────────────────────────────┘

Task Received:
┌─────────────────────────────────────┐
│ 1. Analyze task prompt              │
│    "Extract text from report.pdf"   │
│                                     │
│ 2. Check skill triggers             │
│    - PDF skill: ["pdf", "extract"]  │
│    - Match found: "pdf" in prompt   │
│                                     │
│ 3. Dynamically load PDF skill       │
│    - Read pdf.SKILL.md              │
│    - Add to active_skills           │
│                                     │
│ 4. Rebuild system prompt            │
│    - Now includes PDF skill         │
└─────────────────────────────────────┘

Execution:
┌─────────────────────────────────────┐
│ Subagent now has PDF expertise      │
│ Can load more skills if needed      │
└─────────────────────────────────────┘
```

## Configuration Reference

### SubagentDefinition Fields

```yaml
---
name: string              # Subagent identifier
description: string       # Short description
skillMode: string         # "none" | "static" | "dynamic"
skills: [string]          # List of skill names (for static mode)
tools: [string]           # Allowed tools
maxTurns: int             # Max conversation turns
---
```

### Skill Modes

| Mode | Description | When to Use |
|------|-------------|-------------|
| `none` | No skill support | Simple subagents that don't need skills |
| `static` | Pre-defined skills always loaded | Specialized subagents (PDF expert, Excel expert) |
| `dynamic` | Skills loaded on-demand | General-purpose subagents that adapt to tasks |

## Built-in Examples

### Specialized Subagents (Static)

**pdf-specialist.md:**
```yaml
---
name: pdf-specialist
skillMode: static
skills: [pdf]
---
```
- Always has PDF expertise
- Optimized for PDF tasks
- Predictable behavior

### General-Purpose Subagents (Dynamic)

**general.md:**
```yaml
---
name: general
skillMode: dynamic
---
```
- Adapts to any task type
- Loads skills as needed
- Token efficient

### Simple Subagents (No Skills)

**researcher.md, developer.md, analyst.md:**
```yaml
---
name: researcher
# No skillMode specified = "none"
---
```
- No skill system overhead
- Relies on system prompt only
- Lightweight

## Usage Examples

### Example 1: Specialized Subagent

```python
# PDF specialist always has PDF skill
Agent(
    subagent_type="pdf-specialist",
    prompt="Extract form fields from tax-form.pdf",
    description="Extract form fields"
)

# Output:
# 📚 Loading static skills for pdf-specialist:
#    ✓ pdf
# 🔄 Spawning subagent: pdf-specialist (agent-0001)
```

### Example 2: Dynamic Subagent (PDF Task)

```python
# General agent dynamically acquires PDF skill
Agent(
    subagent_type="general",
    prompt="Analyze the content of report.pdf and summarize key findings",
    description="Analyze PDF report"
)

# Output:
# 🎯 Subagent agent-0002 has dynamic skill access
# 🔄 Spawning subagent: general (agent-0002)
# 🎯 Dynamically activated skill: pdf
```

### Example 3: Dynamic Subagent (Web Task)

```python
# Same general agent, different task type
Agent(
    subagent_type="general",
    prompt="Research AWS Bedrock pricing and create a comparison table",
    description="Research AWS pricing"
)

# Output:
# 🎯 Subagent agent-0003 has dynamic skill access
# 🔄 Spawning subagent: general (agent-0003)
# 🎯 Dynamically activated skill: web-research
```

### Example 4: Dynamic Subagent (Multiple Skills)

```python
# Complex task requiring multiple skills
Agent(
    subagent_type="general",
    prompt="Extract data from invoice.pdf and create an Excel spreadsheet summary",
    description="PDF to Excel"
)

# Output:
# 🎯 Subagent agent-0004 has dynamic skill access
# 🔄 Spawning subagent: general (agent-0004)
# 🎯 Dynamically activated skill: pdf
# 🎯 Dynamically activated skill: xlsx
```

## Creating Custom Subagents

### Specialized Subagent Template

```markdown
# subagents/excel-specialist.md
---
name: excel-specialist
description: Excel spreadsheet expert with XLSX skills
tools: [read_file, write_file, bash]
skillMode: static
skills: [xlsx]
maxTurns: 30
---

You are an Excel specialist with expertise in spreadsheet manipulation.

**PRE-LOADED SKILLS**: You have the XLSX skill permanently loaded.

## Your Expertise
- Creating and modifying Excel files
- Data analysis and pivot tables
- Formula creation and validation
- Chart generation

[Rest of system prompt...]
```

### Dynamic Subagent Template

```markdown
# subagents/adaptive-analyst.md
---
name: adaptive-analyst
description: Adaptive analyst that acquires skills based on data type
skillMode: dynamic
maxTurns: 40
---

You are an adaptive analyst that can work with any data format.

**SPECIAL CAPABILITY**: You have dynamic skill access to the complete skills library.

When analyzing data:
1. Identify the data format
2. Leverage any skills that are activated
3. Apply appropriate analysis techniques

[Rest of system prompt...]
```

## Skill Activation Flow

### For Static Skills

```python
# In SubagentExecutor.__init__()
def _initialize_skills(self):
    if self.definition.skill_mode == "static":
        self._load_static_skills()

def _load_static_skills(self):
    for skill_name in self.definition.skills:
        content = self.skill_loader.load_skill_content(skill_name)
        self.active_skills[skill_name] = content
```

### For Dynamic Skills

```python
# In SubagentExecutor.execute_sync()
def execute_sync(self):
    # Check task prompt for skill triggers
    self._check_and_activate_dynamic_skills(self.initial_prompt)

    # Build system prompt with activated skills
    system_prompt = self._build_system_prompt()

    # Execute...

def _check_and_activate_dynamic_skills(self, user_message):
    for skill_name, skill in self.skill_loader.skills.items():
        if skill_name not in self.active_skills:
            if self.skill_loader.should_activate_skill(skill_name, user_message):
                content = self.skill_loader.load_skill_content(skill_name)
                self.active_skills[skill_name] = content
```

## Performance Considerations

### Static Skills

**Pros:**
- Predictable behavior
- No activation overhead
- Always available

**Cons:**
- Higher token usage (skills always in context)
- Less flexible
- One-size-fits-all

**Best For:**
- Domain-specific tasks
- Specialized subagents
- When skill is always needed

### Dynamic Skills

**Pros:**
- Token efficient (load only what's needed)
- Flexible and adaptive
- Can handle diverse tasks

**Cons:**
- Slight activation overhead
- Skills may not activate if triggers don't match
- Less predictable

**Best For:**
- General-purpose tasks
- Variable requirements
- Token optimization

## Troubleshooting

### Static Skill Not Loading

**Problem:** Skill specified but not loading

**Check:**
```python
# 1. Verify skill exists
ls skills/pdf/SKILL.md

# 2. Check subagent definition
cat subagents/pdf-specialist.md
# Should have: skillMode: static, skills: [pdf]

# 3. Test skill loader
python -c "from skill_loader import SkillLoader; loader = SkillLoader('skills'); loader.discover_skills(); print(list(loader.skills.keys()))"
```

### Dynamic Skill Not Activating

**Problem:** Expected skill didn't activate

**Check:**
1. **Trigger keywords** - Does task prompt contain skill triggers?
2. **Skill file** - Does skill have correct triggers in YAML?
3. **SkillMode** - Is subagent set to `dynamic`?

**Example:**
```python
# Check skill triggers
from skill_loader import SkillLoader
loader = SkillLoader('skills')
loader.discover_skills()
pdf_skill = loader.skills['pdf']
print(f"PDF triggers: {pdf_skill.triggers}")

# Trigger should match prompt keywords
```

### Skill Content Not in Prompt

**Problem:** Skill loaded but content not visible

**Debug:**
```python
# Add logging in _build_system_prompt()
print(f"Active skills: {list(self.active_skills.keys())}")
print(f"Prompt length: {len(system_prompt)}")
```

## Best Practices

### For Specialized Subagents

1. **Limit to 1-3 skills** - Don't overload with too many static skills
2. **Match domain** - Skills should align with subagent's purpose
3. **Clear purpose** - Document what the subagent specializes in
4. **Tool alignment** - Ensure tools match skill requirements

### For Dynamic Subagents

1. **Broad capability** - Don't restrict tools too much
2. **Clear triggers** - Ensure skills have good trigger words
3. **Monitor activation** - Log which skills activate
4. **Test variety** - Try different task types

### For All Subagents

1. **Document skill mode** - Make it clear in description
2. **Test thoroughly** - Verify skills load correctly
3. **Monitor tokens** - Watch context size
4. **Iterate** - Refine based on usage patterns

## Summary

The dual-mode skill system provides:

✅ **Flexibility**: Choose static or dynamic based on needs
✅ **Efficiency**: Dynamic mode saves tokens
✅ **Predictability**: Static mode guarantees expertise
✅ **Scalability**: Easy to add new specialized subagents
✅ **Isolation**: Each subagent has its own skill context

**Quick Reference:**
- **Static**: Pre-defined skills always loaded (specialized subagents)
- **Dynamic**: Skills loaded on-demand (general-purpose subagents)
- **None**: No skill system (simple subagents)

For more information:
- [SUBAGENTS.md](SUBAGENTS.md) - Complete subagent guide
- [SKILLS_ARCHITECTURE.md](SKILLS_ARCHITECTURE.md) - Skills system details
- [skill_loader.py](../skill_loader.py) - Implementation source
