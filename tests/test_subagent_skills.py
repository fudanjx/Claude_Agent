"""Test script for subagent skill system (static and dynamic modes)."""

from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from subagent_loader import SubagentRegistry


def test_subagent_skill_modes():
    """Test that subagents have correct skill modes."""
    print("=" * 70)
    print("Testing Subagent Skill Modes")
    print("=" * 70)

    sdk_root = Path(__file__).parent.parent
    registry = SubagentRegistry(sdk_root)

    print(f"\n✓ Loaded {len(registry.list_subagents())} subagent(s):\n")

    # Check each subagent
    for subagent in registry.list_subagents():
        print(f"📋 {subagent.name}")
        print(f"   Description: {subagent.description}")
        print(f"   Skill Mode: {subagent.skill_mode}")

        if subagent.skill_mode == "static":
            print(f"   Static Skills: {subagent.skills}")
            print(f"   ➜ Type 1: Specialized subagent with pre-loaded skills")

        elif subagent.skill_mode == "dynamic":
            print(f"   Skills: Dynamic (can access all skills in /skills)")
            print(f"   ➜ Type 2: Generic subagent with on-demand skill loading")

        elif subagent.skill_mode == "none":
            print(f"   Skills: None (no skill system)")
            print(f"   ➜ Simple subagent without skills")

        print()

    # Verify we have examples of each type
    print("\n" + "=" * 70)
    print("Verification")
    print("=" * 70)

    modes = {s.skill_mode for s in registry.list_subagents()}

    checks = [
        ("static" in modes, "Has at least one specialized subagent (Type 1)"),
        ("dynamic" in modes, "Has at least one generic subagent (Type 2)"),
    ]

    all_passed = True
    for check, description in checks:
        status = "✅" if check else "❌"
        print(f"{status} {description}")
        if not check:
            all_passed = False

    # Check specific subagents
    print("\n" + "=" * 70)
    print("Specific Subagent Checks")
    print("=" * 70)

    # Check pdf-specialist (should be static)
    pdf_spec = registry.get_subagent("pdf-specialist")
    if pdf_spec:
        if pdf_spec.skill_mode == "static" and "pdf" in (pdf_spec.skills or []):
            print("✅ pdf-specialist is Type 1 (static) with PDF skill")
        else:
            print(f"❌ pdf-specialist has wrong config: mode={pdf_spec.skill_mode}, skills={pdf_spec.skills}")
            all_passed = False
    else:
        print("⚠️  pdf-specialist not found (optional)")

    # Check general (should be dynamic)
    general = registry.get_subagent("general")
    if general:
        if general.skill_mode == "dynamic":
            print("✅ general is Type 2 (dynamic) with on-demand skills")
        else:
            print(f"❌ general has wrong config: mode={general.skill_mode}")
            all_passed = False
    else:
        print("❌ general subagent not found")
        all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nSubagent skill system is correctly configured:")
        print("- Type 1 (Static): Specialized subagents with pre-loaded skills")
        print("- Type 2 (Dynamic): Generic subagents with on-demand skills")
        print("\nReady to use!")
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(test_subagent_skill_modes())
