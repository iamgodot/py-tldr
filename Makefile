.PHONY: help install clean lint format test

help:
	@echo "This Makefile supports following rules:"
	@echo "  install: install prod&dev dependencies by PDM."
	@echo "  clean: remove python cache&build results."
	@echo "  lint: check linting by ruff."
	@echo "  format: format code by black&ruff."
	@echo "  test: clean first, then check lint and test."

install:
	pdm install --dev

clean:
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist

lint:
	ruff check .

format:
	black .
	ruff check --fix .

test: clean lint
	pytest -v --cov=src/py_tldr tests
