# Web Search & Fetch Tools Guide

## 🌐 Overview

Your Claude Agent now has internet access! Two powerful tools enable grounded fact-finding:

1. **web_search** - Search the internet using DuckDuckGo
2. **web_fetch** - Fetch and extract content from URLs

## ✅ Installation

Dependencies are already included in `requirements.txt`:

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## 🔧 Tools

### 1. web_search(query, max_results=5)

Search the internet for information.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (int, optional): Number of results (default: 5)

**Returns:**
```json
{
  "success": true,
  "query": "Python asyncio",
  "results": [
    {
      "title": "asyncio — Asynchronous I/O",
      "url": "https://docs.python.org/3/library/asyncio.html",
      "snippet": "asyncio is a library to write concurrent..."
    }
  ],
  "count": 5
}
```

**Example:**
```python
# Agent will use this tool when you ask to search
python lead_agent.py "Search for Python 3.13 new features"
```

### 2. web_fetch(url, timeout=10)

Fetch and extract readable text from a URL.

**Parameters:**
- `url` (string, required): URL to fetch
- `timeout` (int, optional): Timeout in seconds (default: 10)

**Returns:**
```json
{
  "success": true,
  "url": "https://example.com",
  "content": "Extracted clean text content...",
  "length": 5000,
  "status_code": 200
}
```

**Features:**
- Automatically removes scripts, styles, navigation
- Extracts clean, readable text
- Limits content to 10,000 characters
- Handles timeouts gracefully

## 🚀 Usage Examples

### Example 1: Simple Search

```bash
python lead_agent.py "What are the top 3 Python web frameworks?"
```

The agent will:
1. Use `web_search` to find information
2. Summarize the results
3. Provide source URLs

### Example 2: Deep Research

```bash
python lead_agent.py "Search for Python async frameworks, fetch the top 2 articles, and create a comparison"
```

The agent will:
1. Search the web
2. Use `web_fetch` to read full articles
3. Compare and synthesize information
4. Cite sources

### Example 3: Fact Checking

```bash
python lead_agent.py "Verify: What is the current stable Python version? Provide sources."
```

The agent will:
1. Search for current information
2. Provide the answer with evidence
3. Include source URLs for verification

### Example 4: Multi-Topic Research

```bash
python example_web_search.py 5
```

Creates multiple research tasks for workers:
- Each worker searches and summarizes a topic
- All results include source URLs
- Parallel execution

## 📋 Pre-Made Examples

Run ready-made examples:

```bash
# Example 1 - Simple search and summarize
python example_web_search.py 1

# Example 2 - Multi-source research
python example_web_search.py 2

# Example 3 - Fact checking with sources
python example_web_search.py 3

# Example 4 - Deep dive research
python example_web_search.py 4

# Example 5 - Parallel research with workers
python example_web_search.py 5
```

## 🎯 Best Practices

### 1. Combine Search + Fetch
```python
# Good workflow:
# 1. Search to find relevant sources
# 2. Fetch to read full content
# 3. Synthesize and cite sources

"Search for 'Python type hints', fetch the top result, and summarize with source"
```

### 2. Verify with Multiple Sources
```python
# Compare multiple sources for accuracy
"Search for 'Python GIL removal', fetch 2 articles, compare information"
```

### 3. Always Cite Sources
```python
# Include source URLs in deliverables
"Research X and create a report with source citations"
```

### 4. Use Workers for Parallel Research
```python
# Create multiple research tasks
# Workers will claim and execute in parallel
"Create 3 tasks: research Python frameworks, async libraries, and testing tools"
```

## 🔍 Search Quality Tips

### Good Queries
✅ "Python 3.13 new features"
✅ "asyncio vs threading comparison"
✅ "FastAPI performance benchmarks"
✅ "current Python version 2025"

### Specific Queries Get Better Results
❌ "Python" (too broad)
✅ "Python web frameworks comparison 2025"

❌ "async" (too vague)
✅ "Python asyncio tutorial for beginners"

## 🎓 Use Cases

