default:
	@echo "View Makefile for usage"

sys_deps := poetry pre-commit coveralls

bootstrap: ## Install system dependencies for this project (macOS or pyenv)
	pip install -U $(sys_deps)

bootstrap-user: ## Install system dependencies for this project in user dir (Linux)
	pip install --user -U $(sys_deps)

install:
	pre-commit install
	poetry config settings.virtualenvs.in-project true
	poetry develop

lint:
	poetry run flake8 spellchecker tests samples

test:
	poetry run pytest --cov=spellchecker --cov-report=term-missing -s tests
