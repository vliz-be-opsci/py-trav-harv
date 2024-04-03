TEST_PATH = ./tests/
FLAKE8_EXCLUDE = venv,.venv,.eggs,.tox,.git,__pycache__,*.pyc
PROJECT = pytravharv
AUTHOR = "Flanders Marine Institute, VLIZ vzw"


.PHONY: help clean startup install init init-dev init-docs docs docs-build test test-quick test-with-graphdb test-coverage test-coverage test-coverage-with-graphdb check lint-fix update
.DEFAULT_GOAL := help

clean:
	@find . -name '*.pyc' -exec rm --force {} +
	@find . -name '*.pyo' -exec rm --force {} +
	@find . -name '*~' -exec rm --force {} +
	@rm -rf build
	@rm -rf dist
	@rm -rf *.egg-info
	@rm -f *.sqlite
	@rm -rf .cache

startup:
	pip install --upgrade pip
	which poetry >/dev/null || pip install poetry

install:
	poetry install

init: startup install

init-dev: startup
	poetry install --with 'tests' --with 'dev' --with 'docs'

init-docs: startup
	poetry install --with 'docs'

init-docs: startup  ## initial prepare of the environment for local execution and reading the docs
	@poetry install --with 'docs'

docs:  ## builds the docs
	@poetry run sphinx-quickstart -q --ext-autodoc --ext-githubpages --ext-viewcode --sep --project $(PROJECT) --author '${AUTHOR} -f' source_docs
	@cp ./docs/* ./source_docs/source/
	@sleep 1
	@poetry run sphinx-apidoc -o ./source_docs/source ./$(PROJECT)
	@poetry run sphinx-build -b html ./source_docs/source ./source_docs/build/html
	@cp ./source_docs/source/custom.css ./source_docs/build/html/_static/custom.css
	@cp ./source_docs/source/UML_Diagram.svg ./source_docs/build/html/_static/UML_Diagram.svg

test:
	poetry run pytest ${TEST_PATH}

test-coverage:
	poetry run pytest --cov=$(PROJECT) ${TEST_PATH} --cov-report term-missing

check:
	poetry run black --check --diff .
	poetry run isort --check --diff .
	poetry run flake8 . --exclude ${FLAKE8_EXCLUDE} --ignore=E501,E201,E202,W503

lint-fix:
	poetry run black .
	poetry run isort .

update:
	poetry update


build: update check test docs
	poetry build

release: build
	poetry release