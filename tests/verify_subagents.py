"""Comprehensive verification of subagent implementation."""

import sys
from pathlib import Path

def verify_files():
    """Verify all required files exist."""
    print("=" * 70)
    print("VERIFYING FILE STRUCTURE")
    print("=" * 70)

    required_files = [
        "subagent_loader.py",
        "subagent_executor.py",
        "subagents/researcher.md",
        "subagents/developer.md",
        "subagents/analyst.md",
        "subagents/general.md",
        "test_subagents.py",
        "SUBAGENTS.md",
        "SUBAGENT_QUICKSTART.md",
        "IMPLEMENTATION_SUMMARY.md"
    ]

    sdk_root = Path(__file__).parent
    all_exist = True

    for file_path in required_files:
        full_path = sdk_root / file_path
        exists = full_path.exists()
        status = "✅" if exists else "❌"
        print(f"{status} {file_path}")
        if not exists:
            all_exist = False

    return all_exist

def verify_subagent_loading():
    """Verify subagents load correctly."""
    print("\n" + "=" * 70)
    print("VERIFYING SUBAGENT LOADING")
    print("=" * 70)

    try:
        from subagent_loader import SubagentRegistry

        sdk_root = Path(__file__).parent
        registry = SubagentRegistry(sdk_root)

        subagents = registry.list_subagents()
        print(f"\n✅ Loaded {len(subagents)} subagent(s)")

        expected = {'researcher', 'developer', 'analyst', 'general'}
        loaded = {s.name for s in subagents}

        if expected == loaded:
            print("✅ All expected subagents present")
            for subagent in subagents:
                print(f"   - {subagent.name}")
            return True
        else:
            print(f"❌ Missing subagents: {expected - loaded}")
            return False

    except Exception as e:
        print(f"❌ Error loading subagents: {e}")
        return False

def verify_tool_definitions():
    """Verify Agent tool definition is generated correctly."""
    print("\n" + "=" * 70)
    print("VERIFYING TOOL DEFINITIONS")
    print("=" * 70)

    try:
        from subagent_loader import SubagentRegistry

        sdk_root = Path(__file__).parent
        registry = SubagentRegistry(sdk_root)

        tool_def = registry.get_tool_definition_for_lead()

        # Verify structure
        checks = [
            ("name" in tool_def, "Has 'name' field"),
            (tool_def.get("name") == "Agent", "'name' is 'Agent'"),
            ("description" in tool_def, "Has 'description' field"),
            ("input_schema" in tool_def, "Has 'input_schema' field"),
            ("properties" in tool_def.get("input_schema", {}), "Has 'properties'"),
        ]

        all_passed = True
        for check, description in checks:
            status = "✅" if check else "❌"
            print(f"{status} {description}")
            if not check:
                all_passed = False

        # Verify enum
        enum_list = tool_def.get("input_schema", {}).get("properties", {}).get("subagent_type", {}).get("enum", [])
        expected_enum = ['analyst', 'general', 'researcher', 'developer']
        if set(enum_list) == set(expected_enum):
            print(f"✅ Correct subagent types in enum: {enum_list}")
        else:
            print(f"❌ Incorrect enum: {enum_list}")
            all_passed = False

        return all_passed

    except Exception as e:
        print(f"❌ Error generating tool definition: {e}")
        return False

