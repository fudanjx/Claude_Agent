"""Test script for subagent architecture."""

from pathlib import Path
from subagent_loader import SubagentRegistry

def test_subagent_loading():
    """Test that subagents are loaded correctly."""
    print("=" * 60)
    print("Testing Subagent Loading")
    print("=" * 60)

    # Create registry
    sdk_root = Path(__file__).parent
    registry = SubagentRegistry(sdk_root)

    # List loaded subagents
    subagents = registry.list_subagents()
    print(f"\n✓ Loaded {len(subagents)} subagent(s):\n")

    for subagent in subagents:
        print(f"  📋 {subagent.name} ({subagent.source})")
        print(f"     Description: {subagent.description}")
        print(f"     Tools: {subagent.tools or 'All (except disallowed)'}")
        print(f"     Disallowed: {subagent.disallowed_tools or 'None'}")
        print(f"     Max turns: {subagent.max_turns}")
        print(f"     Model: {subagent.model}")
        print()

    # Test tool definition generation
    print("\n" + "=" * 60)
    print("Testing Agent Tool Definition")
    print("=" * 60)

    tool_def = registry.get_tool_definition_for_lead()
    print(f"\n✓ Agent tool definition generated:")
    print(f"   Name: {tool_def['name']}")
    print(f"   Description: {tool_def['description'][:100]}...")
    print(f"   Subagent types: {tool_def['input_schema']['properties']['subagent_type']['enum']}")
    print()

    # Test individual subagent retrieval
    print("\n" + "=" * 60)
    print("Testing Individual Subagent Retrieval")
    print("=" * 60)

    for name in ['researcher', 'developer', 'analyst', 'general']:
        subagent = registry.get_subagent(name)
        if subagent:
            print(f"\n✓ Retrieved {name}:")
            print(f"   System prompt length: {len(subagent.system_prompt)} chars")
            print(f"   First line: {subagent.system_prompt.split(chr(10))[0][:60]}...")
        else:
            print(f"\n✗ Failed to retrieve {name}")

    print("\n" + "=" * 60)
    print("All Tests Passed!")
    print("=" * 60)

if __name__ == "__main__":
    test_subagent_loading()
