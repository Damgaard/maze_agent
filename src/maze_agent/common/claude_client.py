"""Client for calling Claude Code via subprocess."""

import subprocess


def call_claude(prompt: str, timeout: int = 60) -> str | None:
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
