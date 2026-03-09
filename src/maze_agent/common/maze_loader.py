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

    def _parse_header_and_description(self, lines: list[str]) -> tuple[str, str]:
        """Parse maze header and description from file lines.

        Args:
            lines: The file lines

        Returns:
            Tuple of (name, description)

        """
        header_line = lines[0].strip()
        name = header_line.split(":", 1)[1].strip().rstrip("=").strip()

        description_lines = []
        for i in range(1, len(lines)):
            line = lines[i].rstrip()
            if not line:
                break
            description_lines.append(line)
        description = " ".join(description_lines)

        return name, description

    def _scan_grid_for_rooms(self, grid_lines: list[str], max_len: int) -> dict[tuple[int, int], dict]:
        """Scan grid and find all rooms.

        Args:
            grid_lines: The grid lines
            max_len: Maximum line length

        Returns:
            Dictionary mapping room coordinates to room info

        """
        rooms_by_coord = {}
        room_counter = 0

        for row_idx in range(0, len(grid_lines), 6):
            for col_idx in range(0, max_len, 6):
                if row_idx + 4 < len(grid_lines) and col_idx + 4 < max_len:
                    top_wall = grid_lines[row_idx][col_idx : col_idx + 5]
                    if top_wall == "#####":
                        center_row = row_idx + 2
                        center_col = col_idx + 2
                        center_char = grid_lines[center_row][center_col]
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

        return rooms_by_coord

    def _check_connection(
        self,
        grid_lines: list[str],
        marker_row: int,
        marker_col: int,
        conn_row_offset: int,
        conn_col_offset: int,
    ) -> str | None:
        """Check for connection character (D or X) at a specific offset.

        Args:
            grid_lines: The grid lines
            marker_row: The marker row
            marker_col: The marker column
            conn_row_offset: Row offset from marker
            conn_col_offset: Column offset from marker

        Returns:
            'D' for door, 'X' for secret, None for no connection

        """
        conn_row = marker_row + conn_row_offset
        conn_col = marker_col + conn_col_offset

        if 0 <= conn_row < len(grid_lines) and 0 <= conn_col < len(grid_lines[conn_row]):
            conn_char = grid_lines[conn_row][conn_col]
            if conn_char in ("D", "X"):
                return conn_char

        return None

    def _build_room_connections(self, rooms_by_coord: dict, grid_lines: list[str], rooms: dict) -> None:
        """Build connections between rooms.

        Args:
            rooms_by_coord: Mapping of room coordinates
            grid_lines: The grid lines
            rooms: The rooms dictionary to update

        """
        for coord, room_info in rooms_by_coord.items():
            room_row, room_col = coord
            room_id = room_info["id"]
            marker_row, marker_col = room_info["marker_pos"]

            # Check all four directions
            directions = [
                ("north", -1, 0, -3, 0),
                ("south", 1, 0, 3, 0),
                ("east", 0, 1, 0, 3),
                ("west", 0, -1, 0, -3),
            ]

            for direction, coord_row_offset, coord_col_offset, conn_row_offset, conn_col_offset in directions:
                neighbor_coord = (room_row + coord_row_offset, room_col + coord_col_offset)
                if neighbor_coord in rooms_by_coord:
                    conn_char = self._check_connection(
                        grid_lines,
                        marker_row,
                        marker_col,
                        conn_row_offset,
                        conn_col_offset,
                    )
                    if conn_char == "D":
                        rooms[room_id]["doors"][direction] = rooms_by_coord[neighbor_coord]["id"]
                    elif conn_char == "X":
                        rooms[room_id]["secrets"][direction] = rooms_by_coord[neighbor_coord]["id"]

    def _parse_maze_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a maze file and build the maze structure.

        Args:
            file_path: Path to the maze file

        Returns:
            Maze configuration dictionary

        """
        with file_path.open("r", encoding="utf-8") as f:
            lines = f.readlines()

        name, description = self._parse_header_and_description(lines)

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

        # Find all rooms
        rooms_by_coord = self._scan_grid_for_rooms(grid_lines, max_len)

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

        self._build_room_connections(rooms_by_coord, grid_lines, rooms)

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
