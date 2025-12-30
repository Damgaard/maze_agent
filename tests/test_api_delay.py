"""Tests for API call delay protection."""

import os
import time
from unittest.mock import MagicMock, patch

import pytest

from maze_agent.common.claude_client import _make_call_with_delay


@pytest.fixture(autouse=True)
def reset_delay_tracking():
    """Reset the module-level delay tracking and API call counter before each test."""
    import maze_agent.common.claude_client as client_module

    client_module._last_api_call_time = None
    client_module._api_call_count = 0
    yield
    client_module._last_api_call_time = None
    client_module._api_call_count = 0


@pytest.fixture
def mock_client():
    """Create a mock Anthropic client."""
    client = MagicMock()
    client.messages.create.return_value = MagicMock(content=[MagicMock(text="Test response")])
    return client


def test_first_call_has_no_delay(mock_client):
    """First API call should not have artificial delay."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "1.0"}):
        start = time.perf_counter()
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # First call should complete quickly (within 100ms)
        assert elapsed < 0.1
        assert mock_client.messages.create.called


def test_second_call_respects_delay(mock_client):
    """Second API call should enforce minimum delay."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0.5"}):
        # First call
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])

        # Second call immediately after
        start = time.perf_counter()
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # Should have delayed at least 0.5 seconds (with small tolerance)
        assert elapsed >= 0.45  # Allow 50ms tolerance
        assert mock_client.messages.create.call_count == 2


def test_multiple_rapid_calls_accumulate_delays(mock_client):
    """Multiple rapid calls should each enforce the delay."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0.3"}):
        # First call
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])

        # Make 3 more calls and measure total time
        start = time.perf_counter()
        for _ in range(3):
            _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # 3 calls with 0.3s delay each = at least 0.9s total (with tolerance)
        assert elapsed >= 0.85  # Allow 50ms tolerance per call
        assert mock_client.messages.create.call_count == 4


def test_delay_uses_environment_variable(mock_client):
    """Delay should use the value from MINIMAL_API_CALL_DELAY environment variable."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0.2"}):
        # First call
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])

        # Second call
        start = time.perf_counter()
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # Should respect the 0.2s delay (with tolerance)
        assert elapsed >= 0.15
        assert elapsed < 0.4  # Should not delay longer than necessary


def test_arguments_passed_through_correctly(mock_client):
    """Arguments should be passed through to client.messages.create()."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0.1"}):
        test_kwargs = {
            "model": "claude-3-sonnet",
            "max_tokens": 500,
            "messages": [{"role": "user", "content": "test"}],
            "system": "You are a test assistant",
        }

        _make_call_with_delay(mock_client, **test_kwargs)

        # Verify all arguments were passed through
        mock_client.messages.create.assert_called_once_with(**test_kwargs)


def test_default_delay_when_env_not_set(mock_client):
    """Should use default 1.0 second delay when environment variable not set."""
    # Remove the env var if it exists
    env_without_delay = {k: v for k, v in os.environ.items() if k != "MINIMAL_API_CALL_DELAY"}

    with patch.dict(os.environ, env_without_delay, clear=True):
        # First call
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])

        # Second call
        start = time.perf_counter()
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # Should use default 1.0 second delay (with tolerance)
        assert elapsed >= 0.95


def test_calls_separated_by_delay_dont_add_extra_wait(mock_client):
    """If calls are naturally separated by more than the delay, no extra wait should occur."""
    with patch.dict(os.environ, {"MINIMAL_API_CALL_DELAY": "0.2"}):
        # First call
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])

        # Wait longer than the delay
        time.sleep(0.3)

        # Second call should not add extra delay
        start = time.perf_counter()
        _make_call_with_delay(mock_client, model="claude-3", max_tokens=100, messages=[])
        elapsed = time.perf_counter() - start

        # Should complete quickly since we already waited
        assert elapsed < 0.1
