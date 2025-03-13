#!/bin/bash

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -base64 32)
    # Update the secret key in the .env file
    sed -i "s/your-secret-key-here/$SECRET_KEY/g" .env
fi

# Build and start the containers
echo "Building and starting the containers..."
docker-compose -f docker-compose.prod.yml up -d

# Print helpful information
echo "Production environment is ready!"
echo "You can access the application at http://your-server-ip:8000"
echo "Admin credentials: admin / admin123"
echo "Dentist credentials: dentist / dentist123"
echo "Staff credentials: staff / staff123" 