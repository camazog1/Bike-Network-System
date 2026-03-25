# Research: Bike CRUD API

**Branch**: `001-bike-crud-api` | **Date**: 2026-03-24

---

## 1. Web Framework

**Decision**: Flask 3 (latest stable)
**Rationale**: Explicitly specified by the user. Flask 3 is production-ready, widely deployed in microservice architectures, and fully supports Pydantic v2 alongside SQLAlchemy via manual integration (no native dependency injection, but the CQRS layered structure compensates).
**Alternatives considered**:
- FastAPI — constitution defaults to it; rejected because user explicitly chose Flask
- Flask 2.x — superseded by Flask 3; no reason to use older version

---

## 2. ORM & Database Access

**Decision**: Flask-SQLAlchemy 3 + SQLAlchemy 2 (async-capable, but sync mode used here for simplicity)
**Rationale**: Flask-SQLAlchemy is the de-facto ORM integration for Flask, providing session lifecycle management tied to the request context. SQLAlchemy 2 introduces a cleaner `select()`-style query API that is more testable and explicit than the legacy `Model.query` pattern.
**Alternatives considered**:
- Raw PyMySQL / SQL strings — rejected; too brittle, no migration support, harder to test
- Tortoise ORM / SQLModel — rejected; less mature Flask integration, less community precedent

---

## 3. Database Migrations

**Decision**: Flask-Migrate (wraps Alembic)
**Rationale**: Flask-Migrate adds `flask db init / migrate / upgrade` CLI commands on top of Alembic, the standard SQLAlchemy migration engine. Migration files are auto-generated from model diffs and committed to version control. Running `flask db upgrade` at container startup keeps the schema in sync automatically.
**Alternatives considered**:
- Raw Alembic without Flask-Migrate — works but requires more boilerplate wiring; Flask-Migrate is the simpler wrapper with no downsides
- Flyway / Liquibase — JVM-based, not idiomatic for Python projects

---

## 4. MySQL Driver

**Decision**: PyMySQL (pure Python)
**Rationale**: PyMySQL requires no native C extensions, making it trivially installable in a minimal Linux Docker image without build tools. It is fully compatible with SQLAlchemy via the `mysql+pymysql://` connection string.
**Alternatives considered**:
- mysqlclient — faster (C extension) but requires `libmysqlclient-dev` in the Docker image, adding image size and build complexity
- mysql-connector-python — official Oracle driver but slower and larger than PyMySQL for this use case

---

## 5. Request Validation & Response Serialisation

**Decision**: Pydantic v2
**Rationale**: Pydantic v2 provides fast, type-annotated validation with excellent enum support (critical for `BikeType` and `BikeState`). In Flask, Pydantic is used manually: parse `request.get_json()` with `BikeCreate.model_validate(data)`, and serialise with `bike_response.model_dump()` passed to `jsonify()`. This satisfies the user requirement that "all responses should be Pydantic models parsed to JSON".
**Alternatives considered**:
- Marshmallow — older Flask serialisation library; less ergonomic than Pydantic v2 type annotations
- Flask-Pydantic — thin wrapper; adds a dependency without meaningful benefit over manual integration

---

## 6. Package Management

**Decision**: `uv` with `pyproject.toml` (NON-NEGOTIABLE per constitution)
**Rationale**: `uv` is mandated by the constitution as the sole dependency management tool. `uv.lock` is committed to ensure reproducible installs in CI and Docker builds. `pip` and `poetry` are forbidden.
**Docker integration**: Dockerfile uses `uv sync --frozen --no-dev` in the runtime stage to install only production dependencies from the lockfile.

---

## 7. Testing

**Decision**: pytest + pytest-flask
**Rationale**: `pytest` is mandated by the constitution. `pytest-flask` provides the `app` fixture and `client` fixture pattern for Flask. Unit tests mock `BikeRepository` using `unittest.mock.MagicMock` — no I/O permitted. Integration tests spin up against a dedicated test MySQL database (configured via `DATABASE_TEST_URL` env var); the schema is applied via `flask db upgrade` before the test session.
**Coverage**: `pytest-cov` enforces ≥ 80% on `services/` and `repositories/` via `--cov-fail-under=80`.
**Alternatives considered**:
- unittest — rejected; pytest is constitutionally mandated and more ergonomic
- TestContainers — useful for spinning up MySQL in CI; considered optional and can be added later without architectural changes

---

## 8. Containerisation

**Decision**: Multi-stage Dockerfile (builder + runtime)
**Rationale**: A multi-stage build keeps the final image lean: the builder stage installs `uv` and resolves dependencies; the runtime stage copies only the virtual environment and application source. Base image: `python:3.12-slim` for minimal attack surface.
**Key patterns**:
- `COPY uv.lock pyproject.toml ./` before `COPY app/ ./app/` to maximise Docker layer caching
- `uv sync --frozen --no-dev` installs from lockfile without dev dependencies
- `CMD ["uv", "run", "flask", "run", "--host=0.0.0.0", "--port=8080"]` (or gunicorn for production)
- Non-root user for security

---

## 9. Kubernetes Deployment

**Decision**: Standard Deployment + ClusterIP Service; env vars via Secrets (DB credentials) and ConfigMap (non-sensitive config)
**Rationale**: The service is stateless — all state lives in MySQL — so horizontal scaling via `replicas` is trivial. DB connection string components are injected via a Kubernetes Secret to keep credentials out of image layers and ConfigMaps. Health checks use `/api/v1/health` (a lightweight GET endpoint returning 200).
**Key patterns**:
- `readinessProbe` and `livenessProbe` on the health endpoint prevent traffic to non-ready pods
- `migrations` run as a Kubernetes Job or init container before the Deployment rolls out
- `imagePullPolicy: Always` for rolling updates

---

## 10. Error Handling

**Decision**: Constitution-mandated envelope `{"code": "...", "message": "...", "details": {...}}`
**Rationale**: This supersedes the spec clarification Q3 suggestion of `{"error": "..."}`. The constitution is the higher-order rule; consistent error envelopes across all microservices reduce client integration friction. A Flask `@app.errorhandler` registers handlers for 400, 404, 422, and 500.
**HTTP status mapping**:
- `404` — bike not found
- `422` — Pydantic validation failure (unprocessable entity)
- `400` — malformed request (non-JSON body, etc.)
- `500` — unhandled server error (logged, generic message returned)

---

## 11. Environment Variables

All required keys (to be reflected in `.env.example`):

| Key | Description |
|-----|-------------|
| `DATABASE_URL` | SQLAlchemy connection string, e.g. `mysql+pymysql://user:pass@host:3306/bikes` |
| `DATABASE_TEST_URL` | Separate test database URL (used only by pytest integration tests) |
| `FLASK_ENV` | `development` or `production` |
| `FLASK_SECRET_KEY` | Flask session secret (required even for API-only apps) |
| `PORT` | Container port (default 8080) |
