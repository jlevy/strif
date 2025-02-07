.DEFAULT_GOAL := default

.PHONY: default lint test

default: lint test

lint:
	poetry run python devtools/lint.py

test:
	poetry run pytest
