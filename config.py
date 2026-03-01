"""Configuration management with .env and YAML support for Claude Agent SDK."""

import os
from pathlib import Path
from typing import Any, Dict, Union
import yaml
from dotenv import load_dotenv

# Load .env file (if exists)
# Note: override=True ensures .env values take precedence over system environment
dotenv_path = Path(__file__).parent / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path, override=True)
    print(f"✓ Loaded environment variables from {dotenv_path}")
else:
    print("ℹ No .env file found, using defaults from config.yaml")

# Load YAML config
config_file = Path(__file__).parent / "config.yaml"
_yaml_config: Dict[str, Any] = {}

if config_file.exists():
    try:
        with open(config_file, 'r') as f:
            _yaml_config = yaml.safe_load(f) or {}
        print(f"✓ Loaded configuration from {config_file}")
    except Exception as e:
        print(f"⚠ Warning: Could not load config.yaml: {e}")
        print("  Using built-in defaults")
else:
    print("ℹ No config.yaml file found, using built-in defaults")


def get_config(section: str, key: str, default: Any = None, env_var: str = None) -> Any:
    """
    Get configuration value with precedence: ENV > YAML > Default

    Args:
        section: YAML section name (e.g., 'agent', 'bedrock')
        key: Key within the section
        default: Default value if not found
        env_var: Environment variable name to check first

    Returns:
        Configuration value with type matching default
    """
    # Check environment variable first (highest priority)
    if env_var and os.getenv(env_var):
        env_value = os.getenv(env_var)
        # Try to convert to the type of default
        if default is not None:
            try:
                return type(default)(env_value)
            except (ValueError, TypeError):
                return env_value
        return env_value

    # Check YAML config
    if section and key and section in _yaml_config:
        yaml_value = _yaml_config[section].get(key, default)
        return yaml_value

    # Return default
    return default


def get_nested_config(section: str, key: str, subkey: str, default: Any = None) -> Any:
    """
    Get nested configuration value (e.g., agent.max_iterations.lead)

    Args:
        section: YAML section name
        key: Key within the section
        subkey: Nested key
        default: Default value if not found

    Returns:
        Configuration value
    """
    if section in _yaml_config and key in _yaml_config[section]:
        nested_value = _yaml_config[section][key]
        if isinstance(nested_value, dict):
            return nested_value.get(subkey, default)
    return default


# ============================================================================
# AWS Configuration (from .env, highest priority for sensitive values)
# ============================================================================

AWS_PROFILE = os.getenv("AWS_PROFILE", "work")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
MODEL_ID = os.getenv("MODEL_ID", "global.anthropic.claude-sonnet-4-6")
FALLBACK_MODEL_ID = os.getenv("FALLBACK_MODEL_ID", "anthropic.claude-sonnet-4-5-20250929-v1:0")

# ============================================================================
# Agent Settings
# ============================================================================

TEMPERATURE = float(get_config("agent", "temperature", 1.0, "TEMPERATURE"))
MAX_TOKENS = int(get_config("agent", "max_tokens", 20000, "MAX_TOKENS"))

# Max iterations with separate settings for lead and worker
MAX_ITERATIONS = int(get_nested_config("agent", "max_iterations", "lead", 50))
if os.getenv("MAX_ITERATIONS"):
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS"))

WORKER_MAX_ITERATIONS = int(get_nested_config("agent", "max_iterations", "worker", 20))
if os.getenv("WORKER_MAX_ITERATIONS"):
    WORKER_MAX_ITERATIONS = int(os.getenv("WORKER_MAX_ITERATIONS"))

# ============================================================================
# Bedrock Client Settings
# ============================================================================

BEDROCK_READ_TIMEOUT = int(get_config("bedrock", "read_timeout", 300, "BEDROCK_READ_TIMEOUT"))
BEDROCK_CONNECT_TIMEOUT = int(get_config("bedrock", "connect_timeout", 60, "BEDROCK_CONNECT_TIMEOUT"))
MAX_RETRIES = int(get_config("bedrock", "max_retries", 3, "MAX_RETRIES"))
RETRY_BACKOFF_BASE = int(get_config("bedrock", "retry_backoff_base", 2, "RETRY_BACKOFF_BASE"))

# ============================================================================
# Compression Settings
# ============================================================================

WORKING_SET_MAX_CHARS = int(get_config("compression", "working_set_max_chars", 10000, "WORKING_SET_MAX_CHARS"))
ROLLING_SUMMARY_MAX_CHARS = int(get_config("compression", "rolling_summary_max_chars", 20000, "ROLLING_SUMMARY_MAX_CHARS"))

# ============================================================================
# Worker Settings
# ============================================================================

WORKER_SCAN_INTERVAL = int(get_config("worker", "scan_interval", 10, "WORKER_SCAN_INTERVAL"))

# ============================================================================
# Skills Configuration
# ============================================================================

SKILLS_ENABLED = get_config("skills", "enabled", True, "SKILLS_ENABLED")
# Handle string boolean values from environment variables
if isinstance(SKILLS_ENABLED, str):
    SKILLS_ENABLED = SKILLS_ENABLED.lower() in ("true", "1", "yes")

skills_dir = get_config("skills", "directory", "skills")
SKILLS_DIR = Path(__file__).parent / skills_dir

# ============================================================================
# State Directory Configuration
# ============================================================================

state_dir_name = get_config("state", "directory", ".agent_state")
STATE_DIR = Path(state_dir_name)
BOARD_DIR = STATE_DIR / "board"
TASKS_DIR = STATE_DIR / "tasks"
MAILBOXES_DIR = STATE_DIR / "mailboxes"
WORKTREES_DIR = STATE_DIR / "worktrees"


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


# ============================================================================
# Configuration Validation (run at import time)
# ============================================================================

def print_config_summary():
    """Print a summary of loaded configuration."""
    print("\n📋 Configuration Summary:")
    print(f"   AWS Profile: {AWS_PROFILE}")
    print(f"   AWS Region: {AWS_REGION}")
    print(f"   Model ID: {MODEL_ID}")
    print(f"   Max Iterations (Lead): {MAX_ITERATIONS}")
    print(f"   Max Iterations (Worker): {WORKER_MAX_ITERATIONS}")
    print(f"   Skills Enabled: {SKILLS_ENABLED}")
    print(f"   State Directory: {STATE_DIR}")
    print()


# Run validation when module is imported
if __name__ != "__main__":
    from config_schema import validate_config_at_startup
    validate_config_at_startup()
    print_config_summary()
