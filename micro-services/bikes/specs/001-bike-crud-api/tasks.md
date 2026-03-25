# Tasks: Bike CRUD API

**Input**: Design documents from `/specs/001-bike-crud-api/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/api.md ✅

**Tests**: Included — pytest was explicitly requested in the implementation plan.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US4, maps to spec.md)
- All file paths are relative to the repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize project files, package management, and container configuration before any code is written.

- [X] T001 Create project directory structure: `app/`, `app/models/`, `app/schemas/`, `app/repositories/`, `app/services/`, `app/routes/`, `app/routes/commands/`, `app/routes/queries/`, `app/utils/`, `migrations/`, `tests/`, `tests/unit/`, `tests/integration/`
- [X] T002 Create `pyproject.toml` declaring all dependencies with `uv` (Flask 3, Flask-SQLAlchemy 3, Flask-Migrate, Pydantic v2, PyMySQL, pytest, pytest-flask, pytest-cov); run `uv sync` to generate `uv.lock`
- [X] T003 [P] Create `.env.example` with all five required keys (`DATABASE_URL`, `DATABASE_TEST_URL`, `FLASK_ENV`, `FLASK_SECRET_KEY`, `PORT`); add `.env` to `.gitignore`
- [X] T004 [P] Create `Dockerfile` as a multi-stage build (builder stage: install uv + sync deps from lockfile; runtime stage: copy venv + app source, non-root user, expose PORT, CMD with flask run)
- [X] T005 [P] Create `docker-compose.yml` defining two services: `mysql` (image: mysql:8.0, env vars, volume for persistence) and `app` (build: ., env_file: .env, depends_on: mysql, port mapping)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core application wiring — Flask factory, DB integration, error handling, shared utilities, ORM model, Pydantic schemas, and database migration. **No user story work can begin until this phase is complete.**

**⚠️ CRITICAL**: All phases 3–6 depend on this phase being fully complete.

- [X] T006 Create `app/config.py` with a `Config` class that reads `DATABASE_URL`, `FLASK_SECRET_KEY`, `FLASK_ENV`, and `PORT` from environment variables using `os.environ`; add a `TestingConfig` subclass that reads `DATABASE_TEST_URL` and sets `TESTING = True`
- [X] T007 Create `app/__init__.py` with a `create_app(config=None)` factory: initialise Flask, load config, initialise Flask-SQLAlchemy (`db`), initialise Flask-Migrate, register error handlers from `app/errors.py`, register blueprints from `routes/commands/` and `routes/queries/`
- [X] T008 [P] Create `app/errors.py` implementing Flask `@app.errorhandler` functions for HTTP 400, 404, 422, and 500; all responses MUST use the `{"code": "...", "message": "...", "details": {...}}` envelope and return `application/json`
- [X] T009 [P] Create `app/utils/pagination.py` with a `parse_pagination(args)` helper that extracts `page` (default 1, min 1) and `page_size` (default 20, min 1, max 100) from Flask `request.args`; returns `(page, page_size, offset)`
- [X] T010 Create `main.py` as the application entry point: `from app import create_app; app = create_app()`
- [X] T011 Create `app/models/__init__.py` (empty) and `app/models/bike.py` defining `BikeType(enum.Enum)` (`Cross`, `Mountain`, `Street`), `BikeState(enum.Enum)` (`Rented`, `Free`), and `Bike(db.Model)` SQLAlchemy model with columns: `id` (String(36) PK, default `lambda: str(uuid.uuid4())`), `brand` (String 100, NOT NULL), `type` (Enum BikeType, NOT NULL), `colour` (String 50, NOT NULL), `state` (Enum BikeState, NOT NULL, default Free)
- [X] T012 [P] Create `app/schemas/__init__.py` (empty) and `app/schemas/bike.py` with four Pydantic v2 models: `BikeCreate` (brand, type, colour, state with default Free), `BikeUpdate` (all fields Optional), `BikeResponse` (id: str — UUID v4 string, brand, type, colour, state; `model_config = {"from_attributes": True}`), `BikeListResponse` (bikes: List[BikeResponse], total: int, page: int, page_size: int)
- [X] T013 Run `uv run flask db init` to initialise the `migrations/` Alembic directory; verify `migrations/env.py` and `migrations/alembic.ini` are created
- [X] T014 Run `uv run flask db migrate -m "create bikes table"` to auto-generate the initial migration from the `Bike` model; review the generated file in `migrations/versions/` to confirm it creates the `bikes` table with all columns and MySQL ENUM types
- [X] T015 Run `uv run flask db upgrade` against the development database; verify the `bikes` table exists with the correct schema using a MySQL client
- [X] T016 Create `tests/conftest.py` with: an `app` fixture that calls `create_app(TestingConfig)`, a `client` fixture using `app.test_client()`, and a `db_session` fixture that creates all tables before the test session and drops them after (using `DATABASE_TEST_URL`)

**Checkpoint**: Foundation ready — all user story phases can now begin.

---

## Phase 3: User Story 1 — Register a New Bike (Priority: P1) 🎯 MVP

**Goal**: Enable creation of a new bike with full field validation; returns the persisted bike with its system-assigned ID.

**Independent Test**: `POST /api/v1/bikes` with valid payload returns 201 with all fields including `id`; invalid enum values or missing fields return 422.

### Tests for User Story 1

> **Write these tests FIRST — ensure they FAIL before implementation begins.**

- [X] T017 [P] [US1] Write unit test for `BikeService.create_bike()` in `tests/unit/test_bike_service.py`: mock `BikeRepository`; assert correct repository method called; assert `BikeResponse` returned on success; assert `ValidationError` raised on invalid enum values
- [X] T018 [P] [US1] Write integration test for `POST /api/v1/bikes` in `tests/integration/test_bikes_api.py`: test valid creation returns 201 + full bike JSON; test missing `brand` returns 422 with `{"code": "VALIDATION_ERROR", ...}`; test invalid `type` value returns 422

### Implementation for User Story 1

- [X] T019 [US1] Create `app/repositories/__init__.py` (empty) and `app/repositories/bike_repository.py` with `BikeRepository` class; implement `create(data: BikeCreate) -> Bike` method: construct `Bike` ORM instance, add to session, commit, return the instance
- [X] T020 [US1] Create `app/services/__init__.py` (empty) and `app/services/bike_service.py` with `BikeService` class (receives `BikeRepository` via constructor injection); implement `create_bike(data: BikeCreate) -> BikeResponse`: validate input, call repository, return `BikeResponse.model_validate(orm_instance)` (depends on T019)
- [X] T021 [US1] Create `app/routes/commands/__init__.py` and `app/routes/commands/bikes.py` with a Flask `Blueprint`; implement `POST /api/v1/bikes` handler: parse body with `BikeCreate.model_validate(request.get_json())`, call `BikeService.create_bike()`, return `jsonify(response.model_dump())` with status 201; register blueprint in `app/__init__.py` (depends on T020)

**Checkpoint**: `POST /api/v1/bikes` is fully functional. Run `uv run pytest tests/unit/test_bike_service.py tests/integration/test_bikes_api.py::test_create_bike -v` to verify US1 independently.

---

## Phase 4: User Story 2 — Retrieve Bike Information (Priority: P1)

**Goal**: Enable querying of individual bikes by ID and listing of the full fleet with optional State/Type filters and pagination.

**Independent Test**: `GET /api/v1/bikes` returns `{"bikes": [...], "total": N, "page": 1, "page_size": 20}`; `GET /api/v1/bikes/<uuid>` returns single bike; `?state=Free&type=Mountain` filters correctly; non-existent UUID returns 404.

### Tests for User Story 2

> **Write these tests FIRST — ensure they FAIL before implementation begins.**

- [X] T022 [P] [US2] Write unit tests for `BikeService.get_bike()` and `BikeService.list_bikes()` in `tests/unit/test_bike_service.py`: mock `BikeRepository`; assert 404 error raised when bike not found; assert filters are passed to repository; assert `BikeListResponse` pagination fields are correct
- [X] T023 [P] [US2] Write integration tests for `GET /api/v1/bikes` and `GET /api/v1/bikes/<id>` in `tests/integration/test_bikes_api.py`: test listing with no filters, with `?state=Free`, with `?type=Mountain`, with combined filters; test get-by-id success and 404; test empty listing returns `{"bikes": [], "total": 0, ...}`

### Implementation for User Story 2

- [X] T024 [US2] Add `get_by_id(bike_id: int) -> Bike | None` and `list(state: BikeState | None, type: BikeType | None, offset: int, limit: int) -> tuple[list[Bike], int]` methods to `app/repositories/bike_repository.py`; `list()` applies optional WHERE filters and returns both the page of results and the total count
- [X] T025 [US2] Add `get_bike(bike_id: int) -> BikeResponse` and `list_bikes(state, type, page, page_size) -> BikeListResponse` to `app/services/bike_service.py`; `get_bike()` raises a 404 `HTTPException` if not found; `list_bikes()` uses pagination helper and returns `BikeListResponse` (depends on T024)
- [X] T026 [US2] Create `app/routes/queries/__init__.py` and `app/routes/queries/bikes.py` with a Flask `Blueprint`; implement `GET /api/v1/bikes` (reads `state`, `type`, `page`, `page_size` from query args, returns `BikeListResponse`) and `GET /api/v1/bikes/<string:id>` (returns single `BikeResponse` or 404); register blueprint in `app/__init__.py` (depends on T025)
- [X] T027 [P] [US2] Implement `GET /api/v1/health` endpoint in `app/routes/queries/health.py` returning `{"status": "ok"}` with 200; register blueprint in `app/__init__.py` (Kubernetes liveness/readiness probe)

**Checkpoint**: All GET endpoints functional. Run `uv run pytest tests/unit/test_bike_service.py tests/integration/test_bikes_api.py -k "retrieve or list or get or health" -v`.

---

## Phase 5: User Story 3 — Update Bike Details or State (Priority: P2)

**Goal**: Enable partial or full update of a bike's fields, most critically its state (Free ↔ Rented) to support the rental lifecycle.

**Independent Test**: `PUT /api/v1/bikes/1 {"state": "Rented"}` updates state and returns full updated bike; subsequent `GET /api/v1/bikes/1` reflects the change; invalid `state` value returns 422; non-existent ID returns 404.

### Tests for User Story 3

> **Write these tests FIRST — ensure they FAIL before implementation begins.**

- [X] T028 [P] [US3] Write unit test for `BikeService.update_bike()` in `tests/unit/test_bike_service.py`: mock repository; assert 404 raised for missing bike; assert only provided fields are updated (partial update); assert updated `BikeResponse` returned
- [X] T029 [P] [US3] Write integration test for `PUT /api/v1/bikes/<id>` in `tests/integration/test_bikes_api.py`: test state transition Free→Rented; test partial update (only `colour`); test invalid `type` value returns 422; test non-existent ID returns 404

### Implementation for User Story 3

- [X] T030 [US3] Add `update(bike_id: int, data: BikeUpdate) -> Bike | None` method to `app/repositories/bike_repository.py`; only update fields that are not `None` in `data`; commit and return the updated instance
- [X] T031 [US3] Add `update_bike(bike_id: int, data: BikeUpdate) -> BikeResponse` to `app/services/bike_service.py`; raise 404 if bike not found; call repository update; return `BikeResponse` (depends on T030)
- [X] T032 [US3] Implement `PUT /api/v1/bikes/<string:id>` handler in `app/routes/commands/bikes.py`: parse body with `BikeUpdate.model_validate(request.get_json())`, call `BikeService.update_bike()`, return `jsonify(response.model_dump())` with 200 (depends on T031)

**Checkpoint**: `PUT /api/v1/bikes/<id>` functional. Run `uv run pytest -k "update" -v`.

---

## Phase 6: User Story 4 — Remove a Bike from the Fleet (Priority: P3)

**Goal**: Enable permanent deletion of a bike record by ID; supports fleet decommissioning workflows.

**Independent Test**: `DELETE /api/v1/bikes/1` returns 204 No Content; subsequent `GET /api/v1/bikes/1` returns 404; deleting a non-existent ID returns 404 without side effects.

### Tests for User Story 4

> **Write these tests FIRST — ensure they FAIL before implementation begins.**

- [X] T033 [P] [US4] Write unit test for `BikeService.delete_bike()` in `tests/unit/test_bike_service.py`: mock repository; assert 404 raised for missing bike; assert repository delete called exactly once; assert no return value
- [X] T034 [P] [US4] Write integration test for `DELETE /api/v1/bikes/<id>` in `tests/integration/test_bikes_api.py`: test successful delete returns 204 empty body; test that deleted bike no longer appears in GET; test delete non-existent ID returns 404

### Implementation for User Story 4

- [X] T035 [US4] Add `delete(bike_id: int) -> bool` method to `app/repositories/bike_repository.py`: fetch by ID, delete from session, commit; return `True` if deleted, `False` if not found
- [X] T036 [US4] Add `delete_bike(bike_id: int) -> None` to `app/services/bike_service.py`; raise 404 if repository returns `False`; return no content (depends on T035)
- [X] T037 [US4] Implement `DELETE /api/v1/bikes/<string:id>` handler in `app/routes/commands/bikes.py`: call `BikeService.delete_bike()`, return empty response with 204 (depends on T036)

**Checkpoint**: All four CRUD operations fully functional. Run `uv run pytest -v` to confirm all stories pass.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Coverage enforcement, repository-level unit tests, and full-stack validation.

- [X] T038 [P] Create `tests/unit/test_bike_repository.py` with unit tests for all `BikeRepository` methods using a mocked SQLAlchemy session; assert SQL expressions, commit calls, and return values — no I/O permitted
- [X] T039 [P] Run full test suite with coverage enforcement: `uv run pytest --cov=app/services --cov=app/repositories --cov-report=term-missing --cov-fail-under=80 -v`; fix any gaps until ≥ 80% is achieved
- [X] T040 [P] Validate Docker build and compose stack: `docker-compose up --build`; confirm `GET /api/v1/health` returns 200; confirm `POST /api/v1/bikes` creates a record
- [X] T041 Validate `quickstart.md` steps end-to-end on a clean environment; update any step that is out of date

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: No dependencies — start immediately
- **Phase 2 (Foundational)**: Depends on Phase 1 — **BLOCKS all user story phases**
- **Phase 3 (US1)**: Depends on Phase 2 completion
- **Phase 4 (US2)**: Depends on Phase 2 completion — can run in parallel with Phase 3
- **Phase 5 (US3)**: Depends on Phase 2 completion — can run in parallel with Phases 3 & 4
- **Phase 6 (US4)**: Depends on Phase 2 completion — can run in parallel with Phases 3, 4 & 5
- **Phase 7 (Polish)**: Depends on all desired user story phases being complete

### User Story Dependencies

- **US1 (P1)**: No dependency on other stories — first MVP increment
- **US2 (P1)**: No dependency on US1 (reads don't need create to exist at the code level); integrates naturally when both are complete
- **US3 (P2)**: No dependency on US1/US2 at the code level; the `update()` path in the repository is independent
- **US4 (P3)**: No dependency on other stories at the code level; `delete()` is a standalone path

### Within Each User Story

1. Tests FIRST → ensure they FAIL
2. Repository method(s)
3. Service method(s) (depends on repository)
4. Route handler(s) (depends on service)
5. Run tests → confirm they PASS

---

## Parallel Opportunities

### Phase 1 — run together

```
T001 (structure) → then T002, T003, T004, T005 in parallel
```

### Phase 2 — run in waves

```
Wave 1 (parallel): T006, T008, T009, T012
Wave 2: T007 (needs T006), T011 (needs T006+T007)
Wave 3: T013 → T014 → T015 (sequential — migration workflow)
Wave 4: T016 (needs T015)
```

### Phase 3 (US1)

```
Wave 1 (parallel): T017, T018 (tests — write and confirm FAIL)
Wave 2 (sequential): T019 → T020 → T021
Wave 3: confirm tests pass
```

### Phase 4 (US2)

```
Wave 1 (parallel): T022, T023, T027 (tests + health endpoint)
Wave 2 (sequential): T024 → T025 → T026
Wave 3: confirm tests pass
```

---

## Implementation Strategy

### MVP First (User Story 1 only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (**critical blocker**)
3. Complete Phase 3: US1 — Register a New Bike
4. **STOP and VALIDATE**: `POST /api/v1/bikes` works end-to-end
5. Deploy / demo if ready

### Incremental Delivery

1. Phase 1 + Phase 2 → foundation ready
2. Phase 3 (US1) → create works → **MVP**
3. Phase 4 (US2) → reads + filtering work → **usable by FE**
4. Phase 5 (US3) → state updates work → **rental lifecycle complete**
5. Phase 6 (US4) → deletion works → **full CRUD**
6. Phase 7 → coverage enforced, Docker validated → **production-ready**

### Parallel Team Strategy

With two developers after Phase 2 is done:

- **Developer A**: Phase 3 (US1: Register) → Phase 5 (US3: Update) → Phase 6 (US4: Delete) — all mutating operations in `routes/commands/`
- **Developer B**: Phase 4 (US2: Retrieve) — all read operations in `routes/queries/`, filtering, pagination

---

## Notes

- `[P]` = different files, no incomplete task dependencies — safe to run concurrently
- `[USn]` label maps task to a specific user story for traceability
- Tests must be written before implementation and confirmed to FAIL first
- Each story phase is a complete, independently deployable increment
- Commit after each phase checkpoint at minimum
- `uv` is the only permitted package management tool — never use `pip install`
- Error envelope `{"code", "message", "details"}` is mandatory on all non-2xx responses (constitution rule)
