# Implementation Plan: Test Protections

## Task

From user request:

> Create plan for test implementation.

This plan addresses the fourth missing protection: **Test protections** (Section 4 of cost_protection.md)

## Overview

Implement test-level protections to prevent accidental API calls during test execution. According to `docs/03_cost_protection.md:17-19`:

> Running tests should not make unmocked calls to the LLM. There are 2 levels of protection against this. First the system always overrides the keys at start of pytest, to ensure that if the key is attempted used it will be used with an invalid value. Secondly, the API function to call calude is auto mocked. Should any test needs to mock it with a particular result, then it can remock the test to return another result.

### Current Status

**NOT IMPLEMENTED** - Missing components:

1. No `conftest.py` file to configure pytest fixtures
2. No automatic override of `ANTHROPIC_API_KEY` at test startup
3. No automatic mocking of `call_claude_via_api()` function
4. Tests rely on manual mocking instead of automatic protection

### Why This Protection Matters

Without these protections:

- A developer could accidentally write a test that makes real API calls
- Tests could incur costs during CI/CD runs
- Local test runs could consume API credits
- No safety net for mistakes in test code

## Implementation Steps

### Step 1: Create conftest.py

**File**: `tests/conftest.py` (new file)

Create pytest configuration file with fixtures:

```python
"""Pytest configuration and fixtures for cost protection."""

import os
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture(autouse=True)
def override_api_key(monkeypatch):
    """Override ANTHROPIC_API_KEY with invalid value (cost protection).

    This ensures that if any test accidentally tries to use the real API,
    it will fail with an authentication error rather than incur costs.

    autouse=True means this fixture runs for ALL tests automatically.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "sk-ant-test-invalid-key-for-testing")


@pytest.fixture(autouse=True)
def mock_call_claude_via_api():
    """Auto-mock call_claude_via_api to prevent accidental API calls (cost protection).

    This provides a default mock that returns a safe response. Individual tests
    can override this mock if they need specific behavior.

    autouse=True means this fixture runs for ALL tests automatically.
    """
    with patch("maze_agent.common.claude_client.call_claude_via_api") as mock_api:
        # Default mock response structure
        mock_api.return_value = {
            "text": "Mocked response",
            "messages": [],
            "input_tokens": 0,
            "output_tokens": 0,
        }
        yield mock_api
```

**Location**: Create at the root of the `tests/` directory.

**Rationale**:

- `conftest.py` is automatically discovered by pytest
- Fixtures with `autouse=True` run automatically for all tests
- Provides two layers of protection as specified

### Step 2: Update Existing Test Files

**Files**: Various test files that might need adjustments

Most tests won't need changes because:

- They don't use `call_claude_via_api()` at all
- They test business logic, not API interactions

Tests that **do** need updates:

- `tests/test_api_delay.py` - currently manually mocks, can rely on auto-mock

**Changes for test_api_delay.py**:

- The test currently tests `_make_call_with_delay()` which calls `client.messages.create()`
- These tests are fine as-is because they mock the client directly
- No changes needed for this file

### Step 3: Add Documentation Comment

**File**: `tests/conftest.py`

Add module-level docstring explaining the protections:

```python
"""Pytest configuration and fixtures for cost protection.

This file provides automatic protections against accidental API calls during testing:

1. API Key Override: All tests run with an invalid ANTHROPIC_API_KEY
2. Auto-Mocking: call_claude_via_api() is automatically mocked

These protections ensure that tests never incur API costs, even if written incorrectly.

To override the mock in a specific test:
    def test_something(mock_call_claude_via_api):
        # Re-configure the mock for this test
        mock_call_claude_via_api.return_value = {"text": "Custom response", ...}
        # Test code here
"""
```

### Step 4: Add Tests for the Protections

**File**: Create `tests/test_cost_protections.py`

Create tests to verify the protections are working:

```python
"""Tests to verify cost protection mechanisms are in place."""

import os

import pytest


def test_api_key_is_overridden():
    """Verify that ANTHROPIC_API_KEY is overridden in tests."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    assert api_key == "sk-ant-test-invalid-key-for-testing"
    assert "invalid" in api_key
    assert "test" in api_key


def test_call_claude_via_api_is_mocked(mock_call_claude_via_api):
    """Verify that call_claude_via_api is auto-mocked."""
    from maze_agent.common.claude_client import call_claude_via_api

    # Call should work and return mocked response
    result = call_claude_via_api(prompt="test")

    # Verify it was the mock that was called
    assert mock_call_claude_via_api.called
    assert result is not None


def test_mock_can_be_overridden(mock_call_claude_via_api):
    """Verify that individual tests can override the default mock."""
    from maze_agent.common.claude_client import call_claude_via_api

    # Override the mock for this test
    custom_response = {
        "text": "Custom test response",
        "messages": [{"role": "assistant", "content": "test"}],
        "input_tokens": 10,
        "output_tokens": 20,
    }
    mock_call_claude_via_api.return_value = custom_response

    # Call and verify custom response
    result = call_claude_via_api(prompt="test")
    assert result == custom_response
    assert result["text"] == "Custom test response"
```

