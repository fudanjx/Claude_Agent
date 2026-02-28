"""Error recovery and retry strategies."""

import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, Callable
from dataclasses import dataclass, asdict
from enum import Enum


class ErrorType(Enum):
    """Classification of errors."""
    TRANSIENT = "transient"  # Temporary, retry likely to succeed
    PERMANENT = "permanent"  # Won't fix with retry
    RATE_LIMIT = "rate_limit"  # Hit rate limit, need backoff
    TIMEOUT = "timeout"  # Operation timed out
    TOOL_ERROR = "tool_error"  # Tool execution failed
    UNKNOWN = "unknown"  # Unclassified


@dataclass
class RetryConfig:
    """Configuration for retry behavior."""
    max_retries: int = 3
    initial_delay: float = 1.0  # seconds
    max_delay: float = 60.0  # seconds
    exponential_base: float = 2.0
    jitter: bool = True  # Add randomness to prevent thundering herd


@dataclass
class ErrorRecord:
    """Record of an error occurrence."""
    task_id: str
    error_type: ErrorType
    error_message: str
    timestamp: str
    retry_count: int
    recovered: bool = False
    recovery_strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        d = asdict(self)
        d["error_type"] = self.error_type.value
        return d


class ErrorClassifier:
    """Classifies errors for appropriate handling."""

    @staticmethod
    def classify(error: Exception, context: Dict[str, Any] = None) -> ErrorType:
        """Classify an error type.

        Args:
            error: The exception
            context: Optional context (e.g., {"tool": "web_search"})

        Returns:
            ErrorType enum
        """
        error_str = str(error).lower()
        error_class = type(error).__name__

        # Timeout errors
        if "timeout" in error_str or error_class in ["TimeoutError", "Timeout"]:
            return ErrorType.TIMEOUT

        # Rate limiting
        if "rate limit" in error_str or "429" in error_str:
            return ErrorType.RATE_LIMIT

        # Network errors (likely transient)
        if any(x in error_str for x in ["connection", "network", "dns"]):
            return ErrorType.TRANSIENT

        # Tool-specific errors
        if context and "tool" in context:
            tool_name = context["tool"]
            if tool_name in ["web_search", "web_fetch"]:
                # Web tools often have transient errors
                return ErrorType.TRANSIENT

        # File not found (permanent)
        if "not found" in error_str or error_class == "FileNotFoundError":
            return ErrorType.PERMANENT

        # Permission errors (permanent)
        if "permission" in error_str or error_class == "PermissionError":
            return ErrorType.PERMANENT

        # Default to unknown
        return ErrorType.UNKNOWN


