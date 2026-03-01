"""Configuration schema validation for Claude Agent SDK."""

from typing import Any, Dict
import sys


class ConfigValidator:
    """Validates configuration values."""

    @staticmethod
    def validate_all(config_dict: Dict[str, Any]) -> tuple[bool, list[str]]:
        """
        Validate all configuration values.

        Returns:
            tuple: (is_valid, error_messages)
        """
        validators = [
            ConfigValidator.validate_aws_config,
            ConfigValidator.validate_agent_config,
            ConfigValidator.validate_bedrock_config,
            ConfigValidator.validate_compression_config,
        ]

        errors = []
        for validator in validators:
            is_valid, validator_errors = validator(config_dict)
            if not is_valid:
                errors.extend(validator_errors)

        return len(errors) == 0, errors

    @staticmethod
    def validate_aws_config(config: Dict) -> tuple[bool, list[str]]:
        """Validate AWS configuration."""
        errors = []

        if not config.get("AWS_PROFILE"):
            errors.append("AWS_PROFILE not set")

        if not config.get("AWS_REGION"):
            errors.append("AWS_REGION not set")

        if not config.get("MODEL_ID"):
            errors.append("MODEL_ID not set")

        if not config.get("FALLBACK_MODEL_ID"):
            errors.append("FALLBACK_MODEL_ID not set")

        return len(errors) == 0, errors

    @staticmethod
    def validate_agent_config(config: Dict) -> tuple[bool, list[str]]:
        """Validate agent configuration."""
        errors = []

        max_tokens = config.get("MAX_TOKENS", 0)
        if max_tokens < 1000 or max_tokens > 200000:
            errors.append(f"MAX_TOKENS must be between 1000 and 200000, got {max_tokens}")

        temperature = config.get("TEMPERATURE", 0)
        if temperature < 0 or temperature > 2:
            errors.append(f"TEMPERATURE must be between 0 and 2, got {temperature}")

        max_iterations = config.get("MAX_ITERATIONS", 0)
        if max_iterations < 1 or max_iterations > 1000:
            errors.append(f"MAX_ITERATIONS must be between 1 and 1000, got {max_iterations}")

        worker_max_iterations = config.get("WORKER_MAX_ITERATIONS", 0)
        if worker_max_iterations < 1 or worker_max_iterations > 1000:
            errors.append(f"WORKER_MAX_ITERATIONS must be between 1 and 1000, got {worker_max_iterations}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_bedrock_config(config: Dict) -> tuple[bool, list[str]]:
        """Validate Bedrock configuration."""
        errors = []

        read_timeout = config.get("BEDROCK_READ_TIMEOUT", 0)
        if read_timeout < 10 or read_timeout > 3600:
            errors.append(f"BEDROCK_READ_TIMEOUT must be between 10 and 3600 seconds, got {read_timeout}")

        connect_timeout = config.get("BEDROCK_CONNECT_TIMEOUT", 0)
        if connect_timeout < 5 or connect_timeout > 300:
            errors.append(f"BEDROCK_CONNECT_TIMEOUT must be between 5 and 300 seconds, got {connect_timeout}")

        max_retries = config.get("MAX_RETRIES", 0)
        if max_retries < 0 or max_retries > 10:
            errors.append(f"MAX_RETRIES must be between 0 and 10, got {max_retries}")

        return len(errors) == 0, errors

    @staticmethod
    def validate_compression_config(config: Dict) -> tuple[bool, list[str]]:
        """Validate compression configuration."""
        errors = []

        working_set = config.get("WORKING_SET_MAX_CHARS", 0)
        if working_set < 1000 or working_set > 100000:
            errors.append(f"WORKING_SET_MAX_CHARS must be between 1000 and 100000, got {working_set}")

        rolling_summary = config.get("ROLLING_SUMMARY_MAX_CHARS", 0)
        if rolling_summary < 1000 or rolling_summary > 200000:
            errors.append(f"ROLLING_SUMMARY_MAX_CHARS must be between 1000 and 200000, got {rolling_summary}")

        return len(errors) == 0, errors


def validate_config_at_startup() -> None:
    """
    Validate configuration when imported.
    Exits with error code 1 if validation fails.
    """
    # Import here to avoid circular dependency
    import config

    config_dict = {
        "AWS_PROFILE": config.AWS_PROFILE,
        "AWS_REGION": config.AWS_REGION,
        "MODEL_ID": config.MODEL_ID,
        "FALLBACK_MODEL_ID": config.FALLBACK_MODEL_ID,
        "MAX_TOKENS": config.MAX_TOKENS,
        "TEMPERATURE": config.TEMPERATURE,
        "MAX_ITERATIONS": config.MAX_ITERATIONS,
        "WORKER_MAX_ITERATIONS": config.WORKER_MAX_ITERATIONS,
        "BEDROCK_READ_TIMEOUT": config.BEDROCK_READ_TIMEOUT,
        "BEDROCK_CONNECT_TIMEOUT": config.BEDROCK_CONNECT_TIMEOUT,
        "MAX_RETRIES": config.MAX_RETRIES,
        "WORKING_SET_MAX_CHARS": config.WORKING_SET_MAX_CHARS,
        "ROLLING_SUMMARY_MAX_CHARS": config.ROLLING_SUMMARY_MAX_CHARS,
    }

    is_valid, errors = ConfigValidator.validate_all(config_dict)

    if not is_valid:
        print("\n❌ Configuration validation failed:")
        for error in errors:
            print(f"   • {error}")
        print("\nPlease check your .env and config.yaml files.")
        print("See .env.example for a template.\n")
        sys.exit(1)
    else:
        print("✅ Configuration validated successfully")
