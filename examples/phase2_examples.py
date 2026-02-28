#!/usr/bin/env python3
"""Phase 2 Feature Examples - Background Jobs, Workers, Compression."""

from lead_agent import LeadAgent
from worker_agent import WorkerAgent
from task_manager import TaskManager
from background_jobs import BackgroundJobManager
from mailbox import MailboxManager
import config
import time


def example_1_background_jobs():
    """Example: Using background jobs for long-running tasks."""
    print("\n" + "="*60)
    print("PHASE 2 EXAMPLE 1: Background Jobs")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Create a task and spawn a background job that sleeps for 5 seconds, "
        "then check the job status"
    )


def example_2_multi_agent():
    """Example: Create tasks for workers to claim."""
    print("\n" + "="*60)
    print("PHASE 2 EXAMPLE 2: Multi-Agent Coordination")
    print("="*60)

    config.init_directories()
    task_mgr = TaskManager(config.STATE_DIR)

    # Create multiple tasks
    print("Creating tasks for workers...")

    task1 = task_mgr.create_task(
        goal="Research the top 3 Python web frameworks and create a comparison",
        priority="high"
    )
    print(f"✓ Created {task1.task_id}")

    task2 = task_mgr.create_task(
        goal="Analyze the security features of Python's asyncio module",
        priority="med"
    )
    print(f"✓ Created {task2.task_id}")

    task3 = task_mgr.create_task(
        goal="Create a summary of Python's type hinting evolution",
        priority="low"
    )
    print(f"✓ Created {task3.task_id}")

    print(f"""
Tasks created! Now start workers in separate terminals:

Terminal 2:
  source .venv/bin/activate && python worker_agent.py Worker_alpha

Terminal 3:
  source .venv/bin/activate && python worker_agent.py Worker_beta

Workers will automatically claim and execute these tasks.
Monitor progress with:
  python lead_agent.py
  > /tasks
  > /inbox
    """)


def example_3_mailbox_communication():
    """Example: Mailbox communication between agents."""
    print("\n" + "="*60)
    print("PHASE 2 EXAMPLE 3: Mailbox Communication")
    print("="*60)

    config.init_directories()
    mailbox = MailboxManager(config.STATE_DIR)

    # Send a test message
    msg = mailbox.create_request_message(
        from_agent="Lead",
        to_agent="Worker_alpha",
        task_id="T-TEST-0001",
        intent="research",
        goal="Test mailbox communication",
        priority="med"
    )

    print(f"✓ Sent message {msg.msg_id}")
    print(f"  From: {msg.from_agent}")
    print(f"  To: {msg.to_agent}")
    print(f"  Type: {msg.type}")
    print(f"  Task: {msg.task_id}")

    # Check inbox
    unread = mailbox.get_unread_count("Worker_alpha")
    print(f"\n📬 Worker_alpha has {unread} unread message(s)")

    # Read messages
    messages = mailbox.read_inbox("Worker_alpha", mark_read=False)
    for m in messages:
        print(f"\nMessage {m.msg_id}:")
        print(f"  Type: {m.type}")
        print(f"  Body: {m.body}")


def example_4_compression():
    """Example: Context compression."""
    print("\n" + "="*60)
    print("PHASE 2 EXAMPLE 4: Context Compression")
    print("="*60)

    config.init_directories()
    task_mgr = TaskManager(config.STATE_DIR)

    # Create a task
    task = task_mgr.create_task(
        goal="Long-running research task that will demonstrate compression",
        priority="med"
    )

    from compression import CompressionManager
    task_dir = config.TASKS_DIR / task.task_id
    compression = CompressionManager(task_dir)

    # Create initial working set
    compression.create_initial_working_set(
        goal=task.goal,
        plan="1. Research\n2. Analyze\n3. Summarize"
    )

    print(f"✓ Created task {task.task_id}")
    print(f"✓ Initialized compression layers")

    # Show compression structure
    print(f"\nCompression files:")
    print(f"  Working Set: {compression.working_set_file}")
    print(f"  Rolling Summary: {compression.rolling_summary_file}")
    print(f"  Archive: {compression.archive_dir}")

    # Read working set
    working_set = compression.get_working_set()
    print(f"\nWorking Set Preview:")
    print(working_set[:300] + "...")


def example_5_worker_scan():
    """Example: Worker scanning for tasks."""
    print("\n" + "="*60)
    print("PHASE 2 EXAMPLE 5: Worker Self-Claim")
    print("="*60)

    config.init_directories()
    task_mgr = TaskManager(config.STATE_DIR)

    # Create a simple task
    task = task_mgr.create_task(
        goal="Check Python version and create a report file",
        priority="high"
    )

    print(f"✓ Created task {task.task_id}")
    print(f"\nNow running worker in single-scan mode...")

    # Create worker and run single scan
    worker = WorkerAgent("Worker_test")
    worker.run_scan_cycle()

    print(f"\n✓ Worker scan complete")
    print(f"  Check task status: {task_mgr.get_task(task.task_id).status}")


if __name__ == "__main__":
    import sys

    examples = {
        "1": ("Background Jobs", example_1_background_jobs),
        "2": ("Multi-Agent Coordination", example_2_multi_agent),
        "3": ("Mailbox Communication", example_3_mailbox_communication),
        "4": ("Context Compression", example_4_compression),
        "5": ("Worker Self-Claim", example_5_worker_scan)
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, func = examples[sys.argv[1]]
        print(f"\n🚀 Running: {name}")
        func()
    else:
        print("""
Phase 2 Examples - Available:

  python phase2_examples.py 1  - Background Jobs
  python phase2_examples.py 2  - Multi-Agent Coordination
  python phase2_examples.py 3  - Mailbox Communication
  python phase2_examples.py 4  - Context Compression
  python phase2_examples.py 5  - Worker Self-Claim

Each example demonstrates a Phase 2 feature.
        """)
