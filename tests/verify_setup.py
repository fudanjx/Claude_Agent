#!/usr/bin/env python3
"""Verify that the Claude Agent setup is working correctly."""

import sys
from pathlib import Path


def check_python_version():
    """Check Python version."""
    print("Checking Python version...")
    if sys.version_info < (3, 8):
        print("  ❌ Python 3.8+ required")
        return False
    print(f"  ✓ Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    return True


def check_dependencies():
    """Check if required packages are installed."""
    print("\nChecking dependencies...")
    required = ["boto3", "anthropic", "pydantic"]
    all_ok = True

    for package in required:
        try:
            __import__(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ❌ {package} not installed")
            all_ok = False

    return all_ok


def check_aws_credentials():
    """Check AWS credentials."""
    print("\nChecking AWS credentials...")
    try:
        import boto3
        session = boto3.Session(profile_name="work")
        sts = session.client("sts")
        identity = sts.get_caller_identity()
        print(f"  ✓ AWS profile 'work' configured")
        print(f"    Account: {identity['Account']}")
        print(f"    User/Role: {identity['Arn'].split('/')[-1]}")
        return True
    except Exception as e:
        print(f"  ❌ AWS profile 'work' not configured or invalid")
        print(f"     Error: {e}")
        return False


def check_bedrock_access():
    """Check AWS Bedrock access."""
    print("\nChecking AWS Bedrock access...")
    try:
        import boto3
        import config

        session = boto3.Session(profile_name=config.AWS_PROFILE)
        bedrock = session.client(
            service_name="bedrock-runtime",
            region_name=config.AWS_REGION
        )

        # Try to invoke the model with a minimal request
        # Note: This will make an actual API call
        print(f"  Testing connection to {config.MODEL_ID}...")
        print(f"  (This will make a small API call to verify access)")

        response = bedrock.invoke_model(
            modelId=config.MODEL_ID,
            body='{"anthropic_version":"bedrock-2023-05-31","max_tokens":10,"messages":[{"role":"user","content":"Hi"}]}'
        )

        print(f"  ✓ Bedrock access confirmed")
        print(f"    Model: {config.MODEL_ID}")
        print(f"    Region: {config.AWS_REGION}")
        return True

    except Exception as e:
        print(f"  ❌ Cannot access Bedrock")
        print(f"     Error: {e}")
        print(f"\n  Common fixes:")
        print(f"  1. Ensure your AWS account has Bedrock access enabled")
        print(f"  2. Request access to Claude models in AWS Console")
        print(f"  3. Check that your IAM permissions include bedrock:InvokeModel")
        return False


def check_project_structure():
    """Check project structure."""
    print("\nChecking project structure...")
    required_files = [
        "config.py",
        "prompts.py",
        "tools.py",
        "task_manager.py",
        "lead_agent.py",
        "requirements.txt",
        "PRD.md"
    ]

    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  ✓ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_ok = False

    return all_ok


def main():
    """Run all checks."""
    print("="*60)
    print("Claude Agent Setup Verification")
    print("="*60)

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("AWS Credentials", check_aws_credentials),
        ("Project Structure", check_project_structure),
    ]

    results = {}
    for name, check_func in checks:
        results[name] = check_func()

    # Optional Bedrock check
    print("\n" + "="*60)
    if all(results.values()):
        print("Basic checks passed! Testing Bedrock access...")
        print("="*60)
        results["Bedrock Access"] = check_bedrock_access()
    else:
        print("⚠️  Fix the issues above before testing Bedrock access")

    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)

    all_passed = all(results.values())
    for name, passed in results.items():
        status = "✓" if passed else "❌"
        print(f"{status} {name}")

    if all_passed:
        print("\n🎉 All checks passed! Your setup is ready.")
        print("\nNext steps:")
        print("  1. Read QUICKSTART.md")
        print("  2. Try: python example.py 1")
        print("  3. Or run: python lead_agent.py")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("\nTo install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nTo configure AWS:")
        print("  aws configure --profile work")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
