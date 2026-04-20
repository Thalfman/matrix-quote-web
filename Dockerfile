# Multi-stage build: compile the SPA, then copy into the Python runtime image.

FROM node:20-bookworm-slim@sha256:f93745c153377ee2fbbdd6e24efcd03cd2e86d6ab1d8aa9916a3790c40313a55 AS frontend
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install --no-audit --no-fund
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim-bookworm@sha256:9c6f90801e6b68e772b7c0ca74260cbf7af9f320acec894e26fccdaccfbe3b47 AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data \
    PORT=8000

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libcairo2 \
        libharfbuzz0b \
        fonts-liberation \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY core ./core
COPY service ./service
COPY backend ./backend
COPY --from=frontend /app/frontend/dist ./frontend/dist

RUN groupadd --system --gid 10001 app \
    && useradd --system --uid 10001 --gid 10001 --home-dir /app --shell /usr/sbin/nologin app \
    && mkdir -p /data/data/master /data/models \
    && chown -R app:app /app /data

USER app

EXPOSE 8000
CMD ["sh", "-c", "gunicorn backend.app.main:app -k uvicorn.workers.UvicornWorker -w 2 -t 600 -b 0.0.0.0:${PORT}"]
