.DEFAULT_GOAL := default

.PHONY: default install_deps lint test build clean

default: install_deps lint test

install_deps:
	poetry install

lint:
	poetry run python devtools/lint.py

test:
	poetry run pytest

build:
	poetry build

clean:
	-rm -rf dist/
	-rm -rf *.egg-info/
	-rm -rf .pytest_cache/
	-rm -rf .mypy_cache/
	-rm -rf .venv/
	-find . -type d -name "__pycache__" -exec rm -rf {} +