# Configuration Guide

This guide explains how to configure the Claude Agent SDK using `.env` files and `config.yaml`.

## Overview

The configuration system uses a **three-tier precedence model**:

1. **Environment Variables** (highest priority) - Set in `.env` file or system environment
2. **YAML Configuration** (medium priority) - Set in `config.yaml`
3. **Built-in Defaults** (lowest priority) - Hardcoded fallback values

This allows you to:
- Keep sensitive values (AWS profile, credentials) out of source control
- Use different configurations for dev/staging/prod environments
- Override settings without modifying code
- Share non-sensitive defaults via `config.yaml` in git

## Quick Start

### 1. Create Your Environment File

Copy the example template:

```bash
cp .env.example .env
```

Edit `.env` and set your AWS configuration:

```env
AWS_PROFILE=your-aws-profile
AWS_REGION=us-east-1
MODEL_ID=global.anthropic.claude-sonnet-4-6
FALLBACK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
```

### 2. Customize Application Settings (Optional)

Edit `config.yaml` to adjust agent behavior, timeouts, compression settings, etc.

### 3. Run Your Agents

```bash
python lead_agent.py "Your task description"
```

The configuration will be automatically loaded and validated at startup.

## Configuration Files

### `.env` - Environment-Specific Settings

**Location:** `/Users/jinxin/Documents/Claude_SDK/.env`
**Status:** Gitignored (not committed to source control)
**Purpose:** Store sensitive and environment-specific values

**Required Variables:**
```env
# AWS Configuration
AWS_PROFILE=work                    # Your AWS profile name
AWS_REGION=us-east-1                # AWS region for Bedrock

# Model Configuration
MODEL_ID=global.anthropic.claude-sonnet-4-6
FALLBACK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0
```

**Optional Overrides:**
You can override any `config.yaml` setting by adding it to `.env`:

```env
# Override agent settings
MAX_TOKENS=30000
TEMPERATURE=0.7
MAX_ITERATIONS=100
WORKER_MAX_ITERATIONS=30

# Override Bedrock timeouts
BEDROCK_READ_TIMEOUT=600
BEDROCK_CONNECT_TIMEOUT=120

# Override compression thresholds
WORKING_SET_MAX_CHARS=15000
ROLLING_SUMMARY_MAX_CHARS=30000

# Override worker settings
WORKER_SCAN_INTERVAL=5

# Disable skills
SKILLS_ENABLED=false
```

### `config.yaml` - Application Defaults

**Location:** `/Users/jinxin/Documents/Claude_SDK/config.yaml`
**Status:** Committed to git
**Purpose:** Non-sensitive application settings shared across team

**Structure:**

```yaml
agent:
  temperature: 1.0        # Model sampling temperature
  max_tokens: 20000       # Max tokens per response
  max_iterations:
    lead: 50              # Lead agent max iterations
    worker: 20            # Worker agent max iterations

bedrock:
  read_timeout: 300       # Response timeout (seconds)
  connect_timeout: 60     # Connection timeout (seconds)
  max_retries: 3          # Retries before fallback
  retry_backoff_base: 2   # Exponential backoff base

compression:
  working_set_max_chars: 10000      # Working set size
  rolling_summary_max_chars: 20000  # Summary size

worker:
  scan_interval: 10       # Task scan interval (seconds)

skills:
  enabled: true           # Enable skills system
  directory: "skills"     # Skills directory

state:
  directory: ".agent_state"  # State storage directory
```

### `.env.example` - Template

**Location:** `/Users/jinxin/Documents/Claude_SDK/.env.example`
**Status:** Committed to git
**Purpose:** Template for creating `.env` file

This file documents all available environment variables with example values. Use it as a starting point for your `.env` file.

## Configuration Reference

### AWS Settings

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `AWS_PROFILE` | AWS profile name from `~/.aws/credentials` | `"work"` | `.env` |
| `AWS_REGION` | AWS region for Bedrock service | `"us-east-1"` | `.env` |
| `MODEL_ID` | Primary model ID or inference profile | `"global.anthropic.claude-sonnet-4-6"` | `.env` |
| `FALLBACK_MODEL_ID` | Fallback model if primary fails | `"anthropic.claude-sonnet-4-5-20250929-v1:0"` | `.env` |

### Agent Settings

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `TEMPERATURE` | Model sampling temperature (0.0-2.0) | `1.0` | `config.yaml` or `.env` |
| `MAX_TOKENS` | Maximum tokens per model response | `20000` | `config.yaml` or `.env` |
| `MAX_ITERATIONS` | Lead agent max iterations before stopping | `50` | `config.yaml` or `.env` |
| `WORKER_MAX_ITERATIONS` | Worker agent max iterations | `20` | `config.yaml` or `.env` |

