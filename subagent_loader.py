"""Subagent definition loader for Claude Agent SDK.

This module implements Claude Code's subagent architecture, where subagents are
defined as Markdown files with YAML frontmatter and spawned via an Agent tool.
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set


@dataclass
class SubagentDefinition:
    """Subagent configuration loaded from markdown file."""

    name: str
    description: str
    system_prompt: str  # Markdown body
    tools: Optional[List[str]] = None  # Allowlist
    disallowed_tools: Optional[List[str]] = None  # Denylist
    model: str = "inherit"  # sonnet, opus, haiku, inherit
    permission_mode: str = "default"
    max_turns: int = 20
    skills: Optional[List[str]] = None  # Pre-defined skills (static mode)
    skill_mode: str = "none"  # none, static, dynamic
    memory: Optional[str] = None  # user, project, local
    background: bool = False
    hooks: Optional[Dict[str, Any]] = None

    # Computed
    file_path: Optional[Path] = None
    source: str = "built-in"  # built-in, project, user


class SubagentRegistry:
    """Registry for loading and managing subagent definitions."""

    def __init__(self, sdk_root: Path):
        self.sdk_root = sdk_root
        self.subagents: Dict[str, SubagentDefinition] = {}

        # Load subagents from all sources (priority order: built-in < user < project)
        self._load_built_in_subagents()
        self._load_user_subagents()
        self._load_project_subagents()

    def _load_built_in_subagents(self):
        """Load subagents from sdk_root/subagents/"""
        subagents_dir = self.sdk_root / "subagents"
        if subagents_dir.exists():
            self._load_from_directory(subagents_dir, source="built-in")

    def _load_user_subagents(self):
        """Load subagents from ~/.claude/agents/"""
        user_agents_dir = Path.home() / ".claude" / "agents"
        if user_agents_dir.exists():
            self._load_from_directory(user_agents_dir, source="user")

    def _load_project_subagents(self):
        """Load subagents from .claude/agents/"""
        project_agents_dir = Path.cwd() / ".claude" / "agents"
        if project_agents_dir.exists():
            self._load_from_directory(project_agents_dir, source="project")

    def _load_from_directory(self, directory: Path, source: str):
        """Load all .md files from directory."""
        for md_file in directory.glob("*.md"):
            try:
                definition = self._parse_subagent_file(md_file, source)
                # Higher priority sources override lower
                self.subagents[definition.name] = definition
            except Exception as e:
                print(f"⚠️  Failed to load subagent {md_file}: {e}")

    def _parse_subagent_file(self, file_path: Path, source: str) -> SubagentDefinition:
        """Parse markdown file with YAML frontmatter."""
        content = file_path.read_text()

        # Split frontmatter and body
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                frontmatter_str = parts[1]
                body = parts[2].strip()
            else:
                raise ValueError("Invalid frontmatter format")
        else:
            raise ValueError("No frontmatter found")

        # Parse YAML frontmatter
        frontmatter = yaml.safe_load(frontmatter_str)

        # Determine skill mode
        skills = frontmatter.get('skills')
        skill_mode = frontmatter.get('skillMode', 'none')

        # Auto-detect skill mode if not specified
        if skill_mode == 'none' and skills:
            skill_mode = 'static'  # Has predefined skills
        elif skill_mode == 'none' and frontmatter.get('dynamicSkills', False):
            skill_mode = 'dynamic'  # Explicitly dynamic

        # Build definition
        return SubagentDefinition(
            name=frontmatter['name'],
            description=frontmatter['description'],
            system_prompt=body,
            tools=frontmatter.get('tools'),
            disallowed_tools=frontmatter.get('disallowedTools'),
            model=frontmatter.get('model', 'inherit'),
            permission_mode=frontmatter.get('permissionMode', 'default'),
            max_turns=frontmatter.get('maxTurns', 20),
            skills=skills,
            skill_mode=skill_mode,
            memory=frontmatter.get('memory'),
            background=frontmatter.get('background', False),
            hooks=frontmatter.get('hooks'),
            file_path=file_path,
            source=source
        )

    def get_subagent(self, name: str) -> Optional[SubagentDefinition]:
        """Get subagent definition by name."""
        return self.subagents.get(name)

    def list_subagents(self) -> List[SubagentDefinition]:
        """List all loaded subagents."""
        return list(self.subagents.values())

    def get_tool_definition_for_lead(self) -> Dict[str, Any]:
        """Generate Agent tool definition for lead agent (shows available subagents)."""
        subagent_types = [
            {"name": defn.name, "description": defn.description}
            for defn in self.subagents.values()
        ]

        # Build enum and descriptions
        enum_list = [s['name'] for s in subagent_types]
        descriptions = " ".join(f"'{s['name']}': {s['description']}" for s in subagent_types)

        return {
            "name": "Agent",
            "description": (
                "Delegate a focused subtask to a specialized subagent. "
                "The subagent runs in an isolated context with its own tool set and returns results. "
                "Use this when you need specialized work with restricted tool access or when you want to "
                "isolate verbose output from your main context. "
                f"Available types: {', '.join(enum_list)}"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "subagent_type": {
                        "type": "string",
                        "enum": enum_list if enum_list else ["general"],
                        "description": f"Type of subagent to use. {descriptions}"
                    },
                    "prompt": {
                        "type": "string",
                        "description": "Clear task description for the subagent. Be specific about what you need."
                    },
                    "description": {
                        "type": "string",
                        "description": "Short (3-5 word) summary of what this subagent will do"
                    },
                    "run_in_background": {
                        "type": "boolean",
                        "description": "Run subagent in background (async). Default: False",
                        "default": False
                    },
                    "resume": {
                        "type": "string",
                        "description": "Optional: Agent ID to resume from previous execution with full context preserved"
                    }
                },
                "required": ["subagent_type", "prompt", "description"]
            }
        }