**Location**: Create in `tests/` directory.

### Step 5: Update Documentation

**File**: `docs/03_cost_protection.md`

Add note about how to override mocks in specific tests:

````markdown
## Test protections

Running tests should not make unmocked calls to the LLM. There are 2 levels of protection against this. First the system always overrides the keys at start of pytest, to ensure that if the key is attempted used it will be used with an invalid value. Secondly, the API function to call calude is auto mocked. Should any test needs to mock it with a particular result, then it can remock the test to return another result.

### Overriding the Mock in Specific Tests

If a test needs specific mock behavior, it can access the auto-mock fixture:

```python
def test_something(mock_call_claude_via_api):
    # Configure the mock for this test
    mock_call_claude_via_api.return_value = {
        "text": "Expected response",
        "messages": [],
        "input_tokens": 5,
        "output_tokens": 10,
    }

    # Run test code
    result = my_function_that_calls_api()
    assert "Expected response" in result
```
````

````

## Technical Considerations

### pytest Fixture Scope
- Using `autouse=True` makes fixtures run automatically
- These fixtures apply to ALL tests in the suite
- Individual tests can still override by accepting the fixture as a parameter

### Fixture Execution Order
1. `override_api_key` runs first (sets invalid key)
2. `mock_call_claude_via_api` runs second (mocks the function)
3. Test code executes with both protections active
4. Fixtures clean up automatically after the test

### Interaction with Existing Tests
- Tests that don't use the API are unaffected
- Tests that manually mock will have both mocks (no conflict)
- Tests using the API directly will get the auto-mock

### monkeypatch vs patch
- `monkeypatch` is pytest's built-in fixture for environment variables
- `patch` is from unittest.mock for mocking functions
- Both are appropriate for their respective use cases

## Potential Risks and Challenges

### Risk 1: Tests That Need Real API
**Impact**: Low - No tests should need real API
**Mitigation**: All tests should be unit tests using mocks

### Risk 2: Fixture Conflicts
**Impact**: Low - Fixtures might conflict with manual mocks
**Mitigation**: Tests can override the auto-mock by accepting the fixture parameter

### Risk 3: False Sense of Security
**Impact**: Low - Developers might assume all API calls are safe
**Mitigation**: Documentation makes it clear these are protections, not permissions

### Risk 4: Breaking Existing Tests
**Impact**: Low - Most tests don't use call_claude_via_api
**Mitigation**: Run full test suite after implementation to verify

## Testing Approach

### Unit Tests
Create `tests/test_cost_protections.py`:
- Verify API key is overridden
- Verify auto-mock is active
- Verify mock can be overridden per-test

### Integration Testing
Run existing test suite:
```bash
uv run pytest -v
````

All tests should continue to pass with the new protections in place.

### Manual Verification

1. Try to import and call `call_claude_via_api()` in a test
2. Verify it returns the mocked response, not real API call
3. Verify environment variable shows invalid key

## Dependencies and Prerequisites

### Dependencies

- pytest (already installed)
- unittest.mock (Python standard library)
- No new dependencies required

### Prerequisites

- Understanding of pytest fixtures
- Understanding of monkeypatch and patch

## Success Criteria

1. `tests/conftest.py` exists with both fixture definitions
2. `override_api_key` fixture sets `ANTHROPIC_API_KEY` to invalid value
3. `mock_call_claude_via_api` fixture auto-mocks the API function
4. Both fixtures use `autouse=True` to run automatically
5. New tests in `test_cost_protections.py` verify protections work
6. All existing tests continue to pass (61/61)
7. Documentation updated with override instructions
8. Individual tests can override the mock when needed

## Implementation Order

1. Create `tests/conftest.py` with both fixtures
2. Create `tests/test_cost_protections.py` with verification tests
3. Run test suite to verify no breakage
4. Update documentation in `docs/03_cost_protection.md`
5. Verify protections work as expected

## Future Enhancements

- Add warning if test tries to override API key to a real value
- Log which tests override the mock (for debugging)
- Add fixture to track mock call counts across test suite
- CI/CD check to ensure conftest.py is never removed
