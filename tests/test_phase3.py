#!/usr/bin/env python3
"""Test script for Phase 3 features."""

import sys
from pathlib import Path


def test_worker_skills():
    """Test worker skill matching."""
    print("Testing Worker Skills...")
    try:
        from worker_skills import WorkerSkills, SkillMatcher, get_worker_profile

        # Test skill matching
        worker_skills = {WorkerSkills.RESEARCH, WorkerSkills.WEB_SEARCH}
        required_skills = {WorkerSkills.RESEARCH}

        can_claim = SkillMatcher.can_claim(worker_skills, required_skills)
        assert can_claim, "Worker should be able to claim task"

        score = SkillMatcher.skill_match_score(worker_skills, required_skills)
        assert score == 1.0, "Score should be 1.0 for perfect match"

        # Test worker profiles
        researcher_skills = get_worker_profile("researcher")
        assert WorkerSkills.RESEARCH in researcher_skills

        print("  ✓ Worker skills working")
        return True
    except Exception as e:
        print(f"  ❌ Worker skills test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_recovery():
    """Test error classification and retry."""
    print("\nTesting Error Recovery...")
    try:
        from error_recovery import (
            ErrorClassifier, ErrorType, RetryStrategy,
            ErrorRecord, RetryConfig
        )

        # Test error classification
        timeout_error = TimeoutError("Connection timed out")
        error_type = ErrorClassifier.classify(timeout_error)
        assert error_type == ErrorType.TIMEOUT

        # Test retry strategy
        config = RetryConfig(max_retries=2, initial_delay=0.1)
        strategy = RetryStrategy(config)

        # Should retry transient errors
        should_retry = strategy.should_retry(
            Exception("network error"), 0, ErrorType.TRANSIENT
        )
        assert should_retry, "Should retry transient errors"

        # Should not retry permanent errors
        should_not_retry = strategy.should_retry(
            Exception("file not found"), 0, ErrorType.PERMANENT
        )
        assert not should_not_retry, "Should not retry permanent errors"

        # Test exponential backoff
        delay_0 = strategy.calculate_delay(0)
        delay_1 = strategy.calculate_delay(1)
        assert delay_1 > delay_0, "Delay should increase"

        print("  ✓ Error recovery working")
        return True
    except Exception as e:
        print(f"  ❌ Error recovery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_task_skills():
    """Test task creation with required skills."""
    print("\nTesting Task Skills...")
    try:
        import config
        from task_manager import TaskManager
        from worker_skills import WorkerSkills

        config.init_directories()
        tm = TaskManager(config.STATE_DIR)

        # Create task with required skills
        task = tm.create_task(
            goal="Research Python frameworks",
            priority="high",
            required_skills=[WorkerSkills.RESEARCH, WorkerSkills.WEB_SEARCH]
        )

        assert task.required_skills is not None
        assert WorkerSkills.RESEARCH in task.required_skills

        # Verify task was saved with skills
        loaded_task = tm.get_task(task.task_id)
        assert loaded_task.required_skills == task.required_skills

        print("  ✓ Task skills working")
        return True
    except Exception as e:
        print(f"  ❌ Task skills test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_skilled_worker_creation():
    """Test creating workers with different skill profiles."""
    print("\nTesting Skilled Worker Creation...")
    try:
        from worker_agent import WorkerAgent
        from worker_skills import WorkerSkills

        # Create researcher worker
        worker_researcher = WorkerAgent("Worker_researcher", profile="researcher")
        assert WorkerSkills.RESEARCH in worker_researcher.skills

        # Create developer worker
        worker_dev = WorkerAgent("Worker_dev", profile="developer")
        assert WorkerSkills.CODING in worker_dev.skills

        # Create custom skilled worker
        custom_skills = {WorkerSkills.WEB_SEARCH, WorkerSkills.ANALYSIS}
        worker_custom = WorkerAgent("Worker_custom", skills=custom_skills)
        assert worker_custom.skills == custom_skills

        print("  ✓ Skilled workers working")
        return True
    except Exception as e:
        print(f"  ❌ Skilled worker test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_error_logging():
    """Test error logging and stats."""
    print("\nTesting Error Logging...")
    try:
        import config
        from error_recovery import (
            ErrorRecoveryManager, ErrorRecord, ErrorType
        )
        from datetime import datetime

        config.init_directories()
        erm = ErrorRecoveryManager(config.STATE_DIR)

        # Log an error
        record = ErrorRecord(
            task_id="T-TEST-0001",
            error_type=ErrorType.TRANSIENT,
            error_message="Test error",
            timestamp=datetime.now().isoformat(),
            retry_count=1,
            recovered=True,
            recovery_strategy="retry"
        )

        erm.log_error(record)

        # Get history
        history = erm.get_error_history("T-TEST-0001")
        assert len(history) >= 1

        # Get stats
        stats = erm.get_error_stats()
        assert stats["total"] >= 1

        print("  ✓ Error logging working")
        return True
    except Exception as e:
        print(f"  ❌ Error logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all Phase 3 tests."""
    print("="*60)
    print("Phase 3 Feature Tests")
    print("="*60)

    tests = [
        ("Worker Skills", test_worker_skills),
        ("Error Recovery", test_error_recovery),
        ("Task Skills", test_task_skills),
        ("Skilled Workers", test_skilled_worker_creation),
        ("Error Logging", test_error_logging),
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
        print("\n🎉 All Phase 3 tests passed!")
        print("\nPhase 3 Features:")
        print("  ✓ Worker Specialization (skill-based claiming)")
        print("  ✓ Error Recovery (retry + exponential backoff)")
        print("  ✓ Error Classification")
        print("  ✓ Error Logging & Stats")
        print("\nTry:")
        print("  python phase3_examples.py")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
