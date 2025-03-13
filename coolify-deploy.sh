#!/bin/bash

# This script is used for deploying to Coolify
# It ensures that static files are properly collected and served

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear

# Initialize database with basic data
echo "Initializing database with basic data..."
python init_db.py

# Start the application with Gunicorn
echo "Starting the application..."
gunicorn core.wsgi:application --bind 0.0.0.0:8000 