**Temperature Guide:**
- `0.0` - Fully deterministic, same output every time
- `0.5` - Balanced, some variation
- `1.0` - Default, good balance of creativity and consistency
- `1.5+` - Very creative, more variation

### Bedrock Client Settings

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `BEDROCK_READ_TIMEOUT` | Timeout for reading response (seconds) | `300` (5 min) | `config.yaml` or `.env` |
| `BEDROCK_CONNECT_TIMEOUT` | Timeout for connection (seconds) | `60` (1 min) | `config.yaml` or `.env` |
| `MAX_RETRIES` | Number of retries before fallback | `3` | `config.yaml` or `.env` |
| `RETRY_BACKOFF_BASE` | Exponential backoff base (delay = base^attempt) | `2` | `config.yaml` or `.env` |

**Retry Behavior:**
With `MAX_RETRIES=3` and `RETRY_BACKOFF_BASE=2`:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt 4: Wait 8 seconds
- After 4 attempts: Fall back to `FALLBACK_MODEL_ID`

### Compression Settings

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `WORKING_SET_MAX_CHARS` | Max characters in working set before compression | `10000` (~10KB) | `config.yaml` or `.env` |
| `ROLLING_SUMMARY_MAX_CHARS` | Max characters in rolling summary | `20000` (~20KB) | `config.yaml` or `.env` |

**Compression Behavior:**
- When context exceeds limits, older messages are compressed into summaries
- Larger values = more context retained = higher token usage
- Smaller values = more aggressive compression = lower token usage

### Worker Settings

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `WORKER_SCAN_INTERVAL` | Seconds between task scans | `10` | `config.yaml` or `.env` |

### Skills Configuration

| Variable | Description | Default | Source |
|----------|-------------|---------|--------|
| `SKILLS_ENABLED` | Enable/disable skills system | `true` | `config.yaml` or `.env` |

**Note:** Skills directory is configured in `config.yaml` only (not environment variable).

### State Directory

| Variable | Description | Default |
|----------|-------------|---------|
| State directory | Root directory for agent state | `.agent_state` |

**Note:** State directory is configured in `config.yaml` only.

## Usage Examples

### Example 1: Development Environment

**`.env`:**
```env
AWS_PROFILE=dev-profile
AWS_REGION=us-east-1
MODEL_ID=global.anthropic.claude-sonnet-4-6
FALLBACK_MODEL_ID=anthropic.claude-sonnet-4-5-20250929-v1:0

# Use faster settings for development
MAX_ITERATIONS=20
WORKER_MAX_ITERATIONS=10
WORKER_SCAN_INTERVAL=5
```

### Example 2: Production Environment

**`.env`:**
```env
AWS_PROFILE=prod-profile
AWS_REGION=us-west-2
MODEL_ID=global.anthropic.claude-opus-4-6
FALLBACK_MODEL_ID=global.anthropic.claude-sonnet-4-6

# Use higher limits for production
MAX_TOKENS=30000
MAX_ITERATIONS=100
BEDROCK_READ_TIMEOUT=600
```

### Example 3: Testing with Lower Token Usage

**`.env`:**
```env
AWS_PROFILE=test-profile
AWS_REGION=us-east-1
MODEL_ID=global.anthropic.claude-sonnet-4-6

# Reduce token usage for testing
MAX_TOKENS=10000
WORKING_SET_MAX_CHARS=5000
ROLLING_SUMMARY_MAX_CHARS=10000
```

### Example 4: High-Performance Setup

**`.env`:**
```env
AWS_PROFILE=work
AWS_REGION=us-east-1
MODEL_ID=global.anthropic.claude-opus-4-6
FALLBACK_MODEL_ID=global.anthropic.claude-sonnet-4-6

# Maximize performance
MAX_TOKENS=40000
MAX_ITERATIONS=200
WORKER_MAX_ITERATIONS=50
BEDROCK_READ_TIMEOUT=900
WORKING_SET_MAX_CHARS=20000
ROLLING_SUMMARY_MAX_CHARS=40000
```

## Configuration Validation

The system validates all configuration values at startup. If validation fails, you'll see clear error messages:

```
❌ Configuration validation failed:
   • MAX_TOKENS must be between 1000 and 200000, got 999999
   • TEMPERATURE must be between 0 and 2, got 5.0

Please check your .env and config.yaml files.
See .env.example for a template.
```

### Validation Rules

