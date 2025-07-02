#!/bin/bash

# Amazon SP-API Mock Service Startup Script
# This script runs database migrations and starts the FastAPI application

set -e

echo "🚀 Starting Amazon SP-API Mock Service..."

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
while ! pg_isready -h amazon-db -p 5432 -U amazon_user -d amazon_sp_db; do
    echo "Database not ready, waiting..."
    sleep 2
done

echo "✅ Database is ready!"

# Run Alembic migrations
echo "🔄 Running database migrations..."
alembic upgrade head

echo "✅ Database migrations completed!"

# Start the application
echo "🚀 Starting FastAPI application..."
exec python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload