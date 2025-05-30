#!/bin/bash
set -e

echo "Running pre-build checks..."

# Run pre-commit checks on all files
echo "Running pre-commit checks..."
poetry run pre-commit run --all-files || { echo "Pre-commit checks failed. Please fix issues before building."; exit 1; }

# Run isort on all files
echo "Running isort checks on all files..."
poetry run isort kreatisite --check || { echo "isort check failed. Please fix import ordering issues."; exit 1; }

# Run additional checks
echo "Running additional checks..."
poetry run check || { echo "Checks failed. Please fix issues before building."; exit 1; }

echo "All checks passed! Building package..."
poetry build
