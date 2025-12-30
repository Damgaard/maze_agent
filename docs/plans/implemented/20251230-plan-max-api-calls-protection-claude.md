# Implementation Plan: Max API Calls Protection

## Task

From user request:
> Create a plan for implementing this [MAX_API_CALLS protection]. Main code should be in the wrapper function we implemented earlier. Set default max api calls to 10.

This plan addresses the third missing protection: **Max API calls** (Section 3 of cost_protection.md)

## Overview

Implement a maximum API call limit per maze solving session to prevent runaway costs. According to `docs/03_cost_protection.md:15`:
> For each maze there is a maximum amount of API calls, as defined by MAX_API_CALLS set in environment variables. If it is exceeded, the solver will throw an exception and stop.

### Current Status

**NOT IMPLEMENTED** - Missing components:
1. No `MAX_API_CALLS` environment variable in `.env` or `env.example`
2. No API call counter tracking total calls made
3. No exception raised when limit is exceeded
4. No counter reset mechanism between maze solves

### Key Difference from max_actions

- **max_actions**: Limits agent decisions (navigate, search_secrets) - currently 6, hardcoded
- **MAX_API_CALLS**: Limits actual API requests to Anthropic - should default to 10

A single action can result in multiple API calls due to the tool use loop, so MAX_API_CALLS provides additional cost protection.

## Implementation Steps

### Step 1: Add Environment Variable
**Files**: `.env` and `env.example`

Add to `.env`:
```
MAX_API_CALLS=10
```

Add to `env.example` with documentation:
```
# Max API Calls (Cost Protection)
# Maximum number of API calls allowed per maze solving session
# Default: 10
# Purpose: Hard limit on API usage even if actions are within limit
# Note: Will raise exception when exceeded
MAX_API_CALLS=10
```

**Rationale**: 10 calls provides reasonable headroom (6 actions × ~1.5 avg calls per action) while preventing runaway costs.

### Step 2: Add Module-Level Counter
**File**: `src/maze_agent/common/claude_client.py`

Add at module level (after `_last_api_call_time`):
```python
# Track API call count for cost protection
_api_call_count: int = 0
```

### Step 3: Create Counter Reset Function
**File**: `src/maze_agent/common/claude_client.py`

Create new function to reset the counter between maze solves:
```python
def reset_api_call_counter():
    """Reset the API call counter.

    Should be called at the start of each maze solving session
    to ensure accurate counting per session.
    """
    global _api_call_count
    _api_call_count = 0
```

**Location**: Insert after `_make_call_with_delay()` function, before `call_claude_via_api()`.

### Step 4: Enforce Limit in Wrapper Function
**File**: `src/maze_agent/common/claude_client.py`
**Function**: `_make_call_with_delay()` (line 54)

Add enforcement logic at the beginning of the function (after loading min_delay):
```python
# Load max API calls limit from environment (default 10)
max_api_calls = int(os.environ.get("MAX_API_CALLS", "10"))

# Check if we've exceeded the limit
if _api_call_count >= max_api_calls:
    raise RuntimeError(
        f"API call limit exceeded: {_api_call_count}/{max_api_calls} calls made. "
        "This is a cost protection measure. Increase MAX_API_CALLS in .env if needed."
    )

# Increment counter
_api_call_count += 1
```

**Implementation location**: After line 73 (after loading min_delay), before the delay enforcement logic.

### Step 5: Call Reset in Agent Functions
**File**: `src/maze_agent/agent.py`
**Functions**: `run_agent_debug()` (line 48) and `run_agent_production()` (line 280)

Add at the beginning of each function (right after the print header):
```python
from maze_agent.common.claude_client import call_claude_via_api, get_model_info, reset_api_call_counter

# Reset API call counter at start of session
reset_api_call_counter()
```

**Locations**:
- `run_agent_debug()`: After line 59 (after status file setup)
- `run_agent_production()`: After line 305 (after initializing token tracking)

### Step 6: Update Import Statement
**File**: `src/maze_agent/agent.py`

Update the import at line 7:
```python
from maze_agent.common.claude_client import call_claude_via_api, get_model_info, reset_api_call_counter
```

### Step 7: Add Tests
**File**: Create `tests/test_max_api_calls.py`

Test cases:
1. Counter starts at 0
2. Counter increments with each call
3. Exception raised when limit exceeded
4. Exception message contains useful info
5. Reset function works correctly
6. Limit uses environment variable value
7. Default limit is 10 when env var not set

**Testing approach**:
- Mock the actual API call to avoid costs
- Test the counter and limit enforcement
- Verify exception type and message

## Technical Considerations

### Centralized Enforcement
Using `_make_call_with_delay()` for enforcement provides:
- **Single point of control**: All API calls are counted and limited
- **Automatic tracking**: No need to manually increment counters elsewhere
- **Tool use loop protection**: Internal tool calls are counted toward the limit

### Counter Scope
The counter is module-level and persists for the lifetime of the process. It's reset explicitly at the start of each maze solving session via `reset_api_call_counter()`.

### Exception Handling
- Uses `RuntimeError` to signal a configuration/limit issue
- Provides clear message with current count and limit
- Suggests increasing MAX_API_CALLS if needed

### Agent Loop Behavior
When the exception is raised:
- The agent loop will catch it (or it will propagate up)
- Maze solving will stop
- User gets clear error message about cost protection

## Potential Risks and Challenges

### Risk 1: Counter Not Reset
**Impact**: Medium - If counter isn't reset between sessions, second session could fail immediately
**Mitigation**: Reset is called explicitly at the start of each agent function

### Risk 2: Exception Handling in Agent Loop
**Impact**: Low - Exception might not be caught gracefully
**Mitigation**: The agent loop should catch and log the exception appropriately. May need to add try/catch in agent functions.

### Risk 3: Tool Use Loop Behavior
**Impact**: Low - Limit might be hit mid-action during tool use
**Mitigation**: Acceptable - cost protection is more important than completing an action

### Risk 4: Testing with Actual API
**Impact**: Low - Tests might inadvertently make real API calls
**Mitigation**: All tests mock the API call, counter is tested in isolation

## Testing Approach

### Unit Tests
Create `tests/test_max_api_calls.py`:
- Mock anthropic API calls
- Test counter increment logic
- Test limit enforcement
- Test reset function
- Verify exception message

### Manual Testing
1. Set `MAX_API_CALLS=3` in `.env`
2. Run maze solver
3. Verify it stops after 3 API calls with clear error message

### Integration Testing
Existing integration tests should continue to pass (they mock the API).

## Dependencies and Prerequisites

### Dependencies
- No new dependencies required
- Uses existing `os` module for environment variables

### Prerequisites
- Requires the `_make_call_with_delay()` wrapper function (already implemented)
- Requires access to modify agent.py import statements

## Success Criteria

1. Environment variable `MAX_API_CALLS` exists in `.env` and `env.example`
2. Module-level counter `_api_call_count` tracks all API calls
3. `reset_api_call_counter()` function exists and is called at session start
4. Exception raised when limit exceeded with clear message
5. Default limit is 10 calls
6. Counter is reset at the start of each maze solving session
7. All existing tests continue to pass
8. New tests verify limit enforcement
9. Manual test confirms cost protection works as expected

## Future Enhancements

- Add counter value to agent status output (e.g., "API calls: 3/10")
- Log warning when approaching limit (e.g., at 80%)
- Track calls per-session in status file for debugging
