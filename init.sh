#!/bin/bash
echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo "Generating initial Alembic migration..."
docker compose exec backend uv run alembic revision --autogenerate -m "Initial generation"

echo "Applying database migrations..."
docker compose exec backend uv run alembic upgrade head

echo "System initialized successfully."
