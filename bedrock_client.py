"""Robust Bedrock client with retry logic, fallback model, and timeout handling."""

import json
import time
import boto3
from botocore.config import Config
from botocore.exceptions import ReadTimeoutError, ConnectTimeoutError, ClientError
from typing import Dict, Any, Optional
import config


class BedrockClientWrapper:
    """Wrapper around AWS Bedrock client with retry and fallback logic."""

    def __init__(self, profile_name: str, region: str):
        """Initialize Bedrock client with custom timeout configuration.

        Args:
            profile_name: AWS profile name
            region: AWS region
        """
        self.profile_name = profile_name
        self.region = region
        self.primary_model = config.MODEL_ID
        self.fallback_model = config.FALLBACK_MODEL_ID

        # Configure client with custom timeouts
        boto_config = Config(
            read_timeout=config.BEDROCK_READ_TIMEOUT,
            connect_timeout=config.BEDROCK_CONNECT_TIMEOUT,
            retries={'max_attempts': 0}  # Disable boto3 auto-retry, we handle it
        )

        session = boto3.Session(profile_name=profile_name)
        self.bedrock = session.client(
            service_name="bedrock-runtime",
            region_name=region,
            config=boto_config
        )

        self.current_model = self.primary_model
        self.total_retries = 0
        self.fallback_mode = False

    def invoke_model_with_retry(
        self,
        request_body: Dict[str, Any],
        model_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Invoke Bedrock model with retry logic and fallback.

        Args:
            request_body: Request body for Bedrock API
            model_id: Optional model ID (uses current_model if not specified)

        Returns:
            Response body from Bedrock

        Raises:
            Exception: If all retries and fallback fail
        """
        if model_id is None:
            model_id = self.current_model

        last_error = None

        for attempt in range(config.MAX_RETRIES):
            try:
                # Attempt to invoke model
                response = self.bedrock.invoke_model(
                    modelId=model_id,
                    body=json.dumps(request_body)
                )

                response_body = json.loads(response["body"].read())

                # Success! Reset state if we were in fallback mode
                if self.fallback_mode and attempt == 0:
                    print("  ✅ Recovered! Primary model working again.")
                    self.fallback_mode = False
                    self.current_model = self.primary_model

                return response_body

            except (ReadTimeoutError, ConnectTimeoutError) as e:
                last_error = e
                self.total_retries += 1

                if attempt < config.MAX_RETRIES - 1:
                    # Calculate backoff
                    backoff = config.RETRY_BACKOFF_BASE ** attempt
                    print(f"  ⚠️  Timeout error (attempt {attempt + 1}/{config.MAX_RETRIES})")
                    print(f"     Retrying in {backoff} seconds...")
                    time.sleep(backoff)
                else:
                    # Max retries reached with primary model
                    print(f"  ❌ Max retries ({config.MAX_RETRIES}) reached with {model_id}")

            except ClientError as e:
                error_code = e.response.get('Error', {}).get('Code', '')

                if error_code == 'ThrottlingException':
                    # Rate limit - retry with backoff
                    last_error = e
                    self.total_retries += 1

                    if attempt < config.MAX_RETRIES - 1:
                        backoff = config.RETRY_BACKOFF_BASE ** attempt * 2  # Longer backoff for throttling
                        print(f"  ⚠️  Rate limit hit (attempt {attempt + 1}/{config.MAX_RETRIES})")
                        print(f"     Backing off for {backoff} seconds...")
                        time.sleep(backoff)
                    else:
                        print(f"  ❌ Rate limit persists after {config.MAX_RETRIES} retries")
                else:
                    # Other client errors - don't retry
                    print(f"  ❌ Bedrock API error: {e}")
                    raise

            except Exception as e:
                # Unexpected error - don't retry
                print(f"  ❌ Unexpected error: {e}")
                raise

        # If we get here, all retries failed
        # Try fallback model if we haven't already
        if model_id == self.primary_model and self.fallback_model:
            print(f"\n  🔄 Switching to fallback model: {self.fallback_model}")
            self.fallback_mode = True
            self.current_model = self.fallback_model

            try:
                return self.invoke_model_with_retry(request_body, model_id=self.fallback_model)
            except Exception as fallback_error:
                print(f"  ❌ Fallback model also failed: {fallback_error}")
                raise Exception(
                    f"Both primary ({self.primary_model}) and fallback ({self.fallback_model}) models failed. "
                    f"Last error: {last_error}"
                )

        # No fallback available or already tried fallback
        raise Exception(f"Model invocation failed after {config.MAX_RETRIES} retries: {last_error}")

    def invoke_model(self, modelId: str, body: str) -> Dict[str, Any]:
        """Compatibility wrapper for standard boto3 invoke_model interface.

        Args:
            modelId: Model ID (ignored, uses current_model)
            body: JSON string request body

        Returns:
            Response dict compatible with boto3 response format
        """
        request_body = json.loads(body)
        response_body = self.invoke_model_with_retry(request_body)

        # Return in boto3 response format
        # Create a simple class to mimic boto3's StreamingBody
        class FakeStreamingBody:
            def __init__(self, content):
                self.content = content

            def read(self):
                return self.content

        return {
            "body": FakeStreamingBody(json.dumps(response_body).encode('utf-8')),
            "ResponseMetadata": {"HTTPStatusCode": 200}
        }

    def get_status(self) -> Dict[str, Any]:
        """Get current client status.

        Returns:
            Dict with current model, fallback mode, and retry count
        """
        return {
            "current_model": self.current_model,
            "primary_model": self.primary_model,
            "fallback_model": self.fallback_model,
            "fallback_mode": self.fallback_mode,
            "total_retries": self.total_retries
        }

    def reset_to_primary(self):
        """Reset to primary model (useful after temporary issues resolve)."""
        if self.fallback_mode:
            print(f"  🔄 Resetting to primary model: {self.primary_model}")
            self.current_model = self.primary_model
            self.fallback_mode = False


def create_bedrock_client(profile_name: str = None, region: str = None) -> BedrockClientWrapper:
    """Factory function to create a Bedrock client wrapper.

    Args:
        profile_name: AWS profile (uses config.AWS_PROFILE if not specified)
        region: AWS region (uses config.AWS_REGION if not specified)

    Returns:
        BedrockClientWrapper instance
    """
    profile = profile_name or config.AWS_PROFILE
    reg = region or config.AWS_REGION

    return BedrockClientWrapper(profile, reg)