### 1. Current Information
```bash
# Get up-to-date facts
python lead_agent.py "What is the latest Python version?"
```

### 2. Technical Research
```bash
# Research technical topics
python lead_agent.py "Compare Python ASGI servers: Uvicorn, Hypercorn, Daphne"
```

### 3. Documentation Lookup
```bash
# Find official docs
python lead_agent.py "Search for Python typing module documentation"
```

### 4. Trend Analysis
```bash
# Research trends
python lead_agent.py "Search for Python framework popularity trends in 2025"
```

### 5. Problem Solving
```bash
# Find solutions
python lead_agent.py "Search for solutions to Python memory leaks in asyncio"
```

## 🧪 Testing

Test the tools:

```bash
# Test both tools
python test_web_tools.py

# Should show:
# ✓ Web Search
# ✓ Web Fetch
```

## 📊 Capabilities

| Feature | Status | Notes |
|---------|--------|-------|
| Web Search | ✅ | DuckDuckGo, no API key needed |
| Web Fetch | ✅ | Clean text extraction |
| HTML Parsing | ✅ | BeautifulSoup4 |
| Source Citations | ✅ | URLs included in results |
| Rate Limiting | ✅ | Automatic via ddgs |
| Timeout Handling | ✅ | Configurable |
| Error Recovery | ✅ | Graceful failures |

## ⚠️ Limitations

1. **Search Results:** Max 10 results per query (DuckDuckGo limit)
2. **Content Length:** Fetched content limited to 10,000 chars
3. **No Authentication:** Can't access pages requiring login
4. **JavaScript:** Limited support for JS-heavy sites
5. **Rate Limits:** Automatic throttling by search provider

## 🔧 Configuration

Edit search behavior in `tools.py`:

```python
# WebSearchTool
max_results = 5  # Change default result count

# WebFetchTool
max_length = 10000  # Change content limit
timeout = 10  # Change request timeout
```

## 🎉 Integration with Existing Features

### With Background Jobs
```bash
"Spawn background job to search and download research papers while I plan analysis"
```

### With Workers
```bash
"Create 5 research tasks for workers, each should web_search their topic"
```

### With Compression
```bash
# Long research sessions automatically compress
# Search results are preserved in rolling summary
```

### With Task Board
```python
task = task_mgr.create_task(
    goal="Search for Python security best practices and create guide",
    priority="high"
)
# Workers can claim and use web_search
```

## 🚀 Advanced Patterns

### Pattern 1: Research Pipeline
```
1. Search for topic → Get URLs
2. Fetch top 3 URLs → Get content
3. Synthesize → Create report with sources
```

### Pattern 2: Fact Verification
```
1. Search claim → Find sources
2. Fetch sources → Read evidence
3. Compare → Verify accuracy
```

### Pattern 3: Comparative Analysis
```
1. Search topic A → Get info
2. Search topic B → Get info
3. Fetch details → Compare
4. Report → With all sources cited
```

### Pattern 4: Parallel Research
```
1. Create N research tasks
2. Workers claim tasks
3. Each uses web_search + web_fetch
4. Combine results → Master report
```

## 📚 Example Workflows

### Workflow 1: Quick Fact Check
```bash
python lead_agent.py "What year was Python created? Verify with sources."
```
⏱️ ~10 seconds

### Workflow 2: Comprehensive Research
```bash
python lead_agent.py "Research Python web frameworks: Django, Flask, FastAPI. Search for each, fetch documentation, create comparison table with sources."
```
⏱️ ~2-3 minutes

### Workflow 3: Multi-Agent Research
```bash
# Terminal 1
python lead_agent.py "Create 3 research tasks on Python topics"

# Terminal 2
python worker_agent.py Worker_alpha
```
⏱️ Parallel execution

## 🎊 Summary

You now have:
- ✅ Internet search capability (DuckDuckGo)
- ✅ Web content fetching
- ✅ Clean text extraction
- ✅ Source citation
- ✅ No API keys required
- ✅ Full integration with Phase 2 features

**Your agent can now find grounded facts from the internet!** 🌐
