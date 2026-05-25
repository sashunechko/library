.PHONY: help build up down restart logs migrate seed test test-file shell psql build-local reset ps

DC := docker compose

help:
	@echo "Targets:"
	@echo "  make build         собрать образ"
	@echo "  make up            поднять db + app (миграции применятся автоматически)"
	@echo "  make down          остановить контейнеры"
	@echo "  make restart       рестартануть app"
	@echo "  make logs          tail логов app"
	@echo "  make ps            статус контейнеров"
	@echo "  make migrate       alembic upgrade head внутри контейнера"
	@echo "  make seed          залить демо-данные"
	@echo "  make test          прогнать pytest"
	@echo "  make test-file FILE=tests/test_loans.py"
	@echo "  make shell         bash внутри app"
	@echo "  make psql          psql внутри db"
	@echo "  make build-local   создать .venv для IDE (без Docker)"
	@echo "  make reset         down + удалить том БД (потеря данных!)"

build:
	$(DC) build

up:
	$(DC) up -d --build

down:
	$(DC) down

restart:
	$(DC) restart app

logs:
	$(DC) logs -f app

ps:
	$(DC) ps

migrate:
	$(DC) exec app alembic -c migrations/alembic.ini upgrade head

seed:
	$(DC) exec app python scripts/seed.py

test:
	$(DC) exec app pytest tests/ -v

test-file:
	$(DC) exec app pytest $(FILE) -v

shell:
	$(DC) exec app bash

psql:
	$(DC) exec db psql -U library -d library

build-local:
	python -m venv .venv
	. .venv/bin/activate && pip install -e ".[test]"
	@echo
	@echo ".venv готов. Активируй:"
	@echo "  source .venv/bin/activate   (mac/linux)"
	@echo "  .venv\\Scripts\\activate     (windows)"

reset:
	$(DC) down -v
