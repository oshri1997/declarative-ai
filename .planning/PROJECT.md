# Declarative AI Build System

## What This Is

A CLI tool that takes a YAML spec describing a desired codebase and autonomously builds it using a closed-loop multi-agent system. Four specialized Claude agents (Planner, Worker, State Generator, Validator) iterate until the generated codebase matches the spec or max iterations are reached. Each iteration is git-committed for auditability and rollback.

## Core Value

Given a declarative YAML spec, the system produces a working codebase that matches the spec — automatically, with no human intervention during the build loop.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] CLI accepts a YAML spec file and runs the full build loop
- [ ] Planner Agent decomposes spec into a dependency-aware task graph
- [ ] Worker Agents execute tasks in parallel via thread pool
- [ ] Workers write real files to disk (current directory), each batch git-committed
- [ ] State Generator reads the codebase and produces a structured snapshot matching spec schema
- [ ] Validator Agent diffs current state against desired spec and emits gap report
- [ ] Loop continues until validator confirms full alignment or max_iterations reached
- [ ] Planner produces only delta tasks on subsequent iterations (not full re-plan)
- [ ] Blocked workers are detected and their blockers resolved by re-planning
- [ ] All agent communication uses structured JSON (no prose in agent outputs)
- [ ] YAML spec format supports any codebase type (APIs, UI, models, config)
- [ ] Shared state object tracks iteration, task graph, codebase snapshot, gap report, status

### Out of Scope

- Web UI or dashboard — CLI only for v1
- Local LLM support — Claude API only for v1
- Real-time streaming of agent outputs — batch results are fine
- Multi-repo or monorepo workspace support — single output directory
- Spec validation/linting tool — users write valid YAML

## Context

- Each agent is a Claude API call with a role-specific system prompt
- The orchestrator is Python, managing the loop, file I/O, and agent coordination
- Worker parallelism uses Python threads (thread pool for concurrent Claude API calls)
- Git-backed: each iteration batch commits to a local repo for rollback capability
- The desired spec is YAML — structured enough for reliable agent parsing, readable enough for humans to author
- The spec schema covers: APIs, components, data models, configuration — language/framework agnostic
- Output lands in the current working directory

## Constraints

- **API**: Claude API (Anthropic SDK for Python) — all agent calls go through this
- **Language**: Python 3.x for the orchestrator
- **Parallelism**: Thread pool for worker agents (Claude API is I/O-bound)
- **Output**: Files written to current directory, git-committed per batch
- **Spec format**: YAML with structured fields and natural language descriptions

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| YAML for spec format | Best balance of structure (agents parse reliably) and readability (humans can author) | — Pending |
| Thread pool for parallelism | Claude API calls are I/O-bound; threads are simpler than multiprocessing for this | — Pending |
| Git-backed iterations | Each batch committed — enables rollback, auditability, and diffing between iterations | — Pending |
| CLI-only interface | Simplest delivery for v1; library extraction possible later | — Pending |
| Claude API exclusively | Consistent agent quality; multi-provider adds complexity without clear v1 value | — Pending |

---
*Last updated: 2026-03-15 after initialization*
