# Makefile for Django Portfolio Blog with NYC Taxi API
# Usage: make <target>

.PHONY: help build up down restart logs shell migrate makemigrations createsuperuser collectstatic test clean load-sample load-taxi-data

# Default target
help:
	@echo "Available commands:"
	@echo "  build          - Build Docker containers"
	@echo "  up             - Start the application"
	@echo "  down           - Stop the application"
	@echo "  restart        - Restart the application"
	@echo "  logs           - View application logs"
	@echo "  shell          - Open Django shell"
	@echo "  bash           - Open bash shell in web container"
	@echo "  migrate        - Run database migrations"
	@echo "  makemigrations - Create new migrations"
	@echo "  createsuperuser - Create Django superuser"
	@echo "  collectstatic  - Collect static files"
	@echo "  test           - Run tests"
	@echo "  clean          - Clean up containers and volumes"
	@echo "  load-sample    - Load sample taxi data (1000 records)"
	@echo "  load-taxi-data - Load full taxi dataset (interactive)"
	@echo "  api-test       - Test API endpoints"

# Docker commands
build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Application started at http://localhost:8000"
	@echo "API endpoints available at http://localhost:8000/api/"

down:
	docker-compose down

restart: down up

logs:
	docker-compose logs -f

# Django management commands
shell:
	docker-compose run --rm web python manage.py shell

bash:
	docker-compose run --rm web bash

migrate:
	docker-compose run --rm web python manage.py migrate

makemigrations:
	docker-compose run --rm web python manage.py makemigrations

createsuperuser:
	docker-compose run --rm web python manage.py createsuperuser

collectstatic:
	docker-compose run --rm web python manage.py collectstatic --noinput

test:
	docker-compose run --rm web python manage.py test

# Data loading commands
load-sample:
	@echo "Loading sample taxi data (1000 records)..."
	docker-compose run --rm web python manage.py load_taxi_data --sample-size 1000 --year 2014 --month 1

load-taxi-data:
	@echo "Available options:"
	@echo "  Sample sizes: --sample-size <number>"
	@echo "  Full dataset: --get-all"
	@echo "  Specific year/month: --year <year> --month <month>"
	@echo "  Batch size: --batch-size <size> (default: 10000)"
	@echo "  Clear existing data: --clear-data"
	@echo ""
	@echo "Examples:"
	@echo "  make load-taxi-data ARGS='--sample-size 5000'"
	@echo "  make load-taxi-data ARGS='--get-all --year 2014 --month 1'"
	@echo "  make load-taxi-data ARGS='--clear-data --sample-size 10000'"
	@echo ""
	@read -p "Enter arguments (or press Enter for default 1000 sample): " args; \
	if [ -z "$$args" ]; then \
		args="--sample-size 1000"; \
	fi; \
	docker-compose run --rm web python manage.py load_taxi_data $$args

# API testing
api-test:
	@echo "Testing API endpoints..."
	@echo "Make sure the application is running (make up) first"
	@echo ""
	@echo "Available endpoints:"
	@echo "  GET  /api/trips/          - List trips"
	@echo "  GET  /api/trips/summary/  - Trip summary"
	@echo "  GET  /api/trips/heatmap/  - Heatmap data"
	@echo "  GET  /api/trips/revenue/  - Revenue analytics"
	@echo "  GET  /api/trips/stats/    - Trip statistics"
	@echo "  GET  /api/zones/          - List zones"
	@echo ""
	@echo "Testing basic endpoints..."
	@curl -s http://localhost:8000/api/trips/ | head -c 200 || echo "API not responding"
	@echo ""
	@curl -s http://localhost:8000/api/trips/summary/ | head -c 200 || echo "Summary endpoint not responding"

# Database commands
db-reset:
	@echo "WARNING: This will delete all data!"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose down; \
		docker volume rm new_profile_postgres_data 2>/dev/null || true; \
		docker-compose up -d postgres; \
		sleep 5; \
		docker-compose run --rm web python manage.py migrate; \
		echo "Database reset complete"; \
	else \
		echo "Cancelled"; \
	fi

# Development commands
dev-setup: build migrate load-sample
	@echo "Development environment setup complete!"
	@echo "Run 'make up' to start the application"

# Cleanup commands
clean:
	docker-compose down -v
	docker system prune -f
	docker volume prune -f

clean-all: clean
	docker-compose down --rmi all -v
	docker system prune -a -f

# Status check
status:
	@echo "Container status:"
	@docker-compose ps
	@echo ""
	@echo "Recent logs:"
	@docker-compose logs --tail=10

# Quick development cycle
quick-restart:
	docker-compose restart web
	@echo "Web container restarted"

# View Django logs specifically
django-logs:
	docker-compose logs -f web
