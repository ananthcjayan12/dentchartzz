#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
fi

# Build and start the containers
echo "Building and starting the containers..."
docker-compose up -d

# Print helpful information
echo "Development environment is ready!"
echo "You can access the application at http://localhost:8000"
echo "Admin credentials: admin / admin123"
echo "Dentist credentials: dentist / dentist123"
echo "Staff credentials: staff / staff123" 