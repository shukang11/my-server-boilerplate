#!/bin/bash

# Configure python environment directory
poetry config virtualenvs.in-project true

# Install dependencies
poetry install

# Install pre-commit hooks
pre-commit install

# Database
# Initialize
# poetry run alembic init alembic
poetry run python -m pip install --upgrade pip
poetry run python -m pip install fastapi
poetry run python -m pip install h11
