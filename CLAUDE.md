# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Kreatisite is a Python CLI application for registering, creating, and deploying websites. It primarily interfaces with AWS Route53 for domain operations and requires AWS CLI v2+ as an external dependency.

## Development Commands

```bash
# Install dependencies
poetry install

# Development environment
poetry shell

# Linting and code quality
poetry run lint          # Run flake8 linting
poetry run check         # Run all checks (lint + tests)

# Testing
poetry run test          # Run pytest
poetry run pytest -v    # Verbose test output
poetry run pytest tests/test_cli.py  # Run specific test file
poetry run pytest --cov=kreatisite  # Run with coverage

# Pre-commit hooks
poetry run setup-hooks   # Install pre-commit hooks (one-time setup)
poetry run pre-commit run --all-files  # Run hooks manually

# Build process
./prebuild.sh           # Run all checks + build package
```

## Architecture

The CLI application follows a modular structure:

- **cli.py**: Main entry point with dependency checking and command routing
- **parser.py**: Argument parsing configuration
- **cmd.py**: Core command implementations (check-domain, register-domain)
- **scripts.py**: Development scripts (lint, test, check_all, setup_hooks)

### Command Flow
1. CLI entry point validates Python version (3.9+) and AWS CLI availability
2. Parser processes arguments and routes to appropriate command handler
3. Commands execute AWS CLI subprocesses with proper error handling
4. Results are formatted and returned to user

### AWS Integration
- Domain availability checking via `aws route53domains check-domain-availability`
- Domain registration via `aws route53domains register-domain` with YAML config
- Privacy protection enabled by default for all contact types
- Configuration file required: `aws-register-domain.yaml` (based on `.example` file)

## Key Dependencies

- **External**: AWS CLI v2+ (checked at runtime for AWS commands)
- **Python**: pyyaml for config file parsing
- **Dev**: pytest, flake8, mypy, isort, pre-commit

## Testing Strategy

The project uses pytest with comprehensive unit test coverage. Future improvements planned include mocked AWS testing and E2E smoke tests (see TODO.md for detailed testing architecture plans).
