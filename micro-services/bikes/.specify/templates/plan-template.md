# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]
**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

[Extract from feature spec: primary requirement + technical approach from research]

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: [e.g., Python 3.11, Swift 5.9, Rust 1.75 or NEEDS CLARIFICATION]  
**Primary Dependencies**: [e.g., FastAPI, UIKit, LLVM or NEEDS CLARIFICATION]  
**Storage**: [if applicable, e.g., PostgreSQL, CoreData, files or N/A]  
**Testing**: [e.g., pytest, XCTest, cargo test or NEEDS CLARIFICATION]  
**Target Platform**: [e.g., Linux server, iOS 15+, WASM or NEEDS CLARIFICATION]
**Project Type**: [e.g., library/cli/web-service/mobile-app/compiler/desktop-app or NEEDS CLARIFICATION]  
**Performance Goals**: [domain-specific, e.g., 1000 req/s, 10k lines/sec, 60 fps or NEEDS CLARIFICATION]  
**Constraints**: [domain-specific, e.g., <200ms p95, <100MB memory, offline-capable or NEEDS CLARIFICATION]  
**Scale/Scope**: [domain-specific, e.g., 10k users, 1M LOC, 50 screens or NEEDS CLARIFICATION]

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [ ] All dependencies declared in `pyproject.toml`; `uv` is the only tool used
- [ ] Route handlers split into `routes/commands/` (mutating) and `routes/queries/` (read-only)
- [ ] Business logic confined to `services/`; DB access confined to `repositories/`
- [ ] No upward imports: `routes` → `services` → `repositories` → DB (strictly one-way)
- [ ] All endpoints versioned under `/api/v{n}/`
- [ ] All error responses use `{"code": ..., "message": ..., "details": ...}` envelope
- [ ] All collection endpoints include pagination (`page`, `page_size`, total count)
- [ ] Unit tests contain no I/O; integration tests use a dedicated test database
- [ ] `services/` and `repositories/` coverage target ≥ 80%
- [ ] `.env.example` updated for any new environment variables

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
# [REMOVE IF UNUSED] Option 1: CQRS microservice (DEFAULT for this project)
routes/
├── commands/    # POST, PUT, PATCH, DELETE handlers
└── queries/     # GET handlers — read-only, no side effects

services/        # Business logic only — no direct DB access

repositories/    # DB access only — no business logic

tests/
├── unit/        # No I/O permitted
└── integration/ # Dedicated test database required

# [REMOVE IF UNUSED] Option 2: Feature sub-package (when feature is large)
routes/
├── commands/
│   └── [feature]/
└── queries/
    └── [feature]/

services/
└── [feature]/

repositories/
└── [feature]/

tests/
├── unit/
│   └── [feature]/
└── integration/
    └── [feature]/
```

**Structure Decision**: [Document the selected structure and reference the real
directories captured above]

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
