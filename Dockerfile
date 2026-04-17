# Multi-stage build: compile the SPA, then copy into the Python runtime image.

FROM node:20-bookworm-slim AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY core ./core
COPY service ./service
COPY backend ./backend
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN mkdir -p /data/data/master /data/models

EXPOSE 8000
CMD ["sh", "-c", "gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker -w 2 -t 600 -b 0.0.0.0:${PORT}"]
