"""Loader for Claude Skills following Anthropic's skills format."""

import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class Skill:
    """Represents a Claude Skill."""
    name: str
    description: str
    file_path: Path
    metadata: Dict[str, Any] = field(default_factory=dict)
    content: Optional[str] = None
    loaded: bool = False

    def __repr__(self) -> str:
        status = "loaded" if self.loaded else "metadata-only"
        return f"<Skill name={self.name} status={status}>"


class SkillLoader:
    """Loads and manages Claude Skills from a directory structure."""

    def __init__(self, skills_dir: Path):
        """
        Initialize the skill loader.

        Args:
            skills_dir: Path to the skills directory
        """
        self.skills_dir = Path(skills_dir)
        self.skills: Dict[str, Skill] = {}
        self.index_file = self.skills_dir / "SKILLS.md"

    def discover_skills(self) -> Dict[str, Skill]:
        """
        Scan the skills directory and load skill metadata.

        Returns:
            Dictionary of skill_name -> Skill objects
        """
        if not self.skills_dir.exists():
            print(f"⚠️  Skills directory not found: {self.skills_dir}")
            return {}

        skill_count = 0
        for skill_dir in self.skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith('.'):
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    try:
                        skill = self._parse_metadata(skill_file)
                        self.skills[skill.name] = skill
                        skill_count += 1
                    except Exception as e:
                        print(f"⚠️  Failed to load skill from {skill_dir.name}: {e}")

        return self.skills

    def _parse_metadata(self, file_path: Path) -> Skill:
        """
        Parse YAML frontmatter from SKILL.md file.

        Args:
            file_path: Path to the SKILL.md file

        Returns:
            Skill object with metadata loaded (content not loaded yet)
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract YAML frontmatter
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if not match:
            # No frontmatter found, create basic metadata from filename
            skill_name = file_path.parent.name
            return Skill(
                name=skill_name,
                description=f"Skill: {skill_name}",
                file_path=file_path,
                metadata={"name": skill_name}
            )

        # Parse YAML frontmatter
        yaml_content = match.group(1)
        metadata = yaml.safe_load(yaml_content)

        # Extract required fields
        name = metadata.get("name", file_path.parent.name)
        description = metadata.get("description", f"Skill: {name}")

        return Skill(
            name=name,
            description=description,
            file_path=file_path,
            metadata=metadata
        )

    def load_skill_content(self, skill_name: str) -> Optional[str]:
        """
        Load full skill instructions on-demand.

        Args:
            skill_name: Name of the skill to load

        Returns:
            Full skill content, or None if skill not found
        """
        skill = self.skills.get(skill_name)
        if not skill:
            return None

        if not skill.loaded:
            try:
                with open(skill.file_path, 'r', encoding='utf-8') as f:
                    skill.content = f.read()
                skill.loaded = True
            except Exception as e:
                print(f"⚠️  Failed to load skill content for {skill_name}: {e}")
                return None

        return skill.content

    def get_skills_summary(self) -> str:
        """
        Get a formatted summary of all available skills.

        Returns:
            Formatted string listing all skills with descriptions
        """
        if not self.skills:
            return "No skills available."

        lines = ["Available Skills:"]
        for name, skill in sorted(self.skills.items()):
            # Truncate description if too long
            desc = skill.description
            if len(desc) > 100:
                desc = desc[:97] + "..."
            lines.append(f"  - {name}: {desc}")

        return "\n".join(lines)

    def should_activate_skill(self, skill_name: str, user_message: str) -> bool:
        """
        Determine if a skill should be activated based on user message.

        Args:
            skill_name: Name of the skill
            user_message: User's message text

        Returns:
            True if skill should be activated
        """
        # Simple keyword matching - skill name appears in message
        message_lower = user_message.lower()
        skill_lower = skill_name.lower()

        # Check for exact skill name match
        if skill_lower in message_lower:
            return True

        # Check for skill keywords in metadata
        skill = self.skills.get(skill_name)
        if skill and skill.metadata:
            keywords = skill.metadata.get("keywords", [])
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    return True

        return False

    def get_skill(self, skill_name: str) -> Optional[Skill]:
        """
        Get a skill by name.

        Args:
            skill_name: Name of the skill

        Returns:
            Skill object or None
        """
        return self.skills.get(skill_name)

    def list_skill_names(self) -> list[str]:
        """
        Get list of all available skill names.

        Returns:
            List of skill names
        """
        return list(self.skills.keys())
