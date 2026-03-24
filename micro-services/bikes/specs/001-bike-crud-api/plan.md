# Implementation Plan: Bike CRUD API

**Branch**: `001-bike-crud-api` | **Date**: 2026-03-24 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-bike-crud-api/spec.md`

## Summary

Build a Flask 3 HTTP microservice exposing full CRUD operations on a `Bike` entity (Brand, Type, Colour, State) backed by MySQL 8.0. The service is containerised as a Docker image and deployed on Kubernetes. All request payloads are validated and all responses are serialised via Pydantic v2 models. The architecture follows the CQRS-inspired layered layout mandated by the constitution: `routes/commands/` + `routes/queries/` → `services/` → `repositories/` → MySQL via SQLAlchemy. Migrations are managed with Alembic (Flask-Migrate). Dependencies are managed exclusively with `uv`.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: Flask 3, Flask-SQLAlchemy 3, Flask-Migrate, Pydantic v2, PyMySQL, pytest, pytest-flask
**Storage**: MySQL 8.0
**Testing**: pytest + pytest-flask; unit tests (no I/O), integration tests (dedicated test database)
**Target Platform**: Linux container (Docker image); deployed on Kubernetes
**Project Type**: CQRS microservice (web-service)
**Performance Goals**: All CRUD endpoints respond within 1 second under normal load; listing supports ≥ 100 concurrent requests without data corruption
**Constraints**: Stateless service — all state in MySQL; horizontal scaling via Kubernetes replicas; all credentials supplied via environment variables
**Scale/Scope**: Initial target ≥ 100 concurrent requests; single MySQL instance for this phase

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] All dependencies declared in `pyproject.toml`; `uv` is the only tool used
- [x] Route handlers split into `routes/commands/` (mutating) and `routes/queries/` (read-only)
- [x] Business logic confined to `services/`; DB access confined to `repositories/`
- [x] No upward imports: `routes` → `services` → `repositories` → DB (strictly one-way)
- [x] All endpoints versioned under `/api/v1/`
- [x] All error responses use `{"code": ..., "message": ..., "details": ...}` envelope *(supersedes spec clarification Q3 which proposed `{"error": "..."}` — see Complexity Tracking)*
- [x] All collection endpoints include pagination (`page`, `page_size`, total count)
- [x] Unit tests contain no I/O; integration tests use a dedicated test database
- [x] `services/` and `repositories/` coverage target ≥ 80%
- [x] `.env.example` updated for all new environment variables

## Project Structure

### Documentation (this feature)

```text
specs/001-bike-crud-api/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output (/speckit.tasks — not created here)
```

### Source Code (repository root)

```text
app/
├── __init__.py              # Flask app factory (create_app)
├── config.py                # Configuration class — reads all values from env vars
├── models/
│   ├── __init__.py
│   └── bike.py              # SQLAlchemy ORM model: Bike
├── schemas/
│   ├── __init__.py
│   └── bike.py              # Pydantic v2 schemas: BikeCreate, BikeUpdate, BikeResponse, BikeListResponse
├── repositories/
│   ├── __init__.py
│   └── bike_repository.py   # All DB access: create, get_by_id, list (with filters + pagination), update, delete
├── services/
│   ├── __init__.py
│   └── bike_service.py      # Business logic: orchestrates repository calls, raises domain errors
└── routes/
    ├── __init__.py
    ├── commands/
    │   ├── __init__.py
    │   └── bikes.py         # POST /api/v1/bikes, PUT /api/v1/bikes/<id>, DELETE /api/v1/bikes/<id>
    └── queries/
        ├── __init__.py
        └── bikes.py         # GET /api/v1/bikes, GET /api/v1/bikes/<id>

migrations/                  # Alembic migrations managed via Flask-Migrate
└── versions/

tests/
├── conftest.py              # Fixtures: Flask test app, test client, test DB session
├── unit/
│   ├── test_bike_service.py    # No I/O — mocks BikeRepository
│   └── test_bike_repository.py # No I/O — mocks SQLAlchemy session
└── integration/
    └── test_bikes_api.py    # Full HTTP cycle against dedicated test MySQL database

main.py                      # Entry point: `from app import create_app; app = create_app()`
pyproject.toml               # uv-managed dependencies + project metadata
uv.lock                      # Committed lockfile
.env.example                 # All required env var keys with empty values
Dockerfile                   # Multi-stage build (builder + runtime)
docker-compose.yml           # Local dev stack: app + MySQL 8.0
```

**Structure Decision**: Option 1 (CQRS microservice). Single `Bike` entity — no sub-package nesting required. `models/` holds SQLAlchemy ORM definitions; `schemas/` holds Pydantic v2 contracts — both are pure declarations, not logic, and sit outside the routes/services/repositories dependency chain.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Flask instead of FastAPI (constitution defaults to FastAPI community guidelines) | Flask was explicitly specified by the user as the required web framework | FastAPI was not requested; Flask is a production-grade Python web framework and fully supports the CQRS structure + Pydantic integration required by the constitution |
| Error envelope: spec Q3 clarification proposed `{"error": "..."}` but constitution mandates `{"code", "message", "details"}` | Constitution is the higher-order rule and supersedes spec-level clarifications | A bare `{"error": "..."}` envelope would break consistency with all other microservices in the platform and fail the PR gate check |