class RetryStrategy:
    """Implements retry strategies with exponential backoff."""

    def __init__(self, config: RetryConfig = None):
        """Initialize retry strategy.

        Args:
            config: RetryConfig or None for defaults
        """
        self.config = config or RetryConfig()

    def calculate_delay(self, retry_count: int) -> float:
        """Calculate delay before next retry.

        Args:
            retry_count: Current retry attempt (0-indexed)

        Returns:
            Delay in seconds
        """
        # Exponential backoff
        delay = self.config.initial_delay * (
            self.config.exponential_base ** retry_count
        )

        # Cap at max delay
        delay = min(delay, self.config.max_delay)

        # Add jitter if enabled
        if self.config.jitter:
            import random
            jitter = random.uniform(0, delay * 0.1)
            delay += jitter

        return delay

    def should_retry(
        self,
        error: Exception,
        retry_count: int,
        error_type: ErrorType = None
    ) -> bool:
        """Determine if operation should be retried.

        Args:
            error: The exception
            retry_count: Current retry count
            error_type: Classified error type (optional)

        Returns:
            True if should retry
        """
        # Exceeded max retries
        if retry_count >= self.config.max_retries:
            return False

        # Classify if not provided
        if error_type is None:
            error_type = ErrorClassifier.classify(error)

        # Don't retry permanent errors
        if error_type == ErrorType.PERMANENT:
            return False

        # Retry transient, timeout, and rate limit errors
        if error_type in [ErrorType.TRANSIENT, ErrorType.TIMEOUT, ErrorType.RATE_LIMIT]:
            return True

        # For unknown errors, retry once
        if error_type == ErrorType.UNKNOWN and retry_count == 0:
            return True

        return False

    def execute_with_retry(
        self,
        func: Callable,
        *args,
        **kwargs
    ) -> tuple[Any, Optional[ErrorRecord]]:
        """Execute function with automatic retry.

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Tuple of (result, error_record)
            - If successful: (result, None)
            - If failed after retries: (None, ErrorRecord)
        """
        retry_count = 0
        last_error = None
        error_type = None

        while retry_count <= self.config.max_retries:
            try:
                result = func(*args, **kwargs)

                # Success!
                if last_error:
                    # Recovered from error
                    record = ErrorRecord(
                        task_id=kwargs.get("task_id", "unknown"),
                        error_type=error_type or ErrorType.UNKNOWN,
                        error_message=str(last_error),
                        timestamp=datetime.now().isoformat(),
                        retry_count=retry_count,
                        recovered=True,
                        recovery_strategy="retry"
                    )
                    return result, record

                return result, None

            except Exception as e:
                last_error = e
                error_type = ErrorClassifier.classify(e, kwargs.get("context", {}))

                if not self.should_retry(e, retry_count, error_type):
                    # Failed, no more retries
                    record = ErrorRecord(
                        task_id=kwargs.get("task_id", "unknown"),
                        error_type=error_type,
                        error_message=str(e),
                        timestamp=datetime.now().isoformat(),
                        retry_count=retry_count,
                        recovered=False
                    )
                    return None, record

                # Calculate delay and retry
                delay = self.calculate_delay(retry_count)
                print(f"  ⚠️  Retry {retry_count + 1}/{self.config.max_retries} after {delay:.1f}s: {e}")
                time.sleep(delay)
                retry_count += 1

        # Should not reach here, but handle just in case
        record = ErrorRecord(
            task_id=kwargs.get("task_id", "unknown"),
            error_type=error_type or ErrorType.UNKNOWN,
            error_message=str(last_error),
            timestamp=datetime.now().isoformat(),
            retry_count=retry_count,
            recovered=False
        )
        return None, record


class ErrorRecoveryManager:
    """Manages error records and recovery strategies."""

    def __init__(self, state_dir: Path):
        """Initialize error recovery manager.

        Args:
            state_dir: Root state directory
        """
        self.state_dir = state_dir
        self.errors_dir = state_dir / "errors"
        self.errors_dir.mkdir(parents=True, exist_ok=True)
        self.errors_file = self.errors_dir / "errors.jsonl"

    def log_error(self, error_record: ErrorRecord):
        """Log an error record.

        Args:
            error_record: ErrorRecord to log
        """
        with open(self.errors_file, "a") as f:
            f.write(json.dumps(error_record.to_dict()) + "\n")

    def get_error_history(self, task_id: str = None) -> list[ErrorRecord]:
        """Get error history.

        Args:
            task_id: Optional filter by task ID

        Returns:
            List of ErrorRecord objects
        """
        if not self.errors_file.exists():
            return []

        errors = []
        with open(self.errors_file, "r") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    # Convert error_type string back to enum
                    data["error_type"] = ErrorType(data["error_type"])
                    record = ErrorRecord(**data)

                    if task_id is None or record.task_id == task_id:
                        errors.append(record)

        return errors

    def get_error_stats(self) -> Dict[str, Any]:
        """Get error statistics.

        Returns:
            Dict with error stats
        """
        errors = self.get_error_history()

        if not errors:
            return {"total": 0}

        stats = {
            "total": len(errors),
            "recovered": sum(1 for e in errors if e.recovered),
            "failed": sum(1 for e in errors if not e.recovered),
            "by_type": {}
        }

        # Count by type
        for error in errors:
            error_type = error.error_type.value
            if error_type not in stats["by_type"]:
                stats["by_type"][error_type] = {"total": 0, "recovered": 0}

            stats["by_type"][error_type]["total"] += 1
            if error.recovered:
                stats["by_type"][error_type]["recovered"] += 1

        return stats
