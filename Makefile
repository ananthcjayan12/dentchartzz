# Makefile for DentChartzz project

.PHONY: help build up down logs test shell db-shell clean restart status collectstatic

# Default target
help:
	@echo "Available commands:"
	@echo "  make build      - Build all containers"
	@echo "  make up        - Start all containers"
	@echo "  make down      - Stop all containers"
	@echo "  make logs      - View container logs"
	@echo "  make test      - Run tests"
	@echo "  make shell     - Open a shell in the web container"
	@echo "  make db-shell  - Open a PostgreSQL shell"
	@echo "  make clean     - Remove all containers and volumes"
	@echo "  make restart   - Restart all containers"
	@echo "  make status    - Show status of containers"
	@echo "  make collectstatic - Collect static files"
	@echo ""
	@echo "Production commands:"
	@echo "  make prod-build  - Build containers for production"
	@echo "  make prod-up     - Start containers in production mode"
	@echo "  make prod-down   - Stop production containers"
	@echo "  make prod-logs   - View production container logs"

# Development environment
build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f

test:
	docker-compose exec web python -m pytest

shell:
	docker-compose exec web /bin/bash

db-shell:
	docker-compose exec db psql -U dentchartzz -d dentchartzz_db

clean:
	docker-compose down -v
	docker system prune -f

restart:
	docker-compose restart

status:
	docker-compose ps

# Collect static files
collectstatic:
	docker-compose exec web python manage.py collectstatic --noinput --clear

# Production environment
prod-build:
	docker-compose -f docker-compose.prod.yml build

prod-up:
	docker-compose -f docker-compose.prod.yml up -d

prod-down:
	docker-compose -f docker-compose.prod.yml down

prod-logs:
	docker-compose -f docker-compose.prod.yml logs -f

# Initialize environment
init:
	@if [ ! -f .env ]; then \
		cp .env.example .env; \
		echo "Created .env file from .env.example"; \
	fi

# Development setup (includes initialization)
dev: init build up
	@echo "Development environment is ready!"
	@echo "Access the application at http://localhost:8000"
	@echo "Admin credentials: admin / admin123"
	@echo "Dentist credentials: dentist / dentist123"
	@echo "Staff credentials: staff / staff123"

# Production setup (includes initialization)
prod: init prod-build prod-up
	@echo "Production environment is ready!"
	@echo "Access the application at http://your-server-ip:8000"
	@echo "Admin credentials: admin / admin123"
	@echo "Dentist credentials: dentist / dentist123"
	@echo "Staff credentials: staff / staff123" 