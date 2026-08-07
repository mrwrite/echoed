#!/usr/bin/env bash
set -e

python -m scripts.validate_operational_config
alembic upgrade heads
python -m scripts.verify_migrations
