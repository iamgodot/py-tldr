REPO = 'pytldr'

.PHONY: help venv lint test clean

help:
	@echo "Use 'make target' of which target is from the following:"
	@echo "  venv		to create an virtual environment"
	@echo "  install	to install via requirements.txt"
	@echo "  test 		to test through all test cases"

venv:
	virtualenv --python=$(which python3) --prompt '<venv: $(REPO)>' venv

install:
	pip install -r requirements/dev.txt
	pip install -e .

clean:
	find . -iname "*__pycache__" | xargs rm -rf
	find . -iname "*.pyc" | xargs rm -rf
	rm -rf .pytest_cache

lint:
	flake8 --format=pylint --count

test: clean lint
	pytest --cov=pytldr tests
