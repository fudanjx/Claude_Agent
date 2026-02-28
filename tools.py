"""Tool handlers for the agent system."""

import subprocess
import json
import requests
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from bs4 import BeautifulSoup


class ToolHandler:
    """Base class for tool handlers."""

    def __init__(self, state_dir: Path):
        self.state_dir = state_dir
        self.logs_dir = state_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def log_tool_call(self, tool_name: str, params: Dict[str, Any], result: Dict[str, Any]):
        """Log tool calls to disk."""
        log_file = self.logs_dir / "tool_calls.jsonl"
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "tool": tool_name,
            "params": params,
            "result": result
        }
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")


class BashTool(ToolHandler):
    """Execute bash commands."""

    def __call__(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Execute a bash command and return result."""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            output = {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "success": result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            output = {
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "exit_code": -1,
                "success": False
            }
        except Exception as e:
            output = {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "success": False
            }

        self.log_tool_call("bash", {"command": command}, output)
        return output


class ReadFileTool(ToolHandler):
    """Read file contents."""

    def __call__(self, path: str) -> Dict[str, Any]:
        """Read a file and return its contents."""
        try:
            file_path = Path(path).expanduser()
            if not file_path.exists():
                result = {"error": f"File not found: {path}", "success": False}
            elif not file_path.is_file():
                result = {"error": f"Not a file: {path}", "success": False}
            else:
                content = file_path.read_text()
                result = {"content": content, "success": True, "path": str(file_path)}
        except Exception as e:
            result = {"error": str(e), "success": False}

        self.log_tool_call("read_file", {"path": path}, result)
        return result


class WriteFileTool(ToolHandler):
    """Write content to a file."""

    def __call__(self, path: str, content: str) -> Dict[str, Any]:
        """Write content to a file."""
        try:
            file_path = Path(path).expanduser()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            result = {"success": True, "path": str(file_path)}
        except Exception as e:
            result = {"error": str(e), "success": False}

        self.log_tool_call("write_file", {"path": path, "content_length": len(content)}, result)
        return result


class ListDirTool(ToolHandler):
    """List directory contents."""

    def __call__(self, path: str = ".") -> Dict[str, Any]:
        """List contents of a directory."""
        try:
            dir_path = Path(path).expanduser()
            if not dir_path.exists():
                result = {"error": f"Directory not found: {path}", "success": False}
            elif not dir_path.is_dir():
                result = {"error": f"Not a directory: {path}", "success": False}
            else:
                items = [
                    {
                        "name": item.name,
                        "type": "dir" if item.is_dir() else "file",
                        "size": item.stat().st_size if item.is_file() else None
                    }
                    for item in sorted(dir_path.iterdir())
                ]
                result = {"items": items, "success": True, "path": str(dir_path)}
        except Exception as e:
            result = {"error": str(e), "success": False}

        self.log_tool_call("list_dir", {"path": path}, result)
        return result


class WebSearchTool(ToolHandler):
    """Search the web for information."""

    def __call__(self, query: str, max_results: int = 5) -> Dict[str, Any]:
        """Search the web using DuckDuckGo.

        Args:
            query: Search query
            max_results: Maximum number of results to return (default: 5)

        Returns:
            Dict with search results
        """
        try:
            from ddgs import DDGS

            results = []
            with DDGS() as ddgs:
                search_results = ddgs.text(query, max_results=max_results)
                for r in search_results:
                    results.append({
                        "title": r.get("title", ""),
                        "url": r.get("href", ""),
                        "snippet": r.get("body", "")
                    })

            result = {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }

        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "query": query
            }

        self.log_tool_call("web_search", {"query": query, "max_results": max_results}, result)
        return result


class WebFetchTool(ToolHandler):
    """Fetch and extract text content from a URL."""

    def __call__(self, url: str, timeout: int = 10) -> Dict[str, Any]:
        """Fetch content from a URL and extract readable text.

        Args:
            url: URL to fetch
            timeout: Request timeout in seconds (default: 10)

        Returns:
            Dict with extracted content
        """
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (compatible; ClaudeAgentBot/1.0)"
            }

            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            # Limit length
            max_length = 10000
            if len(text) > max_length:
                text = text[:max_length] + "\n\n[Content truncated...]"

            result = {
                "success": True,
                "url": url,
                "content": text,
                "length": len(text),
                "status_code": response.status_code
            }

        except requests.Timeout:
            result = {
                "success": False,
                "error": f"Request timed out after {timeout} seconds",
                "url": url
            }
        except requests.RequestException as e:
            result = {
                "success": False,
                "error": str(e),
                "url": url
            }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "url": url
            }

        self.log_tool_call("web_fetch", {"url": url}, result)
        return result


class ToolDispatcher:
    """Dispatcher for all tools."""

    def __init__(self, state_dir: Path):
        self.handlers = {
            "bash": BashTool(state_dir),
            "read_file": ReadFileTool(state_dir),
            "write_file": WriteFileTool(state_dir),
            "list_dir": ListDirTool(state_dir),
            "web_search": WebSearchTool(state_dir),
            "web_fetch": WebFetchTool(state_dir),
        }
        # Task management tools are handled separately in lead_agent.py
        # to avoid circular dependency with TaskManager

    def dispatch(self, tool_name: str, **params) -> Dict[str, Any]:
        """Dispatch a tool call to the appropriate handler."""
        if tool_name not in self.handlers:
            return {"error": f"Unknown tool: {tool_name}", "success": False}

        handler = self.handlers[tool_name]
        return handler(**params)

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get Claude API tool definitions."""
        return [
            {
                "name": "bash",
                "description": "Execute a bash command. Returns stdout, stderr, and exit code.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "The bash command to execute"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout in seconds (default: 30)",
                            "default": 30
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "read_file",
                "description": "Read the contents of a file.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to read"
                        }
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file. Creates parent directories if needed.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the file to write"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file"
                        }
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_dir",
                "description": "List contents of a directory.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "path": {
                            "type": "string",
                            "description": "Path to the directory to list (default: current directory)",
                            "default": "."
                        }
                    }
                }
            },
            {
                "name": "web_search",
                "description": "Search the internet for information using DuckDuckGo. Returns titles, URLs, and snippets of search results. Use this to find current information, facts, and sources on any topic.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The search query"
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return (default: 5)",
                            "default": 5
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "web_fetch",
                "description": "Fetch and extract readable text content from a URL. Use this after web_search to read the full content of a webpage. Automatically removes navigation, scripts, and formatting to get clean text.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "url": {
                            "type": "string",
                            "description": "The URL to fetch content from"
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Request timeout in seconds (default: 10)",
                            "default": 10
                        }
                    },
                    "required": ["url"]
                }
            },
            {
                "name": "create_task",
                "description": "Create a new task in the task board. Returns the created task with task_id.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "goal": {
                            "type": "string",
                            "description": "Clear description of the task goal"
                        },
                        "deps": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of task IDs this task depends on",
                            "default": []
                        },
                        "priority": {
                            "type": "string",
                            "enum": ["low", "med", "high"],
                            "description": "Task priority",
                            "default": "med"
                        }
                    },
                    "required": ["goal"]
                }
            },
            {
                "name": "update_task",
                "description": "Update an existing task's status or properties.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "task_id": {
                            "type": "string",
                            "description": "The task ID to update"
                        },
                        "updates": {
                            "type": "object",
                            "description": "Dictionary of fields to update (e.g., {\"status\": \"IN_PROGRESS\", \"owner\": \"Lead\"})"
                        }
                    },
                    "required": ["task_id", "updates"]
                }
            },
            {
                "name": "list_tasks",
                "description": "List all tasks with optional filters. Returns tasks and summary by status.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "spawn_job",
                "description": "Spawn a background job for long-running commands. Job runs asynchronously and you can check status later.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "command": {
                            "type": "string",
                            "description": "Shell command to execute in background"
                        }
                    },
                    "required": ["command"]
                }
            },
            {
                "name": "get_job_status",
                "description": "Get the status of a background job.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Job ID to check"
                        }
                    },
                    "required": ["job_id"]
                }
            },
            {
                "name": "get_job_output",
                "description": "Get the output (stdout and stderr) of a background job.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "Job ID to get output from"
                        }
                    },
                    "required": ["job_id"]
                }
            },
            {
                "name": "list_jobs",
                "description": "List all background jobs and their status.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "read_inbox",
                "description": "Read messages from Lead's inbox. Returns messages from worker agents.",
                "input_schema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "send_message",
                "description": "Send a message to another agent (worker) via mailbox protocol.",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "to_agent": {
                            "type": "string",
                            "description": "Target agent name (e.g., 'Worker_alpha')"
                        },
                        "msg_type": {
                            "type": "string",
                            "enum": ["REQUEST", "RESPONSE", "PROGRESS", "COMPLETE", "BLOCKED"],
                            "description": "Message type"
                        },
                        "task_id": {
                            "type": "string",
                            "description": "Associated task ID"
                        },
                        "body": {
                            "type": "object",
                            "description": "Message body (dict)"
                        }
                    },
                    "required": ["to_agent", "msg_type", "task_id", "body"]
                }
            }
        ]
