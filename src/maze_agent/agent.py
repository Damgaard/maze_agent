"""Core maze-solving agent logic."""

import json
from pathlib import Path

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
    """Run the agent in debug mode (manual step-by-step with status.txt/response.txt).

    This mode allows manual control over each iteration:
    1. Maintains status.txt as a living document with full history
    2. Waits for user to press Enter
    3. Reads response from response.txt
    4. Appends action and results to status.txt

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

    # STEP 0: Initialize status.txt with header and initial state
    initial_situation = maze.get_status_description()
    initial_content = f"""{"=" * 70}
MAZE SOLVING SESSION - MAZE {maze_number}
{"=" * 70}

{SYSTEM_PROMPT}

{"=" * 70}
INITIAL STATE
{"=" * 70}

{initial_situation}

{"=" * 70}
INSTRUCTIONS FOR NEXT ACTION
{"=" * 70}

What do you do?

IMPORTANT: Save your response to response.txt before printing it.
Your response should be ONLY a JSON object in this format:
{{"action": "navigate", "direction": "north"}}
or
{{"action": "search_secrets"}}

"""

    status_file.write_text(initial_content, encoding="utf-8")
    print("✓ Initialized status.txt with maze state")

    # THE AUTONOMOUS AGENT LOOP (DEBUG MODE)
    max_actions = 20
    while not maze.solved and maze.action_count < max_actions:
        print(f"\n{'=' * 50}")
        print(f"ITERATION {maze.action_count + 1}")
        print(f"{'=' * 50}")

        # STEP 1: Wait for user to press Enter
        print("\n📋 Next steps:")
        print("   1. In Claude Code CLI, run: Read @status.txt and follow instructions")
        print("   2. Claude will save its response to response.txt")
        print("   3. Press Enter here to continue...")
        input()

        # STEP 2: Read response from response.txt
        if not response_file.exists():
            print("⚠️  response.txt not found. Please ensure Claude saved the response.")
            continue

        response = response_file.read_text(encoding="utf-8").strip()

        if not response:
            print("⚠️  response.txt is empty")
            continue

        print("\n📥 Response read from response.txt")

        # STEP 3: Parse the action
        action = parse_action(response)

        if not action:
            print("⚠️  Could not parse valid action from response")

            # Append error to status.txt
            error_update = f"""
{"=" * 70}
ACTION {maze.action_count + 1}: PARSE ERROR
{"=" * 70}

Response received:
{response}

ERROR: Could not parse valid JSON action. Please respond with valid JSON.

{"=" * 70}
INSTRUCTIONS FOR NEXT ACTION
{"=" * 70}

What do you do?

IMPORTANT: Save your response to response.txt before printing it.
Your response should be ONLY a JSON object in this format:
{{"action": "navigate", "direction": "north"}}
or
{{"action": "search_secrets"}}

"""
            with status_file.open("a", encoding="utf-8") as f:
                f.write(error_update)

            continue

        print(f"🎯 Parsed action: {json.dumps(action, indent=2)}")

        # STEP 4: Execute the action and update state
        action_description = ""
        result_message = ""

        if action["action"] == "navigate":
            direction = action.get("direction", "unknown")
            action_description = f"Navigate {direction.upper()}"
            print(f"\n✓ Executing: {action_description}")

            result = maze.navigate(direction)
            result_message = result["message"]

            if result["success"]:
                print(f"   {result['message']}")
                if result.get("reached_exit", False):
                    print("🎉 MAZE SOLVED! Agent found the exit!\n")

                    # Append final success to status.txt
                    final_update = f"""
{"=" * 70}
ACTION {maze.action_count}: {action_description}
{"=" * 70}

Decision: {json.dumps(action, indent=2)}

Result: {result_message}

{"=" * 70}
MAZE SOLVED!
{"=" * 70}

Total actions: {maze.action_count}
"""
                    with status_file.open("a", encoding="utf-8") as f:
                        f.write(final_update)

                    break

            else:
                print(f"   ❌ {result['message']}")

        elif action["action"] == "search_secrets":
            action_description = "Search for secrets"
            print(f"\n🔍 Executing: {action_description}")

            result = maze.search_secrets()
            result_message = result["message"]
            print(f"   {result['message']}")

        else:
            print(f"⚠️  Unknown action: {action['action']}")
            action_description = f"Unknown action: {action['action']}"
            result_message = "ERROR: Unknown action. Use 'navigate' or 'search_secrets'."

        # STEP 5: Append to status.txt with action result and new state
        new_situation = maze.get_status_description()

        update_content = f"""
{"=" * 70}
ACTION {maze.action_count}: {action_description}
{"=" * 70}

Decision: {json.dumps(action, indent=2)}

Result: {result_message}

{"=" * 70}
CURRENT STATE
{"=" * 70}

{new_situation}

{"=" * 70}
INSTRUCTIONS FOR NEXT ACTION
{"=" * 70}

What do you do?

IMPORTANT: Save your response to response.txt before printing it.
Your response should be ONLY a JSON object in this format:
{{"action": "navigate", "direction": "north"}}
or
{{"action": "search_secrets"}}

"""

        with status_file.open("a", encoding="utf-8") as f:
            f.write(update_content)

        print("✓ Updated status.txt with action result")

    # Final results
    print(f"\n{'=' * 50}")
    if not maze.solved:
        print(f"❌ Agent failed to solve the maze in {max_actions} actions.")

        # Append failure to status.txt
        failure_update = f"""
{"=" * 70}
SESSION ENDED - FAILED
{"=" * 70}

Failed to solve maze in {max_actions} actions.
"""
        with status_file.open("a", encoding="utf-8") as f:
            f.write(failure_update)
    else:
        print(f"✅ Maze solved in {maze.action_count} action(s)!")
    print(f"{'=' * 50}\n")


def run_agent_production() -> None:
    """Run the agent in production mode (API-based).

    This mode uses direct API calls for autonomous operation.

    """
    raise NotImplementedError("Production mode is not yet implemented. Run in debug mode (default) for now.")


def run_agent(production_mode: bool = False, maze_number: int = 1) -> None:
    """Run the maze-solving agent.

    Args:
        production_mode: If True, runs in production mode (API-based).
                        If False (default), runs in debug mode (step-by-step).
        maze_number: The maze number to solve (default: 1).

    """
    if production_mode:
        run_agent_production()
    else:
        run_agent_debug(maze_number=maze_number)
