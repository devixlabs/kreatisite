#!/bin/bash
set -e

echo "Running pre-build checks..."

# Run all checks
poetry run check

if [ $? -eq 0 ]; then
    echo "All checks passed! Building package..."
    poetry build
else
    echo "Checks failed. Please fix issues before building."
    exit 1
fi