# Quickstart: Bike CRUD API

**Branch**: `001-bike-crud-api` | **Date**: 2026-03-24

---

## Prerequisites

- [uv](https://docs.astral.sh/uv/) installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- Docker + Docker Compose
- Python 3.12 (uv will install it automatically if missing)

---

## 1. Environment Setup

```bash
cp .env.example .env
```

Edit `.env` and fill in the required values:

```env
DATABASE_URL=mysql+pymysql://bikes_user:bikes_pass@localhost:3306/bikes_db
DATABASE_TEST_URL=mysql+pymysql://bikes_user:bikes_pass@localhost:3306/bikes_test_db
FLASK_ENV=development
FLASK_SECRET_KEY=change-me-in-production
PORT=8080
```

---

## 2. Install Dependencies

```bash
uv sync
```

This installs all dependencies from `uv.lock` into a local virtual environment. Do not use `pip install`.

---

## 3. Start the Local Database

```bash
docker-compose up -d mysql
```

This starts a MySQL 8.0 container on port 3306 with the databases and credentials matching `.env.example`.

---

## 4. Run Migrations

```bash
uv run flask db upgrade
```

Applies all pending Alembic migrations to create the `bikes` table.

---

## 5. Start the Development Server

```bash
uv run flask run --host=0.0.0.0 --port=8080
```

The API is available at `http://localhost:8080/api/v1/`.

---

## 6. Run Tests

**Unit tests only (no database required)**:
```bash
uv run pytest tests/unit/ -v
```

**Integration tests (requires running MySQL)**:
```bash
uv run pytest tests/integration/ -v
```

**All tests with coverage report**:
```bash
uv run pytest --cov=app/services --cov=app/repositories --cov-fail-under=80 -v
```

---

## 7. Build & Run the Docker Image

```bash
# Build
docker build -t bike-service:local .

# Run (with env vars)
docker run --env-file .env -p 8080:8080 bike-service:local
```

---

## 8. Full Local Stack (App + MySQL)

```bash
docker-compose up --build
```

The app will run migrations automatically on startup and then serve on `http://localhost:8080`.

---

## 9. Kubernetes Deployment (outline)

1. Build and push the image to your container registry.
2. Apply the `Secret` with `DATABASE_URL` and `FLASK_SECRET_KEY`.
3. Apply the `ConfigMap` with `FLASK_ENV` and `PORT`.
4. Deploy the `Job` (or init container) to run `flask db upgrade` against the production database.
5. Apply the `Deployment` and `Service` manifests.
6. Verify readiness: `kubectl get pods -l app=bike-service`

Health probe endpoint: `GET /api/v1/health` → `200 {"status": "ok"}`

---

## Quick API Reference

| Method   | Path                  | Description                        |
|----------|-----------------------|------------------------------------|
| `POST`   | `/api/v1/bikes`       | Create a new bike                  |
| `GET`    | `/api/v1/bikes`       | List bikes (filters + pagination)  |
| `GET`    | `/api/v1/bikes/{id}`  | Get a single bike by ID            |
| `PUT`    | `/api/v1/bikes/{id}`  | Update a bike                      |
| `DELETE` | `/api/v1/bikes/{id}`  | Delete a bike                      |
| `GET`    | `/api/v1/health`      | Health/readiness probe             |

See `contracts/api.md` for full request/response schemas.
