#!/usr/bin/env python3
"""Command-line entry point for the maze agent."""

import argparse

from maze_agent.agent import run_agent


def main() -> None:
    """Run the maze-solving agent."""
    parser = argparse.ArgumentParser(description="Autonomous maze-solving agent")
    parser.add_argument("--prod", action="store_true", help="Run in production mode (uses API calls)")
    parser.add_argument("--maze", type=int, default=1, help="Maze number to solve (default: 1)")

    args = parser.parse_args()

    # Run the agent with the selected mode and maze
    run_agent(production_mode=args.prod, maze_number=args.maze)


if __name__ == "__main__":
    main()
