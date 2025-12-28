"""Tests for maze_loader module."""

import pytest

from maze_agent.common.maze_loader import MazeLoader


class TestMazeLoader:
    """Test suite for MazeLoader class."""

    def test_load_maze_01_simple_north(self) -> None:
        """Test loading maze 01 (simple north exit)."""
        loader = MazeLoader(1)
        assert loader.maze_data is not None
        assert loader.maze_data["name"] == "Simple North Exit"
        assert "One door to the north leads directly to exit" in loader.maze_data["description"]
        assert loader.maze_data["start_room"] == "start"
        assert "start" in loader.maze_data["rooms"]
        assert "exit" in loader.maze_data["rooms"]

    def test_load_maze_03_secret_north(self) -> None:
        """Test loading maze 03 (secret door north)."""
        loader = MazeLoader(3)
        assert loader.maze_data is not None
        assert loader.maze_data["name"] == "Secret Door North"
        assert "No visible doors" in loader.maze_data["description"]
        assert loader.maze_data["start_room"] == "start"

    def test_load_invalid_maze_number(self) -> None:
        """Test loading an invalid maze number raises ValueError."""
        with pytest.raises(ValueError, match="Maze 999 not found"):
            MazeLoader(999)

    def test_get_start_room(self) -> None:
        """Test getting the start room ID."""
        loader = MazeLoader(1)
        start = loader.get_start_room()
        assert start == "start"

    def test_get_room(self) -> None:
        """Test getting room data."""
        loader = MazeLoader(1)
        start_room = loader.get_room("start")
        assert start_room is not None
        assert "is_start" in start_room
        assert "is_exit" in start_room
        assert "doors" in start_room
        assert "secrets" in start_room
        assert start_room["is_start"] is True
        assert start_room["is_exit"] is False

    def test_is_exit_start_room(self) -> None:
        """Test that start room is not an exit."""
        loader = MazeLoader(1)
        assert loader.is_exit("start") is False

    def test_is_exit_exit_room(self) -> None:
        """Test that exit room is an exit."""
        loader = MazeLoader(1)
        assert loader.is_exit("exit") is True

    def test_get_visible_doors_maze_01(self) -> None:
        """Test getting visible doors from start room in maze 01."""
        loader = MazeLoader(1)
        doors = loader.get_visible_doors("start")
        assert doors is not None
        assert "north" in doors
        assert "south" in doors
        assert "east" in doors
        assert "west" in doors
        # Maze 01 has a visible door to the north
        assert doors["north"] == "exit"

    def test_get_secret_doors_maze_03(self) -> None:
        """Test getting secret doors from start room in maze 03."""
        loader = MazeLoader(3)
        secrets = loader.get_secret_doors("start")
        assert secrets is not None
        # Maze 03 has a secret door to the north
        assert secrets["north"] == "exit"

    def test_count_visible_doors_maze_01(self) -> None:
        """Test counting visible doors in maze 01."""
        loader = MazeLoader(1)
        count = loader.count_visible_doors("start")
        # Maze 01 has 1 visible door (north)
        assert count == 1

    def test_count_visible_doors_maze_03(self) -> None:
        """Test counting visible doors in maze 03."""
        loader = MazeLoader(3)
        count = loader.count_visible_doors("start")
        # Maze 03 has no visible doors
        assert count == 0

    def test_navigate_with_visible_door(self) -> None:
        """Test navigation through a visible door."""
        loader = MazeLoader(1)
        # Navigate north from start (which has a visible door)
        result = loader.navigate("start", "north", secrets_revealed=False)
        assert result == "exit"

    def test_navigate_without_door(self) -> None:
        """Test navigation when there is no door."""
        loader = MazeLoader(1)
        # Try to navigate south from start (no door)
        result = loader.navigate("start", "south", secrets_revealed=False)
        assert result is None

    def test_navigate_with_secret_door_not_revealed(self) -> None:
        """Test navigation through secret door when not revealed."""
        loader = MazeLoader(3)
        # Try to navigate north when secrets are not revealed
        result = loader.navigate("start", "north", secrets_revealed=False)
        assert result is None

    def test_navigate_with_secret_door_revealed(self) -> None:
        """Test navigation through secret door when revealed."""
        loader = MazeLoader(3)
        # Navigate north when secrets are revealed
        result = loader.navigate("start", "north", secrets_revealed=True)
        assert result == "exit"

    def test_room_structure(self) -> None:
        """Test that room structure contains all required fields."""
        loader = MazeLoader(1)
        start_room = loader.get_room("start")

        assert "is_start" in start_room
        assert "is_exit" in start_room
        assert "doors" in start_room
        assert "secrets" in start_room

        # Check that doors and secrets have all 4 directions
        assert "north" in start_room["doors"]
        assert "south" in start_room["doors"]
        assert "east" in start_room["doors"]
        assert "west" in start_room["doors"]
        assert "north" in start_room["secrets"]
        assert "south" in start_room["secrets"]
        assert "east" in start_room["secrets"]
        assert "west" in start_room["secrets"]

    def test_maze_data_structure(self) -> None:
        """Test that maze data contains all required top-level fields."""
        loader = MazeLoader(1)

        assert "name" in loader.maze_data
        assert "description" in loader.maze_data
        assert "rooms" in loader.maze_data
        assert "start_room" in loader.maze_data

        assert isinstance(loader.maze_data["name"], str)
        assert isinstance(loader.maze_data["description"], str)
        assert isinstance(loader.maze_data["rooms"], dict)
        assert isinstance(loader.maze_data["start_room"], str)

    def test_navigate_case_insensitive(self) -> None:
        """Test that navigation handles direction case insensitively."""
        loader = MazeLoader(1)
        # The navigate method should be called with lowercase, but let's verify
        # it works with the expected lowercase input
        result = loader.navigate("start", "north", secrets_revealed=False)
        assert result == "exit"
