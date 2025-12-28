#!/usr/bin/env python3
"""CLI command to list all available mazes."""

import re
from pathlib import Path
from typing import List, Dict, Any


def parse_maze_header(maze_file: Path) -> Dict[str, Any]:
    """
    Parse the header of a maze file to extract metadata.

    Args:
        maze_file: Path to the maze file

    Returns:
        Dictionary with maze metadata (number, name, description)
    """
    try:
        content = maze_file.read_text(encoding="utf-8")
        lines = content.split("\n")

        # Extract maze number from filename (XX_name.txt)
        filename = maze_file.name
        match = re.match(r"(\d+)_", filename)
        if not match:
            return None

        maze_number = int(match.group(1))

        # Parse header line: === MAZE XX: Name ===
        header_line = lines[0].strip() if lines else ""
        name_match = re.search(r"MAZE \d+:\s*(.+?)\s*===", header_line)
        maze_name = name_match.group(1) if name_match else "Unknown"

        # Description is usually on the second line
        description = lines[1].strip() if len(lines) > 1 else ""

        return {"number": maze_number, "name": maze_name, "description": description, "filename": filename}

    except Exception as e:
        print(f"Error parsing {maze_file}: {e}")
        return None


def list_mazes() -> None:
    """List all available mazes with their descriptions."""
    # Find the mazes directory
    # Assuming this is run from the project root
    mazes_dir = Path("mazes")

    if not mazes_dir.exists():
        print("Error: mazes directory not found.")
        print(f"Expected location: {mazes_dir.absolute()}")
        return

    # Find all maze files
    maze_files = list(mazes_dir.glob("*.txt"))

    if not maze_files:
        print("No maze files found in the mazes directory.")
        return

    # Parse all maze files
    mazes = []
    for maze_file in maze_files:
        maze_info = parse_maze_header(maze_file)
        if maze_info:
            mazes.append(maze_info)

    # Sort by maze number
    mazes.sort(key=lambda m: m["number"])

    # Display the list
    print("=" * 70)
    print("AVAILABLE MAZES")
    print("=" * 70)
    print()

    for maze in mazes:
        print(f"Maze {maze['number']:2d}: {maze['name']}")
        print(f"         {maze['description']}")
        print()

    print("=" * 70)
    print(f"Total: {len(mazes)} maze(s)")
    print()
    print("Usage: uv run solve --maze <number>")
    print("Example: uv run solve --maze 3")
    print("=" * 70)


def main() -> None:
    """Main entry point for the maze-list command."""
    list_mazes()


if __name__ == "__main__":
    main()
