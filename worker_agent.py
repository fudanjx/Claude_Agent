"""Worker Agent - autonomous teammate that claims and executes tasks."""

import json
import time
import boto3
from pathlib import Path
from typing import List, Dict, Any, Optional

import config
from prompts import WORKER_AGENT_PROMPT
from tools import ToolDispatcher
from task_manager import TaskManager, Task
from mailbox import MailboxManager
from compression import CompressionManager
from worker_skills import WorkerSkills, SkillMatcher, get_worker_profile
from error_recovery import RetryStrategy, ErrorClassifier, ErrorRecoveryManager, ErrorType
from skill_loader import SkillLoader
from bedrock_client import create_bedrock_client


class WorkerAgent:
    """Worker agent that self-claims tasks and reports via mailboxes."""

    def __init__(self, name: str, skills: set = None, profile: str = None):
        """Initialize worker agent.

        Args:
            name: Worker name (e.g., "Worker_alpha")
            skills: Set of skills (optional, uses profile if not provided)
            profile: Worker profile name (e.g., "researcher", "developer")
        """
        self.name = name

        # Phase 3: Skills
        if skills:
            self.skills = skills
        elif profile:
            self.skills = get_worker_profile(profile)
        else:
            # Default to general worker
            self.skills = {WorkerSkills.GENERAL}

        print(f"  Skills: {', '.join(self.skills)}")

        # Initialize AWS Bedrock client with retry and fallback
        self.bedrock = create_bedrock_client()

        # Initialize components
        self.tool_dispatcher = ToolDispatcher(config.STATE_DIR)
        self.task_manager = TaskManager(config.STATE_DIR)
        self.mailbox = MailboxManager(config.STATE_DIR)
        self.error_recovery = ErrorRecoveryManager(config.STATE_DIR)
        self.retry_strategy = RetryStrategy()

        # Initialize skill loader for specialized task guidance
        self.skill_loader = None
        if config.SKILLS_ENABLED and config.SKILLS_DIR.exists():
            self.skill_loader = SkillLoader(config.SKILLS_DIR)
            self.skill_loader.discover_skills()
            print(f"  📚 Skills: {len(self.skill_loader.skills)} skill packages available")

        # Create worker mailbox
        worker_inbox = config.MAILBOXES_DIR / self.name / "inbox"
        worker_inbox.mkdir(parents=True, exist_ok=True)
        (config.MAILBOXES_DIR / self.name / "outbox").mkdir(parents=True, exist_ok=True)

        # Worker state
        self.current_task: Optional[Task] = None
        self.messages: List[Dict[str, Any]] = []

        print(f"✓ Worker Agent '{self.name}' initialized")

    def _call_claude(self, user_message: Optional[str] = None) -> Dict[str, Any]:
        """Call Claude API via AWS Bedrock."""
        if user_message:
            self.messages.append({
                "role": "user",
                "content": user_message
            })

        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.TEMPERATURE,
            "system": WORKER_AGENT_PROMPT,
            "messages": self.messages,
            "tools": self.tool_dispatcher.get_tool_definitions()
        }

        try:
            response = self.bedrock.invoke_model(
                modelId=config.MODEL_ID,
                body=json.dumps(request_body)
            )
            return json.loads(response["body"].read())
        except Exception as e:
            print(f"❌ Worker {self.name} - Bedrock error: {e}")
            raise

    def _handle_tool_use(self, tool_use_block: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool use."""
        tool_name = tool_use_block["name"]
        tool_input = tool_use_block["input"]
        tool_use_id = tool_use_block["id"]

        print(f"  🔧 {self.name} Tool: {tool_name}")

        try:
            result = self.tool_dispatcher.dispatch(tool_name, **tool_input)
        except Exception as e:
            print(f"  ❌ Tool error: {e}")
            print(f"     Tool: {tool_name}")
            print(f"     Input: {tool_input}")
            result = {
                "success": False,
                "error": f"{type(e).__name__}: {str(e)}",
                "tool": tool_name,
                "input_received": tool_input
            }

        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": json.dumps(result)
        }

    def _process_response(self, response: Dict[str, Any]) -> bool:
        """Process Claude's response. Returns True if should continue."""
        content = response.get("content", [])

        assistant_message = {
            "role": "assistant",
            "content": content
        }
        self.messages.append(assistant_message)

        has_tool_use = False
        tool_results = []

        for block in content:
            if block["type"] == "text":
                print(f"  💬 {self.name}: {block['text'][:200]}...")

            elif block["type"] == "tool_use":
                has_tool_use = True
                tool_result = self._handle_tool_use(block)
                tool_results.append(tool_result)

        if has_tool_use:
            self.messages.append({
                "role": "user",
                "content": tool_results
            })
            return True

        return response.get("stop_reason") != "end_turn"

    def scan_for_claimable_tasks(self) -> List[Task]:
        """Scan task board for claimable tasks (Phase 3: skill-aware)."""
        tasks = self.task_manager.list_tasks(status="OPEN")

        # Filter tasks with no owner and no blocking deps
        claimable = []
        for task in tasks:
            if task.owner is None:
                # Check if dependencies are satisfied
                all_deps_done = True
                for dep_id in task.deps:
                    dep_task = self.task_manager.get_task(dep_id)
                    if dep_task and dep_task.status != "DONE":
                        all_deps_done = False
                        break

                if not all_deps_done:
                    continue

                # Phase 3: Check skills
                required_skills = set(task.required_skills or [])
                if SkillMatcher.can_claim(self.skills, required_skills):
                    # Calculate match score for prioritization
                    score = SkillMatcher.skill_match_score(self.skills, required_skills)
                    claimable.append((task, score))

        # Sort by skill match score (best matches first)
        claimable.sort(key=lambda x: x[1], reverse=True)

        # Return just tasks (without scores)
        return [task for task, score in claimable]

    def claim_task(self, task: Task) -> bool:
        """Attempt to claim a task atomically.

        Returns:
            True if claim succeeded
        """
        # Try to update task with owner
        updated_task = self.task_manager.update_task(
            task.task_id,
            {"owner": self.name, "status": "CLAIMED"}
        )

        if updated_task:
            self.current_task = updated_task

            # Send CLAIM message
            self.mailbox.create_claim_message(
                from_agent=self.name,
                task_id=task.task_id,
                why_me=f"Worker {self.name} available and capable",
                eta_hint="medium",
                workdir=task.workdir
            )

            print(f"✓ {self.name} claimed task {task.task_id}")
            return True

        return False

    def execute_task(self, task: Task):
        """Execute a claimed task."""
        print(f"\n{'='*60}")
        print(f"🔨 {self.name} executing: {task.task_id}")
        print(f"   Goal: {task.goal}")
        print(f"{'='*60}\n")

        # Update task status
        self.task_manager.update_task(task.task_id, {"status": "IN_PROGRESS"})

        # Initialize compression for this task
        task_dir = config.TASKS_DIR / task.task_id
        compression = CompressionManager(task_dir)

        # Create initial working set
        compression.create_initial_working_set(
            goal=task.goal,
            plan="(Will be created by worker)"
        )

        # Reset messages for isolated context
        self.messages = []

        # Build task context
        context = f"""You are working on task {task.task_id}.

Goal: {task.goal}

Priority: {task.priority}

Acceptance Criteria:
{chr(10).join(f"- {c}" for c in task.acceptance_criteria) if task.acceptance_criteria else "None specified"}

Your working directory is: {task.workdir}

Please:
1. Plan your approach
2. Execute the task using available tools
3. Produce clear outputs/deliverables
4. Report completion with summary

Remember: You are a Worker agent. Keep your context isolated and cite tool outputs.
"""

        # Inject relevant skill guidance if available
        if self.skill_loader and self.skill_loader.skills:
            activated_skills = []
            for skill_name, skill in self.skill_loader.skills.items():
                if self.skill_loader.should_activate_skill(skill_name, task.goal):
                    content = self.skill_loader.load_skill_content(skill_name)
                    if content:
                        context += f"\n\n<skill_guidance name=\"{skill_name}\">\n{content}\n</skill_guidance>\n"
                        activated_skills.append(skill_name)

            if activated_skills:
                print(f"  🎯 Activated skills: {', '.join(activated_skills)}")
            else:
                print(f"  📚 No specific skills activated for this task")

        try:
            # Send context and start execution
            iteration = 0
            max_iterations = config.WORKER_MAX_ITERATIONS
            should_continue = True

            response = self._call_claude(context)
            should_continue = self._process_response(response)

            while should_continue and iteration < max_iterations:
                iteration += 1
                response = self._call_claude()
                should_continue = self._process_response(response)

            # Mark task as done
            self.task_manager.update_task(
                task.task_id,
                {"status": "DONE"}
            )

            # Send COMPLETE message
            self.mailbox.create_complete_message(
                from_agent=self.name,
                to_agent="Lead",
                task_id=task.task_id,
                deliverable=f"Task completed by {self.name}",
                files=[],
                next_steps=[]
            )

            print(f"\n✅ {self.name} completed task {task.task_id}")

        except Exception as e:
            print(f"\n❌ {self.name} - Error executing task: {e}")
            import traceback
            traceback.print_exc()

            # Release task ownership on critical error
            self.task_manager.update_task(
                task.task_id,
                {"status": "OPEN", "owner": None}
            )

            print(f"  → Task {task.task_id} released back to OPEN status")

            # Send BLOCKED message
            try:
                self.mailbox.create_blocked_message(
                    from_agent=self.name,
                    to_agent="Lead",
                    task_id=task.task_id,
                    reason=f"Error: {str(e)}",
                    unblock_options=["Fix tool usage", "Retry", "Reassign"]
                )
            except Exception as msg_error:
                print(f"  ⚠️  Could not send blocked message: {msg_error}")

    def run_scan_cycle(self):
        """Run one scan-and-claim cycle."""
        print(f"\n{self.name}: Scanning for claimable tasks...")

        claimable = self.scan_for_claimable_tasks()

        if not claimable:
            print(f"  No claimable tasks found.")
            return

        print(f"  Found {len(claimable)} claimable task(s)")

        # Try to claim first available task
        for task in claimable:
            if self.claim_task(task):
                self.execute_task(task)
                break

    def run_daemon(self, scan_interval: int = 10):
        """Run worker in daemon mode (continuous scanning).

        Args:
            scan_interval: Seconds between scans
        """
        print(f"\n{'='*60}")
        print(f"🤖 {self.name} running in daemon mode")
        print(f"   Scan interval: {scan_interval}s")
        print(f"{'='*60}\n")

        try:
            while True:
                self.run_scan_cycle()
                time.sleep(scan_interval)

        except KeyboardInterrupt:
            print(f"\n{self.name} stopped by user")


def main():
    """Main entry point for worker agent."""
    import sys

    worker_name = sys.argv[1] if len(sys.argv) > 1 else "Worker_alpha"
    scan_interval = int(sys.argv[2]) if len(sys.argv) > 2 else config.WORKER_SCAN_INTERVAL

    worker = WorkerAgent(worker_name)

    if "--once" in sys.argv:
        # Run single scan cycle
        worker.run_scan_cycle()
    else:
        # Run in daemon mode
        worker.run_daemon(scan_interval=scan_interval)


if __name__ == "__main__":
    main()
