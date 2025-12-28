"""Maze state management for tracking player progress."""

from typing import Any

from maze_agent.common.maze_loader import MazeLoader


class MazeState:
    """Manages the current state of the maze game."""

    def __init__(self, maze_number: int = 1) -> None:
        """Initialize maze state.

        Args:
            maze_number: The maze to load

        """
        self.maze = MazeLoader(maze_number)
        self.current_room = self.maze.get_start_room()
        self.secrets_revealed = False  # Secrets in current room revealed
        self.action_count = 0
        self.move_history: list[str] = []
        self.solved = False

    def get_current_room_info(self) -> dict[str, Any]:
        """Get information about the current room visible to the player.

        Returns:
            Dictionary with visible room information

        """
        room = self.maze.get_room(self.current_room)
        visible_doors = self.maze.get_visible_doors(self.current_room)

        # Count visible doors
        door_count = self.maze.count_visible_doors(self.current_room)

        # List available directions
        available_directions = []
        for direction, destination in visible_doors.items():
            if destination is not None:
                available_directions.append(direction)

        # Add secret doors if revealed
        if self.secrets_revealed:
            secret_doors = self.maze.get_secret_doors(self.current_room)
            for direction, destination in secret_doors.items():
                if destination is not None and direction not in available_directions:
                    available_directions.append(direction)
                    door_count += 1

        return {
            "door_count": door_count,
            "available_directions": available_directions,
            "is_exit": room["is_exit"],
            "secrets_revealed": self.secrets_revealed,
        }

    def navigate(self, direction: str) -> dict[str, Any]:
        """Attempt to navigate in a direction.

        Args:
            direction: Direction to move (north, south, east, west)

        Returns:
            Result dictionary with success status and message

        """
        direction = direction.lower()

        # Attempt navigation
        new_room = self.maze.navigate(self.current_room, direction, self.secrets_revealed)

        if new_room is None:
            return {"success": False, "message": f"Cannot go {direction}. There is a wall in that direction."}

        # Move successful
        old_room = self.current_room
        self.current_room = new_room
        self.secrets_revealed = False  # Reset secrets for new room
        self.action_count += 1
        self.move_history.append(f"{old_room} -> {direction} -> {new_room}")

        # Check if we reached the exit
        if self.maze.is_exit(new_room):
            self.solved = True
            return {"success": True, "message": f"Moved {direction}. You found the EXIT!", "reached_exit": True}

        return {"success": True, "message": f"Moved {direction} to a new room.", "reached_exit": False}

    def search_secrets(self) -> dict[str, Any]:
        """Search for secret doors in the current room.

        Returns:
            Result dictionary with success status and message

        """
        secret_doors = self.maze.get_secret_doors(self.current_room)
        has_secrets = any(dest is not None for dest in secret_doors.values())

        self.secrets_revealed = True
        self.action_count += 1

        if has_secrets:
            # Find which directions have secrets
            secret_directions = [direction for direction, dest in secret_doors.items() if dest is not None]
            return {
                "success": True,
                "found_secrets": True,
                "message": f"Found secret door(s) to the: {', '.join(secret_directions)}!",
                "secret_directions": secret_directions,
            }

        return {"success": True, "found_secrets": False, "message": "No secret doors found in this room."}

    def get_status_description(self) -> str:
        """Generate a description of the current game state for the player.

        Returns:
            Human-readable status description showing only visible information

        """
        room_info = self.get_current_room_info()

        # Build status message
        status_lines = []
        status_lines.append("You are in a room.")
        status_lines.append(f"There are {room_info['door_count']} door(s) visible.")

        if room_info["available_directions"]:
            directions_str = ", ".join(room_info["available_directions"]).upper()
            status_lines.append(f"You can see doors to the: {directions_str}")

        if room_info["secrets_revealed"]:
            status_lines.append("(You have searched for secrets in this room)")

        return "\n".join(status_lines)
