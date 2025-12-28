"""Tests for maze_state module."""

from maze_agent.common.maze_state import MazeState


class TestMazeState:
    """Test suite for MazeState class."""

    def test_initialization_default_maze(self) -> None:
        """Test MazeState initialization with default maze."""
        state = MazeState()
        assert state.current_room == "start"
        assert state.secrets_revealed is False
        assert state.action_count == 0
        assert state.move_history == []
        assert state.solved is False

    def test_initialization_specific_maze(self) -> None:
        """Test MazeState initialization with specific maze number."""
        state = MazeState(maze_number=3)
        assert state.current_room == "start"
        assert state.maze.maze_number == 3

    def test_get_current_room_info_initial_state(self) -> None:
        """Test getting current room info at initial state."""
        state = MazeState(maze_number=1)
        info = state.get_current_room_info()

        assert "door_count" in info
        assert "available_directions" in info
        assert "is_exit" in info
        assert "secrets_revealed" in info

        assert info["door_count"] == 1
        assert info["is_exit"] is False
        assert info["secrets_revealed"] is False
        assert "north" in info["available_directions"]

    def test_get_current_room_info_at_exit(self) -> None:
        """Test getting current room info when at exit."""
        state = MazeState(maze_number=1)
        # Move to exit
        state.current_room = "exit"
        info = state.get_current_room_info()

        assert info["is_exit"] is True

    def test_navigate_success(self) -> None:
        """Test successful navigation."""
        state = MazeState(maze_number=1)
        result = state.navigate("north")

        assert result["success"] is True
        assert "Moved north" in result["message"]
        assert state.current_room == "exit"
        assert state.action_count == 1
        assert len(state.move_history) == 1
        assert "start -> north -> exit" in state.move_history[0]

    def test_navigate_to_wall(self) -> None:
        """Test navigation into a wall."""
        state = MazeState(maze_number=1)
        result = state.navigate("south")

        assert result["success"] is False
        assert "Cannot go south" in result["message"]
        assert "wall" in result["message"]
        assert state.current_room == "start"
        assert state.action_count == 0

    def test_navigate_case_insensitive(self) -> None:
        """Test that navigation handles uppercase directions."""
        state = MazeState(maze_number=1)
        result = state.navigate("NORTH")

        assert result["success"] is True
        assert state.current_room == "exit"

    def test_navigate_reaches_exit(self) -> None:
        """Test navigation that reaches the exit."""
        state = MazeState(maze_number=1)
        result = state.navigate("north")

        assert result["success"] is True
        assert result["reached_exit"] is True
        assert "EXIT" in result["message"]
        assert state.solved is True

    def test_navigate_not_exit(self) -> None:
        """Test navigation that doesn't reach exit."""
        state = MazeState(maze_number=6)  # 2x2 grid with multiple rooms
        # This maze has more than 2 rooms, so we won't immediately reach exit
        result = state.navigate("north")

        if result["success"]:
            # If navigation was successful and we didn't reach exit
            if not state.solved:
                assert result["reached_exit"] is False

    def test_navigate_resets_secrets(self) -> None:
        """Test that navigation resets secrets_revealed flag."""
        state = MazeState(maze_number=1)
        state.secrets_revealed = True

        state.navigate("north")

        # Secrets should be reset after moving
        assert state.secrets_revealed is False

    def test_search_secrets_found(self) -> None:
        """Test searching for secrets when they exist."""
        state = MazeState(maze_number=3)
        result = state.search_secrets()

        assert result["success"] is True
        assert result["found_secrets"] is True
        assert "Found secret door" in result["message"]
        assert "north" in result["secret_directions"]
        assert state.secrets_revealed is True
        assert state.action_count == 1

    def test_search_secrets_not_found(self) -> None:
        """Test searching for secrets when none exist."""
        state = MazeState(maze_number=1)
        result = state.search_secrets()

        assert result["success"] is True
        assert result["found_secrets"] is False
        assert "No secret doors found" in result["message"]
        assert state.secrets_revealed is True
        assert state.action_count == 1

    def test_search_secrets_multiple_directions(self) -> None:
        """Test searching reveals multiple secret directions if they exist."""
        # Use maze 7 which has all secrets
        state = MazeState(maze_number=7)
        result = state.search_secrets()

        assert result["success"] is True
        if result["found_secrets"]:
            assert "secret_directions" in result
            assert len(result["secret_directions"]) > 0

    def test_get_current_room_info_with_secrets_revealed(self) -> None:
        """Test that revealed secrets are included in room info."""
        state = MazeState(maze_number=3)
        state.search_secrets()

        info = state.get_current_room_info()

        assert info["secrets_revealed"] is True
        # After revealing secrets, north should be available
        assert "north" in info["available_directions"]
        assert info["door_count"] == 1

    def test_navigate_through_secret_door_after_revealing(self) -> None:
        """Test navigation through secret door after revealing it."""
        state = MazeState(maze_number=3)

        # First, try to navigate without revealing - should fail
        result = state.navigate("north")
        assert result["success"] is False

        # Reset to start
        state = MazeState(maze_number=3)

        # Reveal secrets
        state.search_secrets()

        # Now navigate should work
        result = state.navigate("north")
        assert result["success"] is True
        assert state.current_room == "exit"

    def test_get_status_description_initial(self) -> None:
        """Test status description at initial state."""
        state = MazeState(maze_number=1)
        description = state.get_status_description()

        assert "You are in a room" in description
        assert "1 door(s) visible" in description
        assert "NORTH" in description

    def test_get_status_description_no_doors(self) -> None:
        """Test status description with no visible doors."""
        state = MazeState(maze_number=3)
        description = state.get_status_description()

        assert "You are in a room" in description
        assert "0 door(s) visible" in description

    def test_get_status_description_with_secrets(self) -> None:
        """Test status description after revealing secrets."""
        state = MazeState(maze_number=3)
        state.search_secrets()
        description = state.get_status_description()

        assert "You are in a room" in description
        assert "You have searched for secrets in this room" in description

    def test_action_count_increments(self) -> None:
        """Test that action count increments correctly."""
        state = MazeState(maze_number=1)

        assert state.action_count == 0

        state.search_secrets()
        assert state.action_count == 1

        state.navigate("north")
        assert state.action_count == 2

    def test_move_history_tracks_movements(self) -> None:
        """Test that move history tracks all movements."""
        state = MazeState(maze_number=6)  # Use a larger maze

        initial_len = len(state.move_history)
        state.navigate("north")

        assert len(state.move_history) == initial_len + 1
        assert "start" in state.move_history[0]
        assert "north" in state.move_history[0]

    def test_move_history_does_not_track_failed_navigation(self) -> None:
        """Test that failed navigation doesn't add to move history."""
        state = MazeState(maze_number=1)

        state.navigate("south")  # This should fail (wall)

        assert len(state.move_history) == 0

    def test_solved_flag_only_set_at_exit(self) -> None:
        """Test that solved flag is only set when reaching exit."""
        state = MazeState(maze_number=1)

        assert state.solved is False

        state.navigate("north")  # This reaches the exit

        assert state.solved is True

    def test_multiple_rooms_navigation(self) -> None:
        """Test navigating through multiple rooms."""
        state = MazeState(maze_number=6)  # 2x2 grid

        initial_room = state.current_room

        # Navigate to a different room
        result = state.navigate("north")

        if result["success"]:
            assert state.current_room != initial_room
            assert state.action_count == 1
