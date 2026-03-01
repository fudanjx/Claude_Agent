# Available Skills

This directory contains Claude Skills - reusable packages of expertise that teach the agent specialized capabilities.

## What are Skills?

Skills are self-contained instruction packages following Anthropic's official skills format. Each skill provides:
- Specialized domain knowledge
- Step-by-step methodologies
- Best practices and guidelines
- Tool usage patterns

Skills are loaded progressively: metadata is always available, full instructions load on-demand when relevant to the user's request.

## Skills Index

### Research & Information Gathering

- [web-research](web-research/SKILL.md) - Comprehensive web research methodology using search and analysis tools. Use for researching topics, comparing information, or gathering data from the internet.

## Adding New Skills

To add a new skill:

1. Create a directory: `skills/your-skill-name/`
2. Add a `SKILL.md` file with YAML frontmatter:
   ```markdown
   ---
   name: your-skill-name
   description: Brief description of what the skill does
   keywords: [optional, keyword, list]
   ---

   # Your Skill Name

   Full instructions and guidance...
   ```

3. The skill will be automatically discovered and loaded when the agent starts.

## Skill Format

Skills follow the standard format:
- YAML frontmatter with metadata (name, description, keywords)
- Markdown body with instructions
- Optional subdirectories: `scripts/`, `references/`

For more details, see: https://github.com/anthropics/skills
