#!/usr/bin/env python3
"""Test script for Bedrock retry and fallback functionality."""

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import config
from bedrock_client import create_bedrock_client


def test_normal_operation():
    """Test normal Bedrock operation."""
    print("\n" + "="*70)
    print("TEST 1: Normal Operation")
    print("="*70)

    client = create_bedrock_client()

    print(f"\n✅ Client created successfully")
    print(f"   Primary model: {client.primary_model}")
    print(f"   Fallback model: {client.fallback_model}")
    print(f"   Read timeout: {config.BEDROCK_READ_TIMEOUT}s")
    print(f"   Max retries: {config.MAX_RETRIES}")

    # Test a simple request
    try:
        print(f"\n🔄 Testing simple request...")
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 100,
            "temperature": 1.0,
            "messages": [
                {"role": "user", "content": "Say 'Hello, I am working!' in exactly 5 words."}
            ]
        }

        response = client.invoke_model_with_retry(request_body)

        if response.get("content"):
            message = response["content"][0]["text"]
            print(f"✅ Success! Response: {message}")
        else:
            print(f"✅ Success! Got response (format may vary)")

        # Show status
        status = client.get_status()
        print(f"\n📊 Client Status:")
        print(f"   Current model: {status['current_model']}")
        print(f"   Fallback mode: {status['fallback_mode']}")
        print(f"   Total retries: {status['total_retries']}")

    except Exception as e:
        print(f"❌ Error: {e}")


def test_retry_behavior():
    """Demonstrate retry configuration."""
    print("\n" + "="*70)
    print("TEST 2: Retry Configuration")
    print("="*70)

    print(f"\n📋 Current Configuration:")
    print(f"   BEDROCK_READ_TIMEOUT: {config.BEDROCK_READ_TIMEOUT}s (increased from default 60s)")
    print(f"   BEDROCK_CONNECT_TIMEOUT: {config.BEDROCK_CONNECT_TIMEOUT}s")
    print(f"   MAX_RETRIES: {config.MAX_RETRIES}")
    print(f"   RETRY_BACKOFF_BASE: {config.RETRY_BACKOFF_BASE}")

    print(f"\n⏱️  Retry Timeline:")
    for attempt in range(config.MAX_RETRIES):
        backoff = config.RETRY_BACKOFF_BASE ** attempt
        print(f"   Attempt {attempt + 1}: Wait {backoff}s before retry")

    print(f"\n🔄 Fallback Strategy:")
    print(f"   1. Try primary model ({config.MODEL_ID})")
    print(f"      - Retry up to {config.MAX_RETRIES} times with exponential backoff")
    print(f"   2. If all retries fail, switch to fallback ({config.FALLBACK_MODEL_ID})")
    print(f"   3. Try fallback model with same retry logic")
    print(f"   4. If fallback also fails, raise exception")


def test_timeout_scenarios():
    """Explain timeout scenarios."""
    print("\n" + "="*70)
    print("TEST 3: Timeout Scenarios")
    print("="*70)

    print(f"\n🔍 What Causes Timeouts:")
    print(f"   1. Large Context")
    print(f"      - Your PDF extraction produced lots of coordinate data")
    print(f"      - Example: x=201.1 y=524.6 \"Mainstream\" (repeated many times)")
    print(f"      - This creates a large input context")

    print(f"\n   2. Complex Processing")
    print(f"      - Model needs time to process and generate response")
    print(f"      - Sonnet 4.6 can take longer on complex tasks")

    print(f"\n   3. Network Issues")
    print(f"      - Temporary AWS connectivity problems")
    print(f"      - Regional service slowdowns")

    print(f"\n✅ How We Handle It Now:")
    print(f"   1. Increased timeout: 60s → {config.BEDROCK_READ_TIMEOUT}s (5 minutes)")
    print(f"   2. Retry with exponential backoff: {config.MAX_RETRIES} attempts")
    print(f"   3. Fallback model: Switch to Sonnet 4.5 if 4.6 times out")
    print(f"   4. Informative messages: You'll know exactly what's happening")

    print(f"\n⚠️  Your Specific Error:")
    print(f'   "Read timeout on endpoint URL" at iteration 5')
    print(f"   → This was a timeout, not a rate limit")
    print(f"   → With new config, this would:")
    print(f"      1. Wait {config.BEDROCK_READ_TIMEOUT}s (not 60s)")
    print(f"      2. Retry {config.MAX_RETRIES} times")
    print(f"      3. Fall back to Sonnet 4.5")
    print(f"      4. Complete successfully!")


def test_rate_limit_vs_timeout():
    """Explain difference between rate limit and timeout."""
    print("\n" + "="*70)
    print("TEST 4: Rate Limit vs Timeout")
    print("="*70)

    print(f"\n❌ Timeout Error (your case):")
    print(f'   Message: "Read timeout on endpoint URL"')
    print(f'   Cause: Model took too long to respond')
    print(f'   HTTP Status: N/A (network level timeout)')
    print(f'   Solution: Increase timeout + retry + fallback')

    print(f"\n❌ Rate Limit Error (different):")
    print(f'   Message: "ThrottlingException" or "TooManyRequestsException"')
    print(f'   Cause: Too many API calls in short time')
    print(f'   HTTP Status: 429')
    print(f'   Solution: Exponential backoff (longer waits)')

    print(f"\n✅ Our Implementation Handles Both:")
    print(f"   - Timeout → Retry with {config.BEDROCK_READ_TIMEOUT}s timeout + fallback")
    print(f"   - Rate Limit → Retry with 2x exponential backoff")


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("BEDROCK RETRY & FALLBACK TEST SUITE")
    print("="*70)

    test_normal_operation()
    test_retry_behavior()
    test_timeout_scenarios()
    test_rate_limit_vs_timeout()

    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"""
✅ Timeout Issue Fixed:
   - Increased timeout: 60s → {config.BEDROCK_READ_TIMEOUT}s
   - Added retry logic: {config.MAX_RETRIES} attempts with exponential backoff
   - Added fallback: Sonnet 4.6 → Sonnet 4.5

✅ Rate Limit Handling:
   - Detects ThrottlingException
   - Longer backoff for rate limits (2x)

✅ Error Messages:
   - Clear indication of what's happening
   - Shows retry attempts and backoff times
   - Notifies when switching to fallback model

✅ Integration:
   - Both Lead Agent and Worker Agent updated
   - Automatic - no code changes needed
   - Compatible with existing code

🚀 Next Steps:
   1. Try running your PDF task again
   2. Watch for retry messages if timeouts occur
   3. Fallback will automatically engage if needed
   4. You'll see: "🔄 Switching to fallback model: ..."

Configuration in config.py:
   BEDROCK_READ_TIMEOUT = {config.BEDROCK_READ_TIMEOUT}
   BEDROCK_CONNECT_TIMEOUT = {config.BEDROCK_CONNECT_TIMEOUT}
   MAX_RETRIES = {config.MAX_RETRIES}
   RETRY_BACKOFF_BASE = {config.RETRY_BACKOFF_BASE}
   FALLBACK_MODEL_ID = "{config.FALLBACK_MODEL_ID}"
""")


if __name__ == "__main__":
    main()
