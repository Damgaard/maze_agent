"""Parser for extracting actions from Claude's responses."""

import json
from typing import Any


def parse_action(response: str) -> dict[str, Any] | None:
    """Extract action from Claude's response.

    Args:
        response: The raw response from Claude.

    Returns:
        A dictionary containing the parsed action, or None if parsing failed.

    """
    print(f"\nClaude's response:\n{response}\n")

    # Try to find JSON in the response
    start = response.find("{")
    end = response.rfind("}") + 1
    if start >= 0 and end > start:
        json_str = response[start:end]
        return json.loads(json_str)