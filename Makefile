TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc
PROJECT = travharv
AUTHOR = "Flanders Marine Institute, VLIZ vzw"


.PHONY: help clean startup install init init-dev init-docs docs docs-build test test-quick test-with-graphdb test-coverage test-coverage test-coverage-with-graphdb check lint-fix update
.DEFAULT_GOAL := help


help:  ## Shows this list of available targets and their effect.
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


clean:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -f *.sqlite
	@rm -rf .cache

startup:           ## guarantee dependencies
	pip install --upgrade pip
	which poetry >/dev/null || pip install poetry

install:           ## local install in current environment
	poetry install

init: startup install

init-dev: startup  ## initial prepare of the environment for all purposes
	poetry install --with 'tests' --with 'dev' --with 'docs'

init-docs: startup ## initial prepare of the environment for local execution and reading the docs
	@poetry install --with 'docs'

docs:              ## builds the docs
	@poetry run sphinx-quickstart -q --ext-autodoc --ext-githubpages --ext-viewcode --sep --project $(PROJECT) --author '${AUTHOR} -f' source_docs
	@cp ./docs/* ./source_docs/source/
	@sleep 1
	@poetry run sphinx-apidoc -o ./source_docs/source ./$(PROJECT)
	@poetry run sphinx-build -b html ./source_docs/source ./source_docs/build/html
	@cp ./source_docs/source/custom.css ./source_docs/build/html/_static/custom.css
	@cp ./source_docs/source/UML_Diagram.svg ./source_docs/build/html/_static/UML_Diagram.svg

test:              ## runs the tests
	poetry run pytest ${TEST_PATH}

test-coverage:     ## runs the tests and calculates the coverage
	poetry run pytest --cov=$(PROJECT) ${TEST_PATH} --cov-report term-missing

check:             ## perform lint check, report issues
	poetry run black --check --diff .
	poetry run isort --check --diff .
	poetry run flake8 . --exclude ${FLAKE8_EXCLUDE}

lint-fix:          ## fix lint issues
	poetry run black .
	poetry run isort .

update:            ## update dependencies, sync lock file
	poetry update


build: update check test docs
	poetry build

release: build
	poetry release