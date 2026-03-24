FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /build

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY app/ ./app/
COPY main.py ./
COPY migrations/ ./migrations/

# --- Runtime stage ---
FROM python:3.12-slim

RUN groupadd --system app && useradd --system --gid app app

WORKDIR /app

COPY --from=builder /build/.venv /app/.venv
COPY --from=builder /build/app ./app
COPY --from=builder /build/main.py ./
COPY --from=builder /build/migrations ./migrations

ENV PATH="/app/.venv/bin:$PATH"
ENV FLASK_APP=main.py

EXPOSE 8080

USER app

CMD ["python", "-m", "flask", "run", "--host=0.0.0.0", "--port=8080"]
