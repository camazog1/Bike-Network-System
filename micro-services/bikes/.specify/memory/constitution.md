<!--
SYNC IMPACT REPORT
==================
Version change: [placeholder] → 1.0.0 (initial ratification — all content new)
Modified principles: N/A (first write — replacing template placeholders)
Added sections:
  - I. Package Management
  - II. CQRS-Inspired Layered Architecture
  - III. REST API Standards
  - IV. Testing Discipline
  - V. Environment Management
  - Development Workflow
  - Governance
Removed sections: N/A
Templates requiring updates:
  - ✅ .specify/templates/plan-template.md — Constitution Check gates updated
  - ✅ .specify/templates/tasks-template.md — Path conventions updated for CQRS layout
  - ✅ .specify/templates/spec-template.md — No structural changes required
Follow-up TODOs: None — all placeholders resolved.
-->

# Bike Network System — Bikes Microservice Constitution

## Core Principles

### I. Package Management (NON-NEGOTIABLE)

All Python dependencies MUST be managed exclusively with `uv`.
`pip`, `poetry`, and `pipenv` are forbidden at every stage of development,
CI, and deployment. Every dependency MUST be declared in `pyproject.toml`.
`uv.lock` MUST be committed to version control and kept up to date.

**Rationale**: Reproducible, fast, single-tool dependency management eliminates
environment drift and onboarding friction across the team.

### II. CQRS-Inspired Layered Architecture (NON-NEGOTIABLE)

Routes MUST be split into two sub-packages:

- `routes/commands/` — state-mutating handlers (POST, PUT, PATCH, DELETE)
- `routes/queries/` — read-only handlers (GET only, no side effects)

Business logic MUST live exclusively in `services/`.
All database access MUST be encapsulated in `repositories/`.
The dependency direction is strictly unidirectional:

```
Routes → Services → Repositories → Database
```

No upward imports are permitted. A service MUST NOT import from `routes/`.
A repository MUST NOT import from `services/`. Violations fail code review.

**Rationale**: Separating read and write paths enables independent scaling,
testability, and unambiguous reasoning about side effects.

### III. REST API Standards (NON-NEGOTIABLE)

- All endpoints MUST use path-based versioning: `/api/v{n}/`
- HTTP status codes MUST comply with RFC 9110
- All error responses MUST use the following JSON envelope:

  ```json
  {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {}
  }
  ```

- Every collection endpoint MUST support pagination via `page` and `page_size`
  query parameters and MUST return total-count metadata in the response body

**Rationale**: Consistent contracts reduce client integration friction and
enable forward-compatible versioning without breaking existing consumers.

### IV. Testing Discipline (NON-NEGOTIABLE)

- `pytest` is the sole test runner; no alternatives are permitted
- `services/` and `repositories/` MUST maintain ≥ 80% line coverage at all times
- Unit tests MUST perform no I/O — no network calls, no filesystem reads, no
  database access; mock or stub at system boundaries only
- Integration tests MUST target a dedicated test database that is isolated
  from development and production databases

**Rationale**: High coverage on business logic and data access layers catches
regressions early; I/O-free unit tests remain fast and deterministic in CI.

### V. Environment Management (NON-NEGOTIABLE)

- All environment variables MUST be declared in a `.env` file at the project root
- `.env` MUST be listed in `.gitignore` and MUST NOT be committed
- A `.env.example` file containing every required key with empty values MUST
  be committed and kept synchronized whenever `.env` keys are added or removed
- Environment variables MUST be loaded at runtime; hard-coding values is forbidden

**Rationale**: Secrets stay out of version control while onboarding remains
frictionless — developers clone, copy `.env.example` to `.env`, and fill values.

## Development Workflow

### Project Structure

Every feature MUST follow this directory layout:

```
routes/
├── commands/     # POST, PUT, PATCH, DELETE handlers
└── queries/      # GET handlers — read-only, zero side effects

services/         # All business logic — no direct DB access permitted

repositories/     # All database access — no business logic permitted

tests/
├── unit/         # No I/O — mock/stub at all external boundaries
└── integration/  # Dedicated test database required
```

### PR Gates (checked on every pull request)

- [ ] No import from `routes/` inside `services/` or `repositories/`
- [ ] No import from `services/` inside `repositories/`
- [ ] All new endpoints versioned under `/api/v{n}/`
- [ ] All new collection endpoints include `page`/`page_size` pagination
- [ ] All error responses use the standard `code/message/details` envelope
- [ ] New environment variables reflected in `.env.example`
- [ ] `uv.lock` committed if `pyproject.toml` dependencies changed
- [ ] `services/` and `repositories/` coverage ≥ 80% after changes

## Governance

This constitution supersedes all other project conventions.
Any practice not covered here defaults to PEP 8 and FastAPI community guidelines.

**Amendment procedure**: Amendments require a pull request updating this file,
a version bump per the policy below, a Sync Impact Report (HTML comment at the
top of this file), and approval from at least one other developer. Affected
templates MUST be updated in the same PR.

**Versioning policy**:
- MAJOR: Backward-incompatible principle removals or redefinitions
- MINOR: New principle or section added, or materially expanded guidance
- PATCH: Clarifications, wording fixes, non-semantic refinements

**Compliance review**: Constitution gates MUST be checked in every PR review
and enforced in CI where automatable (coverage thresholds, import-order linting).

**Version**: 1.0.0 | **Ratified**: 2026-03-24 | **Last Amended**: 2026-03-24
