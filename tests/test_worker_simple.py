#!/usr/bin/env python3
"""Simple worker test with minimal complexity."""

import config
from task_manager import TaskManager
from worker_agent import WorkerAgent

def main():
    """Test worker with a very simple task."""
    print("="*60)
    print("Testing Worker with Simple Task")
    print("="*60)

    config.init_directories()
    task_mgr = TaskManager(config.STATE_DIR)

    # Create a very simple task
    task = task_mgr.create_task(
        goal="Use bash to run 'echo Hello from worker > /tmp/worker_test.txt'",
        priority="high"
    )

    print(f"\n✓ Created simple task: {task.task_id}")
    print(f"  Goal: {task.goal}")
    print(f"  Status: {task.status}")

    # Create worker and run single scan
    print(f"\n🤖 Starting worker...")
    worker = WorkerAgent("Worker_simple_test")

    try:
        worker.run_scan_cycle()

        # Check task status after
        updated_task = task_mgr.get_task(task.task_id)
        print(f"\n📊 Final task status: {updated_task.status}")

        # Check if file was created
        import os
        if os.path.exists("/tmp/worker_test.txt"):
            with open("/tmp/worker_test.txt", "r") as f:
                content = f.read()
            print(f"✓ Output file created:")
            print(f"  Content: {content.strip()}")
        else:
            print(f"⚠️  Output file not found (task may have failed)")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
