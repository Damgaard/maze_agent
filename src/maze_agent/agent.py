"""Core maze-solving agent logic."""

import json
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


def run_agent() -> None:
    """
    Main autonomous agent loop.

    Runs the maze-solving agent until the maze is solved or the maximum
    number of actions is reached.
    """
    print("=== AUTONOMOUS MAZE SOLVING AGENT ===")
    print("Using Claude Code via subprocess\n")
    print("=" * 50)
    print(f"\n{INITIAL_DESCRIPTION}\n")
    
    current_prompt = INITIAL_DESCRIPTION
    
    # THE AUTONOMOUS AGENT LOOP
    while not maze_state['solved'] and maze_state['action_count'] < 10:
        print(f"\n{'='*50}")
        print(f"ITERATION {maze_state['action_count'] + 1}")
        print(f"{'='*50}")
        
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
            current_prompt = "Please respond with a valid JSON action: {\"action\": \"navigate\", \"direction\": \"north\"} or {\"action\": \"search_secrets\"}"
            maze_state['action_count'] += 1
            continue
        
        print(f"🎯 Parsed action: {json.dumps(action, indent=2)}")
        
        # STEP 3: Execute the action
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