**Agent Settings:**
- `MAX_TOKENS`: 1,000 - 200,000
- `TEMPERATURE`: 0.0 - 2.0
- `MAX_ITERATIONS`: 1 - 1,000
- `WORKER_MAX_ITERATIONS`: 1 - 1,000

**Bedrock Settings:**
- `BEDROCK_READ_TIMEOUT`: 10 - 3,600 seconds
- `BEDROCK_CONNECT_TIMEOUT`: 5 - 300 seconds
- `MAX_RETRIES`: 0 - 10

**Compression Settings:**
- `WORKING_SET_MAX_CHARS`: 1,000 - 100,000
- `ROLLING_SUMMARY_MAX_CHARS`: 1,000 - 200,000

## Troubleshooting

### Configuration Not Loading

**Problem:** Changes to `.env` or `config.yaml` not taking effect

**Solution:**
1. Ensure `.env` is in the same directory as `config.py`
2. Check file permissions (must be readable)
3. Restart your Python process
4. Check for syntax errors in YAML file

### Validation Errors

**Problem:** Configuration validation fails at startup

**Solution:**
1. Check error messages for specific issues
2. Compare your `.env` with `.env.example`
3. Verify values are within valid ranges (see Validation Rules)
4. Check for typos in variable names

### Environment Variables Not Overriding YAML

**Problem:** `.env` values not taking precedence

**Solution:**
1. Ensure `.env` file exists and is in correct location
2. Check variable names match exactly (case-sensitive)
3. Verify `python-dotenv` is installed: `pip install python-dotenv`
4. Check for syntax errors in `.env` (no spaces around `=`)

### AWS Credentials Issues

**Problem:** AWS authentication fails

**Solution:**
1. Verify `AWS_PROFILE` matches profile name in `~/.aws/credentials`
2. Check AWS region is correct for your Bedrock setup
3. Ensure AWS credentials are valid and not expired
4. Test with: `aws bedrock list-foundation-models --profile your-profile`

## Migration from Old Configuration

If you're upgrading from an older version with hardcoded `config.py`:

### Step 1: Create `.env` File

```bash
cp .env.example .env
# Edit .env with your AWS settings
```

### Step 2: Verify Defaults

The new system uses the same defaults as before, so existing setups should work without changes.

### Step 3: Test Configuration

```bash
python -c "import config; print('✅ Configuration loaded successfully')"
```

### Step 4: Customize (Optional)

Add any custom overrides to `.env` or modify `config.yaml` as needed.

## Best Practices

### Security

1. ✅ **Always gitignore `.env`** - Never commit sensitive values
2. ✅ **Use `.env.example`** - Provide template for team members
3. ✅ **Rotate credentials regularly** - Update AWS profiles periodically
4. ✅ **Use IAM roles in production** - Avoid long-lived credentials

### Organization

1. ✅ **Use `.env` for sensitive values** - AWS profiles, API keys
2. ✅ **Use `config.yaml` for shared settings** - Timeouts, limits, features
3. ✅ **Document custom settings** - Add comments to explain non-obvious values
4. ✅ **Keep `.env.example` updated** - When adding new variables

### Environment Management

1. ✅ **Use separate `.env` files** - `.env.dev`, `.env.staging`, `.env.prod`
2. ✅ **Version control `config.yaml`** - Share defaults with team
3. ✅ **Test with defaults first** - Ensure system works without custom config
4. ✅ **Validate before deployment** - Check configuration in each environment

## Advanced Usage

### Multiple Environments

Use separate `.env` files for different environments:

```bash
# Development
cp .env.dev .env

# Staging
cp .env.staging .env

# Production
cp .env.prod .env
```

### Automated Deployment

In CI/CD pipelines, set environment variables directly:

```bash
export AWS_PROFILE=ci-profile
export AWS_REGION=us-east-1
export MODEL_ID=global.anthropic.claude-sonnet-4-6
python lead_agent.py "Task description"
```

### Configuration as Code

For programmatic configuration:

```python
import os
os.environ['MAX_TOKENS'] = '30000'
os.environ['TEMPERATURE'] = '0.5'

import config
# Configuration will use environment variables
```

## Support

For issues or questions:

1. Check this documentation first
2. Review `.env.example` for variable reference
3. Verify validation rules are met
4. Check AWS Bedrock service status
5. Review logs for specific error messages

## Summary

The configuration system provides:
- ✅ **Flexibility** - Environment variables override YAML override defaults
- ✅ **Security** - Sensitive values in gitignored `.env` file
- ✅ **Validation** - Automatic checking at startup with clear errors
- ✅ **Documentation** - Self-documenting YAML with comments
- ✅ **Portability** - Easy to switch between environments
- ✅ **Backward Compatibility** - Works with sensible defaults
