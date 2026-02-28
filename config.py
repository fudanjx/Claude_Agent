"""Configuration for Claude Agent with AWS Bedrock."""

import os
from pathlib import Path

# AWS Bedrock Configuration
AWS_PROFILE = "work"
AWS_REGION = "us-east-1"  # Adjust if needed
MODEL_ID = "global.anthropic.claude-sonnet-4-6"  # Inference profile ID for Claude Sonnet 4.6

# Agent State Directory
STATE_DIR = Path(".agent_state")
BOARD_DIR = STATE_DIR / "board"
TASKS_DIR = STATE_DIR / "tasks"
MAILBOXES_DIR = STATE_DIR / "mailboxes"
WORKTREES_DIR = STATE_DIR / "worktrees"

# Compression thresholds
WORKING_SET_MAX_SIZE = 2000  # characters
COMPRESSION_TRIGGER_THRESHOLD = 5000  # characters

# Agent settings
MAX_ITERATIONS = 50
TEMPERATURE = 1.0
MAX_TOKENS = 4096

def init_directories():
    """Create necessary directories if they don't exist."""
    STATE_DIR.mkdir(exist_ok=True)
    BOARD_DIR.mkdir(exist_ok=True)
    TASKS_DIR.mkdir(exist_ok=True)
    MAILBOXES_DIR.mkdir(exist_ok=True)
    WORKTREES_DIR.mkdir(exist_ok=True)

    # Create Lead mailbox
    (MAILBOXES_DIR / "Lead" / "inbox").mkdir(parents=True, exist_ok=True)
    (MAILBOXES_DIR / "Lead" / "outbox").mkdir(parents=True, exist_ok=True)

    # Create tasks.jsonl if not exists
    tasks_file = BOARD_DIR / "tasks.jsonl"
    if not tasks_file.exists():
        tasks_file.touch()

    print(f"✓ Initialized agent state directory: {STATE_DIR.absolute()}")
