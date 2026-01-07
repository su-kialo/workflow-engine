.PHONY: help build up down logs shell migrate migrate-create test lint format install

help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies locally"
	@echo "  make build         - Build Docker images"
	@echo "  make up            - Start all services"
	@echo "  make down          - Stop all services"
	@echo "  make logs          - View logs"
	@echo "  make shell         - Open shell in API container"
	@echo "  make migrate       - Run database migrations"
	@echo "  make migrate-create name=<name> - Create new migration"
	@echo "  make test          - Run tests"
	@echo "  make lint          - Run linter"
	@echo "  make format        - Format code"

install:
	pip install -e ".[dev]"

build:
	docker compose -f docker/docker-compose.yml build

up:
	docker compose -f docker/docker-compose.yml up -d

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

shell:
	docker compose -f docker/docker-compose.yml exec api /bin/bash

migrate:
	docker compose -f docker/docker-compose.yml exec api alembic upgrade head

migrate-create:
	docker compose -f docker/docker-compose.yml exec api alembic revision --autogenerate -m "$(name)"

test:
	docker compose -f docker/docker-compose.yml exec api pytest

test-local:
	pytest

lint:
	ruff check src/ tests/

format:
	ruff format src/ tests/
