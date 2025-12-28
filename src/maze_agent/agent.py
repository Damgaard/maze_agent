"""Core maze-solving agent logic."""

import json
from pathlib import Path
from typing import Dict, Any

from maze_agent.common.claude_client import call_claude
from maze_agent.common.action_parser import parse_action
from maze_agent.common.maze_state import MazeState


# System prompt template
SYSTEM_PROMPT = """You are an autonomous maze-solving agent. Your goal is to escape the maze as quickly as possible.

You have two available tools:
1. navigate(direction) - Move in a direction: north, south, east, or west
2. search_secrets() - Search for hidden passages (expensive, use only if stuck)

Respond with ONLY a JSON object in this exact format:
{"action": "navigate", "direction": "north"}
or
{"action": "search_secrets"}

Choose the best action to solve the maze quickly."""


def run_agent_debug(maze_number: int = 1) -> None:
    """
    Run the agent in debug mode (manual step-by-step with status.txt/response.txt).

    This mode allows manual control over each iteration:
    1. Writes instructions to status.txt
    2. Waits for user to press Enter
    3. Reads response from response.txt
    4. Processes the action and updates state

    Args:
        maze_number: The maze to load (default: 1)
    """
    print("=== AUTONOMOUS MAZE SOLVING AGENT (DEBUG MODE) ===")
    print(f"Loading Maze {maze_number}")
    print("Step-by-step interactive mode\n")
    print("=" * 50)

    # Initialize maze state
    maze = MazeState(maze_number=maze_number)

    status_file = Path("status.txt")
    response_file = Path("response.txt")

    # Generate initial prompt with current room status
    current_situation = maze.get_status_description()

    # THE AUTONOMOUS AGENT LOOP (DEBUG MODE)
    max_actions = 20
    while not maze.solved and maze.action_count < max_actions:
        print(f"\n{'='*50}")
        print(f"ITERATION {maze.action_count + 1}")
        print(f"{'='*50}")
        print(f"Current room status: {current_situation}")

        # STEP 1: Write instructions to status.txt
        instructions = f"""{SYSTEM_PROMPT}

Current situation:
{current_situation}

What do you do?

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
            current_situation = "ERROR: Invalid action format. Please respond with valid JSON."
            continue

        print(f"🎯 Parsed action: {json.dumps(action, indent=2)}")

        # STEP 5: Execute the action and update state
        if action['action'] == 'navigate':
            direction = action.get('direction', 'unknown')
            print(f"\n✓ Executing: Navigate {direction.upper()}")

            result = maze.navigate(direction)

            if result['success']:
                print(f"   {result['message']}")
                if result.get('reached_exit', False):
                    print("🎉 MAZE SOLVED! Agent found the exit!\n")
                    break
                else:
                    # Update situation for next iteration
                    current_situation = maze.get_status_description()
            else:
                print(f"   ❌ {result['message']}")
                current_situation = f"{result['message']}\n\n{maze.get_status_description()}"

        elif action['action'] == 'search_secrets':
            print(f"\n🔍 Executing: Search for secrets")

            result = maze.search_secrets()
            print(f"   {result['message']}")

            if result['found_secrets']:
                # Update situation to show newly revealed doors
                current_situation = maze.get_status_description()
            else:
                current_situation = f"No secrets found.\n\n{maze.get_status_description()}"

        else:
            print(f"⚠️  Unknown action: {action['action']}")
            current_situation = "ERROR: Unknown action. Use 'navigate' or 'search_secrets'."

    # Final results
    print(f"\n{'='*50}")
    if not maze.solved:
        print(f"❌ Agent failed to solve the maze in {max_actions} actions.")
    else:
        print(f"✅ Maze solved in {maze.action_count} action(s)!")
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


def run_agent(production_mode: bool = False, maze_number: int = 1) -> None:
    """
    Main entry point for the maze-solving agent.

    Args:
        production_mode: If True, runs in production mode (API-based).
                        If False (default), runs in debug mode (step-by-step).
        maze_number: The maze number to solve (default: 1).
    """
    if production_mode:
        run_agent_production()
    else:
        run_agent_debug(maze_number=maze_number)

