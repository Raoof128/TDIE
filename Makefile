.PHONY: install dev-install lint format test run ci

install:
	python -m pip install --upgrade pip
	pip install -r requirements.txt

dev-install:
	python -m pip install --upgrade pip
	pip install -r requirements-dev.txt

lint:
	ruff check .
	black --check .

format:
	ruff format .
	black .

test:
	pytest

run:
	uvicorn backend.main:app --reload

ci: lint test
	@echo "CI checks completed"
