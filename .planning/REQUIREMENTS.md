# Requirements: Declarative AI Build System

**Defined:** 2026-03-15
**Core Value:** Given a declarative YAML spec, the system produces a working codebase that matches the spec — automatically, with no human intervention during the build loop.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Spec Input

- [x] **SPEC-01**: User can provide a YAML spec file as CLI argument to start a build
- [x] **SPEC-02**: Spec schema supports defining API endpoints (method, path, request/response shape)
- [x] **SPEC-03**: Spec schema supports defining UI components (name, props, behavior)
- [x] **SPEC-04**: Spec schema supports defining data models (fields, types, relations)
- [x] **SPEC-05**: Spec schema supports defining configuration (env vars, feature flags)
- [x] **SPEC-06**: Spec schema is language/framework agnostic (no hardcoded language assumptions)
- [ ] **SPEC-07**: User can configure max_iterations via CLI flag (default: 10)

### Shared State

- [x] **STATE-01**: Shared state object tracks iteration count, status, task graph, codebase snapshot, and gap report
- [x] **STATE-02**: Shared state is a Pydantic model with typed fields and validation
- [x] **STATE-03**: Status field transitions through: planning → building → validating → done | failed

### Planner Agent

- [ ] **PLAN-01**: Planner reads desired spec and decomposes it into a task graph on first iteration
- [ ] **PLAN-02**: Each task has a unique ID, target file path, task type, acceptance criteria, and dependencies
- [ ] **PLAN-03**: Tasks are grouped into parallel execution batches based on dependency analysis
- [ ] **PLAN-04**: Planner output is structured JSON validated against a defined schema
- [ ] **PLAN-05**: On subsequent iterations, Planner receives gap report and produces only delta tasks

### Worker Agent

- [ ] **WORK-01**: One worker agent is spawned per task in the current execution batch
- [ ] **WORK-02**: Workers run in parallel via Python ThreadPoolExecutor
- [ ] **WORK-03**: Each worker writes or modifies only its assigned target file
- [ ] **WORK-04**: Worker outputs complete file content (no truncation or placeholders)
- [ ] **WORK-05**: Worker can report "blocked" status with a reason if dependencies are missing
- [ ] **WORK-06**: Worker output is structured JSON validated against a defined schema

### State Generator Agent

- [ ] **SGEN-01**: State Generator reads all files in the output directory after each worker batch
- [ ] **SGEN-02**: State Generator produces a structured snapshot in the same schema shape as the desired spec
- [ ] **SGEN-03**: Snapshot covers APIs, components, models, and config found in the codebase
- [ ] **SGEN-04**: State Generator output is structured JSON validated against a defined schema

### Validator Agent

- [ ] **VALD-01**: Validator compares current state snapshot against desired spec field by field
- [ ] **VALD-02**: Each discrepancy is emitted as a gap entry with feature, current state, desired state, and severity
- [ ] **VALD-03**: Gap severity levels are: critical, major, minor
- [ ] **VALD-04**: If no gaps exist, Validator sets status to "done"
- [ ] **VALD-05**: If max_iterations reached with gaps remaining, Validator sets status to "failed"
- [ ] **VALD-06**: Validator output is structured JSON validated against a defined schema

### Orchestrator Loop

- [ ] **ORCH-01**: Orchestrator runs the full loop: Planner → Workers → State Generator → Validator
- [ ] **ORCH-02**: Loop continues until status is "done" or "failed"
- [ ] **ORCH-03**: Each completed worker batch is git-committed with an iteration-tagged message
- [ ] **ORCH-04**: Blocked workers are detected and their blockers fed back to the Planner for re-planning
- [ ] **ORCH-05**: Final status and summary are printed to stdout on completion

### CLI

- [ ] **CLI-01**: CLI accepts a YAML spec file path as positional argument
- [ ] **CLI-02**: CLI accepts --max-iterations flag (default: 10)
- [ ] **CLI-03**: CLI requires ANTHROPIC_API_KEY environment variable (or .env file)
- [ ] **CLI-04**: CLI prints iteration progress to stdout (iteration N of M, current status)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Resilience

- **RESL-01**: Configurable worker concurrency (thread pool size as CLI flag)
- **RESL-02**: Run history persisted for cross-session comparison

### UX

- **UX-01**: Rich progress output with task-level detail
- **UX-02**: Spec schema linting/validation before build starts

### Extensibility

- **EXT-01**: Multi-provider LLM support (OpenAI, local models)
- **EXT-02**: Plugin/hook system for post-iteration actions (run tests, lint, format)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Web UI / dashboard | CLI is sufficient for developer audience; UI adds massive scope |
| Real-time streaming of agent outputs | Batch results are fine; streaming requires async architecture changes |
| Interactive "chat with spec" mode | Contradicts core value of unattended autonomy |
| Local LLM support | Lower instruction-following quality for structured JSON; doubles test surface |
| Monorepo / multi-repo workspaces | Single output directory for v1; multiplies complexity |
| Autonomous deployment / CI execution | Security boundary minefield; irreversible side effects |
| Per-agent persistent memory | Context window per-call is sufficient; memory adds hallucination surface |
| Natural-language spec input | Ambiguous specs produce ambiguous codebases; YAML is the quality gate |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SPEC-01 | Phase 1 | Pending |
| SPEC-02 | Phase 1 | Pending |
| SPEC-03 | Phase 1 | Pending |
| SPEC-04 | Phase 1 | Pending |
| SPEC-05 | Phase 1 | Pending |
| SPEC-06 | Phase 1 | Pending |
| SPEC-07 | Phase 5 | Pending |
| STATE-01 | Phase 1 | Complete |
| STATE-02 | Phase 1 | Complete |
| STATE-03 | Phase 1 | Complete |
| PLAN-01 | Phase 2 | Pending |
| PLAN-02 | Phase 2 | Pending |
| PLAN-03 | Phase 2 | Pending |
| PLAN-04 | Phase 2 | Pending |
| PLAN-05 | Phase 2 | Pending |
| WORK-01 | Phase 3 | Pending |
| WORK-02 | Phase 3 | Pending |
| WORK-03 | Phase 3 | Pending |
| WORK-04 | Phase 3 | Pending |
| WORK-05 | Phase 3 | Pending |
| WORK-06 | Phase 3 | Pending |
| SGEN-01 | Phase 4 | Pending |
| SGEN-02 | Phase 4 | Pending |
| SGEN-03 | Phase 4 | Pending |
| SGEN-04 | Phase 4 | Pending |
| VALD-01 | Phase 4 | Pending |
| VALD-02 | Phase 4 | Pending |
| VALD-03 | Phase 4 | Pending |
| VALD-04 | Phase 4 | Pending |
| VALD-05 | Phase 4 | Pending |
| VALD-06 | Phase 4 | Pending |
| ORCH-01 | Phase 5 | Pending |
| ORCH-02 | Phase 5 | Pending |
| ORCH-03 | Phase 5 | Pending |
| ORCH-04 | Phase 5 | Pending |
| ORCH-05 | Phase 5 | Pending |
| CLI-01 | Phase 5 | Pending |
| CLI-02 | Phase 5 | Pending |
| CLI-03 | Phase 5 | Pending |
| CLI-04 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 40 total
- Mapped to phases: 40
- Unmapped: 0

Note: The original coverage count of 30 was incorrect. Actual count is 40 (SPEC x7, STATE x3, PLAN x5, WORK x6, SGEN x4, VALD x6, ORCH x5, CLI x4).

---
*Requirements defined: 2026-03-15*
*Last updated: 2026-03-15 after roadmap creation — traceability populated*
