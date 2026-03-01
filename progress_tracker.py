"""Progress tracking system for multi-step tasks with token/cost/time monitoring."""

import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field, asdict


@dataclass
class TaskProgress:
    """Represents progress of a single task."""
    task_id: str
    description: str
    status: str  # pending, in_progress, completed, failed
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    tokens_used: int = 0
    cost_usd: float = 0.0
    notes: str = ""

    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None:
            return 0.0
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


@dataclass
class ProgressSession:
    """Tracks progress for an entire session/plan."""
    session_id: str
    title: str
    tasks: List[TaskProgress] = field(default_factory=list)
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_tokens: int = 0
    total_cost: float = 0.0

    def add_task(self, task_id: str, description: str) -> TaskProgress:
        """Add a new task to track."""
        task = TaskProgress(
            task_id=task_id,
            description=description,
            status="pending"
        )
        self.tasks.append(task)
        return task

    def start_task(self, task_id: str) -> Optional[TaskProgress]:
        """Mark task as started."""
        task = self.get_task(task_id)
        if task:
            task.status = "in_progress"
            task.start_time = time.time()
        return task

    def complete_task(self, task_id: str, tokens: int = 0, cost: float = 0.0, notes: str = "") -> Optional[TaskProgress]:
        """Mark task as completed."""
        task = self.get_task(task_id)
        if task:
            task.status = "completed"
            task.end_time = time.time()
            task.tokens_used = tokens
            task.cost_usd = cost
            task.notes = notes
            self.total_tokens += tokens
            self.total_cost += cost
        return task

    def fail_task(self, task_id: str, reason: str = "") -> Optional[TaskProgress]:
        """Mark task as failed."""
        task = self.get_task(task_id)
        if task:
            task.status = "failed"
            task.end_time = time.time()
            task.notes = reason
        return task

    def get_task(self, task_id: str) -> Optional[TaskProgress]:
        """Get task by ID."""
        for task in self.tasks:
            if task.task_id == task_id:
                return task
        return None

    def get_completed_tasks(self) -> List[TaskProgress]:
        """Get all completed tasks."""
        return [t for t in self.tasks if t.status == "completed"]

    def get_pending_tasks(self) -> List[TaskProgress]:
        """Get all pending tasks."""
        return [t for t in self.tasks if t.status == "pending"]

    def get_in_progress_tasks(self) -> List[TaskProgress]:
        """Get all in-progress tasks."""
        return [t for t in self.tasks if t.status == "in_progress"]

    def get_failed_tasks(self) -> List[TaskProgress]:
        """Get all failed tasks."""
        return [t for t in self.tasks if t.status == "failed"]

    def elapsed_time(self) -> float:
        """Get total elapsed time in seconds."""
        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def completion_percentage(self) -> float:
        """Get completion percentage."""
        if not self.tasks:
            return 0.0
        completed = len(self.get_completed_tasks())
        return (completed / len(self.tasks)) * 100

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "session_id": self.session_id,
            "title": self.title,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_tokens": self.total_tokens,
            "total_cost": self.total_cost,
            "elapsed_time": self.elapsed_time(),
            "completion_percentage": self.completion_percentage(),
            "tasks": [t.to_dict() for t in self.tasks]
        }


