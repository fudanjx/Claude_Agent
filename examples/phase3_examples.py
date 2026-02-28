#!/usr/bin/env python3
"""Phase 3 Feature Examples - Skills and Error Recovery."""

import config
from task_manager import TaskManager
from worker_agent import WorkerAgent
from worker_skills import WorkerSkills
from error_recovery import RetryStrategy, ErrorRecoveryManager


def example_1_skilled_workers():
    """Example: Create workers with different skill profiles."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLE 1: Skilled Workers")
    print("="*60)

    config.init_directories()

    print("\nCreating specialized workers:")

    # Researcher worker
    researcher = WorkerAgent("Researcher_A", profile="researcher")
    print(f"\n{researcher.name}:")
    print(f"  Skills: {', '.join(researcher.skills)}")
    print("  Best for: Research, web search, analysis, documentation")

    # Developer worker
    developer = WorkerAgent("Developer_B", profile="developer")
    print(f"\n{developer.name}:")
    print(f"  Skills: {', '.join(developer.skills)}")
    print("  Best for: Coding, testing, documentation")

    # Web specialist
    web_specialist = WorkerAgent("WebSpec_C", profile="web_specialist")
    print(f"\n{web_specialist.name}:")
    print(f"  Skills: {', '.join(web_specialist.skills)}")
    print("  Best for: Web search, research, documentation")

    # General worker (can do anything)
    general = WorkerAgent("General_D", profile="general")
    print(f"\n{general.name}:")
    print(f"  Skills: {', '.join(general.skills)}")
    print("  Best for: Any task")

    print("\n✓ Workers created with specialized skills")


def example_2_skill_based_tasks():
    """Example: Create tasks that require specific skills."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLE 2: Skill-Based Task Assignment")
    print("="*60)

    config.init_directories()
    tm = TaskManager(config.STATE_DIR)

    print("\nCreating tasks with skill requirements:")

    # Research task
    task1 = tm.create_task(
        goal="Search and analyze Python web frameworks",
        priority="high",
        required_skills=[WorkerSkills.RESEARCH, WorkerSkills.WEB_SEARCH]
    )
    print(f"\n✓ {task1.task_id}: {task1.goal}")
    print(f"  Requires: {', '.join(task1.required_skills)}")
    print(f"  → Best match: Researcher or Web Specialist workers")

    # Coding task
    task2 = tm.create_task(
        goal="Write unit tests for compression module",
        priority="med",
        required_skills=[WorkerSkills.CODING, WorkerSkills.TESTING]
    )
    print(f"\n✓ {task2.task_id}: {task2.goal}")
    print(f"  Requires: {', '.join(task2.required_skills)}")
    print(f"  → Best match: Developer workers")

    # Analysis task
    task3 = tm.create_task(
        goal="Analyze performance metrics and create report",
        priority="med",
        required_skills=[WorkerSkills.ANALYSIS, WorkerSkills.DATA_PROCESSING]
    )
    print(f"\n✓ {task3.task_id}: {task3.goal}")
    print(f"  Requires: {', '.join(task3.required_skills)}")
    print(f"  → Best match: Analyst workers")

    # General task (no skills required)
    task4 = tm.create_task(
        goal="Check system status",
        priority="low",
        required_skills=[]
    )
    print(f"\n✓ {task4.task_id}: {task4.goal}")
    print(f"  Requires: No specific skills")
    print(f"  → Any worker can claim")

    print("\n\n📋 Now start specialized workers:")
    print("  python worker_agent.py Researcher_A --profile researcher")
    print("  python worker_agent.py Developer_B --profile developer")
    print("\nWorkers will only claim tasks matching their skills!")


