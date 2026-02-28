"""File-based task management system."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class Task:
    """Task data model."""
    task_id: str
    goal: str
    status: str  # OPEN, CLAIMED, IN_PROGRESS, BLOCKED, DONE
    owner: Optional[str] = None
    deps: List[str] = None
    created_at: str = None
    updated_at: str = None
    priority: str = "med"  # low, med, high
    workdir: str = None
    inputs: List[str] = None
    outputs: List[str] = None
    acceptance_criteria: List[str] = None
    required_skills: List[str] = None  # Phase 3: Skills required for task
    retry_count: int = 0  # Phase 3: Number of retry attempts
    max_retries: int = 3  # Phase 3: Maximum retry attempts

    def __post_init__(self):
        if self.deps is None:
            self.deps = []
        if self.inputs is None:
            self.inputs = []
        if self.outputs is None:
            self.outputs = []
        if self.acceptance_criteria is None:
            self.acceptance_criteria = []
        if self.required_skills is None:
            self.required_skills = []
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
        if self.workdir is None:
            self.workdir = f"worktrees/{self.task_id}/"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class TaskManager:
    """Manages file-based task board and task lifecycle."""

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.board_dir = state_dir / "board"
        self.tasks_dir = state_dir / "tasks"
        self.worktrees_dir = state_dir / "worktrees"
        self.tasks_file = self.board_dir / "tasks.jsonl"

        # Ensure directories exist
        self.board_dir.mkdir(parents=True, exist_ok=True)
        self.tasks_dir.mkdir(parents=True, exist_ok=True)
        self.worktrees_dir.mkdir(parents=True, exist_ok=True)

        # Create tasks.jsonl if not exists
        if not self.tasks_file.exists():
            self.tasks_file.touch()

    def _generate_task_id(self) -> str:
        """Generate a unique task ID."""
        date_str = datetime.now().strftime("%Y%m%d")
        # Count existing tasks for today
        count = sum(1 for _ in self._read_tasks() if _.task_id.startswith(f"T-{date_str}"))
        return f"T-{date_str}-{count + 1:04d}"

    def _read_tasks(self) -> List[Task]:
        """Read all tasks from tasks.jsonl."""
        tasks = []
        if self.tasks_file.exists():
            with open(self.tasks_file, "r") as f:
                for line in f:
                    if line.strip():
                        task_data = json.loads(line)
                        tasks.append(Task(**task_data))
        return tasks

    def _append_task_record(self, task: Task):
        """Append task record to tasks.jsonl (append-only log)."""
        with open(self.tasks_file, "a") as f:
            f.write(json.dumps(task.to_dict()) + "\n")

    def _write_task_file(self, task: Task):
        """Write task.json to task directory."""
        task_dir = self.tasks_dir / task.task_id
        task_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (task_dir / "context").mkdir(exist_ok=True)
        (task_dir / "context" / "archive").mkdir(exist_ok=True)
        (task_dir / "mail" / "inbox").mkdir(parents=True, exist_ok=True)
        (task_dir / "mail" / "outbox").mkdir(parents=True, exist_ok=True)
        (task_dir / "logs").mkdir(exist_ok=True)
        (task_dir / "outputs" / "artifacts").mkdir(parents=True, exist_ok=True)

        # Write task.json
        task_file = task_dir / "task.json"
        with open(task_file, "w") as f:
            json.dump(task.to_dict(), f, indent=2)

        # Create worktree README
        worktree_dir = self.worktrees_dir / task.task_id
        worktree_dir.mkdir(parents=True, exist_ok=True)
        readme_path = worktree_dir / "README.md"
        readme_content = f"""# Task: {task.task_id}

## Goal
{task.goal}

## Status
{task.status}

## Owner
{task.owner or "Unassigned"}

## Priority
{task.priority}

## Dependencies
{", ".join(task.deps) if task.deps else "None"}

## Acceptance Criteria
{chr(10).join(f"- {criterion}" for criterion in task.acceptance_criteria) if task.acceptance_criteria else "None specified"}
"""
        readme_path.write_text(readme_content)

    def create_task(
        self,
        goal: str,
        deps: List[str] = None,
        priority: str = "med",
        owner: Optional[str] = None,
        acceptance_criteria: List[str] = None,
        required_skills: List[str] = None
    ) -> Task:
        """Create a new task."""
        task_id = self._generate_task_id()
        task = Task(
            task_id=task_id,
            goal=goal,
            status="OPEN",
            owner=owner,
            deps=deps or [],
            priority=priority,
            acceptance_criteria=acceptance_criteria or [],
            required_skills=required_skills or []
        )

        # Write to append-only log
        self._append_task_record(task)

        # Write task directory structure
        self._write_task_file(task)

        return task

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID (reads from task.json)."""
        task_file = self.tasks_dir / task_id / "task.json"
        if not task_file.exists():
            return None

        with open(task_file, "r") as f:
            task_data = json.load(f)
            return Task(**task_data)

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> Optional[Task]:
        """Update a task."""
        task = self.get_task(task_id)
        if not task:
            return None

        # Apply updates
        for key, value in updates.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.updated_at = datetime.now().isoformat()

        # Write updated task
        self._write_task_file(task)

        # Append update record to log
        self._append_task_record(task)

        return task

    def list_tasks(self, status: Optional[str] = None, owner: Optional[str] = None) -> List[Task]:
        """List tasks with optional filters."""
        # Build index from task directories (latest state)
        tasks = []
        for task_dir in self.tasks_dir.iterdir():
            if task_dir.is_dir():
                task_file = task_dir / "task.json"
                if task_file.exists():
                    with open(task_file, "r") as f:
                        task_data = json.load(f)
                        task = Task(**task_data)

                        # Apply filters
                        if status and task.status != status:
                            continue
                        if owner and task.owner != owner:
                            continue

                        tasks.append(task)

        return sorted(tasks, key=lambda t: t.created_at)

    def get_task_summary(self) -> Dict[str, int]:
        """Get summary of tasks by status."""
        tasks = self.list_tasks()
        summary = {"OPEN": 0, "CLAIMED": 0, "IN_PROGRESS": 0, "BLOCKED": 0, "DONE": 0}
        for task in tasks:
            summary[task.status] = summary.get(task.status, 0) + 1
        return summary
