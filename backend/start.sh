#!/usr/bin/env bash
set -e

# Run migrations on deploy/start
alembic upgrade head

# Start API on Railway-provided port
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
