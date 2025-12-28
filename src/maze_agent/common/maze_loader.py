"""Maze loader and parser for maze files."""

from pathlib import Path
from typing import Dict, Any, Optional


class MazeLoader:
    """Loads and manages maze configurations."""

    def __init__(self, maze_number: int = 1):
        """
        Initialize maze loader.

        Args:
            maze_number: The maze number to load (e.g., 1 for 01_*.txt)
        """
        self.maze_number = maze_number
        self.maze_data = self._load_maze(maze_number)

    def _load_maze(self, maze_number: int) -> Dict[str, Any]:
        """
        Load maze configuration by number.

        For now, this uses hardcoded maze structures based on the visual files.
        Future enhancement: Parse the .txt files directly.

        Args:
            maze_number: The maze to load

        Returns:
            Maze configuration dictionary
        """
        # Maze definitions based on mazes/*.txt files
        mazes = {
            1: {
                'name': 'Simple North Exit',
                'description': 'One door to the north leads directly to exit.',
                'rooms': {
                    'start': {
                        'is_start': True,
                        'is_exit': False,
                        'doors': {'north': 'exit', 'south': None, 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    },
                    'exit': {
                        'is_start': False,
                        'is_exit': True,
                        'doors': {'north': None, 'south': 'start', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    }
                },
                'start_room': 'start'
            },
            2: {
                'name': 'Corridor to North',
                'description': 'Door north leads to middle room with north/south doors.',
                'rooms': {
                    'start': {
                        'is_start': True,
                        'is_exit': False,
                        'doors': {'north': 'middle', 'south': None, 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    },
                    'middle': {
                        'is_start': False,
                        'is_exit': False,
                        'doors': {'north': 'exit', 'south': 'start', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    },
                    'exit': {
                        'is_start': False,
                        'is_exit': True,
                        'doors': {'north': None, 'south': 'middle', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    }
                },
                'start_room': 'start'
            },
            3: {
                'name': 'Secret Door North',
                'description': 'No visible doors. Secret door north leads to exit.',
                'rooms': {
                    'start': {
                        'is_start': True,
                        'is_exit': False,
                        'doors': {'north': None, 'south': None, 'east': None, 'west': None},
                        'secrets': {'north': 'exit', 'south': None, 'east': None, 'west': None}
                    },
                    'exit': {
                        'is_start': False,
                        'is_exit': True,
                        'doors': {'north': None, 'south': 'start', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    }
                },
                'start_room': 'start'
            },
            4: {
                'name': 'Simple South Exit',
                'description': 'One door to the south leads directly to exit.',
                'rooms': {
                    'start': {
                        'is_start': True,
                        'is_exit': False,
                        'doors': {'north': None, 'south': 'exit', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    },
                    'exit': {
                        'is_start': False,
                        'is_exit': True,
                        'doors': {'north': 'start', 'south': None, 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    }
                },
                'start_room': 'start'
            },
            5: {
                'name': 'Secret vs Dead End',
                'description': 'Door south leads to dead end. Secret north leads to exit.',
                'rooms': {
                    'start': {
                        'is_start': True,
                        'is_exit': False,
                        'doors': {'north': None, 'south': 'deadend', 'east': None, 'west': None},
                        'secrets': {'north': 'exit', 'south': None, 'east': None, 'west': None}
                    },
                    'deadend': {
                        'is_start': False,
                        'is_exit': False,
                        'doors': {'north': 'start', 'south': None, 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    },
                    'exit': {
                        'is_start': False,
                        'is_exit': True,
                        'doors': {'north': None, 'south': 'start', 'east': None, 'west': None},
                        'secrets': {'north': None, 'south': None, 'east': None, 'west': None}
                    }
                },
                'start_room': 'start'
            }
        }

        if maze_number not in mazes:
            raise ValueError(f"Maze {maze_number} not found. Available: {list(mazes.keys())}")

        return mazes[maze_number]

    def get_start_room(self) -> str:
        """Get the starting room ID."""
        return self.maze_data['start_room']

    def get_room(self, room_id: str) -> Dict[str, Any]:
        """Get room data by ID."""
        return self.maze_data['rooms'][room_id]

    def is_exit(self, room_id: str) -> bool:
        """Check if a room is the exit."""
        return self.maze_data['rooms'][room_id]['is_exit']

    def get_visible_doors(self, room_id: str) -> Dict[str, Optional[str]]:
        """Get visible doors from a room (not including undiscovered secrets)."""
        return self.maze_data['rooms'][room_id]['doors']

    def get_secret_doors(self, room_id: str) -> Dict[str, Optional[str]]:
        """Get secret doors from a room."""
        return self.maze_data['rooms'][room_id]['secrets']

    def count_visible_doors(self, room_id: str) -> int:
        """Count the number of visible doors in a room."""
        doors = self.get_visible_doors(room_id)
        return sum(1 for dest in doors.values() if dest is not None)

    def navigate(self, current_room: str, direction: str, secrets_revealed: bool = False) -> Optional[str]:
        """
        Attempt to navigate in a direction from current room.

        Args:
            current_room: Current room ID
            direction: Direction to move (north, south, east, west)
            secrets_revealed: Whether secrets have been revealed in this room

        Returns:
            New room ID if movement successful, None otherwise
        """
        room = self.get_room(current_room)

        # Check visible doors first
        destination = room['doors'].get(direction)
        if destination:
            return destination

        # Check secret doors if revealed
        if secrets_revealed:
            destination = room['secrets'].get(direction)
            if destination:
                return destination

        return None
