"""Lead Agent with AWS Bedrock integration."""

import json
import boto3
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

import config
from prompts import LEAD_AGENT_PROMPT
from tools import ToolDispatcher
from task_manager import TaskManager
from compression import CompressionManager
from background_jobs import BackgroundJobManager
from mailbox import MailboxManager
from bedrock_client import create_bedrock_client


class LeadAgent:
    """Lead orchestrator agent using Claude Sonnet 4.6 via AWS Bedrock."""

    def __init__(self):
        """Initialize the Lead Agent."""
        # Initialize directories
        config.init_directories()

        # Initialize AWS Bedrock client with retry and fallback
        self.bedrock = create_bedrock_client()
        print(f"  🤖 Primary model: {self.bedrock.primary_model}")
        print(f"  🔄 Fallback model: {self.bedrock.fallback_model}")
        print(f"  ⏱️  Timeout: {config.BEDROCK_READ_TIMEOUT}s")

        # Initialize components
        self.tool_dispatcher = ToolDispatcher(config.STATE_DIR)
        self.task_manager = TaskManager(config.STATE_DIR)
        self.job_manager = BackgroundJobManager(config.STATE_DIR)
        self.mailbox = MailboxManager(config.STATE_DIR)

        # Conversation state
        self.messages: List[Dict[str, Any]] = []
        self.current_task_id: Optional[str] = None
        self.compression: Optional[CompressionManager] = None

        # Event log
        self.events_log = config.STATE_DIR / "logs" / "events.jsonl"
        self.events_log.parent.mkdir(parents=True, exist_ok=True)

        # Load subagent registry
        from subagent_loader import SubagentRegistry
        self.subagent_registry = SubagentRegistry(Path(__file__).parent)

        # Track active/completed subagents
        self.subagents: Dict[str, Any] = {}  # agent_id -> SubagentExecutor
        self.subagent_counter = 0

        # Load skills
        self.skill_loader = None
        if config.SKILLS_ENABLED and config.SKILLS_DIR.exists():
            from skill_loader import SkillLoader
            self.skill_loader = SkillLoader(config.SKILLS_DIR)
            self.skill_loader.discover_skills()
            skill_count = len(self.skill_loader.skills)
            if skill_count > 0:
                print(f"  Skills: {skill_count} available")

        print(f"✓ Lead Agent initialized (Phase 2)")
        print(f"  Model: {config.MODEL_ID}")
        print(f"  AWS Profile: {config.AWS_PROFILE}")
        print(f"  State Directory: {config.STATE_DIR.absolute()}")
        features = "Compression, Background Jobs, Mailbox, Workers"
        if self.skill_loader and len(self.skill_loader.skills) > 0:
            features += ", Skills"
        if len(self.subagent_registry.list_subagents()) > 0:
            subagent_count = len(self.subagent_registry.list_subagents())
            features += f", Subagents ({subagent_count})"
        print(f"  Features: {features}")

    def _log_event(self, event_type: str, data: Dict[str, Any]):
        """Log an event to disk."""
        event = {
            "timestamp": datetime.now().isoformat(),
            "type": event_type,
            "data": data
        }
        with open(self.events_log, "a") as f:
            f.write(json.dumps(event) + "\n")

    def _call_claude(self, user_message: Optional[str] = None) -> Dict[str, Any]:
        """Call Claude API via AWS Bedrock."""
        # Add user message if provided
        if user_message:
            # Check if any skills should be activated
            if self.skill_loader and self.skill_loader.skills:
                for skill_name, skill in self.skill_loader.skills.items():
                    if not skill.loaded and self.skill_loader.should_activate_skill(skill_name, user_message):
                        # Activate skill
                        content = self.skill_loader.load_skill_content(skill_name)
                        if content:
                            print(f"  🎯 Activated skill: {skill_name}")
                            # Inject skill content into user message
                            user_message = f"{user_message}\n\n<skill_activated name=\"{skill_name}\">\n{content}\n</skill_activated>"

            self.messages.append({
                "role": "user",
                "content": user_message
            })

        # Build system prompt with skills summary
        system_prompt = LEAD_AGENT_PROMPT
        if self.skill_loader and self.skill_loader.skills:
            skills_summary = self.skill_loader.get_skills_summary()
            system_prompt = system_prompt.format(skills_summary=skills_summary)
        else:
            system_prompt = system_prompt.format(skills_summary="No skills loaded.")

        # Build tool definitions (includes Agent tool)
        tools = self.tool_dispatcher.get_tool_definitions()
        # Add Agent tool from subagent registry
        agent_tool = self.subagent_registry.get_tool_definition_for_lead()
        tools.append(agent_tool)

        # Prepare request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.TEMPERATURE,
            "system": system_prompt,
            "messages": self.messages,
            "tools": tools
        }

        # Call Bedrock
        try:
            response = self.bedrock.invoke_model(
                modelId=config.MODEL_ID,
                body=json.dumps(request_body)
            )

            response_body = json.loads(response["body"].read())
            return response_body

        except Exception as e:
            print(f"❌ Error calling Bedrock: {e}")
            raise

    def _handle_tool_use(self, tool_use_block: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool use request from Claude."""
        tool_name = tool_use_block["name"]
        tool_input = tool_use_block["input"]
        tool_use_id = tool_use_block["id"]

        print(f"  🔧 Tool: {tool_name}")
        print(f"     Input: {json.dumps(tool_input, indent=2)}")

        # Special handling for Agent tool (spawn subagent)
        if tool_name == "Agent":
            result = self._handle_agent_tool(tool_input)

        # Special handling for task management tools
        elif tool_name == "create_task":
            task = self.task_manager.create_task(
                goal=tool_input["goal"],
                deps=tool_input.get("deps", []),
                priority=tool_input.get("priority", "med")
            )
            result = {"success": True, "task": task.to_dict()}

        elif tool_name == "update_task":
            task = self.task_manager.update_task(
                task_id=tool_input["task_id"],
                updates=tool_input["updates"]
            )
            result = {"success": True, "task": task.to_dict() if task else None}

        elif tool_name == "list_tasks":
            tasks = self.task_manager.list_tasks()
            result = {
                "success": True,
                "tasks": [t.to_dict() for t in tasks],
                "summary": self.task_manager.get_task_summary()
            }

        # Background job tools
        elif tool_name == "spawn_job":
            job = self.job_manager.spawn_job(
                command=tool_input["command"]
            )
            result = {"success": True, "job": job.to_dict()}

        elif tool_name == "get_job_status":
            job = self.job_manager.get_job(tool_input["job_id"])
            if job:
                result = {"success": True, "job": job.to_dict()}
            else:
                result = {"success": False, "error": "Job not found"}

        elif tool_name == "get_job_output":
            output = self.job_manager.get_job_output(tool_input["job_id"])
            result = {"success": True, "output": output}

        elif tool_name == "list_jobs":
            jobs = self.job_manager.list_jobs()
            result = {
                "success": True,
                "jobs": [j.to_dict() for j in jobs]
            }

        # Mailbox tools
        elif tool_name == "read_inbox":
            # Use lightweight summaries instead of full message content
            # This reduces token usage by ~40x (from 4000+ to ~100 tokens per message)
            summaries = self.mailbox.get_inbox_summary("Lead")
            result = {
                "success": True,
                "messages": summaries,
                "count": len(summaries),
                "note": "Messages are lightweight summaries. Use read_file on 'file_path' field to get full message content when needed."
            }

        elif tool_name == "send_message":
            msg = self.mailbox.send_message(
                from_agent="Lead",
                to_agent=tool_input["to_agent"],
                msg_type=tool_input["msg_type"],
                task_id=tool_input["task_id"],
                body=tool_input["body"]
            )
            result = {"success": True, "message": msg.to_dict()}

        else:
            # Dispatch to tool handlers
            result = self.tool_dispatcher.dispatch(tool_name, **tool_input)

        print(f"     Result: {json.dumps(result, indent=2)[:200]}...")

        return {
            "type": "tool_result",
            "tool_use_id": tool_use_id,
            "content": json.dumps(result)
        }

    def _handle_agent_tool(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """Handle Agent tool invocation (spawn subagent)."""
        subagent_type = tool_input['subagent_type']
        prompt = tool_input['prompt']
        description = tool_input.get('description', 'Subagent task')
        run_in_background = tool_input.get('run_in_background', False)
        resume = tool_input.get('resume')

        # Check if resuming existing subagent
        if resume and resume in self.subagents:
            print(f"\n🔄 Resuming subagent: {resume}")
            executor = self.subagents[resume]
            # Add continuation prompt to existing conversation
            executor.messages.append({
                "role": "user",
                "content": prompt
            })
            # Continue execution
            result = executor.execute_sync()
            return result

        # Get subagent definition
        definition = self.subagent_registry.get_subagent(subagent_type)
        if not definition:
            return {
                "success": False,
                "error": f"Unknown subagent type: {subagent_type}"
            }

        # Generate unique subagent ID
        self.subagent_counter += 1
        agent_id = f"agent-{self.subagent_counter:04d}"

        print(f"\n🔄 Spawning subagent: {subagent_type} ({agent_id})")
        print(f"   Task: {description}")

        # Create and execute subagent
        from subagent_executor import SubagentExecutor
        executor = SubagentExecutor(
            agent_id=agent_id,
            definition=definition,
            initial_prompt=prompt,
            parent_agent=self
        )

        # Track subagent
        self.subagents[agent_id] = executor

        # Execute (blocking or background)
        if run_in_background:
            result = executor.execute_async()
            print(f"   Status: Running in background")
            return {
                "success": True,
                "agent_id": agent_id,
                "status": "running",
                "message": f"Subagent {agent_id} started in background. Use agent_id to check status or resume."
            }
        else:
            result = executor.execute_sync()
            print(f"   Status: Completed in {executor.execution.turns} turns")
            return result

    def _process_response(self, response: Dict[str, Any]) -> bool:
        """Process Claude's response. Returns True if conversation should continue."""
        content = response.get("content", [])

        # Build assistant message
        assistant_message = {
            "role": "assistant",
            "content": content
        }
        self.messages.append(assistant_message)

        # Process content blocks
        has_tool_use = False
        tool_results = []

        for block in content:
            if block["type"] == "text":
                print(f"\n💬 Lead: {block['text']}\n")

            elif block["type"] == "tool_use":
                has_tool_use = True
                tool_result = self._handle_tool_use(block)
                tool_results.append(tool_result)

        # If there were tool uses, send results back
        if has_tool_use:
            self.messages.append({
                "role": "user",
                "content": tool_results
            })
            return True  # Continue conversation

        # Check stop reason
        stop_reason = response.get("stop_reason")
        if stop_reason == "end_turn":
            return False  # Conversation complete

        return False

    def _check_and_compress(self):
        """Check if compression is needed and perform it."""
        if self.compression and self.compression.should_compress(self.messages):
            print("\n📦 Compressing context...")

            # Extract key information from messages
            decisions = []
            artifacts = []
            open_tasks = [t.task_id for t in self.task_manager.list_tasks() if t.status != "DONE"]

            # Create compressed summary
            summary = self.compression.compress_messages_to_summary(
                messages=self.messages,
                current_goal=self.messages[0]["content"] if self.messages else "",
                decisions=decisions,
                artifacts=artifacts,
                open_tasks=open_tasks
            )

            # Update rolling summary
            self.compression.update_rolling_summary(summary)

            # Optionally inject context back
            context = self.compression.get_context_for_injection()
            if context:
                print(f"  Compressed {len(str(self.messages))} chars into summary")

    def run(self, goal: str):
        """Run the agent with a user goal."""
        print(f"\n{'='*60}")
        print(f"🎯 Goal: {goal}")
        print(f"{'='*60}\n")

        # Log initial event
        self._log_event("user_goal", {"goal": goal})

        # Check inbox for messages from workers
        unread = self.mailbox.get_unread_count("Lead")
        if unread > 0:
            print(f"📬 You have {unread} unread message(s) from workers")

        # Start conversation
        iteration = 0
        should_continue = True

        try:
            # Send initial goal
            response = self._call_claude(goal)
            should_continue = self._process_response(response)

            # Continue agent loop
            while should_continue and iteration < config.MAX_ITERATIONS:
                iteration += 1
                print(f"\n--- Iteration {iteration} ---")

                # Check for compression trigger
                if iteration % 5 == 0:
                    self._check_and_compress()

                response = self._call_claude()
                should_continue = self._process_response(response)

            print(f"\n{'='*60}")
            print(f"✅ Agent completed after {iteration} iterations")
            print(f"{'='*60}\n")

        except KeyboardInterrupt:
            print("\n\n⚠️  Agent interrupted by user")
        except Exception as e:
            print(f"\n\n❌ Agent error: {e}")
            raise

    def run_interactive(self):
        """Run the agent in interactive mode."""
        print("""
╔════════════════════════════════════════════════════════════╗
║     Claude Lead Agent - Interactive Mode (Phase 2)        ║
║                                                            ║
║  Commands:                                                 ║
║    /tasks    - List all tasks                             ║
║    /jobs     - List background jobs                       ║
║    /inbox    - Check messages from workers                ║
║    /workers  - Show how to start workers                  ║
║    /quit     - Exit                                       ║
║    <text>    - Send goal to agent                         ║
╚════════════════════════════════════════════════════════════╝
        """)

        while True:
            try:
                user_input = input("\n🎯 You: ").strip()

                if not user_input:
                    continue

                if user_input == "/quit":
                    print("Goodbye!")
                    break

                if user_input == "/tasks":
                    tasks = self.task_manager.list_tasks()
                    summary = self.task_manager.get_task_summary()
                    print(f"\n📋 Task Summary: {summary}")
                    for task in tasks:
                        owner_info = f" (owner: {task.owner})" if task.owner else ""
                        print(f"  [{task.status}] {task.task_id}: {task.goal}{owner_info}")
                    continue

                if user_input == "/jobs":
                    jobs = self.job_manager.list_jobs()
                    print(f"\n⚙️  Background Jobs: {len(jobs)}")
                    for job in jobs:
                        print(f"  [{job.status}] {job.job_id}: {job.command[:50]}...")
                    continue

                if user_input == "/inbox":
                    messages = self.mailbox.read_inbox("Lead", mark_read=False)
                    print(f"\n📬 Inbox: {len(messages)} message(s)")
                    for msg in messages:
                        print(f"  [{msg.type}] from {msg.from_agent} re: {msg.task_id}")
                        print(f"     {msg.body}")
                    continue

                if user_input == "/workers":
                    print("""
📚 How to Start Worker Agents:

In a new terminal, run:
  source .venv/bin/activate
  python worker_agent.py Worker_alpha

Or run in single-scan mode:
  python worker_agent.py Worker_alpha --once

Workers will:
- Scan the task board for OPEN tasks
- Claim tasks autonomously
- Execute tasks in isolated contexts
- Report back via mailboxes
                    """)
                    continue

                # Reset conversation for new goal
                self.messages = []
                self.run(user_input)

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    import sys

    agent = LeadAgent()

    if len(sys.argv) > 1:
        # Run with command-line goal
        goal = " ".join(sys.argv[1:])
        agent.run(goal)
    else:
        # Run in interactive mode
        agent.run_interactive()


if __name__ == "__main__":
    main()
