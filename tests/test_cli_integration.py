"""
Integration tests for kreatisite CLI using pytest-console-scripts.

These tests run the installed package as users would execute it,
testing the actual console_scripts entry point behavior.
"""

import os
from pathlib import Path

import pytest


@pytest.mark.integration
def test_kreatisite_help_command(script_runner):
    """Test kreatisite help command shows usage information."""
    result = script_runner.run(["kreatisite", "help"])

    assert result.returncode == 0
    assert "Kreatisite Command Line Application" in result.stdout
    assert "COMMANDS" in result.stdout
    assert "check-domain" in result.stdout
    assert "register-domain" in result.stdout
    assert result.stderr == ""


@pytest.mark.integration
def test_kreatisite_no_args(script_runner):
    """Test kreatisite with no arguments shows help."""
    result = script_runner.run(["kreatisite"])

    assert result.returncode == 0
    assert "Kreatisite Command Line Application" in result.stdout
    assert "COMMANDS" in result.stdout


@pytest.mark.integration
def test_kreatisite_invalid_command(script_runner):
    """Test kreatisite with invalid command shows error."""
    result = script_runner.run(["kreatisite", "invalid-command"])

    assert result.returncode != 0
    assert "invalid choice" in result.stderr


@pytest.mark.integration
def test_check_domain_no_args(script_runner):
    """Test check-domain command without domain name shows error."""
    result = script_runner.run(["kreatisite", "check-domain"])

    assert result.returncode != 0
    assert "arguments are required: domain_name" in result.stderr


@pytest.mark.integration
def test_check_domain_invalid_format(script_runner):
    """Test check-domain with invalid domain format."""
    result = script_runner.run(["kreatisite", "check-domain", "invalid..domain"])

    # This will actually call AWS CLI and return an error, so we check for any error
    assert result.returncode != 0


@pytest.mark.integration
def test_check_domain_missing_aws_cli(script_runner, monkeypatch):
    """Test check-domain when AWS CLI is not available."""
    # Mock PATH to exclude AWS CLI
    monkeypatch.setenv("PATH", "/tmp")

    result = script_runner.run(["kreatisite", "check-domain", "example.com"])

    assert result.returncode != 0
    assert "Missing required commands: aws" in result.stderr


@pytest.mark.integration
def test_register_domain_no_args(script_runner):
    """Test register-domain command without domain name shows error."""
    result = script_runner.run(["kreatisite", "register-domain"])

    assert result.returncode != 0
    assert "arguments are required: domain_name" in result.stderr


@pytest.mark.integration
def test_register_domain_missing_config(script_runner, tmp_path):
    """Test register-domain without configuration file."""
    # Change to temporary directory without config file
    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = script_runner.run(["kreatisite", "register-domain", "example.com"])

        assert result.returncode != 0
        assert "Config file 'aws-register-domain.yaml' not found" in result.stderr
    finally:
        os.chdir(old_cwd)


@pytest.mark.integration
def test_register_domain_invalid_config(script_runner, tmp_path):
    """Test register-domain with invalid configuration file."""
    # Create invalid YAML config file
    config_file = tmp_path / "aws-register-domain.yaml"
    config_file.write_text("invalid: yaml: content: [")

    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        result = script_runner.run(["kreatisite", "register-domain", "example.com"])

        assert result.returncode != 0
        assert "Error parsing YAML config file" in result.stderr
    finally:
        os.chdir(old_cwd)


@pytest.mark.integration
def test_configuration_file_handling(script_runner, tmp_path):
    """Test configuration file validation with valid YAML structure."""
    # Create valid but minimal YAML config file
    config_content = """
AdminContact:
  FirstName: Test
  LastName: User
  ContactType: PERSON
  AddressLine1: 123 Test St
  City: TestCity
  CountryCode: US
  ZipCode: 12345
  PhoneNumber: +1.5551234567
  Email: test@example.com
RegistrantContact:
  FirstName: Test
  LastName: User
  ContactType: PERSON
  AddressLine1: 123 Test St
  City: TestCity
  CountryCode: US
  ZipCode: 12345
  PhoneNumber: +1.5551234567
  Email: test@example.com
TechContact:
  FirstName: Test
  LastName: User
  ContactType: PERSON
  AddressLine1: 123 Test St
  City: TestCity
  CountryCode: US
  ZipCode: 12345
  PhoneNumber: +1.5551234567
  Email: test@example.com
"""

    config_file = tmp_path / "aws-register-domain.yaml"
    config_file.write_text(config_content)

    old_cwd = os.getcwd()
    os.chdir(tmp_path)

    try:
        # This will fail at AWS CLI call (expected), but should pass config validation
        result = script_runner.run(["kreatisite", "register-domain", "example.com"])

        # Should fail at AWS CLI stage, not config parsing
        assert "Error parsing YAML config file" not in result.stderr
    finally:
        os.chdir(old_cwd)


@pytest.mark.integration
def test_python_version_check(script_runner):
    """Test that the CLI properly reports Python version compatibility."""
    # This test ensures the version check code path works
    result = script_runner.run(["kreatisite", "help"])

    # Should not fail due to Python version issues
    assert result.returncode == 0
    assert "Python version" not in result.stderr


@pytest.mark.integration
def test_help_output_completeness(script_runner):
    """Test that help output contains all expected information."""
    result = script_runner.run(["kreatisite", "help"])

    assert result.returncode == 0
    output = result.stdout

    # Check for main sections
    assert "Kreatisite Command Line Application" in output
    assert "COMMANDS" in output

    # Check for command descriptions
    assert "check-domain" in output
    assert "register-domain" in output

    # Check for usage information
    assert "USAGE" in output or "kreatisite" in output


@pytest.mark.integration
def test_error_message_formatting(script_runner):
    """Test that error messages are properly formatted and helpful."""
    result = script_runner.run(["kreatisite", "nonexistent-command"])

    assert result.returncode != 0
    # Error should be informative
    assert len(result.stderr.strip()) > 0
    # Should suggest available commands or show help
    assert (
        "invalid choice" in result.stderr
        or "choose from" in result.stderr
        or "help" in result.stderr
    )
