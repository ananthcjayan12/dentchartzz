#!/bin/sh

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL..."
while ! nc -z db 5432; do
  sleep 0.1
done
echo "PostgreSQL is up and running!"

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Initialize database with basic data
echo "Initializing database with basic data..."
python init_db.py

# Start the application
echo "Starting the application..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000 