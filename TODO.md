# E2E/Smoke Testing Improvements for Kreatisite CLI

## Overview
This document outlines the plan to improve E2E/smoke testing for the kreatisite CLI tool, replacing the basic `smoketest.sh` with a comprehensive Python-based testing solution.

**Status**: Phases 1 & 2 completed (21 unit tests, 87% coverage). Phases 3-5 remain for future implementation.

## Current Issues with smoketest.sh
- No actual assertions on command output
- No exit code verification
- No error scenario testing
- Cannot mock AWS calls for cost-free testing
- Limited test coverage

## Recommended Testing Architecture

### 1. Unit Testing Layer (Fast, Isolated)
**Tool:** `clirunner` (pip install clirunner)
- Works perfectly with argparse-based CLIs
- Provides Click-like testing API
- Captures stdout/stderr and exit codes
- Supports isolated filesystem

**Tool:** `pytest-subprocess` (pip install pytest-subprocess)
- Mock subprocess calls to AWS CLI
- Prevent actual AWS API calls during unit tests
- Fast and predictable

### 2. Integration Testing Layer (Realistic, Controlled)
**Tool:** `pytest-console-scripts` (pip install pytest-console-scripts)
- Test the installed CLI as users would run it
- Supports both in-process and subprocess modes
- Works with console_scripts entry points

### 3. E2E Smoke Testing Layer (Real Environment)
**Approach:** Enhanced Python-based smoke tests
- Replace shell script with Python for better assertions
- Use pytest for structured test execution
- Include real AWS calls with test credentials
- Add comprehensive output validation

## Implementation Tasks

### Phase 1: Setup Testing Infrastructure ✅ COMPLETED
- [x] Add testing dependencies to pyproject.toml:
  ```toml
  [tool.poetry.group.dev.dependencies]
  clirunner = "^0.2.0"
  pytest-subprocess = "^1.5.0"
  pytest-console-scripts = "^1.4.1"
  pytest-timeout = "^2.1.0"
  pytest-cov = "^4.0.0"
  ```
- [x] Create test configuration in pyproject.toml:
  ```toml
  [tool.pytest.ini_options]
  markers = [
      "unit: Unit tests (fast, mocked)",
      "integration: Integration tests (installed package)",
      "e2e: End-to-end tests (real AWS calls)",
  ]
  ```

### Phase 2: Implement Unit Tests with Mocking ✅ COMPLETED
- [x] Create `tests/test_cli_unit.py` using clirunner (11 comprehensive tests)
  - [x] Test all commands with mocked subprocess
  - [x] Test error scenarios and edge cases
  - [x] Test argument parsing and validation
- [x] Create `tests/test_aws_mocking.py` using pytest-subprocess (10 tests)
  - [x] Mock AWS CLI success responses
  - [x] Mock AWS CLI error responses
  - [x] Test network failure scenarios

### Phase 3: Implement Integration Tests
- [ ] Create `tests/test_cli_integration.py` using pytest-console-scripts
  - [ ] Test installed package behavior
  - [ ] Test with various Python versions
  - [ ] Test configuration file handling
  - [ ] Test error messages and help output

### Phase 4: Implement E2E Smoke Tests
- [ ] Create `tests/test_e2e_smoke.py` to replace smoketest.sh
  - [ ] Use pytest markers to separate from unit tests
  - [ ] Implement proper assertions on output
  - [ ] Add timeout handling for network calls
  - [ ] Include environment setup/teardown
- [ ] Create `scripts/run_smoke_tests.py` as entry point
  - [ ] Check for required AWS credentials
  - [ ] Run only E2E marked tests
  - [ ] Generate test report

### Phase 5: CI/CD Integration
- [ ] Add test stages to CI pipeline:
  ```yaml
  - name: Unit Tests
    run: poetry run pytest -m unit --cov=kreatisite

  - name: Integration Tests
    run: poetry run pytest -m integration

  - name: E2E Smoke Tests (optional)
    run: poetry run pytest -m e2e
    if: github.event_name == 'release'
  ```
- [ ] Set coverage requirements (e.g., 80% minimum)
- [ ] Add test result reporting

## Example Test Implementations

### Unit Test Example (clirunner)
```python
from clirunner import CliRunner
from unittest.mock import patch
from kreatisite.cli import main

def test_check_domain_success():
    runner = CliRunner()
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.stdout = '{"Available": true}'
        mock_run.return_value.returncode = 0

        result = runner.invoke(main, ['check-domain', 'example.com'])

        assert result.exit_code == 0
        assert 'Available' in result.output
        mock_run.assert_called_once()
```

### AWS Mocking Example (pytest-subprocess)
```python
def test_aws_cli_call(fp):
    # Register expected AWS CLI call
    fp.register([
        'aws', 'route53domains', 'check-domain-availability',
        '--domain-name', 'example.com'
    ], stdout='{"Available": true}', returncode=0)

    result = check_domain_availability('example.com')
    assert result == 0
```

### Integration Test Example (pytest-console-scripts)
```python
def test_kreatisite_help_command(script_runner):
    result = script_runner.run(['kreatisite', 'help'])
    assert result.returncode == 0
    assert 'Kreatisite Command Line Application' in result.stdout
    assert result.stderr == ''
```

### E2E Smoke Test Example
```python
import pytest
import os
from subprocess import run

@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_check_domain_real_aws():
    """Test with real AWS API call."""
    # Skip if no AWS credentials
    if not os.environ.get('AWS_PROFILE'):
        pytest.skip("AWS credentials not configured")

    result = run(
        ['poetry', 'run', 'kreatisite', 'check-domain', 'example.com'],
        capture_output=True,
        text=True
    )

    assert result.returncode == 0
    assert ('Available' in result.stdout or 'Unavailable' in result.stdout)
    assert 'Error' not in result.stderr
```

## Benefits of This Approach
1. **Fast feedback** during development with mocked tests
2. **Cost-effective** testing without AWS API calls
3. **Comprehensive coverage** including error scenarios
4. **CI/CD friendly** with proper test stages
5. **Better debugging** with Python's rich assertion capabilities
6. **Cross-platform** compatibility (vs shell scripts)

## Migration Path
1. Keep `smoketest.sh` during transition
2. Implement new tests incrementally
3. Run both old and new tests in parallel
4. Deprecate `smoketest.sh` once new tests prove stable
5. Document test execution in README.md

## Implementation Notes (Lessons Learned)

### Pytest Configuration Evolution
- **Best Practice**: Use `pyproject.toml` for pytest configuration, not `pytest.ini`
- **Rationale**: Single configuration file for all tools (pytest, mypy, isort, etc.)
- **Modern Standard**: PEP 518 established pyproject.toml as the standard
- **Poetry Integration**: Consistent with Poetry-based projects
- **Reduced Clutter**: Fewer configuration files in project root

## Additional Best Practices
- Use pytest fixtures for common test setup
- Implement custom markers for test categorization
- Add performance benchmarks for CLI commands
- Consider property-based testing for domain validation
- Use tox for testing across Python versions
- Add mutation testing to verify test quality

## Resources
- [clirunner documentation](https://github.com/click-contrib/clirunner)
- [pytest-subprocess documentation](https://github.com/aklajnert/pytest-subprocess)
- [pytest-console-scripts documentation](https://github.com/kvas-it/pytest-console-scripts)
- [pytest best practices](https://docs.pytest.org/en/stable/explanation/goodpractices.html)
- [Python testing at Google](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings)
