FROM node:20-alpine AS frontend-build

WORKDIR /frontend

COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build


FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /usr/local/bin/

WORKDIR /app

COPY . .
COPY --from=frontend-build /frontend/dist ./frontend/dist

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 10000

CMD ["sh", "-c", "alembic upgrade head && uvicorn job_market_analyzer.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
