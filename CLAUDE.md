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

# Testing (Phase 5: CI/CD Integration)
poetry run test                    # Run basic pytest
poetry run unit-tests             # Run unit tests with 80% coverage requirement
poetry run integration-tests      # Run integration tests (installed package)
poetry run comprehensive-tests    # Run full test suite (unit + integration + e2e)
poetry run smoke-tests           # Run E2E smoke tests (requires AWS credentials)

# Specific test commands
poetry run pytest -v                           # Verbose test output
poetry run pytest tests/test_cli.py           # Run specific test file
poetry run pytest -m unit                     # Run only unit tests
poetry run pytest -m integration              # Run only integration tests
poetry run pytest -m e2e                      # Run only E2E tests
poetry run pytest --cov=kreatisite --cov-fail-under=80  # Coverage with minimum requirement

# Pre-commit hooks
poetry run setup-hooks   # Install pre-commit hooks (one-time setup)
poetry run pre-commit run --all-files  # Run hooks manually

# Build process (Phase 5: CI/CD Integration)
./prebuild.sh           # Run comprehensive CI/CD pipeline:
                        #   - Stage 1: Code quality checks (pre-commit hooks)
                        #   - Stage 2: Comprehensive test suite (unit + integration + e2e)
                        #   - Stage 3: Package build
                        # Enforces 80% test coverage requirement
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
- **Testing**: clirunner, pytest-subprocess, pytest-console-scripts, pytest-timeout, pytest-cov

## CI/CD Integration (Phase 5)

The project includes a comprehensive CI/CD pipeline that can be run locally or in automated environments:

### Local CI/CD Pipeline
- **prebuild.sh**: Runs the complete CI/CD pipeline locally
- **80% coverage requirement**: Enforced for all unit tests
- **Multi-stage testing**: Unit → Integration → E2E testing

### GitHub Actions Template
- **File**: `.github-actions-template.yml`
- **Usage**: Copy to `.github/workflows/ci.yml` to enable GitHub Actions
- **Features**: Multi-Python version testing, coverage reporting, automated PyPI publishing

## Testing Strategy

The project uses a comprehensive 3-layer testing architecture (81 tests total):

### Layer 1: Unit Tests (Fast, Mocked)
- **Tool**: `clirunner` + `pytest-subprocess`
- **Coverage**: 80% minimum requirement enforced
- **Purpose**: Fast feedback, isolated testing with mocked AWS calls

### Layer 2: Integration Tests (Realistic, Controlled)  
- **Tool**: `pytest-console-scripts`
- **Purpose**: Test installed CLI package as users would run it
- **Scope**: Cross-platform compatibility, configuration handling

### Layer 3: E2E Smoke Tests (Real Environment)
- **Tool**: Enhanced Python-based smoke tests
- **Purpose**: Real AWS API calls with proper credentials
- **Scope**: End-to-end validation in production-like environment

All tests are organized with pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.e2e`) for selective execution.
