"""Subagent execution engine with isolated context.

This module implements the execution engine for Claude Code-style subagents,
providing isolated context windows, tool restrictions, and synchronous/async execution.
"""

import json
import time
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field

import config
from bedrock_client import create_bedrock_client


@dataclass
class SubagentExecution:
    """Represents a running or completed subagent execution."""

    agent_id: str
    subagent_type: str
    start_time: float
    messages: List[Dict[str, Any]] = field(default_factory=list)
    status: str = "running"  # running, completed, failed
    output: Optional[str] = None
    tool_uses: int = 0
    turns: int = 0
    error: Optional[str] = None


class SubagentExecutor:
    """Executes a subagent in isolated context."""

    def __init__(
        self,
        agent_id: str,
        definition: 'SubagentDefinition',
        initial_prompt: str,
        parent_agent: 'LeadAgent'
    ):
        self.agent_id = agent_id
        self.definition = definition
        self.initial_prompt = initial_prompt
        self.parent_agent = parent_agent

        # Isolated context - each subagent has its own message history
        self.messages: List[Dict[str, Any]] = []

        # Bedrock client (model selection)
        if definition.model == "inherit":
            self.bedrock = parent_agent.bedrock
            self.model_id = config.MODEL_ID
        else:
            # Create client with specific model
            self.bedrock = create_bedrock_client()
            # Map model names to IDs
            model_map = {
                "sonnet": "global.anthropic.claude-sonnet-4-6",
                "opus": "us.anthropic.claude-opus-4-6",
                "haiku": "us.anthropic.claude-haiku-4-5-20251001"
            }
            self.model_id = model_map.get(definition.model, config.MODEL_ID)

        # Tool dispatcher with restrictions
        self.tool_dispatcher = self._create_restricted_tool_dispatcher()

        # Execution state
        self.execution = SubagentExecution(
            agent_id=agent_id,
            subagent_type=definition.name,
            start_time=time.time()
        )

    def _create_restricted_tool_dispatcher(self) -> 'ToolDispatcher':
        """Create tool dispatcher with subagent's tool restrictions."""
        from tools import ToolDispatcher

        # Create a new dispatcher instance
        dispatcher = ToolDispatcher(config.STATE_DIR)

        # Apply tool restrictions
        if self.definition.tools:
            # Allowlist mode - only allow specified tools
            allowed = set(self.definition.tools)
            # Filter handlers to only allowed tools
            dispatcher.handlers = {
                name: handler
                for name, handler in dispatcher.handlers.items()
                if name in allowed
            }

        if self.definition.disallowed_tools:
            # Remove disallowed tools
            for tool_name in self.definition.disallowed_tools:
                dispatcher.handlers.pop(tool_name, None)

        # CRITICAL: Prevent grandchild spawning - remove Agent tool
        # This is enforced at the dispatcher level
        dispatcher.handlers.pop("Agent", None)

        return dispatcher

    def execute_sync(self) -> Dict[str, Any]:
        """Execute subagent synchronously (blocking)."""
        try:
            # Build system prompt
            system_prompt = self._build_system_prompt()

            # Add initial user message
            self.messages.append({
                "role": "user",
                "content": self.initial_prompt
            })

            # Execute agentic loop
            max_turns = self.definition.max_turns
            for turn in range(max_turns):
                self.execution.turns = turn + 1

                # Call Claude with isolated context
                response = self._call_claude(system_prompt)

                # Process response
                should_continue = self._process_response(response)

                if not should_continue:
                    break

            # Mark completed
            self.execution.status = "completed"
            self.execution.output = self._extract_final_output()

            return {
                "success": True,
                "output": self.execution.output,
                "tool_uses": self.execution.tool_uses,
                "turns": self.execution.turns,
                "agent_id": self.agent_id
            }

        except Exception as e:
            self.execution.status = "failed"
            self.execution.error = str(e)
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id
            }

    def execute_async(self) -> Dict[str, Any]:
        """Execute subagent asynchronously (background)."""
        def run_in_thread():
            result = self.execute_sync()
            # Store result for later retrieval
            self.execution.output = result.get('output', '')
            self.execution.status = "completed" if result.get('success') else "failed"

        thread = threading.Thread(target=run_in_thread, daemon=True)
        thread.start()

        return {
            "success": True,
            "agent_id": self.agent_id,
            "status": "running"
        }

    def _build_system_prompt(self) -> str:
        """Build system prompt from subagent definition."""
        # Start with base subagent system prompt
        prompt = self.definition.system_prompt

        # Add basic environment info
        prompt += f"\n\n## Environment\n"
        prompt += f"- Working directory: {Path.cwd()}\n"
        prompt += f"- Agent ID: {self.agent_id}\n"
        prompt += f"- Subagent type: {self.definition.name}\n"

        # Add tool information
        available_tools = self.tool_dispatcher.get_tool_definitions()
        tools_list = ", ".join(t['name'] for t in available_tools)
        prompt += f"- Available tools: {tools_list}\n"

        # IMPORTANT: Clarify that Agent tool is not available (prevent grandchildren)
        prompt += "\n**IMPORTANT**: You cannot spawn other subagents. The Agent tool is not available to you."

        # Add memory instructions if enabled
        if self.definition.memory:
            memory_dir = self._get_memory_dir()
            if memory_dir:
                prompt += f"\n\n## Agent Memory\n\n"
                prompt += f"You have persistent memory at: {memory_dir}\n"
                prompt += "Use read_file and write_file to persist insights, patterns, and learnings.\n"

        return prompt

    def _call_claude(self, system_prompt: str) -> Dict[str, Any]:
        """Call Claude with isolated context."""
        # Get tool definitions
        tools = self.tool_dispatcher.get_tool_definitions()

        # Prepare request
        request_body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": config.MAX_TOKENS,
            "temperature": config.TEMPERATURE,
            "system": system_prompt,
            "messages": self.messages,
            "tools": tools
        }

        # Call Bedrock
        response = self.bedrock.invoke_model(
            modelId=self.model_id,
            body=json.dumps(request_body)
        )

        response_body = json.loads(response["body"].read())
        return response_body

    def _process_response(self, response: Dict[str, Any]) -> bool:
        """Process Claude's response. Returns True to continue, False to stop."""
        content = response.get('content', [])

        # Add assistant message
        self.messages.append({
            "role": "assistant",
            "content": content
        })

        # Check for stop reason
        stop_reason = response.get('stop_reason')
        if stop_reason == 'end_turn':
            return False

        # Process tool uses
        tool_uses = []
        for block in content:
            if block.get('type') == 'tool_use':
                tool_uses.append(block)

        if not tool_uses:
            return False

        # Execute tools
        tool_results = []
        for tool_use in tool_uses:
            self.execution.tool_uses += 1
            result = self._execute_tool(tool_use)
            tool_results.append(result)

        # Add tool results as user message
        self.messages.append({
            "role": "user",
            "content": tool_results
        })

        return True

    def _execute_tool(self, tool_use: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call."""
        tool_name = tool_use['name']
        tool_input = tool_use['input']

        try:
            # Use restricted tool dispatcher
            result = self.tool_dispatcher.dispatch(tool_name, **tool_input)
            return {
                "type": "tool_result",
                "tool_use_id": tool_use['id'],
                "content": json.dumps(result)
            }
        except Exception as e:
            return {
                "type": "tool_result",
                "tool_use_id": tool_use['id'],
                "is_error": True,
                "content": str(e)
            }

    def _extract_final_output(self) -> str:
        """Extract final output from conversation."""
        # Get last assistant message
        for msg in reversed(self.messages):
            if msg['role'] == 'assistant':
                content = msg.get('content', [])
                # Extract text blocks
                text_parts = []
                for block in content:
                    if isinstance(block, dict) and block.get('type') == 'text':
                        text_parts.append(block.get('text', ''))
                    elif isinstance(block, str):
                        text_parts.append(block)
                return '\n'.join(text_parts)
        return ""

    def _get_memory_dir(self) -> Optional[Path]:
        """Get memory directory path based on scope."""
        if self.definition.memory == "user":
            memory_dir = Path.home() / ".claude" / "agent-memory" / self.definition.name
        elif self.definition.memory == "project":
            memory_dir = Path.cwd() / ".claude" / "agent-memory" / self.definition.name
        elif self.definition.memory == "local":
            memory_dir = Path.cwd() / ".claude" / "agent-memory-local" / self.definition.name
        else:
            return None

        # Create memory directory if it doesn't exist
        memory_dir.mkdir(parents=True, exist_ok=True)
        return memory_dir

    def get_status(self) -> Dict[str, Any]:
        """Get current execution status."""
        return {
            "agent_id": self.agent_id,
            "subagent_type": self.definition.name,
            "status": self.execution.status,
            "turns": self.execution.turns,
            "tool_uses": self.execution.tool_uses,
            "elapsed_time": time.time() - self.execution.start_time
        }