def example_3_error_recovery():
    """Example: Error recovery and retry."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLE 3: Error Recovery")
    print("="*60)

    from error_recovery import RetryConfig, ErrorType
    import time

    print("\nDemonstrating retry strategy:")

    # Create retry strategy
    config_retry = RetryConfig(
        max_retries=3,
        initial_delay=0.5,
        exponential_base=2.0
    )
    strategy = RetryStrategy(config_retry)

    print(f"\nRetry Configuration:")
    print(f"  Max retries: {config_retry.max_retries}")
    print(f"  Initial delay: {config_retry.initial_delay}s")
    print(f"  Exponential base: {config_retry.exponential_base}")

    print(f"\nDelay progression:")
    for i in range(4):
        delay = strategy.calculate_delay(i)
        print(f"  Retry {i}: {delay:.2f}s")

    # Test with mock function
    print(f"\n\nTesting with simulated transient error:")

    attempt = [0]

    def flaky_function():
        attempt[0] += 1
        if attempt[0] < 3:
            print(f"  Attempt {attempt[0]}: Failed (transient)")
            raise Exception("Temporary network error")
        print(f"  Attempt {attempt[0]}: Success!")
        return "Data retrieved"

    result, error_record = strategy.execute_with_retry(
        flaky_function,
        task_id="T-TEST-RETRY"
    )

    if result:
        print(f"\n✓ Operation succeeded after {attempt[0]} attempts")
        print(f"  Result: {result}")
        if error_record:
            print(f"  Recovered: {error_record.recovered}")
    else:
        print(f"\n❌ Operation failed after retries")
        if error_record:
            print(f"  Error: {error_record.error_message}")


def example_4_error_stats():
    """Example: View error statistics."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLE 4: Error Statistics")
    print("="*60)

    config.init_directories()
    erm = ErrorRecoveryManager(config.STATE_DIR)

    print("\nError Statistics:")
    stats = erm.get_error_stats()

    if stats["total"] == 0:
        print("  No errors logged yet")
    else:
        print(f"  Total errors: {stats['total']}")
        print(f"  Recovered: {stats['recovered']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Recovery rate: {stats['recovered']/stats['total']*100:.1f}%")

        if "by_type" in stats:
            print(f"\n  By error type:")
            for error_type, type_stats in stats["by_type"].items():
                print(f"    {error_type}: {type_stats['total']} total, {type_stats['recovered']} recovered")


def example_5_skill_matching():
    """Example: Skill matching algorithm."""
    print("\n" + "="*60)
    print("PHASE 3 EXAMPLE 5: Skill Matching")
    print("="*60)

    from worker_skills import SkillMatcher

    print("\nTesting skill matching:")

    # Task requirements
    task_skills = {WorkerSkills.RESEARCH, WorkerSkills.WEB_SEARCH}
    print(f"\nTask requires: {', '.join(task_skills)}")

    # Available workers
    workers = [
        ("Researcher_A", {WorkerSkills.RESEARCH, WorkerSkills.WEB_SEARCH, WorkerSkills.ANALYSIS}),
        ("Developer_B", {WorkerSkills.CODING, WorkerSkills.TESTING}),
        ("WebSpec_C", {WorkerSkills.WEB_SEARCH, WorkerSkills.RESEARCH}),
        ("General_D", {WorkerSkills.GENERAL}),
    ]

    print(f"\nAvailable workers:")
    for name, skills in workers:
        print(f"  {name}: {', '.join(skills)}")

    # Get suggestions
    suggestions = SkillMatcher.suggest_worker_for_task(task_skills, workers)

    print(f"\nSuggested workers (best match first):")
    for worker_name, score in suggestions:
        match_quality = "Perfect" if score == 1.0 else "Good" if score >= 0.75 else "Acceptable"
        print(f"  {worker_name}: {score:.2f} ({match_quality})")


if __name__ == "__main__":
    import sys

    examples = {
        "1": ("Skilled Workers", example_1_skilled_workers),
        "2": ("Skill-Based Tasks", example_2_skill_based_tasks),
        "3": ("Error Recovery", example_3_error_recovery),
        "4": ("Error Statistics", example_4_error_stats),
        "5": ("Skill Matching", example_5_skill_matching),
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, func = examples[sys.argv[1]]
        print(f"\n🚀 Running: {name}")
        func()
    else:
        print("""
Phase 3 Examples - Available:

  python phase3_examples.py 1  - Skilled Workers
  python phase3_examples.py 2  - Skill-Based Task Assignment
  python phase3_examples.py 3  - Error Recovery Demo
  python phase3_examples.py 4  - Error Statistics
  python phase3_examples.py 5  - Skill Matching Algorithm

Each example demonstrates Phase 3 features.
        """)
