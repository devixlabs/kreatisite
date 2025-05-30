#!/bin/bash

set -e

echo "Cleaning dist/..."
rm -rf dist/

echo "Building..."
poetry build

echo "Running tests..."

#TODO parse output and `exit 1` if unexpected.
poetry run kreatisite help
poetry run kreatisite check-domain example.com
poetry run kreatisite register-domain example.com

echo "Done!"
