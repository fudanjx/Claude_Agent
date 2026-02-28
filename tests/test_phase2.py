#!/usr/bin/env python3
"""Test script to verify Phase 2 features."""

import sys
from pathlib import Path

def test_imports():
    """Test that all Phase 2 modules can be imported."""
    print("Testing imports...")
    try:
        import config
        from compression import CompressionManager
        from background_jobs import BackgroundJobManager
        from mailbox import MailboxManager
        from worker_agent import WorkerAgent
        from lead_agent import LeadAgent
        print("  ✓ All imports successful")
        return True
    except Exception as e:
        print(f"  ❌ Import failed: {e}")
        return False


def test_compression():
    """Test compression manager."""
    print("\nTesting Compression Manager...")
    try:
        import config
        from compression import CompressionManager
        from task_manager import TaskManager

        config.init_directories()
        task_mgr = TaskManager(config.STATE_DIR)
        task = task_mgr.create_task(goal="Test compression", priority="med")

        task_dir = config.TASKS_DIR / task.task_id
        compression = CompressionManager(task_dir)

        # Create working set
        compression.create_initial_working_set(
            goal="Test goal",
            plan="Test plan"
        )

        # Verify files exist
        assert compression.working_set_file.exists()
        assert compression.rolling_summary_file.exists()

        # Test get context
        context = compression.get_context_for_injection()
        assert len(context) > 0

        print("  ✓ Compression manager working")
        return True
    except Exception as e:
        print(f"  ❌ Compression test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_background_jobs():
    """Test background job manager."""
    print("\nTesting Background Jobs...")
    try:
        import config
        from background_jobs import BackgroundJobManager
        import time

        config.init_directories()
        job_mgr = BackgroundJobManager(config.STATE_DIR)

        # Spawn a simple job
        job = job_mgr.spawn_job("echo 'test' && sleep 1")
        print(f"  Spawned job {job.job_id}")

        # Wait a bit
        time.sleep(2)

        # Check job
        job = job_mgr.get_job(job.job_id)
        assert job.status == "COMPLETED"

        # Get output
        output = job_mgr.get_job_output(job.job_id)
        assert "test" in output["stdout"]

        print("  ✓ Background jobs working")
        return True
    except Exception as e:
        print(f"  ❌ Background jobs test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_mailbox():
    """Test mailbox communication."""
    print("\nTesting Mailbox...")
    try:
        import config
        from mailbox import MailboxManager

        config.init_directories()
        mailbox = MailboxManager(config.STATE_DIR)

        # Send message
        msg = mailbox.create_request_message(
            from_agent="Lead",
            to_agent="Worker_test",
            task_id="T-TEST-0001",
            intent="test",
            goal="Test message",
            priority="low"
        )

        print(f"  Sent message {msg.msg_id}")

        # Check inbox
        count = mailbox.get_unread_count("Worker_test")
        assert count >= 1  # At least our message

        # Read messages
        messages = mailbox.read_inbox("Worker_test", mark_read=False)
        assert len(messages) >= 1

        # Find our message
        our_msg = [m for m in messages if m.msg_id == msg.msg_id]
        assert len(our_msg) == 1

        print("  ✓ Mailbox working")
        return True
    except Exception as e:
        print(f"  ❌ Mailbox test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_worker_agent():
    """Test worker agent initialization."""
    print("\nTesting Worker Agent...")
    try:
        from worker_agent import WorkerAgent

        worker = WorkerAgent("Worker_test")
        assert worker.name == "Worker_test"

        print("  ✓ Worker agent initialized")
        return True
    except Exception as e:
        print(f"  ❌ Worker agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_lead_agent_phase2():
    """Test Lead agent with Phase 2 features."""
    print("\nTesting Lead Agent (Phase 2)...")
    try:
        from lead_agent import LeadAgent

        agent = LeadAgent()
        assert agent.job_manager is not None
        assert agent.mailbox is not None

        # Check new tools available
        tools = agent.tool_dispatcher.get_tool_definitions()
        tool_names = [t["name"] for t in tools]

        assert "spawn_job" in tool_names
        assert "get_job_status" in tool_names
        assert "read_inbox" in tool_names

        print("  ✓ Lead agent Phase 2 features present")
        return True
    except Exception as e:
        print(f"  ❌ Lead agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Phase 2 Feature Tests")
    print("="*60)

    tests = [
        ("Imports", test_imports),
        ("Compression", test_compression),
        ("Background Jobs", test_background_jobs),
        ("Mailbox", test_mailbox),
        ("Worker Agent", test_worker_agent),
        ("Lead Agent Phase 2", test_lead_agent_phase2),
    ]

    results = {}
    for name, test_func in tests:
        results[name] = test_func()

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(results.values())
    total = len(results)

    for name, result in results.items():
        status = "✓" if result else "❌"
        print(f"{status} {name}")

    print(f"\nPassed: {passed}/{total}")

    if passed == total:
        print("\n🎉 All Phase 2 tests passed!")
        print("\nYou can now:")
        print("  1. Run phase2_examples.py for feature demos")
        print("  2. Start workers: python worker_agent.py Worker_alpha")
        print("  3. Use Lead agent: python lead_agent.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
