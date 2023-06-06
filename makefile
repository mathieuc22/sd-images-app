.PHONY: format lint typecheck test

format:
	black app
	isort app

lint:
	flake8 app

typecheck:
	mypy app

test:
	pytest tests


all: format lint typecheck
