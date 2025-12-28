#!/usr/bin/env python3
"""Command-line entry point for the maze agent."""

import argparse
from maze_agent.agent import run_agent


def main() -> None:
    """Run the maze-solving agent."""
    parser = argparse.ArgumentParser(description="Autonomous maze-solving agent")
    parser.add_argument(
        "--prod",
        action="store_true",
        help="Run in production mode (uses API calls)"
    )

    args = parser.parse_args()

    # Run the agent with the selected mode
    run_agent(production_mode=args.prod)


if __name__ == "__main__":
    main()

