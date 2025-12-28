"""Maze loader and parser for maze files."""

from pathlib import Path
from typing import Any


class MazeLoader:
    """Loads and manages maze configurations."""

    def __init__(self, maze_number: int = 1) -> None:
        """Initialize maze loader.

        Args:
            maze_number: The maze number to load (e.g., 1 for 01_*.txt)

        """
        self.maze_number = maze_number
        self.maze_data = self._load_maze(maze_number)

    def _find_maze_file(self, maze_number: int) -> Path:
        """Find the maze file for the given number.

        Args:
            maze_number: The maze number to find

        Returns:
            Path to the maze file

        Raises:
            ValueError: If maze file not found

        """
        # Get the project root (assuming this file is in src/maze_agent/common/)
        current_file = Path(__file__)
        project_root = current_file.parent.parent.parent.parent
        mazes_dir = project_root / "mazes"

        # Find file matching pattern XX_*.txt
        pattern = f"{maze_number:02d}_*.txt"
        matches = list(mazes_dir.glob(pattern))

        if not matches:
            raise ValueError(f"Maze {maze_number} not found in {mazes_dir}")

        return matches[0]

    def _parse_maze_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a maze file and build the maze structure.

        Args:
            file_path: Path to the maze file

        Returns:
            Maze configuration dictionary

        """
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        # Parse header
        header_line = lines[0].strip()
        # Extract name from "=== MAZE XX: Name ==="
        name = header_line.split(":", 1)[1].strip().rstrip("=").strip()

        # Extract description (lines until empty line)
        description_lines = []
        for i in range(1, len(lines)):
            line = lines[i].rstrip()
            if not line:
                break
            description_lines.append(line)
        description = " ".join(description_lines)

        # Find grid start (first line after header with #)
        grid_start = 0
        for i in range(len(lines)):
            if "#" in lines[i]:
                grid_start = i
                break

        # Parse the grid
        grid_lines = [line.rstrip() for line in lines[grid_start:] if line.strip()]

        # Pad all lines to same length for easier processing
        max_len = max(len(line) for line in grid_lines) if grid_lines else 0
        grid_lines = [line.ljust(max_len) for line in grid_lines]

        # Find all rooms by looking for room top-left corners (##### pattern)
        # Rooms are 5x5, separated by 1-row/col gaps, so they appear every 6 rows/cols
        rooms_by_coord = {}  # (room_row, room_col) -> room_info
        room_counter = 0

        # Scan for room starting positions (top-left #)
        for row_idx in range(0, len(grid_lines), 6):  # Rooms start every 6 rows
            for col_idx in range(0, max_len, 6):  # Rooms start every 6 cols
                # Check if there's a room here by looking for ##### pattern
                if row_idx + 4 < len(grid_lines) and col_idx + 4 < max_len:
                    # Check for top wall #####
                    top_wall = grid_lines[row_idx][col_idx : col_idx + 5]
                    if top_wall == "#####":
                        # Found a room! The center is at row+2, col+2
                        center_row = row_idx + 2
                        center_col = col_idx + 2
                        center_char = grid_lines[center_row][center_col]

                        # Determine room type
                        room_row = row_idx // 6
                        room_col = col_idx // 6

                        if center_char == "S":
                            room_id = "start"
                            is_start = True
                            is_exit = False
                        elif center_char == "E":
                            room_id = "exit"
                            is_start = False
                            is_exit = True
                        else:
                            # Generic room (no special marker)
                            room_id = f"room_{room_counter}"
                            room_counter += 1
                            is_start = False
                            is_exit = False

                        rooms_by_coord[(room_row, room_col)] = {
                            "id": room_id,
                            "is_start": is_start,
                            "is_exit": is_exit,
                            "marker_pos": (center_row, center_col),
                        }

        # Build room connections by checking for D and X between rooms
        rooms = {}
        for coord, room_info in rooms_by_coord.items():
            room_id = room_info["id"]
            rooms[room_id] = {
                "is_start": room_info["is_start"],
                "is_exit": room_info["is_exit"],
                "doors": {"north": None, "south": None, "east": None, "west": None},
                "secrets": {"north": None, "south": None, "east": None, "west": None},
            }

        # Now find connections
        for coord, room_info in rooms_by_coord.items():
            room_row, room_col = coord
            room_id = room_info["id"]
            marker_row, marker_col = room_info["marker_pos"]

            # Check north (row above, same column)
            north_coord = (room_row - 1, room_col)
            if north_coord in rooms_by_coord:
                # Check the connection row (between the two rooms)
                # The connection is 1 row above the current room's top wall
                conn_row = marker_row - 3  # 2 up to top of room, 1 more to connection
                conn_col = marker_col  # Same column as marker (center)
                if 0 <= conn_row < len(grid_lines) and 0 <= conn_col < len(grid_lines[conn_row]):
                    conn_char = grid_lines[conn_row][conn_col]
                    if conn_char == "D":
                        rooms[room_id]["doors"]["north"] = rooms_by_coord[north_coord]["id"]
                    elif conn_char == "X":
                        rooms[room_id]["secrets"]["north"] = rooms_by_coord[north_coord]["id"]

            # Check south
            south_coord = (room_row + 1, room_col)
            if south_coord in rooms_by_coord:
                conn_row = marker_row + 3
                conn_col = marker_col
                if 0 <= conn_row < len(grid_lines) and 0 <= conn_col < len(grid_lines[conn_row]):
                    conn_char = grid_lines[conn_row][conn_col]
                    if conn_char == "D":
                        rooms[room_id]["doors"]["south"] = rooms_by_coord[south_coord]["id"]
                    elif conn_char == "X":
                        rooms[room_id]["secrets"]["south"] = rooms_by_coord[south_coord]["id"]

            # Check east (same row, column to the right)
            east_coord = (room_row, room_col + 1)
            if east_coord in rooms_by_coord:
                conn_row = marker_row
                conn_col = marker_col + 3
                if 0 <= conn_row < len(grid_lines) and 0 <= conn_col < len(grid_lines[conn_row]):
                    conn_char = grid_lines[conn_row][conn_col]
                    if conn_char == "D":
                        rooms[room_id]["doors"]["east"] = rooms_by_coord[east_coord]["id"]
                    elif conn_char == "X":
                        rooms[room_id]["secrets"]["east"] = rooms_by_coord[east_coord]["id"]

            # Check west
            west_coord = (room_row, room_col - 1)
            if west_coord in rooms_by_coord:
                conn_row = marker_row
                conn_col = marker_col - 3
                if 0 <= conn_row < len(grid_lines) and 0 <= conn_col < len(grid_lines[conn_row]):
                    conn_char = grid_lines[conn_row][conn_col]
                    if conn_char == "D":
                        rooms[room_id]["doors"]["west"] = rooms_by_coord[west_coord]["id"]
                    elif conn_char == "X":
                        rooms[room_id]["secrets"]["west"] = rooms_by_coord[west_coord]["id"]

        # Find start room
        start_room = None
        for room_id, room_data in rooms.items():
            if room_data["is_start"]:
                start_room = room_id
                break

        return {
            "name": name,
            "description": description,
            "rooms": rooms,
            "start_room": start_room,
        }

    def _load_maze(self, maze_number: int) -> dict[str, Any]:
        """Load maze configuration by number.

        Args:
            maze_number: The maze to load

        Returns:
            Maze configuration dictionary

        """
        maze_file = self._find_maze_file(maze_number)
        return self._parse_maze_file(maze_file)

    def get_start_room(self) -> str:
        """Get the starting room ID."""
        return self.maze_data["start_room"]

    def get_room(self, room_id: str) -> dict[str, Any]:
        """Get room data by ID."""
        return self.maze_data["rooms"][room_id]

    def is_exit(self, room_id: str) -> bool:
        """Check if a room is the exit."""
        return self.maze_data["rooms"][room_id]["is_exit"]

    def get_visible_doors(self, room_id: str) -> dict[str, str | None]:
        """Get visible doors from a room (not including undiscovered secrets)."""
        return self.maze_data["rooms"][room_id]["doors"]

    def get_secret_doors(self, room_id: str) -> dict[str, str | None]:
        """Get secret doors from a room."""
        return self.maze_data["rooms"][room_id]["secrets"]

    def count_visible_doors(self, room_id: str) -> int:
        """Count the number of visible doors in a room."""
        doors = self.get_visible_doors(room_id)
        return sum(1 for dest in doors.values() if dest is not None)

    def navigate(self, current_room: str, direction: str, secrets_revealed: bool = False) -> str | None:
        """Attempt to navigate in a direction from current room.

        Args:
            current_room: Current room ID
            direction: Direction to move (north, south, east, west)
            secrets_revealed: Whether secrets have been revealed in this room

        Returns:
            New room ID if movement successful, None otherwise

        """
        room = self.get_room(current_room)

        # Check visible doors first
        destination = room["doors"].get(direction)
        if destination:
            return destination

        # Check secret doors if revealed
        if secrets_revealed:
            destination = room["secrets"].get(direction)
            if destination:
                return destination

        return None
