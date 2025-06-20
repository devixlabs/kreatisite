# kreatisite

A command line application to register, create, and deploy a new website.

## System Requirements

- Python 3.9 or higher
- AWS CLI v2+ (for domain operations)

### Installing System Dependencies

**AWS CLI Installation:**

Ubuntu/Debian:
```bash
# Method 1: Official installer (recommended)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

Other platforms: See [AWS CLI Installation Guide](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)

**Configure AWS Credentials:**
```bash
aws configure
```

## Installation

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

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

## Testing

Run the full test suite:

```bash
# Run all tests
poetry run pytest

# Run tests with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_cli.py

# Run tests with coverage
poetry run pytest --cov=kreatisite

# Run tests by category
poetry run pytest -m unit          # Unit tests only (fast, mocked)
poetry run pytest -m integration   # Integration tests only (installed package)
poetry run pytest -m e2e          # End-to-end tests only (real AWS calls)

# Exclude specific test categories
poetry run pytest -m "not e2e"    # All tests except E2E tests
```

### Smoke Testing

The project includes comprehensive E2E smoke tests with proper assertions and error handling:

```bash
# Run smoke tests (requires AWS credentials for full testing)
poetry run smoke-tests

# Alternative: Run smoke tests directly with pytest
poetry run pytest -m e2e tests/test_e2e_smoke.py -v

# Run smoke tests with timeout protection
poetry run pytest -m e2e --timeout=60 tests/test_e2e_smoke.py
```

**AWS Credentials for Smoke Tests:**

The smoke tests can run in two modes:

1. **With AWS credentials**: Full test suite including real AWS API calls
   - Set `AWS_PROFILE` environment variable, OR
   - Set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables

2. **Without AWS credentials**: Limited test suite (AWS-dependent tests are skipped)
   - Tests basic CLI functionality, help commands, and error handling
   - Useful for CI/CD environments without AWS access

**What the smoke tests cover:**
- CLI help and argument parsing
- Domain availability checking (with real AWS API calls)
- Domain registration validation and error handling  
- Configuration file processing
- Error scenarios and edge cases
- Timeout and network failure handling

## Build

The project includes a pre-build script that runs all checks before building:

```bash
./prebuild.sh
```

This will:
1. Run pre-commit hooks on all files
2. Run comprehensive test suite (unit + integration + E2E smoke tests)
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
