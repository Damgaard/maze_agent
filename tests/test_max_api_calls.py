"""Tests for MAX_API_CALLS cost protection."""

import os
from unittest.mock import MagicMock, patch

import pytest

from maze_agent.common.claude_client import _make_call_with_delay, reset_api_call_counter


@pytest.fixture(autouse=True)
def reset_counter_before_test():
    """Reset the API call counter before each test."""
    reset_api_call_counter()
    yield
    reset_api_call_counter()


@pytest.fixture
def mock_client():
    """Create a mock Anthropic client."""
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[MagicMock(text="Test response")])
    return client


def test_counter_starts_at_zero():
    """API call counter should start at 0 after reset."""
    import maze_agent.common.claude_client as client_module

    reset_api_call_counter()
    assert client_module._api_call_count == 0


def test_counter_increments_with_each_call(mock_client):
    """Counter should increment with each API call."""
    import maze_agent.common.claude_client as client_module

    with patch.dict(os.environ, {"MAX_API_CALLS": "10", "MINIMAL_API_CALL_DELAY": "0"}):
        # Make 3 calls
        for i in range(3):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])
            assert client_module._api_call_count == i + 1


def test_exception_raised_when_limit_exceeded(mock_client):
    """Should raise RuntimeError when MAX_API_CALLS is exceeded."""
    with patch.dict(os.environ, {"MAX_API_CALLS": "3", "MINIMAL_API_CALL_DELAY": "0"}):
        # Make 3 successful calls
        for _ in range(3):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        # 4th call should raise exception
        with pytest.raises(RuntimeError) as exc_info:
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        assert "API call limit exceeded" in str(exc_info.value)
        assert "3/3 calls made" in str(exc_info.value)


def test_exception_message_contains_useful_info(mock_client):
    """Exception message should contain count, limit, and helpful guidance."""
    with patch.dict(os.environ, {"MAX_API_CALLS": "2", "MINIMAL_API_CALL_DELAY": "0"}):
        # Make 2 calls
        for _ in range(2):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        # 3rd call should raise with useful message
        with pytest.raises(RuntimeError) as exc_info:
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        error_message = str(exc_info.value)
        assert "2/2 calls made" in error_message
        assert "cost protection" in error_message
        assert "MAX_API_CALLS" in error_message
        assert ".env" in error_message


def test_reset_function_works(mock_client):
    """reset_api_call_counter() should reset the counter to 0."""
    import maze_agent.common.claude_client as client_module

    with patch.dict(os.environ, {"MAX_API_CALLS": "10", "MINIMAL_API_CALL_DELAY": "0"}):
        # Make some calls
        for _ in range(3):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        assert client_module._api_call_count == 3

        # Reset
        reset_api_call_counter()

        assert client_module._api_call_count == 0

        # Should be able to make calls again
        _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])
        assert client_module._api_call_count == 1


def test_limit_uses_environment_variable(mock_client):
    """Limit should use the value from MAX_API_CALLS environment variable."""
    with patch.dict(os.environ, {"MAX_API_CALLS": "5", "MINIMAL_API_CALL_DELAY": "0"}):
        # Should be able to make 5 calls
        for _ in range(5):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        # 6th should fail
        with pytest.raises(RuntimeError) as exc_info:
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        assert "5/5 calls made" in str(exc_info.value)


def test_default_limit_is_10(mock_client):
    """Should use default limit of 10 when MAX_API_CALLS env var not set."""
    # Remove the env var if it exists
    env_without_max = {k: v for k, v in os.environ.items() if k != "MAX_API_CALLS"}

    with patch.dict(os.environ, env_without_max, clear=True):
        # Patch MINIMAL_API_CALL_DELAY to avoid delays
        with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0"}):
            # Should be able to make 10 calls
            for _ in range(10):
                _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

            # 11th should fail with default limit
            with pytest.raises(RuntimeError) as exc_info:
                _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

            assert "10/10 calls made" in str(exc_info.value)


def test_counter_increments_before_api_call(mock_client):
    """Counter should increment even if API call fails."""
    import maze_agent.common.claude_client as client_module

    # Make the API call raise an exception
    mock_client.messages.create.side_effect = Exception("API Error")

    with patch.dict(os.environ, {"MAX_API_CALLS": "10", "MINIMAL_API_CALL_DELAY": "0"}):
        # Counter should still increment even though call fails
        with pytest.raises(Exception, match="API Error"):
            _make_call_with_delay(mock_client, model="test", max_tokens=10, messages=[])

        # Counter should have incremented
        assert client_module._api_call_count == 1
