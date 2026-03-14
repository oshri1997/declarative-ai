---
phase: 01-foundation
plan: 03
subsystem: testing
tags: [python, pydantic, anthropic, tenacity, state-machine, pytest]

# Dependency graph
requires:
  - phase: 01-foundation/01-01
    provides: "Test stubs (RED) for BuildState and call_agent, pytest infra, package scaffold"
provides:
  - BuildState Pydantic model with status transition enforcement via transition() method
  - call_agent() base wrapper for Claude API with tenacity rate-limit retry and parse-retry loop
  - get_client() lazy Anthropic client initialization
  - Full 18-test suite GREEN (test_state.py, test_base_agent.py, test_spec_schema.py)
affects: [all future phases — every agent calls call_agent(); orchestrator uses BuildState]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "transition() method on BuildState enforces state graph — direct status assignment still validated by Literal type at construction"
    - "Pydantic v2 model_config = ConfigDict(validate_assignment=True) for assignment-time type validation"
    - "Tenacity @retry on _call_api_with_retry() handles rate limits; parse-retry loop in call_agent() handles validation failures"
    - "call_agent() accepts explicit client parameter — enables clean unit testing without module-level mocking"
    - "get_client() lazy init with os.environ.get() — avoids crash when ANTHROPIC_API_KEY not set at import time"

key-files:
  created:
    - declarative_ai/state.py
    - declarative_ai/agents/base.py
  modified: []

key-decisions:
  - "BuildState uses a transition() method for graph validation rather than relying solely on field_validator — Pydantic v2 mode=before validators receive empty info.data during validate_assignment, making current-status lookup impossible in the validator; the transition() method reads self.status directly before assignment"
  - "call_agent() accepts client as explicit parameter — tests pass mock_client directly without needing to reset module-level _client global; get_client() remains for production use"
  - "os.environ.get() instead of os.environ[] for ANTHROPIC_API_KEY — allows get_client() to be called in test environments without the key set, since Anthropic SDK accepts None and the constructor mock intercepts it"

patterns-established:
  - "State machine pattern: _TRANSITIONS dict + transition() method — validation at the data layer, not scattered in calling code"
  - "API wrapper pattern: tenacity @retry for network errors, explicit parse-retry loop for validation errors — two distinct retry concerns handled separately"

requirements-completed: [STATE-01, STATE-02, STATE-03]

# Metrics
duration: 8min
completed: 2026-03-15
---

# Phase 1 Plan 03: BuildState and Base Agent Wrapper Summary

**Pydantic v2 BuildState with transition-graph enforcement and Claude API wrapper with tenacity rate-limit retry and parse-retry loop, turning all 18 RED test stubs GREEN**

## Performance

- **Duration:** 8 min
- **Started:** 2026-03-14T22:51:33Z
- **Completed:** 2026-03-14T22:59:00Z
- **Tasks:** 2 of 2
- **Files modified:** 2

## Accomplishments

- BuildState enforces the planning -> building -> validating -> done|failed state graph via the transition() method; Literal type handles construction-time rejection of invalid status strings
- call_agent() provides the single call point for all Claude API interactions with tenacity rate-limit retry (up to 5 attempts) and parse-retry loop (up to 3 attempts)
- Full 18-test suite GREEN — all 6 state tests, all 4 base agent tests, all 8 spec schema tests

## Task Commits

Each task was committed atomically:

1. **Task 1: BuildState with status transition enforcement** - `b189db2` (feat)
2. **Task 2: Base agent wrapper with retry and structured outputs** - `ed12a8d` (feat)

## Files Created/Modified

- `declarative_ai/state.py` — BuildState Pydantic model with _TRANSITIONS dict and transition() method
- `declarative_ai/agents/base.py` — call_agent(), get_client(), _call_api_with_retry() with tenacity

## Decisions Made

- Used `transition()` method for graph validation rather than `@field_validator` — Pydantic v2's `mode="before"` validator receives empty `info.data` during `validate_assignment`, making it impossible to read the current status in the validator. The `transition()` method reads `self.status` directly, which is always available.
- `call_agent()` accepts `client` as an explicit parameter — test files pass `mock_client` directly, which avoids needing to reset the module-level `_client` global between tests. `get_client()` remains for production callers.
- Used `os.environ.get("ANTHROPIC_API_KEY")` instead of `os.environ["ANTHROPIC_API_KEY"]` — allows `get_client()` to be tested (mocked) without requiring the env var to be set, since the mock intercepts the Anthropic constructor before it validates the key.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Used transition() method instead of field_validator for graph enforcement**
- **Found during:** Task 1 verification (test_status_transitions_invalid failing)
- **Issue:** RESEARCH.md Pattern 2 shows `@field_validator("status", mode="before")` reading `info.data.get("status")` to get current status. In Pydantic v2 with `validate_assignment=True`, `info.data` is empty `{}` during assignment re-validation — the current status is not available in the validator context.
- **Fix:** Moved transition graph validation into the `transition()` method which reads `self.status` directly. The `@field_validator` approach was removed; Pydantic's `Literal` type still rejects invalid strings at construction time.
- **Files modified:** declarative_ai/state.py
- **Verification:** All 6 test_state.py tests GREEN including invalid transition and terminal state tests
- **Committed in:** b189db2 (Task 1 commit)

**2. [Rule 1 - Bug] Changed ANTHROPIC_API_KEY access to os.environ.get()**
- **Found during:** Task 2 verification (test_get_client_lazy_init failing)
- **Issue:** `os.environ["ANTHROPIC_API_KEY"]` raises KeyError before the mocked Anthropic constructor is called, because the key isn't set in the test environment
- **Fix:** Changed to `os.environ.get("ANTHROPIC_API_KEY")` — returns None in tests, Anthropic SDK accepts None, and the mock interceptor fires correctly
- **Files modified:** declarative_ai/agents/base.py
- **Verification:** All 4 test_base_agent.py tests GREEN
- **Committed in:** ed12a8d (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes required for tests to pass. The RESEARCH.md Pydantic v2 pattern for `info.data` in cross-field validators is correct for construction time but does not apply during `validate_assignment` re-validation. The transition() method is an equivalent and more explicit design. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 01-02 (SpecModel) was executed earlier (its tests are already GREEN from test_spec_schema.py)
- Phase 1 is complete: SpecModel, BuildState, and agents/base.py are all implemented and tested
- Phase 2 can implement Planner, Worker, State Generator, and Validator agents using call_agent() from agents/base.py and BuildState from state.py
- ANTHROPIC_API_KEY must be set in .env before Phase 2 integration tests

---
*Phase: 01-foundation*
*Completed: 2026-03-15*
