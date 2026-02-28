#!/usr/bin/env python3
"""Test web search and fetch tools."""

import config
from tools import WebSearchTool, WebFetchTool


def test_web_search():
    """Test web search functionality."""
    print("="*60)
    print("Testing Web Search Tool")
    print("="*60)

    config.init_directories()
    search_tool = WebSearchTool(config.STATE_DIR)

    # Test search
    print("\nSearching for: 'Python asyncio tutorial'")
    result = search_tool("Python asyncio tutorial", max_results=3)

    if result["success"]:
        print(f"✓ Found {result['count']} results:")
        for i, r in enumerate(result["results"], 1):
            print(f"\n{i}. {r['title']}")
            print(f"   URL: {r['url']}")
            print(f"   Snippet: {r['snippet'][:100]}...")
        return True
    else:
        print(f"❌ Search failed: {result['error']}")
        return False


def test_web_fetch():
    """Test web fetch functionality."""
    print("\n" + "="*60)
    print("Testing Web Fetch Tool")
    print("="*60)

    config.init_directories()
    fetch_tool = WebFetchTool(config.STATE_DIR)

    # Test fetch
    test_url = "https://www.python.org/"
    print(f"\nFetching: {test_url}")
    result = fetch_tool(test_url)

    if result["success"]:
        print(f"✓ Fetched successfully")
        print(f"  Status: {result['status_code']}")
        print(f"  Length: {result['length']} chars")
        print(f"\nContent preview:")
        print(result["content"][:300] + "...")
        return True
    else:
        print(f"❌ Fetch failed: {result['error']}")
        return False


def main():
    """Run all tests."""
    print("\n🌐 Web Tools Test Suite\n")

    try:
        search_ok = test_web_search()
        fetch_ok = test_web_fetch()

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"{'✓' if search_ok else '❌'} Web Search")
        print(f"{'✓' if fetch_ok else '❌'} Web Fetch")

        if search_ok and fetch_ok:
            print("\n🎉 All web tools working!")
            print("\nYou can now:")
            print("  - Use web_search to find information online")
            print("  - Use web_fetch to read full webpage content")
            print("  - Try: python example_web_search.py")
            return 0
        else:
            print("\n⚠️  Some tests failed")
            print("\nTroubleshooting:")
            print("  1. Check internet connection")
            print("  2. Install dependencies: pip install -r requirements.txt")
            return 1

    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        return 1
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
