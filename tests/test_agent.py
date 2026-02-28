#!/usr/bin/env python3
"""Quick test of the Lead Agent setup."""

try:
    from lead_agent import LeadAgent

    print("="*60)
    print("Testing Lead Agent with a simple task...")
    print("="*60)

    agent = LeadAgent()
    agent.run("What is 2+2? Just tell me the answer.")

    print("\n" + "="*60)
    print("✅ Success! Your agent is working correctly.")
    print("="*60)

except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
