"""Core maze-solving agent logic."""

import json
from pathlib import Path
from typing import Dict, Any

from maze_agent.common.claude_client import call_claude
from maze_agent.common.action_parser import parse_action


# Maze state
maze_state: Dict[str, Any] = {
    'position': 'start_room',
    'solved': False,
    'action_count': 0
}

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


def run_agent_debug() -> None:
    """
    Run the agent in debug mode (manual step-by-step with status.txt/response.txt).

    This mode allows manual control over each iteration:
    1. Writes instructions to status.txt
    2. Waits for user to press Enter
    3. Reads response from response.txt
    4. Processes the action and updates state
    """
    print("=== AUTONOMOUS MAZE SOLVING AGENT (DEBUG MODE) ===")
    print("Step-by-step interactive mode\n")
    print("=" * 50)

    status_file = Path("status.txt")
    response_file = Path("response.txt")

    current_prompt = INITIAL_DESCRIPTION

    # THE AUTONOMOUS AGENT LOOP (DEBUG MODE)
    while not maze_state['solved'] and maze_state['action_count'] < 10:
        print(f"\n{'='*50}")
        print(f"ITERATION {maze_state['action_count'] + 1}")
        print(f"{'='*50}")

        # STEP 1: Write instructions to status.txt
        instructions = f"""{current_prompt}

IMPORTANT: Save your response to response.txt before printing it.
Your response should be ONLY a JSON object in this format:
{{"action": "navigate", "direction": "north"}}
or
{{"action": "search_secrets"}}
"""

        status_file.write_text(instructions, encoding='utf-8')
        print(f"✓ Instructions written to status.txt")

        # STEP 2: Wait for user to press Enter
        print("\n📋 Next steps:")
        print("   1. In Claude Code CLI, run: Read @status.txt and follow instructions")
        print("   2. Claude will save its response to response.txt")
        print("   3. Press Enter here to continue...")
        input()

        # STEP 3: Read response from response.txt
        if not response_file.exists():
            print("⚠️  response.txt not found. Please ensure Claude saved the response.")
            continue

        response = response_file.read_text(encoding='utf-8').strip()

        if not response:
            print("⚠️  response.txt is empty")
            continue

        print(f"\n📥 Response read from response.txt")

        # STEP 4: Parse the action
        action = parse_action(response)

        if not action:
            print("⚠️  Could not parse valid action from response")
            current_prompt = "Please respond with a valid JSON action: {\"action\": \"navigate\", \"direction\": \"north\"} or {\"action\": \"search_secrets\"}"
            maze_state['action_count'] += 1
            continue

        print(f"🎯 Parsed action: {json.dumps(action, indent=2)}")

        # STEP 5: Execute the action
        if action['action'] == 'navigate':
            direction = action.get('direction', 'unknown')
            print(f"\n✓ Executing: Navigate {direction.upper()}")
            print("🎉 MAZE SOLVED! Agent found the exit!\n")
            maze_state['solved'] = True
            break

        elif action['action'] == 'search_secrets':
            print(f"\n🔍 Executing: Search for secrets")
            print("Result: No secrets found.")
            current_prompt = "You searched but found no secrets. The door to the NORTH remains your only option."
            print("No secrets found.")
            maze_state['solved'] = True
            break

        maze_state['action_count'] += 1

    # Final results
    print(f"\n{'='*50}")
    if not maze_state['solved']:
        print("❌ Agent failed to solve the maze in 10 actions.")
    else:
        print(f"✅ Maze solved in {maze_state['action_count'] + 1} action(s)!")
    print(f"{'='*50}\n")


def run_agent_production() -> None:
    """
    Run the agent in production mode (API-based).

    This mode uses direct API calls for autonomous operation.
    """
    raise NotImplementedError(
        "Production mode is not yet implemented. "
        "Run in debug mode (default) for now."
    )


def run_agent(production_mode: bool = False) -> None:
    """
    Main entry point for the maze-solving agent.

    Args:
        production_mode: If True, runs in production mode (API-based).
                        If False (default), runs in debug mode (step-by-step).
    """
    if production_mode:
        run_agent_production()
    else:
        run_agent_debug()

