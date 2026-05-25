#!/bin/sh
set -e

echo "[entrypoint] applying migrations..."
alembic -c migrations/alembic.ini upgrade head

echo "[entrypoint] starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
