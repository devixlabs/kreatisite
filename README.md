# kreatisite

A command line application to register, create, and deploy a new website.

## Installation

```bash
# Install Poetry if you haven't already
pip install poetry

# Install dependencies
poetry install
```

## Usage

```bash
# Display help and commands
poetry run kreatisite help

# Check domain availability
poetry run kreatisite check-domain example.com

# Register a domain (privacy protection is enabled by default)
# YAML contact info must be provided for admin, registrant, and tech contacts (remove '.example' from filename `aws-register-domain.yaml.example` and update with your values).
poetry run kreatisite register-domain example.com
```

## Development

```bash
# Activate the virtual environment
poetry shell

# Now you can run the application directly
kreatisite help

# Set up pre-commit hooks (do this once)
poetry run setup-hooks

# Run linting
poetry run lint

# Run tests
poetry run test

# Run all checks (linting + tests)
poetry run check
```

## Build

The project includes a pre-build script that runs all checks before building:

```bash
./prebuild.sh
```

This will:
1. Run pre-commit hooks on all files
2. Run tests and additional checks
3. Build the package if all checks pass

## Pre-commit Hooks

This project uses pre-commit to enforce code quality. The following hooks are configured:

- Trailing whitespace trimming
- End of file fixing
- YAML and TOML syntax checking
- Large file detection
- Flake8 (with docstring checking)
- isort (import sorting)
- mypy (type checking)
- pytest (automated tests)

These checks run automatically on commit, but you can also run them manually:

```bash
poetry run pre-commit run --all-files
```
