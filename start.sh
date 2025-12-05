#!/bin/bash

# Function to check if the database is available
wait_for_db() {
  echo "Waiting for postgres..."
  # 'postgres' is the service name used in docker-compose.yml
  # '5432' is the container's internal port
  # 'nc' (netcat) is used to check the connection
  while ! nc -z postgres 5432; do
    sleep 0.1
  done

  echo "PostgreSQL started"
}

# Run the waiting function
wait_for_db

# Run Alembic migrations
echo "Running Alembic migrations..."
alembic upgrade head

# Start the FastAPI application
echo "Starting server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000