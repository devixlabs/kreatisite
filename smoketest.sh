#!/bin/bash

set -e

echo "========================================"
echo "DEPRECATED: smoketest.sh is deprecated"
echo "Use: poetry run smoke-tests instead"
echo "========================================"
echo ""

echo "Cleaning dist/..."
rm -rf dist/

echo "Building..."
poetry build

echo "Running new Python-based smoke tests..."
poetry run smoke-tests

echo ""
echo "========================================"
echo "Migration complete! Consider using:"
echo "  poetry run smoke-tests"
echo "  poetry run pytest -m e2e -v"
echo "========================================"
