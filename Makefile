REPO = 'py-tldr'

.PHONY: help install clean lint test rebuild release

help:
	@echo "Use 'make target' of which target is from the following:"
	@echo "  install	to install via requirements.txt"
	@echo "  test 		to test through all test cases"

install:
	pdm install --dev

clean:
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache

lint:
	pdm run flake8 --format=pylint --count

test: clean lint
	pdm run pytest -v --cov=src/py_tldr tests

rebuild:
	rm -rf dist
	python -m build

release: rebuild
	twine upload dist/* --verbose
