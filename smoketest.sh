#!/bin/bash

set -e

echo "Running smoke tests..."

poetry run kreatisite help
poetry run kreatisite check-domain example.com
poetry run kreatisite register-domain example.com

echo "Done!"
