.PHONY: up down scrape load ingest views migrate dashboard notebook test init-db

PYTHON ?= python3
VENV = .venv/bin
PSQL = docker exec -i disney_catalog_db psql -U disney -d disney_catalog

up:
	docker compose up -d

down:
	docker compose down

init-db:
	docker compose up -d postgres
	@echo "Waiting for Postgres..."
	@sleep 3

scrape:
	$(VENV)/python -m scraper.run

scrape-sample:
	$(VENV)/python -m scraper.run --sample

load:
	$(VENV)/python -m ingestion.load_catalog

ingest: scrape load

views:
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < sql/views/create_analytical_views.sql

migrate:
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < schemas/ddl/003_schema_updates.sql
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < schemas/ddl/004_schema_cleanup.sql
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < schemas/ddl/005_credits_table.sql
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < schemas/ddl/006_media_original.sql
	docker exec -i disney_catalog_db psql -U disney -d disney_catalog < schemas/ddl/007_drop_media_format.sql

dashboard:
	$(VENV)/streamlit run dashboard/app.py --server.port 8501

notebook:
	$(VENV)/jupyter notebook notebooks/

test:
	$(VENV)/pytest tests/ -v

install:
	$(PYTHON) -m venv .venv
	$(VENV)/pip install -r requirements.txt

setup: install up
	@echo "Run 'make ingest' to scrape and load catalog data"