class ProgressTracker:
    """Manages progress tracking with persistence."""

    # Token pricing (per million tokens)
    PRICING = {
        "claude-sonnet-4.5": {
            "input": 3.00,  # $3 per million input tokens
            "output": 15.00  # $15 per million output tokens
        },
        "claude-opus-4.6": {
            "input": 15.00,
            "output": 75.00
        },
        "claude-haiku-4.5": {
            "input": 0.80,
            "output": 4.00
        }
    }

    def __init__(self, state_dir: Path, session_id: str = None, title: str = "Task Session"):
        """Initialize progress tracker.

        Args:
            state_dir: Directory to store progress files
            session_id: Optional session ID (auto-generated if not provided)
            title: Session title
        """
        self.state_dir = Path(state_dir)
        self.progress_dir = self.state_dir / "progress"
        self.progress_dir.mkdir(parents=True, exist_ok=True)

        if session_id is None:
            session_id = datetime.now().strftime("session-%Y%m%d-%H%M%S")

        self.session = ProgressSession(
            session_id=session_id,
            title=title
        )

        self.progress_file = self.progress_dir / f"{session_id}.json"

    def add_task(self, task_id: str, description: str) -> TaskProgress:
        """Add a new task."""
        task = self.session.add_task(task_id, description)
        self._save()
        return task

    def start_task(self, task_id: str) -> Optional[TaskProgress]:
        """Start a task."""
        task = self.session.start_task(task_id)
        self._save()
        return task

    def complete_task(self, task_id: str, input_tokens: int = 0, output_tokens: int = 0,
                      model: str = "claude-sonnet-4.5", notes: str = "") -> Optional[TaskProgress]:
        """Complete a task with token tracking.

        Args:
            task_id: Task ID
            input_tokens: Number of input tokens used
            output_tokens: Number of output tokens used
            model: Model name for pricing
            notes: Optional completion notes
        """
        total_tokens = input_tokens + output_tokens
        cost = self._calculate_cost(input_tokens, output_tokens, model)

        task = self.session.complete_task(task_id, total_tokens, cost, notes)
        self._save()
        return task

    def fail_task(self, task_id: str, reason: str = "") -> Optional[TaskProgress]:
        """Fail a task."""
        task = self.session.fail_task(task_id, reason)
        self._save()
        return task

    def _calculate_cost(self, input_tokens: int, output_tokens: int, model: str) -> float:
        """Calculate cost in USD."""
        if model not in self.PRICING:
            model = "claude-sonnet-4.5"  # Default

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        return input_cost + output_cost

    def _save(self):
        """Save progress to disk."""
        with open(self.progress_file, "w") as f:
            json.dump(self.session.to_dict(), f, indent=2)

    def print_summary(self, show_details: bool = False):
        """Print progress summary to console.

        Args:
            show_details: If True, show detailed task breakdown
        """
        print("\n" + "="*70)
        print(f"📊 PROGRESS REPORT: {self.session.title}")
        print("="*70)

        # Overall stats
        elapsed = self.session.elapsed_time()
        elapsed_str = str(timedelta(seconds=int(elapsed)))

        completed = len(self.session.get_completed_tasks())
        failed = len(self.session.get_failed_tasks())
        in_progress = len(self.session.get_in_progress_tasks())
        pending = len(self.session.get_pending_tasks())
        total = len(self.session.tasks)

        print(f"\n📈 Overall Progress: {self.session.completion_percentage():.1f}%")
        print(f"   ✅ Completed: {completed}/{total}")
        if failed > 0:
            print(f"   ❌ Failed: {failed}/{total}")
        if in_progress > 0:
            print(f"   🔄 In Progress: {in_progress}")
        if pending > 0:
            print(f"   ⏳ Pending: {pending}")

        print(f"\n⏱️  Time Elapsed: {elapsed_str}")
        print(f"🎯 Tokens Used: {self.session.total_tokens:,}")
        print(f"💰 Cost Incurred: ${self.session.total_cost:.4f} USD")

        # Cost breakdown by task
        if show_details and self.session.get_completed_tasks():
            print("\n" + "-"*70)
            print("📋 TASK BREAKDOWN:")
            print("-"*70)

            for task in self.session.tasks:
                status_icon = {
                    "completed": "✅",
                    "failed": "❌",
                    "in_progress": "🔄",
                    "pending": "⏳"
                }.get(task.status, "❓")

                print(f"\n{status_icon} [{task.task_id}] {task.description}")
                print(f"   Status: {task.status.upper()}")

                if task.start_time:
                    elapsed_task = task.elapsed_time()
                    print(f"   Time: {str(timedelta(seconds=int(elapsed_task)))}")

                if task.status == "completed":
                    print(f"   Tokens: {task.tokens_used:,}")
                    print(f"   Cost: ${task.cost_usd:.4f}")

                if task.notes:
                    print(f"   Notes: {task.notes}")

        # Outstanding tasks
        pending_tasks = self.session.get_pending_tasks()
        if pending_tasks:
            print("\n" + "-"*70)
            print("⏳ OUTSTANDING TASKS:")
            print("-"*70)
            for task in pending_tasks:
                print(f"   • [{task.task_id}] {task.description}")

        # Current task
        in_progress_tasks = self.session.get_in_progress_tasks()
        if in_progress_tasks:
            print("\n" + "-"*70)
            print("🔄 CURRENT TASK:")
            print("-"*70)
            for task in in_progress_tasks:
                elapsed_task = task.elapsed_time()
                print(f"   • [{task.task_id}] {task.description}")
                print(f"     Running for: {str(timedelta(seconds=int(elapsed_task)))}")

        print("\n" + "="*70 + "\n")

    def print_compact_summary(self):
        """Print compact one-line summary."""
        completed = len(self.session.get_completed_tasks())
        total = len(self.session.tasks)
        percentage = self.session.completion_percentage()
        elapsed = str(timedelta(seconds=int(self.session.elapsed_time())))

        print(f"📊 Progress: {completed}/{total} ({percentage:.0f}%) | "
              f"⏱️  {elapsed} | "
              f"🎯 {self.session.total_tokens:,} tokens | "
              f"💰 ${self.session.total_cost:.4f}")

    @staticmethod
    def load_session(state_dir: Path, session_id: str) -> Optional['ProgressTracker']:
        """Load a saved session."""
        tracker = ProgressTracker(state_dir, session_id)
        if tracker.progress_file.exists():
            with open(tracker.progress_file, "r") as f:
                data = json.load(f)

            # Reconstruct session
            tracker.session.start_time = data["start_time"]
            tracker.session.end_time = data.get("end_time")
            tracker.session.total_tokens = data["total_tokens"]
            tracker.session.total_cost = data["total_cost"]

            # Reconstruct tasks
            tracker.session.tasks = []
            for task_data in data["tasks"]:
                task = TaskProgress(**task_data)
                tracker.session.tasks.append(task)

            return tracker
        return None


# Convenience function for quick tracking
def create_tracker(title: str = "Task Session") -> ProgressTracker:
    """Create a new progress tracker."""
    from pathlib import Path
    import config
    return ProgressTracker(config.STATE_DIR, title=title)
