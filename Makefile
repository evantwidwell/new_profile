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
	@echo "  api-test-duckdb - Test DuckDB-based endpoints"
	@echo "  db-check       - Check database connection"
	@echo "  db-stats       - Show database size and statistics"
	@echo "  db-clean       - Clean database to free space"
	@echo "  db-cleanup     - Advanced database cleanup (interactive)"
	@echo "  db-vacuum      - Vacuum database to reclaim space"

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

# API testing
api-test-duckdb:
	@echo "Testing DuckDB-based API endpoints..."
	@echo "These query parquet files directly - no database storage needed!"
	@echo ""
	@echo "Testing with 2023 data (month 1):"
	@curl -s "http://localhost:8000/api/taxi-data/summary/?year=2023&month=1" | head -c 300
	@echo ""
	@echo "Testing trip stats:"
	@curl -s "http://localhost:8000/api/taxi-data/stats/?year=2023&month=1" | head -c 300
	@echo ""
	@echo "Testing sample trips:"
	@curl -s "http://localhost:8000/api/taxi-data/trips/?year=2023&month=1&limit=5" | head -c 500

# Database commands
db-check:
	@echo "Checking database connection..."
	docker-compose run --rm web python manage.py check --database default

db-stats:
	@echo "Getting database statistics..."
	docker-compose run --rm web python manage.py db_stats

db-clean:
	@echo "Cleaning up database to free space..."
	@echo "This will remove all taxi data but keep the database structure"
	@read -p "Are you sure? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		docker-compose run --rm web python manage.py shell -c "from taxi_api.models import Trip, Zone; Trip.objects.all().delete(); print('Taxi data cleared')"; \
		echo "Database cleaned - taxi data removed"; \
	else \
		echo "Cancelled"; \
	fi

db-vacuum:
	@echo "Running database vacuum to reclaim space..."
	@echo "This will optimize the database and reclaim deleted space"
	docker-compose run --rm web python manage.py shell -c "from django.db import connection; cursor = connection.cursor(); cursor.execute('VACUUM FULL;'); print('Database vacuum completed')"

db-cleanup:
	@echo "Advanced database cleanup options:"
	@echo "  --keep-records N    - Keep N most recent records"
	@echo "  --older-than-days N - Delete records older than N days"
	@echo "  --vacuum           - Run VACUUM after cleanup"
	@echo "  --dry-run          - Show what would be deleted"
	@echo ""
	@echo "Examples:"
	@echo "  make db-cleanup ARGS='--keep-records 5000 --vacuum'"
	@echo "  make db-cleanup ARGS='--older-than-days 30 --dry-run'"
	@echo "  make db-cleanup ARGS='--vacuum'"
	@echo ""
	@read -p "Enter arguments (or press Enter for --dry-run): " args; \
	if [ -z "$$args" ]; then \
		args="--dry-run"; \
	fi; \
	docker-compose run --rm web python manage.py cleanup_data $$args

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
dev-setup: build migrate
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
