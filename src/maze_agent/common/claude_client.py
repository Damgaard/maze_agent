"""Client for calling Claude Code via subprocess or API."""

import os
import subprocess

import anthropic
from dotenv import load_dotenv

# Model version mappings - hardcoded to avoid unexpected changes
MODEL_VERSIONS = {
    "haiku": "claude-3-5-haiku-20241022",
    "sonnet": "claude-sonnet-4-20250514",
    "opus": "claude-opus-4-5-20251101",
    "default": "claude-sonnet-4-20250514",
}


def call_claude_via_cli(prompt: str, timeout: int = 60) -> str | None:
    """Call Claude via subprocess.

    Args:
        prompt: The prompt to send to Claude.
        timeout: Timeout in seconds for the subprocess call.

    Returns:
        Claude's response as a string, or None if the call failed.

    """
    try:
        result = subprocess.run(["claude.cmd", "-p", prompt], capture_output=True, text=True, timeout=timeout)  # noqa: S603

        if result.returncode != 0:
            print(f"Error calling Claude: {result.stderr}")
            return None

        return result.stdout.strip()

    except subprocess.TimeoutExpired:
        print("Claude call timed out")
        return None
    except FileNotFoundError:
        print("ERROR: 'claude' command not found. Make sure Claude Code is installed.")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None


def call_claude_via_api(
    prompt: str | list[dict[str, str]] | None = None,
    timeout: int = 60,
    system: str | None = None,
    messages: list[dict[str, str]] | None = None,
) -> str | None:
    """Call Claude via Anthropic API.

    Args:
        prompt: The prompt to send to Claude (string). Ignored if messages is provided.
        timeout: Timeout in seconds for the API call.
        system: Optional system prompt to set Claude's behavior.
        messages: Optional list of message dicts with 'role' and 'content' keys.
                 If provided, this is used instead of prompt.

    Returns:
        Claude's response as a string, or None if the call failed.

    """
    # Load environment variables from .env file
    load_dotenv()

    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable not set.")

    # Get model from environment variable, default to sonnet
    model_name = os.environ.get("CLAUDE_MODEL", "default").lower()

    if model_name not in MODEL_VERSIONS:
        print(f"Warning: Unknown model '{model_name}', defaulting to sonnet")
        model_name = "default"

    model_version = MODEL_VERSIONS[model_name]
    client = anthropic.Anthropic(api_key=api_key, timeout=timeout)

    # Use provided messages or convert prompt to message
    if messages:
        message_list = messages
    elif prompt:
        message_list = [{"role": "user", "content": prompt}]
    else:
        raise ValueError("Either prompt or messages must be provided")

    # Build API call parameters
    api_params = {
        "model": model_version,
        "max_tokens": 1024,
        "messages": message_list,
    }

    # Add system message if provided
    if system:
        api_params["system"] = system

    response = client.messages.create(**api_params)

    if response.content and len(response.content) > 0:
        return response.content[0].text

    raise ValueError("Empty response from Claude API")


def get_model_info() -> tuple[str, str]:
    """Get the currently configured model name and version.

    Returns:
        Tuple of (model_name, model_version)

    """
    load_dotenv()
    model_name = os.environ.get("CLAUDE_MODEL", "default").lower()

    if model_name not in MODEL_VERSIONS:
        model_name = "default"

    return model_name, MODEL_VERSIONS[model_name]
