#!/usr/bin/env python3
"""Example usage of the Lead Agent."""

from lead_agent import LeadAgent


def example_1_simple_research():
    """Example: Simple research task."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Simple Research Task")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Use bash to check what Python version is installed and create a brief report"
    )


def example_2_task_breakdown():
    """Example: Task breakdown and planning."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Task Breakdown")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Create a task breakdown for building a simple TODO list application. "
        "Create separate tasks for design, backend, frontend, and testing."
    )


def example_3_file_analysis():
    """Example: Analyze files in current directory."""
    print("\n" + "="*60)
    print("EXAMPLE 3: File Analysis")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Analyze all Python files in the current directory and create a summary "
        "of what each module does. Write the summary to a file."
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        if example_num == "1":
            example_1_simple_research()
        elif example_num == "2":
            example_2_task_breakdown()
        elif example_num == "3":
            example_3_file_analysis()
        else:
            print("Usage: python example.py [1|2|3]")
    else:
        print("""
Available examples:
  python example.py 1  - Simple research task
  python example.py 2  - Task breakdown
  python example.py 3  - File analysis

Or run without arguments to see this menu.
        """)
