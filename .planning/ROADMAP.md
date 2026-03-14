# Roadmap: Declarative AI Build System

## Overview

Five phases build the system bottom-up, matching the component dependency graph. Phase 1 lays the data contracts (state, spec schema, API wrapper) that every agent depends on. Phase 2 builds the Planner and task graph. Phase 3 delivers workers and git-backed output. Phase 4 closes the loop with the State Generator and Validator. Phase 5 integrates everything into a working CLI. At the end of Phase 5, a user can point the CLI at a YAML spec and watch the system autonomously build a matching codebase.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Foundation** - Typed state model, spec YAML schema, and base API wrapper with retry and schema enforcement
- [ ] **Phase 2: Planner Agent** - Spec decomposition into dependency-aware task graph with delta re-planning support
- [ ] **Phase 3: Worker Execution** - Parallel file-writing workers, thread pool, and git-backed iteration commits
- [ ] **Phase 4: State Generator and Validator** - Codebase snapshot extraction and gap analysis closing the build loop
- [ ] **Phase 5: Orchestrator and CLI** - Full closed-loop orchestrator integrated with a Typer CLI entry point

## Phase Details

### Phase 1: Foundation
**Goal**: The data contracts, configuration, and API infrastructure that every agent depends on are in place and validated
**Depends on**: Nothing (first phase)
**Requirements**: SPEC-01, SPEC-02, SPEC-03, SPEC-04, SPEC-05, SPEC-06, STATE-01, STATE-02, STATE-03
**Success Criteria** (what must be TRUE):
  1. A YAML spec file with API endpoints, UI components, data models, and config fields can be loaded and validated against a Pydantic schema without error
  2. The BuildState Pydantic model can be instantiated with all required fields and rejects invalid field values at construction time
  3. Status transitions (planning -> building -> validating -> done/failed) are enforced by the state model -- invalid transitions raise validation errors
  4. A call to the base API wrapper returns a Pydantic-validated agent output or raises after three parse-retry attempts
  5. The spec schema accepts any language or framework in its fields -- no hardcoded Python/JS/etc. assumptions exist in the schema
**Plans:** 2/3 plans executed

Plans:
- [x] 01-01-PLAN.md -- Project scaffolding, pyproject.toml, test infrastructure and RED test stubs
- [x] 01-02-PLAN.md -- Spec schema (SpecModel, load_spec) implementation with TDD
- [ ] 01-03-PLAN.md -- BuildState and base agent wrapper implementation with TDD

### Phase 2: Planner Agent
**Goal**: The Planner can decompose a YAML spec into a dependency-aware task graph and, on subsequent iterations, emit only delta tasks from a gap report
**Depends on**: Phase 1
**Requirements**: PLAN-01, PLAN-02, PLAN-03, PLAN-04, PLAN-05
**Success Criteria** (what must be TRUE):
  1. Given a YAML spec, the Planner produces a task graph where every task has a unique ID, target file path, task type, acceptance criteria, and dependency list
  2. Tasks are grouped into parallel execution batches such that no task in a batch depends on another task in the same batch
  3. Given a gap report on iteration 2+, the Planner produces only tasks that address unresolved gaps -- not a full re-plan of already-satisfied requirements
  4. The Planner's output is structured JSON that validates against the task graph Pydantic schema without manual parsing
**Plans**: TBD

### Phase 3: Worker Execution
**Goal**: Workers write real files to disk in parallel, blocked workers surface their blockers, and each completed batch is committed to git
**Depends on**: Phase 2
**Requirements**: WORK-01, WORK-02, WORK-03, WORK-04, WORK-05, WORK-06
**Success Criteria** (what must be TRUE):
  1. Workers for a given batch run concurrently via ThreadPoolExecutor -- multiple files are written in parallel, not sequentially
  2. Each worker writes complete file content to its assigned path -- no placeholder comments, no truncation markers
  3. A worker that cannot proceed (missing dependency) returns a structured "blocked" result with a machine-readable reason rather than failing silently
  4. After all workers in a batch complete, their output is committed to the local git repo with an iteration-tagged commit message
  5. Worker output is structured JSON that validates against the worker result Pydantic schema
**Plans**: TBD

### Phase 4: State Generator and Validator
**Goal**: After each worker batch, the codebase is read and compared against the desired spec, producing a gap report that drives the next iteration or terminates the loop
**Depends on**: Phase 3
**Requirements**: SGEN-01, SGEN-02, SGEN-03, SGEN-04, VALD-01, VALD-02, VALD-03, VALD-04, VALD-05, VALD-06
**Success Criteria** (what must be TRUE):
  1. The State Generator reads all files in the output directory and produces a snapshot whose structure mirrors the desired spec schema (APIs, components, models, config)
  2. Every entity in the snapshot is cross-checked against files that physically exist on disk -- entities without a resolvable source file are marked source_unverified
  3. The Validator compares the snapshot against the spec field by field and emits a gap entry for each discrepancy, with feature, current state, desired state, and severity (critical/major/minor)
  4. When the snapshot fully matches the spec, the Validator sets status to "done" and the loop can terminate
  5. When max_iterations is reached with gaps remaining, the Validator sets status to "failed" with the remaining gap report intact
**Plans**: TBD

### Phase 5: Orchestrator and CLI
**Goal**: A user can run a single CLI command pointing at a YAML spec and the system autonomously iterates until the codebase matches the spec or max iterations is reached
**Depends on**: Phase 4
**Requirements**: ORCH-01, ORCH-02, ORCH-03, ORCH-04, ORCH-05, CLI-01, CLI-02, CLI-03, CLI-04, SPEC-07
**Success Criteria** (what must be TRUE):
  1. Running `declarative-ai build spec.yaml` starts the full loop -- Planner -> Workers -> State Generator -> Validator -- and iterates automatically until done or failed
  2. Blocked workers from one batch are detected and their blockers fed back to the Planner before the next iteration begins, without user intervention
  3. The CLI accepts `--max-iterations N` (default 10) and ANTHROPIC_API_KEY from env or .env, and prints each iteration's number and current status to stdout
  4. On completion, the CLI prints a final summary showing outcome (aligned/timeout/blocked), total iterations, and whether the build succeeded
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Foundation | 2/3 | In Progress|  |
| 2. Planner Agent | 0/TBD | Not started | - |
| 3. Worker Execution | 0/TBD | Not started | - |
| 4. State Generator and Validator | 0/TBD | Not started | - |
| 5. Orchestrator and CLI | 0/TBD | Not started | - |

---
*Roadmap created: 2026-03-15*
