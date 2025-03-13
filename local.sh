#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    # Set DEBUG to True for local development
    sed -i "s/DEBUG=False/DEBUG=True/g" .env
fi

# Build and start the containers
echo "Building and starting the local development environment..."
docker-compose -f docker-compose.local.yml up -d

# Print helpful information
echo "Local development environment is ready!"
echo "You can access the application at http://localhost:8000"
echo "Admin credentials: admin / admin123"
echo "Dentist credentials: dentist / dentist123"
echo "Staff credentials: staff / staff123"
echo "pgAdmin is available at http://localhost:5050"
echo "pgAdmin credentials: admin@example.com / admin123"
echo ""
echo "To view logs, run: docker-compose -f docker-compose.local.yml logs -f"
echo "To stop the environment, run: docker-compose -f docker-compose.local.yml down" 