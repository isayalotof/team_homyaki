#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z ${POSTGRES_HOST} ${POSTGRES_PORT}; do
  sleep 0.1
done
echo "PostgreSQL started"

# Run migrations
echo "Running database migrations"
alembic upgrade head

# Create initial data - This should be run only once, so we comment it out
# echo "Creating initial data"
# python -m app.initial_data 