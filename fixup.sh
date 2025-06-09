#!/bin/bash
# Script to automatically fix static analysis issues
set -e

echo "Running automatic fixes for static analysis issues..."

# Fix code formatting with Black
echo "Fixing code formatting with Black..."
poetry run black kreatisite tests

# Fix isort import ordering
echo "Fixing import ordering with isort..."
poetry run isort kreatisite tests --profile black

# Fix trailing whitespace and end-of-file issues
echo "Fixing trailing whitespace and end-of-file issues..."
poetry run pre-commit run trailing-whitespace --all-files || true
poetry run pre-commit run end-of-file-fixer --all-files || true

# Note: mypy doesn't auto-fix issues, it only reports them
# flake8 also doesn't auto-fix, it only reports issues
echo "Running mypy to check for type issues (no auto-fix available)..."
poetry run mypy kreatisite --show-error-codes || {
    echo "Warning: mypy found type issues that need manual fixing"
}

echo "Running flake8 to check for style issues (no auto-fix available)..."
poetry run flake8 kreatisite || {
    echo "Warning: flake8 found style issues that need manual fixing"
}

echo "Automatic fixes completed!"
echo "Note: mypy and flake8 issues require manual fixes - check their output above"