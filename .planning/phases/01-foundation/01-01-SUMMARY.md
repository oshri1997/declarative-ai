---
phase: 01-foundation
plan: 01
subsystem: testing
tags: [python, pytest, pydantic, pyyaml, anthropic, setuptools, pyproject]

# Dependency graph
requires: []
provides:
  - Python package declarative_ai importable in editable mode
  - pyproject.toml with all production and dev dependencies pinned
  - pytest configured with --import-mode=importlib targeting tests/
  - 18 RED test stubs across 3 test files for Plans 02 and 03
  - tests/fixtures/simple_spec.yaml minimal valid YAML spec fixture
  - tests/conftest.py shared fixtures (sample_spec_dict, sample_spec_path, fresh_build_state, mock_anthropic_client)
affects: [01-02-PLAN, 01-03-PLAN, all subsequent plans]

# Tech tracking
tech-stack:
  added:
    - pydantic>=2.12 (data validation)
    - pyyaml>=6.0 (YAML parsing)
    - anthropic>=0.84 (LLM API client)
    - tenacity>=9.1 (retry logic)
    - python-dotenv>=1.2 (env var loading)
    - pytest>=9.0 (test runner)
    - pytest-mock>=3.15 (mocking)
    - setuptools build backend (editable install)
  patterns:
    - "Editable install via pip install -e .[dev] — package importable without sys.path manipulation"
    - "Lazy imports inside test functions — allows pytest to collect tests even when implementation modules are missing"
    - "--import-mode=importlib — avoids __init__.py import path collisions"

key-files:
  created:
    - pyproject.toml
    - declarative_ai/__init__.py
    - declarative_ai/schema/__init__.py
    - declarative_ai/agents/__init__.py
    - declarative_ai/cli.py
    - tests/__init__.py
    - tests/conftest.py
    - tests/fixtures/simple_spec.yaml
    - tests/test_spec_schema.py
    - tests/test_state.py
    - tests/test_base_agent.py
  modified:
    - .gitignore (added Python patterns)

key-decisions:
  - "Used setuptools.build_meta as build backend instead of setuptools.backends.legacy:build — legacy backend path does not exist in the installed setuptools version on this system"
  - "Moved module imports inside test function bodies — module-level imports cause pytest collection failures when implementation files don't exist; lazy imports let pytest collect 18 tests while still producing RED failures at run time"

patterns-established:
  - "Lazy test imports: all RED imports live inside test function bodies, not at module level"
  - "Fixture YAML at tests/fixtures/: shared spec fixture loaded by conftest.py via yaml.safe_load"

requirements-completed: []

# Metrics
duration: 3min
completed: 2026-03-15
---

# Phase 1 Plan 01: Project Scaffolding and Test Infrastructure Summary

**pyproject.toml editable install with pydantic/anthropic/pyyaml, pytest wired, 18 RED test stubs covering SpecModel, BuildState, and base agent call_agent**

## Performance

- **Duration:** 3 min
- **Started:** 2026-03-14T22:45:58Z
- **Completed:** 2026-03-14T22:49:00Z
- **Tasks:** 2 of 2
- **Files modified:** 11

## Accomplishments

- Package `declarative_ai` is pip-installable in editable mode with all production and dev dependencies
- pytest configured to collect tests in `tests/` using `--import-mode=importlib`
- 18 test stubs written across `test_spec_schema.py` (8 tests), `test_state.py` (6 tests), `test_base_agent.py` (4 tests) — all RED as expected

## Task Commits

Each task was committed atomically:

1. **Task 1: Create project scaffolding and pyproject.toml** - `3caff43` (chore)
2. **Task 2: Create test fixtures and all test file stubs** - `c07d355` (test)

## Files Created/Modified

- `pyproject.toml` — project definition with all dependencies, pytest config, and entry point stub
- `declarative_ai/__init__.py` — empty package marker
- `declarative_ai/schema/__init__.py` — empty subpackage marker
- `declarative_ai/agents/__init__.py` — empty subpackage marker
- `declarative_ai/cli.py` — placeholder `app = None` for Phase 5 entry point
- `tests/__init__.py` — empty test package marker
- `tests/conftest.py` — shared fixtures: sample_spec_dict, sample_spec_path, fresh_build_state, mock_anthropic_client
- `tests/fixtures/simple_spec.yaml` — minimal valid YAML spec (todo-api with endpoints, components, models, config)
- `tests/test_spec_schema.py` — 8 RED tests covering SPEC-01 through SPEC-06
- `tests/test_state.py` — 6 RED tests covering STATE-01 through STATE-03
- `tests/test_base_agent.py` — 4 RED tests for call_agent, retry exhaustion, rate limit retry, lazy client init
- `.gitignore` — updated with Python patterns (__pycache__, *.pyc, .env, dist, *.egg-info, .pytest_cache, .venv)

## Decisions Made

- Used `setuptools.build_meta` instead of `setuptools.backends.legacy:build` — the `backends` submodule path does not exist in the installed setuptools version; `build_meta` is the correct PEP 517 backend
- Moved all module imports inside test function bodies — module-level `from declarative_ai.x import Y` causes pytest collection to abort with collection errors; lazy imports let pytest collect all 18 tests while still producing `ModuleNotFoundError` failures at run time (RED state preserved)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed pyproject.toml build-backend path**
- **Found during:** Task 1 (pip install -e .[dev])
- **Issue:** `setuptools.backends.legacy:build` does not exist in installed setuptools — `BackendUnavailable` error during editable install
- **Fix:** Changed build-backend to `setuptools.build_meta` and added `wheel` to build requirements
- **Files modified:** pyproject.toml
- **Verification:** `pip install -e .[dev]` completed successfully with all packages installed
- **Committed in:** 3caff43 (Task 1 commit)

**2. [Rule 1 - Bug] Moved imports inside test functions to enable pytest collection**
- **Found during:** Task 2 verification (pytest --co -q)
- **Issue:** Module-level imports in test files caused `ModuleNotFoundError` during collection, resulting in 0 tests collected instead of 14+
- **Fix:** Moved all `from declarative_ai.x import Y` statements inside individual test function bodies
- **Files modified:** tests/test_spec_schema.py, tests/test_state.py, tests/test_base_agent.py
- **Verification:** `pytest --co -q` collects 18 tests; `pytest -x` fails on first test with `ModuleNotFoundError` (RED)
- **Committed in:** c07d355 (Task 2 commit)

---

**Total deviations:** 2 auto-fixed (2 bugs)
**Impact on plan:** Both fixes necessary for the plan's stated goals — package installable and pytest collecting. No scope creep.

## Issues Encountered

None beyond the auto-fixed deviations above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plan 01-02 can implement `declarative_ai/schema/spec_schema.py` against 8 RED tests in `tests/test_spec_schema.py`
- Plan 01-03 can implement `declarative_ai/state.py` and `declarative_ai/agents/base.py` against 10 RED tests
- `tests/conftest.py` fixtures provide `sample_spec_dict` and `sample_spec_path` for both plans
- All dependencies already installed; no additional setup needed before Plans 02 and 03

---
*Phase: 01-foundation*
*Completed: 2026-03-15*
