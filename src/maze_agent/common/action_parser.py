"""Parser for extracting actions from Claude's responses."""

import json
from typing import Optional, Dict, Any


def parse_action(response: str) -> Optional[Dict[str, Any]]:
    """
    Extract action from Claude's response.

    Args:
        response: The raw response from Claude.

    Returns:
        A dictionary containing the parsed action, or None if parsing failed.
    """
    print(f"\nClaude's response:\n{response}\n")

    try:
        # Try to find JSON in the response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            action = json.loads(json_str)
            return action
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")

    # Fallback: simple text parsing
    response_lower = response.lower()
    if "navigate" in response_lower:
        for direction in ["north", "south", "east", "west"]:
            if direction in response_lower:
                return {"action": "navigate", "direction": direction}
        return {"action": "navigate", "direction": "north"}
    elif "search" in response_lower:
        return {"action": "search_secrets"}

    return None
