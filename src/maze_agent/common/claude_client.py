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
    tools: list[dict] | None = None,
    tool_executor=None,
) -> dict:
    """Call Claude via Anthropic API with tool use support.

    Args:
        prompt: The prompt to send to Claude (string). Ignored if messages is provided.
        timeout: Timeout in seconds for the API call.
        system: Optional system prompt to set Claude's behavior.
        messages: Optional list of message dicts with 'role' and 'content' keys.
                 If provided, this is used instead of prompt.
        tools: Optional list of tool definitions for Claude to use.
        tool_executor: Optional callable that executes tools. Should accept (tool_name, tool_input)
                      and return the tool result string.

    Returns:
        Dictionary with:
        - 'text': The final text response from Claude
        - 'messages': The updated messages list including all tool use interactions

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
        message_list = messages.copy()  # Make a copy to avoid mutating the input
    elif prompt:
        message_list = [{"role": "user", "content": prompt}]
    else:
        raise ValueError("Either prompt or messages must be provided")

    # Tool use loop - keep calling until we get a final text response
    # Limit to max 2 tool calls to prevent infinite loops
    max_tool_calls = 2
    tool_call_count = 0

    while tool_call_count < max_tool_calls:
        # Build API call parameters
        api_params = {
            "model": model_version,
            "max_tokens": 1024,
            "messages": message_list,
        }

        # Add system message if provided
        if system:
            api_params["system"] = system

        # Add tools if provided
        if tools:
            api_params["tools"] = tools

        response = client.messages.create(**api_params)

        # Check if Claude wants to use a tool
        if response.stop_reason == "tool_use" and tool_executor:
            tool_call_count += 1

            # Extract tool use from response
            tool_use_block = None
            for block in response.content:
                if block.type == "tool_use":
                    tool_use_block = block
                    break

            if tool_use_block:
                # Execute the tool
                tool_name = tool_use_block.name
                tool_input = tool_use_block.input
                tool_result = tool_executor(tool_name, tool_input)

                # Add assistant's response with tool use to messages
                message_list.append({"role": "assistant", "content": response.content})

                # Add tool result to messages
                message_list.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": tool_use_block.id,
                            "content": tool_result,
                        }
                    ],
                })

                # Continue loop to get Claude's response after seeing tool result
                continue

        # No more tool use (or different stop reason) - we have the final response
        # Add final assistant response to messages
        message_list.append({"role": "assistant", "content": response.content})
        break

    # Extract text from final response
    text = None
    if response.content and len(response.content) > 0:
        for block in response.content:
            if hasattr(block, "text"):
                text = block.text
                break

    return {"text": text, "messages": message_list}


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