def verify_lead_agent_integration():
    """Verify lead agent initializes with subagents."""
    print("\n" + "=" * 70)
    print("VERIFYING LEAD AGENT INTEGRATION")
    print("=" * 70)

    try:
        from lead_agent import LeadAgent

        # This will initialize and print status
        agent = LeadAgent()

        # Verify registry exists
        if hasattr(agent, 'subagent_registry'):
            print("✅ Lead agent has subagent_registry")
        else:
            print("❌ Lead agent missing subagent_registry")
            return False

        # Verify subagents dict exists
        if hasattr(agent, 'subagents'):
            print("✅ Lead agent has subagents tracking dict")
        else:
            print("❌ Lead agent missing subagents dict")
            return False

        # Verify counter exists
        if hasattr(agent, 'subagent_counter'):
            print("✅ Lead agent has subagent_counter")
        else:
            print("❌ Lead agent missing subagent_counter")
            return False

        # Verify method exists
        if hasattr(agent, '_handle_agent_tool'):
            print("✅ Lead agent has _handle_agent_tool method")
        else:
            print("❌ Lead agent missing _handle_agent_tool method")
            return False

        return True

    except Exception as e:
        print(f"❌ Error initializing lead agent: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_tool_restrictions():
    """Verify tool restrictions work."""
    print("\n" + "=" * 70)
    print("VERIFYING TOOL RESTRICTIONS")
    print("=" * 70)

    try:
        from subagent_loader import SubagentRegistry

        sdk_root = Path(__file__).parent
        registry = SubagentRegistry(sdk_root)

        # Check researcher restrictions
        researcher = registry.get_subagent('researcher')
        if researcher:
            if 'write_file' in (researcher.disallowed_tools or []):
                print("✅ Researcher cannot write files")
            else:
                print("❌ Researcher should not be able to write files")
                return False

        # Check developer restrictions
        developer = registry.get_subagent('developer')
        if developer:
            if 'web_search' in (developer.disallowed_tools or []):
                print("✅ Developer cannot search web")
            else:
                print("❌ Developer should not be able to search web")
                return False

        # Check analyst restrictions
        analyst = registry.get_subagent('analyst')
        if analyst:
            disallowed = analyst.disallowed_tools or []
            if 'write_file' in disallowed and 'web_search' in disallowed:
                print("✅ Analyst has multiple restrictions")
            else:
                print("❌ Analyst restrictions incorrect")
                return False

        return True

    except Exception as e:
        print(f"❌ Error verifying restrictions: {e}")
        return False

def verify_documentation():
    """Verify documentation files have content."""
    print("\n" + "=" * 70)
    print("VERIFYING DOCUMENTATION")
    print("=" * 70)

    sdk_root = Path(__file__).parent

    docs = [
        ("SUBAGENTS.md", 10000),
        ("SUBAGENT_QUICKSTART.md", 5000),
        ("IMPLEMENTATION_SUMMARY.md", 10000)
    ]

    all_good = True
    for doc, min_size in docs:
        doc_path = sdk_root / doc
        if doc_path.exists():
            size = len(doc_path.read_text())
            if size >= min_size:
                print(f"✅ {doc} ({size:,} chars)")
            else:
                print(f"⚠️  {doc} is small ({size} chars, expected {min_size}+)")
        else:
            print(f"❌ {doc} not found")
            all_good = False

    return all_good

def main():
    """Run all verifications."""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "SUBAGENT IMPLEMENTATION VERIFICATION" + " " * 15 + "║")
    print("╚" + "=" * 68 + "╝")
    print()

    results = []

    results.append(("File Structure", verify_files()))
    results.append(("Subagent Loading", verify_subagent_loading()))
    results.append(("Tool Definitions", verify_tool_definitions()))
    results.append(("Lead Agent Integration", verify_lead_agent_integration()))
    results.append(("Tool Restrictions", verify_tool_restrictions()))
    results.append(("Documentation", verify_documentation()))

    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VERIFICATIONS PASSED!")
        print("=" * 70)
        print("\nSubagent architecture is fully implemented and ready to use!")
        print("\nQuick start:")
        print("  1. Read SUBAGENT_QUICKSTART.md for usage examples")
        print("  2. Read SUBAGENTS.md for complete documentation")
        print("  3. Run: python lead_agent.py")
        print("  4. Try: 'Use the researcher subagent to find...'")
        return 0
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        print("=" * 70)
        return 1

if __name__ == "__main__":
    sys.exit(main())
