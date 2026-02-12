#!/bin/bash
echo "Running database migrations..."
python -c "from src.database.database import create_db_and_tables; create_db_and_tables()"
echo "Starting Uvicorn server..."
exec uvicorn src.main:app --host 0.0.0.0 --port 8000
