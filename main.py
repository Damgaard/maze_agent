#!/usr/bin/env python3
"""Autonomous maze-solving agent using Claude Code via subprocess.

Calls 'claude' CLI command to get agent decisions.
"""

import json
import subprocess

# Maze state
maze_state = {"position": "start_room", "solved": False, "action_count": 0}

# System prompt for the agent
INITIAL_DESCRIPTION = """You are an autonomous maze-solving agent. Your goal is to escape the maze as quickly as possible.

You have two available tools:
1. navigate(direction) - Move in a direction: north, south, east, or west
2. search_secrets() - Search for hidden passages (expensive, use only if stuck)

Respond with ONLY a JSON object in this exact format:
{"action": "navigate", "direction": "north"}
or
{"action": "search_secrets"}

Choose the best action to solve the maze quickly.

There is only 0 doors visible
What do you do?"""


def call_claude(prompt: str) -> str | None:
    """Call Claude via subprocess."""
    try:
        # Call claude with the prompt
        result = subprocess.run(["claude.cmd", "-p", prompt], capture_output=True, text=True, timeout=60)  # noqa: S603

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


def parse_action(response: str) -> dict | None:
    """Extract action from Claude's response."""
    print(f"\nClaude's response:\n{response}\n")

    try:
        # Try to find JSON in the response
        start = response.find("{")
        end = response.rfind("}") + 1
        if start >= 0 and end > start:
            json_str = response[start:end]
            return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}")

    # Fallback: simple text parsing
    response_lower = response.lower()
    if "navigate" in response_lower:
        for direction in ["north", "south", "east", "west"]:
            if direction in response_lower:
                return {"action": "navigate", "direction": direction}
        return {"action": "navigate", "direction": "north"}

    if "search" in response_lower:
        return {"action": "search_secrets"}

    return None


def run_agent() -> None:
    """Run the main autonomous agent loop."""
    print("=== AUTONOMOUS MAZE SOLVING AGENT ===")
    print("Using Claude Code via subprocess\n")
    print("=" * 50)
    print(f"\n{INITIAL_DESCRIPTION}\n")

    current_prompt = INITIAL_DESCRIPTION

    # THE AUTONOMOUS AGENT LOOP
    while not maze_state["solved"] and maze_state["action_count"] < 10:
        print(f"\n{'=' * 50}")
        print(f"ITERATION {maze_state['action_count'] + 1}")
        print(f"{'=' * 50}")

        # STEP 1: Call Claude for decision
        print("🤖 Calling Claude...")
        response = call_claude(current_prompt)

        if not response:
            print("Failed to get response from Claude")
            break

        # STEP 2: Parse the action
        action = parse_action(response)

        if not action:
            print("⚠️  Could not parse valid action from response")
            current_prompt = 'Please respond with a valid JSON action: {"action": "navigate", "direction": "north"} or {"action": "search_secrets"}'
            maze_state["action_count"] += 1
            continue

        print(f"🎯 Parsed action: {json.dumps(action, indent=2)}")

        # STEP 3: Execute the action
        if action["action"] == "navigate":
            direction = action.get("direction", "unknown")
            print(f"\n✓ Executing: Navigate {direction.upper()}")
            print("🎉 MAZE SOLVED! Agent found the exit!\n")
            maze_state["solved"] = True
            break

        elif action["action"] == "search_secrets":
            print("\n🔍 Executing: Search for secrets")
            print("Result: No secrets found.")
            current_prompt = "You searched but found no secrets. The door to the NORTH remains your only option."
            print("No secrets found.")
            maze_state["solved"] = True
            break

        maze_state["action_count"] += 1

    # Final results
    print(f"\n{'=' * 50}")
    if not maze_state["solved"]:
        print("❌ Agent failed to solve the maze in 10 actions.")
    else:
        print(f"✅ Maze solved in {maze_state['action_count'] + 1} action(s)!")
    print(f"{'=' * 50}\n")


if __name__ == "__main__":
    run_agent()
