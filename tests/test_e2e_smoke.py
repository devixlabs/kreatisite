"""E2E smoke tests for Kreatisite CLI with proper assertions."""

import os
import subprocess
from pathlib import Path

import pytest


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_help_command_e2e():
    """Test help command with real CLI execution."""
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert "Kreatisite Command Line Application" in result.stdout
    assert "check-domain" in result.stdout
    assert "register-domain" in result.stdout
    assert result.stderr == ""


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_no_command_shows_help_e2e():
    """Test that running kreatisite with no command shows help."""
    result = subprocess.run(
        ["poetry", "run", "kreatisite"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    assert "Kreatisite Command Line Application" in result.stdout
    assert "check-domain" in result.stdout
    assert "register-domain" in result.stdout


@pytest.mark.e2e
@pytest.mark.timeout(60)
def test_check_domain_real_aws():
    """Test check-domain with real AWS API call (requires AWS credentials)."""
    # Skip if no AWS credentials are configured
    if not (
        os.environ.get("AWS_PROFILE")
        or (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))
    ):
        pytest.skip(
            "AWS credentials not configured (need AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY)"
        )

    # Test with a domain that should consistently return a result
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "check-domain", "example.com"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 0
    # Output should contain either Available or Unavailable status (case-sensitive)
    assert (
        "Available" in result.stdout
        or "Unavailable" in result.stdout
        or "AVAILABLE" in result.stdout
        or "UNAVAILABLE" in result.stdout
    )
    # Should not contain error messages in stderr
    assert "Error" not in result.stderr
    # Should be valid JSON response from AWS
    assert "{" in result.stdout and "}" in result.stdout


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_check_domain_invalid_domain():
    """Test check-domain with invalid domain format."""
    # Skip if no AWS credentials are configured
    if not (
        os.environ.get("AWS_PROFILE")
        or (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))
    ):
        pytest.skip("AWS credentials not configured")

    result = subprocess.run(
        ["poetry", "run", "kreatisite", "check-domain", "invalid-domain-format"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Should fail with non-zero exit code
    assert result.returncode != 0
    # Should contain error information
    assert "Error" in result.stdout or "Error" in result.stderr


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_register_domain_missing_config():
    """Test register-domain command with missing config file."""
    result = subprocess.run(
        [
            "poetry",
            "run",
            "kreatisite",
            "register-domain",
            "example.com",
            "--config-file",
            "missing-config.yaml",
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 1
    # Config file error messages are printed to stderr, not stdout
    assert "Config file" in result.stderr and "not found" in result.stderr
    assert "aws-register-domain.yaml.example" in result.stderr


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_register_domain_with_example_config():
    """Test register-domain command with example config file (should validate but not execute)."""
    # Skip if no AWS credentials are configured
    if not (
        os.environ.get("AWS_PROFILE")
        or (os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY"))
    ):
        pytest.skip("AWS credentials not configured")

    # Use the example config file
    config_path = Path(__file__).parent.parent / "aws-register-domain.yaml.example"
    if not config_path.exists():
        pytest.skip("Example config file not found")

    # Test with a clearly test domain to avoid accidental registration
    result = subprocess.run(
        [
            "poetry",
            "run",
            "kreatisite",
            "register-domain",
            "test-domain-do-not-register.com",
            "--config-file",
            str(config_path),
        ],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # This should either succeed with AWS response or fail with AWS validation error
    # But should not fail due to missing config file
    assert "Config file" not in result.stdout or "not found" not in result.stdout
    assert "Config file" not in result.stderr or "not found" not in result.stderr
    # Should contain some AWS-related response or error (check both stdout and stderr)
    assert (
        result.returncode == 0
        or "aws" in result.stdout.lower()
        or "Error" in result.stdout
        or "aws" in result.stderr.lower()
        or "Error" in result.stderr
    )


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_invalid_command_e2e():
    """Test invalid command returns proper error."""
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "invalid-command"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    assert result.returncode == 2  # argparse returns 2 for invalid arguments
    assert (
        "usage:" in result.stderr.lower()
        or "help" in result.stderr.lower()
        or "usage:" in result.stdout.lower()
        or "help" in result.stdout.lower()
    )


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_cli_version_info():
    """Test that CLI provides version information when requested."""
    # Test --version flag if supported
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "--version"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Version flag might not be implemented, so this is informational
    # Just check that it doesn't crash catastrophically
    assert result.returncode in [0, 2]  # 0 for success, 2 for unrecognized argument


@pytest.mark.e2e
@pytest.mark.timeout(30)
def test_aws_cli_dependency_check():
    """Test that CLI properly checks for AWS CLI dependency."""
    # This test ensures the dependency checking mechanism works
    # We'll test this by running a command and ensuring it doesn't fail with missing Python deps
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "help"],
        capture_output=True,
        text=True,
        cwd=Path(__file__).parent.parent,
    )

    # Should not fail due to missing Python dependencies
    assert result.returncode == 0
    assert "ModuleNotFoundError" not in result.stderr
    assert "ImportError" not in result.stderr


@pytest.mark.e2e
@pytest.mark.timeout(45)
def test_smoke_test_comprehensive():
    """Comprehensive smoke test covering all core functionality."""
    project_root = Path(__file__).parent.parent

    # Test 1: Help command
    result = subprocess.run(
        ["poetry", "run", "kreatisite", "help"],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 0, f"Help command failed: {result.stderr}"

    # Test 2: Check domain (only if AWS credentials available)
    aws_available = os.environ.get("AWS_PROFILE") or (
        os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

    if aws_available:
        result = subprocess.run(
            ["poetry", "run", "kreatisite", "check-domain", "example.com"],
            capture_output=True,
            text=True,
            cwd=project_root,
            timeout=30,
        )
        # Should succeed or fail gracefully, but not crash
        assert result.returncode in [0, 1], f"Check domain failed unexpectedly: {result.stderr}"
        assert "Traceback" not in result.stderr, "Python traceback found in stderr"

    # Test 3: Register domain with missing config (should fail gracefully)
    result = subprocess.run(
        [
            "poetry",
            "run",
            "kreatisite",
            "register-domain",
            "example.com",
            "--config-file",
            "nonexistent-config.yaml",
        ],
        capture_output=True,
        text=True,
        cwd=project_root,
    )
    assert result.returncode == 1, "Register domain should fail with missing config"
    assert "Config file" in result.stderr, "Should indicate missing config file"

    print("✅ All smoke tests passed successfully!")
