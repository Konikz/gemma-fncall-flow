.PHONY: install test lint clean

install:
	pip install -e ".[test,dev]"

test:
	pytest tests/ -v --cov=. --cov-report=term-missing

lint:
	flake8 .
	black . --check
	isort . --check
	mypy .

format:
	black .
	isort .

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf .mypy_cache/
	find . -type d -name "__pycache__" -exec rm -rf {} + 