#!/bin/bash
set -e

echo "Running pre-build checks..."

# Run pre-commit checks on all files (includes Black, isort, flake8, mypy, etc.)
echo "Running pre-commit checks..."
poetry run pre-commit run --all-files || { echo "Pre-commit checks failed. Please fix issues before building."; exit 1; }

# Run additional checks
echo "Running additional checks..."
poetry run check || { echo "Checks failed. Please fix issues before building."; exit 1; }

echo "All checks passed! Building package..."
poetry build
