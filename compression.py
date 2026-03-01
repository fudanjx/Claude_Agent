"""Three-layer compression strategy for infinite sessions."""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import config


class CompressionManager:
    """Manages 3-layer memory compression for infinite sessions."""

    def __init__(self, task_dir: Path):
        """Initialize compression manager for a task.

        Args:
            task_dir: Path to task directory (e.g., .agent_state/tasks/T-xxx)
        """
        self.task_dir = task_dir
        self.context_dir = task_dir / "context"
        self.context_dir.mkdir(parents=True, exist_ok=True)

        self.archive_dir = self.context_dir / "archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.working_set_file = self.context_dir / "working_set.md"
        self.rolling_summary_file = self.context_dir / "rolling_summary.md"

        # Thresholds from configuration (allows customization via config.yaml or .env)
        self.WORKING_SET_MAX_CHARS = config.WORKING_SET_MAX_CHARS
        self.ROLLING_SUMMARY_MAX_CHARS = config.ROLLING_SUMMARY_MAX_CHARS

    def get_working_set(self) -> str:
        """Get current working set."""
        if self.working_set_file.exists():
            return self.working_set_file.read_text()
        return ""

    def get_rolling_summary(self) -> str:
        """Get rolling summary."""
        if self.rolling_summary_file.exists():
            return self.rolling_summary_file.read_text()
        return ""

    def update_working_set(self, content: str):
        """Update working set with new content."""
        self.working_set_file.write_text(content)

        # Check if compression is needed
        if len(content) > self.WORKING_SET_MAX_CHARS:
            self._compress_working_set()

    def update_rolling_summary(self, content: str):
        """Update rolling summary."""
        self.rolling_summary_file.write_text(content)

        # Check if archiving is needed
        if len(content) > self.ROLLING_SUMMARY_MAX_CHARS:
            self._archive_rolling_summary()

    def _compress_working_set(self):
        """Compress working set into rolling summary."""
        working_set = self.get_working_set()
        rolling_summary = self.get_rolling_summary()

        # Create compression prompt
        compression_note = f"""
## Compressed from Working Set ({datetime.now().isoformat()})

{working_set}

---
"""

        # Append to rolling summary
        new_summary = rolling_summary + "\n" + compression_note
        self.update_rolling_summary(new_summary)

        # Clear working set
        self.working_set_file.write_text(
            f"# Working Set\n\n*Previous content compressed to rolling_summary.md*\n"
        )

    def _archive_rolling_summary(self):
        """Archive rolling summary to numbered chunk."""
        rolling_summary = self.get_rolling_summary()

        # Find next chunk number
        existing_chunks = list(self.archive_dir.glob("chunk_*.md"))
        next_num = len(existing_chunks) + 1

        chunk_file = self.archive_dir / f"chunk_{next_num:04d}.md"
        chunk_file.write_text(rolling_summary)

        # Reset rolling summary with pointer
        self.rolling_summary_file.write_text(
            f"""# Rolling Summary

*Previous content archived to: {chunk_file.name}*

## Current State
(Summary will be built as work progresses)
"""
        )

    def compress_messages_to_summary(
        self,
        messages: List[Dict[str, Any]],
        current_goal: str,
        decisions: List[str],
        artifacts: List[str],
        open_tasks: List[str]
    ) -> str:
        """Compress message history into structured summary.

        Returns formatted summary string ready for injection.
        """
        summary = f"""# Task Summary

## Goal
{current_goal}

## Facts We Trust
"""

        # Extract facts from messages
        for msg in messages:
            if msg["role"] == "assistant":
                content = msg.get("content", [])
                if isinstance(content, list):
                    for block in content:
                        if block.get("type") == "text":
                            # Simple extraction - in production, use LLM
                            summary += f"- {block['text'][:100]}...\n"

        summary += f"""

## Decisions Made
"""
        for decision in decisions:
            summary += f"- {decision}\n"

        summary += f"""

## Artifacts & Paths
"""
        for artifact in artifacts:
            summary += f"- {artifact}\n"

        summary += f"""

## Open Tasks
"""
        for task in open_tasks:
            summary += f"- {task}\n"

        summary += f"""

## Next Step
(To be determined based on current context)

---
*Compressed: {datetime.now().isoformat()}*
"""

        return summary

    def should_compress(self, messages: List[Dict[str, Any]]) -> bool:
        """Check if message list should be compressed.

        Args:
            messages: Current message array

        Returns:
            True if compression is needed
        """
        # Count total characters in messages
        total_chars = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total_chars += len(content)
            elif isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        total_chars += len(str(block))

        # Compress if over threshold
        return total_chars > self.ROLLING_SUMMARY_MAX_CHARS

    def get_context_for_injection(self) -> str:
        """Get context string for injecting into messages.

        Returns:
            Formatted context combining all layers
        """
        context = "# Context (from memory)\n\n"

        # Add working set
        working_set = self.get_working_set()
        if working_set:
            context += "## Current Working Set\n\n"
            context += working_set + "\n\n"

        # Add rolling summary
        rolling_summary = self.get_rolling_summary()
        if rolling_summary:
            context += "## Recent History\n\n"
            context += rolling_summary + "\n\n"

        # List archived chunks (don't inject content unless requested)
        chunks = sorted(self.archive_dir.glob("chunk_*.md"))
        if chunks:
            context += "## Archive\n\n"
            context += f"Available chunks: {', '.join(c.name for c in chunks)}\n"
            context += "(Use read_file to access specific chunks if needed)\n\n"

        return context

    def create_initial_working_set(self, goal: str, plan: str):
        """Create initial working set for a new task."""
        content = f"""# Working Set

## Goal
{goal}

## Plan
{plan}

## Current Status
Started

## Key Facts
(Will be updated as work progresses)

## Active Decisions
(Will be tracked here)

---
*Created: {datetime.now().isoformat()}*
"""
        self.update_working_set(content)

        # Initialize rolling summary if it doesn't exist
        if not self.rolling_summary_file.exists():
            initial_summary = f"""# Rolling Summary

## Current State
Task started: {goal}

## Progress
Initialization complete

---
*Created: {datetime.now().isoformat()}*
"""
            self.rolling_summary_file.write_text(initial_summary)
