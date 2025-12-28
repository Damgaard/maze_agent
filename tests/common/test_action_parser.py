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

    def test_parse_action_fallback_navigate_north(self) -> None:
        """Test fallback parsing for navigate north without valid JSON."""
        response = "I will navigate north to explore the room."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "north"

    def test_parse_action_fallback_navigate_south(self) -> None:
        """Test fallback parsing for navigate south without valid JSON."""
        response = "I will navigate south this time."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "south"

    def test_parse_action_fallback_navigate_east(self) -> None:
        """Test fallback parsing for navigate east without valid JSON."""
        response = "I want to navigate east now."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "east"

    def test_parse_action_fallback_navigate_west(self) -> None:
        """Test fallback parsing for navigate west without valid JSON."""
        response = "I'll navigate west now."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "west"

    def test_parse_action_fallback_navigate_default_north(self) -> None:
        """Test fallback parsing defaults to north when navigate is mentioned but no direction found."""
        response = "I want to navigate but I'm not sure where."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "north"

    def test_parse_action_fallback_search_secrets(self) -> None:
        """Test fallback parsing for search secrets without valid JSON."""
        response = "I will search for secret doors in this room."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "search_secrets"

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

    def test_parse_action_case_insensitive_fallback(self) -> None:
        """Test that fallback parsing is case insensitive."""
        response = "I will NAVIGATE SOUTH to the next room."
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "south"

    def test_parse_action_with_extra_json_fields(self) -> None:
        """Test parsing JSON with extra fields."""
        response = '{"action": "navigate", "direction": "east", "reason": "exploring"}'
        result = parse_action(response)
        assert result is not None
        assert result["action"] == "navigate"
        assert result["direction"] == "east"
        assert result.get("reason") == "exploring"
