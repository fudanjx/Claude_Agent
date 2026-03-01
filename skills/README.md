# Claude Skills Quick Reference

## What are Skills?

Skills are reusable instruction packages that teach the agent specialized capabilities. They follow the Anthropic skills format and are loaded progressively to manage context efficiently.

## Directory Structure

```
skills/
├── README.md           # This file
├── SKILLS.md          # Table of contents
└── {skill-name}/
    └── SKILL.md       # Skill definition
```

## Creating a New Skill

### 1. Create the directory
```bash
mkdir -p skills/my-skill-name
```

### 2. Create SKILL.md with frontmatter
```markdown
---
name: my-skill-name
description: Brief description of what this skill does (1-2 sentences)
keywords: [relevant, keywords, for, activation]
---

# My Skill Name

## Overview
Brief overview of the skill and its purpose.

## When to Use This Skill
List the situations when this skill should be activated:
- Use case 1
- Use case 2
- Use case 3

## Methodology
Step-by-step instructions for using the skill:

### Step 1: Title
Instructions...

### Step 2: Title
Instructions...

## Best Practices
- Do this
- Don't do that

## Examples
Show examples of using the skill.

## Quality Checklist
- [ ] Requirement 1
- [ ] Requirement 2
```

### 3. Update SKILLS.md
Add your skill to the index:
```markdown
## Category Name
- [my-skill-name](my-skill-name/SKILL.md) - Brief description
```

### 4. Test it
```bash
python3 test_skills_integration.py
```

## Skill Activation

Skills are activated automatically when:
1. The skill name appears in the user's message
2. Any of the skill's keywords appear in the message

Examples:
- "Research Python frameworks" → Activates `web-research` (keyword: "research")
- "Search for information" → Activates `web-research` (keyword: "search")
- "What is 2+2?" → No activation

## Progressive Loading

**Stage 1 - Startup:**
- All skill metadata loaded (~100 tokens per skill)
- Fast, minimal context usage

**Stage 2 - Activation:**
- Full skill content loaded on-demand
- Injected into conversation context
- Agent follows skill instructions

**Stage 3 - Completion:**
- Skill remains loaded for the session
- No reload needed for subsequent uses

## Skill Best Practices

### Good Skills
✅ Clear, specific instructions
✅ Step-by-step methodology
✅ Concrete examples
✅ Quality checklists
✅ 500-2000 lines (focused but comprehensive)

### Poor Skills
❌ Vague or generic advice
❌ Just a list of links
❌ Too broad (covers too many topics)
❌ Too narrow (single use case)
❌ Over 5000 lines (context bloat)

## Available Skills

See [SKILLS.md](SKILLS.md) for the complete index of available skills.

## Skill Format Reference

### Required Frontmatter
```yaml
---
name: skill-name        # Required: kebab-case
description: text       # Required: 1-2 sentences
---
```

### Optional Frontmatter
```yaml
---
keywords: [list]        # Recommended: for activation
version: "1.0"          # Optional: for versioning
author: "name"          # Optional: attribution
---
```

### Recommended Sections
1. **Overview**: What is this skill?
2. **When to Use**: Activation criteria
3. **Methodology**: Step-by-step instructions
4. **Best Practices**: Do's and don'ts
5. **Examples**: Usage examples
6. **Quality Checklist**: Verification steps

## Testing Skills

### Run the test suite
```bash
python3 test_skills_integration.py
```

### Test with the agent
```bash
python3 lead_agent.py "Your message that should activate the skill"
```

Look for:
```
🎯 Activated skill: skill-name
```

## Debugging

### Skill not discovered
- Check SKILL.md exists in the skill directory
- Verify YAML frontmatter is valid
- Ensure directory name matches skill name

### Skill not activating
- Check keywords in frontmatter
- Test with skill name directly in message
- Review activation logic in test suite

### Skill loading errors
- Verify SKILL.md is valid UTF-8
- Check for YAML parsing errors
- Review error messages in agent output

## Environment Variables

```bash
# Enable/disable skills (default: true)
export SKILLS_ENABLED=true

# Skills directory (default: ./skills)
# export SKILLS_DIR=/path/to/skills
```

## Examples

### Example 1: Research Skill
```markdown
---
name: web-research
description: Perform comprehensive web research using search tools
keywords: [research, search, investigate, study]
---

# Web Research Skill

Use this skill for thorough web research...
```

**Activation:**
- "Research Python frameworks" ✅
- "Search for AI news" ✅
- "What is Python?" ❌ (no research keywords)

### Example 2: Code Review Skill
```markdown
---
name: code-review
description: Systematic code review following best practices
keywords: [review, audit, check, analyze code]
---

# Code Review Skill

Follow this methodology for code reviews...
```

**Activation:**
- "Review this code" ✅
- "Analyze the codebase" ✅
- "Write a function" ❌

## Contributing Skills

1. Follow the skill format
2. Test thoroughly
3. Document clearly
4. Keep focused (single domain)
5. Update SKILLS.md index

## Resources

- **Anthropic Skills Format**: https://github.com/anthropics/skills
- **Implementation Docs**: ../SKILLS_IMPLEMENTATION.md
- **Test Suite**: ../test_skills_integration.py

## Support

For issues or questions:
1. Check the test suite output
2. Review SKILLS_IMPLEMENTATION.md
3. Examine skill_loader.py source code
4. Check agent logs for activation messages
