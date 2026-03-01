#!/usr/bin/env python3
"""Test script to verify Claude Skills integration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import config
from skill_loader import SkillLoader
from prompts import LEAD_AGENT_PROMPT


def test_skill_discovery():
    """Test that skills are discovered correctly."""
    print("=" * 60)
    print("TEST 1: Skill Discovery")
    print("=" * 60)

    loader = SkillLoader(config.SKILLS_DIR)
    skills = loader.discover_skills()

    print(f"\n✓ Discovered {len(skills)} skill(s)")
    for name, skill in skills.items():
        print(f"\n  Skill: {name}")
        print(f"    Description: {skill.description[:60]}...")
        print(f"    File: {skill.file_path}")
        print(f"    Loaded: {skill.loaded}")
        print(f"    Keywords: {skill.metadata.get('keywords', [])}")

    assert len(skills) > 0, "Should discover at least one skill"
    print("\n✅ Test 1 passed!")
    return loader


def test_skill_loading(loader):
    """Test on-demand skill content loading."""
    print("\n" + "=" * 60)
    print("TEST 2: On-Demand Skill Loading")
    print("=" * 60)

    skill_name = "web-research"

    # Verify skill is not loaded initially
    skill = loader.get_skill(skill_name)
    assert skill is not None, f"Skill {skill_name} should exist"
    assert not skill.loaded, "Skill should not be loaded initially"
    print(f"\n✓ Skill '{skill_name}' exists (not loaded yet)")

    # Load skill content
    content = loader.load_skill_content(skill_name)
    assert content is not None, "Should load skill content"
    assert len(content) > 0, "Content should not be empty"
    assert skill.loaded, "Skill should be marked as loaded"
    print(f"✓ Loaded skill content ({len(content)} characters)")

    # Verify content contains expected sections
    assert "## Overview" in content or "# Web Research Skill" in content
    print("✓ Content contains expected sections")

    print("\n✅ Test 2 passed!")


def test_skill_activation_logic(loader):
    """Test skill activation logic."""
    print("\n" + "=" * 60)
    print("TEST 3: Skill Activation Logic")
    print("=" * 60)

    test_cases = [
        ("Research Python frameworks", "web-research", True),
        ("Can you search for information about AI?", "web-research", True),
        ("What is 2+2?", "web-research", False),
        ("Help me investigate this topic", "web-research", True),
    ]

    print()
    for message, skill_name, expected in test_cases:
        result = loader.should_activate_skill(skill_name, message)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{message}' -> {result} (expected {expected})")
        assert result == expected, f"Activation logic failed for: {message}"

    print("\n✅ Test 3 passed!")


def test_prompt_formatting(loader):
    """Test prompt formatting with skills."""
    print("\n" + "=" * 60)
    print("TEST 4: Prompt Formatting")
    print("=" * 60)

    skills_summary = loader.get_skills_summary()
    print(f"\nSkills summary:\n{skills_summary}\n")

    # Format the prompt
    formatted_prompt = LEAD_AGENT_PROMPT.format(skills_summary=skills_summary)

    # Verify formatting
    assert "Available Skills:" in formatted_prompt
    assert "web-research" in formatted_prompt
    print("✓ Prompt formatted successfully")
    print("✓ Skills section present in prompt")

    # Test with no skills
    empty_summary = "No skills loaded."
    formatted_empty = LEAD_AGENT_PROMPT.format(skills_summary=empty_summary)
    assert "No skills loaded." in formatted_empty
    print("✓ Handles empty skills case")

    print("\n✅ Test 4 passed!")


def test_skill_activation_workflow(loader):
    """Simulate the full skill activation workflow."""
    print("\n" + "=" * 60)
    print("TEST 5: Full Skill Activation Workflow")
    print("=" * 60)

    # Simulate user message
    user_message = "Research the latest developments in quantum computing"
    print(f"\nUser message: '{user_message}'")

    # Check which skills should be activated
    activated_skills = []
    for skill_name, skill in loader.skills.items():
        if not skill.loaded and loader.should_activate_skill(skill_name, user_message):
            content = loader.load_skill_content(skill_name)
            if content:
                activated_skills.append(skill_name)
                print(f"✓ Activated skill: {skill_name}")

                # Simulate injecting into message
                injected_message = (
                    f"{user_message}\n\n"
                    f"<skill_activated name=\"{skill_name}\">\n"
                    f"{content}\n"
                    f"</skill_activated>"
                )
                print(f"  Injected {len(injected_message)} characters into message")

    assert len(activated_skills) > 0, "Should activate at least one skill"
    print(f"\n✓ Activated {len(activated_skills)} skill(s) total")

    print("\n✅ Test 5 passed!")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("CLAUDE SKILLS INTEGRATION TEST SUITE")
    print("=" * 60)
    print(f"\nSkills directory: {config.SKILLS_DIR}")
    print(f"Skills enabled: {config.SKILLS_ENABLED}")

    try:
        loader = test_skill_discovery()
        test_skill_loading(loader)

        # Reload loader for fresh state
        loader = SkillLoader(config.SKILLS_DIR)
        loader.discover_skills()

        test_skill_activation_logic(loader)
        test_prompt_formatting(loader)
        test_skill_activation_workflow(loader)

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        print("\nThe Claude Skills System is successfully integrated!")
        print("\nNext steps:")
        print("  1. Run: python lead_agent.py \"Research Python frameworks\"")
        print("  2. Watch for: '🎯 Activated skill: web-research'")
        print("  3. Add more skills by creating new directories in skills/")
        print("=" * 60)

        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
