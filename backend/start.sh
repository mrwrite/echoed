#!/usr/bin/env bash
set -e

# Production schema changes are an explicit release step. Validate before the
# application module is imported, and never let normal startup mutate schema.
python -m scripts.validate_operational_config

# Proxy headers are resolved by EchoEd only for explicitly configured peers.
uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" --no-proxy-headers --timeout-graceful-shutdown "${GRACEFUL_SHUTDOWN_SECONDS:-30}"
