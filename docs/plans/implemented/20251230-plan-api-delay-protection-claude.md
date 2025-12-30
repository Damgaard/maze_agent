# Implementation Plan: API Delay Protection

## Task

From user request:
> Read @docs\03_cost_protection.md . Go through sections one at a time. Validate if the protection they list is implemented. If not, describe why and create a plan to implement. DO NOT DESCRIBE OR IMPLEMENT MULTIPLE MISSING PROTECTIONS AT ONCE.

This plan addresses the first missing protection: **API Delay** (Section 1 of cost_protection.md)

## Overview

Implement a minimum delay between API calls to prevent rapid-fire requests that could quickly accumulate costs if there's a bug causing repeated API calls.

According to `docs/03_cost_protection.md:6-7`:
> The system ensures there is a minimum of MINIMAL_API_CALL_DELAY seconds ( defined in envs ) between each API call.

### Current Status

**NOT IMPLEMENTED** - Missing components:
1. No `MINIMAL_API_CALL_DELAY` environment variable in `.env`
2. No delay tracking mechanism in `claude_client.py`
3. No delay enforcement before API calls in `call_claude_via_api()`

## Implementation Steps

### Step 1: Add Environment Variable
**Files**: `.env` and `env.example`

Add to `.env`:
```
MINIMAL_API_CALL_DELAY=1.0
```

Add to `env.example` with documentation:
```
# API Rate Limiting (Cost Protection)
# Minimum delay in seconds between consecutive API calls
# Default: 1.0 second
# Purpose: Prevents rapid-fire API calls in case of bugs/loops
# Note: Displays sleep message when delay >= 10% of this value
MINIMAL_API_CALL_DELAY=1.0
```

**Rationale**: 1 second provides reasonable protection without significantly impacting normal operation. In a runaway loop scenario, this slows down cost accumulation by 1 second per call.

### Step 2: Add Module-Level Tracking
**File**: `src/maze_agent/common/claude_client.py`

Add at module level (after imports):
```python
import time

# Track last API call time for rate limiting
_last_api_call_time: float | None = None
```

### Step 3: Create Centralized API Call Wrapper
**File**: `src/maze_agent/common/claude_client.py`

Create new function `_make_call_with_delay()` that:
- Accepts `*args` and `**kwargs` to pass through to `client.messages.create()`
- Enforces minimum delay between calls
- Provides single point of control for all API calls
- Can be extended with logging in the future

```python
def _make_call_with_delay(client: anthropic.Anthropic, **kwargs):
    """Wrapper for API calls that enforces minimum delay between calls.

    This function ensures all API calls go through a central point where:
    - Minimum delay between calls is enforced
    - Future logging can be added
    - Rate limiting is managed

    Args:
        client: The Anthropic client instance
        **kwargs: Keyword arguments to pass to client.messages.create()

    Returns:
        The response from client.messages.create()
    """
    global _last_api_call_time

    # Load delay from environment (default 1.0 second)
    min_delay = float(os.environ.get("MINIMAL_API_CALL_DELAY", "1.0"))

    # Enforce delay if this isn't the first call
    if _last_api_call_time is not None:
        elapsed = time.perf_counter() - _last_api_call_time
        if elapsed < min_delay:
            sleep_time = min_delay - elapsed
            # Print message if sleeping for at least 10% of max delay (helps debugging)
            if sleep_time >= min_delay * 0.1:
                print(f"⏱️  API rate limit: sleeping {sleep_time:.2f}s")
            time.sleep(sleep_time)

    # Make the actual API call
    response = client.messages.create(**kwargs)

    # Update last call time
    _last_api_call_time = time.perf_counter()

    return response
```

**Location**: Insert after `call_claude_via_cli()` function (around line 48), before `call_claude_via_api()`.

### Step 4: Update call_claude_via_api() to Use Wrapper
**File**: `src/maze_agent/common/claude_client.py`
**Function**: `call_claude_via_api()` (line 50)

Replace the direct call to `client.messages.create(**api_params)` at line 125 with:
```python
response = _make_call_with_delay(client, **api_params)
```

This ensures all API calls go through the centralized wrapper function.

### Step 5: Add Tests
**File**: Create `tests/test_api_delay.py`

Test cases:
1. First call has no delay
2. Second call respects minimum delay
3. Multiple rapid calls accumulate proper delays
4. Delay uses environment variable value
5. Arguments are correctly passed through to API

**Testing approach**:
- Mock `client.messages.create()` to avoid actual API calls
- Use `time.perf_counter()` to measure elapsed time
- Mock `_make_call_with_delay` in existing tests to avoid delays during test runs

## Technical Considerations

### Centralized API Call Architecture
Using `_make_call_with_delay()` as a wrapper provides:
- **Single point of control**: All API calls go through one function
- **Extensibility**: Easy to add logging, metrics, or additional rate limiting later
- **Testability**: Can mock the wrapper function in tests to avoid delays
- **Maintainability**: Delay logic is isolated and reusable

### Thread Safety
Current implementation is single-threaded (one agent loop per process). Module-level variable is sufficient. If future versions introduce threading, will need `threading.Lock()` around the timing checks and updates.

### Precision
Use `time.perf_counter()` for high-precision timing (better than `time.time()` for intervals). This provides sub-millisecond precision for accurate delay enforcement.

### First Call
First API call should not have artificial delay - only enforce delay between subsequent calls. This is handled by checking if `_last_api_call_time is not None` before enforcing delay.

### Environment Variable Loading
The wrapper loads `MINIMAL_API_CALL_DELAY` from environment on each call. The parent function `call_claude_via_api()` already calls `load_dotenv()` at line 77, so the environment variable will be available.

## Potential Risks and Challenges

### Risk 1: Performance Impact
**Impact**: Low - adds max 1 second delay per call in normal operation
**Mitigation**: Only enforces delay if calls are within the threshold window

### Risk 2: Breaking Existing Tests
**Impact**: Medium - existing tests may fail if they make rapid API calls
**Mitigation**: Tests already mock `call_claude_via_api()`, so delay logic won't affect them

### Risk 3: Multiple Processes
**Impact**: Low - delay tracking is per-process, not global
**Mitigation**: Acceptable - each process independently rate-limits itself

## Testing Approach

### Unit Tests
Create `tests/test_api_delay.py`:
- Mock anthropic API calls
- Measure actual time elapsed
- Verify delay enforcement

### Manual Testing
Run agent with low delay value (0.5s) and observe timing in logs.

### Integration Testing
Existing integration tests should continue to pass (they mock the API).

## Dependencies and Prerequisites

### Dependencies
- No new dependencies required
- Uses existing `time` module (Python standard library)

### Prerequisites
- None - can be implemented immediately

## Success Criteria

1. Environment variable `MINIMAL_API_CALL_DELAY` exists in `.env`
2. Function `_make_call_with_delay()` exists and is used by all API calls
3. All API calls go through the centralized wrapper function
4. Consecutive API calls are delayed by at least the configured amount
5. First API call has no artificial delay
6. All existing tests continue to pass
7. New tests verify delay behavior and argument pass-through
