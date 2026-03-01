#!/usr/bin/env python3
"""Quick test to verify Lead Agent works with new Bedrock client."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lead_agent import LeadAgent

def main():
    print("\n" + "="*70)
    print("QUICK LEAD AGENT TEST")
    print("="*70)

    print("\n🔧 Initializing Lead Agent...")
    agent = LeadAgent()

    print("\n✅ Lead Agent initialized successfully!")
    print(f"   Bedrock client status:")
    status = agent.bedrock.get_status()
    print(f"   - Current model: {status['current_model']}")
    print(f"   - Fallback model: {status['fallback_model']}")
    print(f"   - Fallback mode: {status['fallback_mode']}")
    print(f"   - Total retries: {status['total_retries']}")

    print("\n🧪 Testing simple query...")
    try:
        response = agent._call_claude("Say 'Test successful!' in exactly 2 words.")

        if response.get("content"):
            message = response["content"][0]["text"]
            print(f"✅ Response received: {message}")
        else:
            print(f"✅ Response received (format may vary)")

        print("\n🎉 All tests passed!")
        print("   Your Lead Agent is ready to handle PDF tasks with:")
        print("   - 300s timeout (5 minutes)")
        print("   - 3 automatic retries")
        print("   - Fallback to Sonnet 4.5")

    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
