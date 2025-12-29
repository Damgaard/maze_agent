"""Tests for action_parser module."""

from maze_agent.common.action_parser import parse_action


class TestParseAction:
    """Test suite for parse_action function."""

    def test_parse_action_with_valid_json_navigate_north(self) -> None:
        """Test parsing valid JSON for navigate north action."""
        response = '{"action": "navigate", "direction": "north"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "north"

    def test_parse_action_with_valid_json_navigate_south(self) -> None:
        """Test parsing valid JSON for navigate south action."""
        response = '{"action": "navigate", "direction": "south"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "south"

    def test_parse_action_with_valid_json_navigate_east(self) -> None:
        """Test parsing valid JSON for navigate east action."""
        response = '{"action": "navigate", "direction": "east"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "east"

    def test_parse_action_with_valid_json_navigate_west(self) -> None:
        """Test parsing valid JSON for navigate west action."""
        response = '{"action": "navigate", "direction": "west"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "west"

    def test_parse_action_with_valid_json_search_secrets(self) -> None:
        """Test parsing valid JSON for search_secrets action."""
        response = '{"action": "search_secrets"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "search_secrets"

    def test_parse_action_with_json_in_markdown(self) -> None:
        """Test parsing JSON embedded in markdown text."""
        response = """Here's my decision:

{"action": "navigate", "direction": "north"}

I'm going north because it seems like the best option."""
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "north"

    def test_parse_action_with_surrounding_text(self) -> None:
        """Test parsing JSON with surrounding text."""
        response = 'I will navigate north. {"action": "navigate", "direction": "north"} This is the way.'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "north"

    def test_parse_action_no_json_returns_none(self) -> None:
        """Test that responses without JSON return None."""
        response = "I will navigate north to explore the room."
        result = parse_action(response)
        assert result is None

    def test_parse_action_natural_language_not_supported(self) -> None:
        """Test that natural language without JSON is not parsed."""
        response = "I will search for secret doors in this room."
        result = parse_action(response)
        assert result is None

    def test_parse_action_invalid_json(self) -> None:
        """Test parsing with invalid JSON that cannot be recovered."""
        response = '{"action": "invalid"'
        result = parse_action(response)
        # Should return None since there's no valid JSON and no fallback keywords
        assert result is None

    def test_parse_action_no_recognizable_action(self) -> None:
        """Test parsing with no recognizable action."""
        response = "I don't know what to do."
        result = parse_action(response)
        assert result is None

    def test_parse_action_empty_string(self) -> None:
        """Test parsing with empty string."""
        response = ""
        result = parse_action(response)
        assert result is None

    def test_parse_action_with_extra_json_fields(self) -> None:
        """Test parsing JSON with extra fields."""
        response = '{"action": "navigate", "direction": "east", "reason": "exploring"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "east"
        assert result.get("reason") == "exploring"
