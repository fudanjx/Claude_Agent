#!/usr/bin/env python3
"""Examples using web search and fetch tools with the Lead Agent."""

from lead_agent import LeadAgent


def example_1_simple_search():
    """Example: Simple web search and summarize."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Web Search and Summarize")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Search the web for 'Python 3.13 new features' and create a summary "
        "of the top 3 most important features"
    )


def example_2_research_and_compare():
    """Example: Research multiple sources and compare."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Multi-Source Research")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Search for information about 'asyncio vs threading in Python', "
        "fetch content from the top 2 results, and create a comparison table"
    )


def example_3_fact_checking():
    """Example: Fact-checking with web search."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Fact Checking")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Search the web to verify: 'What is the current stable version of Python?' "
        "Provide the answer with source URLs as evidence"
    )


def example_4_deep_dive():
    """Example: Deep dive into a topic."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Deep Dive Research")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Research 'Python type hints evolution' by searching the web, "
        "fetching relevant articles, and creating a timeline document with sources"
    )


def example_5_background_research():
    """Example: Spawn background web research tasks."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Parallel Web Research with Workers")
    print("="*60)

    agent = LeadAgent()
    agent.run(
        "Create 3 tasks for workers: "
        "1) Search and summarize Python web frameworks, "
        "2) Search and summarize Python async libraries, "
        "3) Search and summarize Python testing tools. "
        "Each should use web_search and create a document with sources."
    )


if __name__ == "__main__":
    import sys

    examples = {
        "1": ("Simple Search", example_1_simple_search),
        "2": ("Multi-Source Research", example_2_research_and_compare),
        "3": ("Fact Checking", example_3_fact_checking),
        "4": ("Deep Dive", example_4_deep_dive),
        "5": ("Parallel Research", example_5_background_research),
    }

    if len(sys.argv) > 1 and sys.argv[1] in examples:
        name, func = examples[sys.argv[1]]
        print(f"\n🌐 Running: {name}")
        func()
    else:
        print("""
Web Search Examples - Available:

  python example_web_search.py 1  - Simple Search and Summarize
  python example_web_search.py 2  - Multi-Source Research
  python example_web_search.py 3  - Fact Checking with Sources
  python example_web_search.py 4  - Deep Dive Research
  python example_web_search.py 5  - Parallel Research with Workers

Each example uses web_search and web_fetch tools to gather grounded facts.
        """)
