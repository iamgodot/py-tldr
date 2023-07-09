help: ## Prints help for targets with comments
	@cat $(MAKEFILE_LIST) | grep -E '^[a-zA-Z_-]+:.*?## .*$$' | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

install: # Install prod&dev dependencies via pdm.
	pdm install --dev

clean: # Remove python cache&build results.
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache
	rm -rf build
	rm -rf dist

lint: # Check linting via ruff.
	pdm run ruff check .

format: # Format code via black&ruff.
	pdm run black .
	pdm run ruff check --fix .

test: clean lint # Clean, check lint and run tests.
	pdm run pytest -v --cov=src/py_tldr tests
