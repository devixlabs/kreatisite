"""Unit tests for CLI using clirunner and mocked subprocess calls."""

from unittest.mock import Mock, patch

import pytest
from clirunner import CliRunner

from kreatisite.cli import main


@pytest.mark.unit
def test_help_command():
    """Test help command with clirunner."""
    runner = CliRunner()
    result = runner.invoke(main, ["help"])

    assert result.exit_code == 0
    assert "Kreatisite Command Line Application" in result.output
    assert "check-domain" in result.output
    assert "register-domain" in result.output


@pytest.mark.unit
def test_no_command_shows_help():
    """Test that no command shows help."""
    runner = CliRunner()
    result = runner.invoke(main, [])

    assert result.exit_code == 0
    assert "Kreatisite Command Line Application" in result.output


@pytest.mark.unit
def test_invalid_command():
    """Test invalid command shows parser help."""
    runner = CliRunner()
    result = runner.invoke(main, ["invalid-command"])

    assert result.exit_code == 2  # argparse returns 2 for invalid arguments
    assert "usage:" in result.output.lower() or "help" in result.output.lower()


@pytest.mark.unit
@patch("kreatisite.cli.check_dependencies")
@patch("subprocess.run")
def test_check_domain_success(mock_run, mock_deps):
    """Test check-domain command with successful AWS response."""
    mock_deps.return_value = None
    mock_run.return_value = Mock(stdout='{"Available": true}', stderr="", returncode=0)

    runner = CliRunner()
    result = runner.invoke(main, ["check-domain", "example.com"])

    assert result.exit_code == 0
    assert '{"Available": true}' in result.output
    mock_run.assert_called_once()
    # Verify the AWS CLI command was constructed correctly
    call_args = mock_run.call_args[0][0]
    assert call_args[:3] == ["aws", "route53domains", "check-domain-availability"]
    assert "--domain-name" in call_args
    assert "example.com" in call_args


@pytest.mark.unit
@patch("kreatisite.cli.check_dependencies")
@patch("subprocess.run")
def test_check_domain_aws_error(mock_run, mock_deps):
    """Test check-domain command with AWS error response."""
    mock_deps.return_value = None
    mock_run.return_value = Mock(
        stdout="", stderr="An error occurred (ValidationException)", returncode=1
    )

    runner = CliRunner()
    result = runner.invoke(main, ["check-domain", "invalid-domain"])

    assert result.exit_code == 1
    assert "Error:" in result.output
    assert "ValidationException" in result.output


@pytest.mark.unit
@patch("kreatisite.cli.check_dependencies")
@patch("subprocess.run", side_effect=Exception("Network error"))
def test_check_domain_subprocess_exception(mock_run, mock_deps):
    """Test check-domain command with subprocess exception."""
    mock_deps.return_value = None

    runner = CliRunner()
    result = runner.invoke(main, ["check-domain", "example.com"])

    assert result.exit_code == 1
    assert "Error executing AWS command" in result.output
    assert "Network error" in result.output


@pytest.mark.unit
@patch("shutil.which", return_value=None)
def test_check_domain_missing_aws_cli(mock_which):
    """Test check-domain command when AWS CLI is missing."""
    runner = CliRunner()
    result = runner.invoke(main, ["check-domain", "example.com"])

    assert result.exit_code == 1
    assert "Missing required commands: aws" in result.output
    assert "install AWS CLI" in result.output


@pytest.mark.unit
def test_register_domain_missing_config():
    """Test register-domain command with missing config file."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        result = runner.invoke(main, ["register-domain", "example.com"])

        assert result.exit_code == 1
        assert "Config file" in result.output and "not found" in result.output
        assert "aws-register-domain.yaml.example" in result.output


@pytest.mark.unit
@patch("kreatisite.cli.check_dependencies")
def test_register_domain_with_config(mock_deps):
    """Test register-domain command with valid config file."""
    mock_deps.return_value = None

    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create a mock config file
        with open("config.yaml", "w") as f:
            f.write("AdminContact:\n  FirstName: Test\n")

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                stdout='{"OperationId": "test-123"}', stderr="", returncode=0
            )

            result = runner.invoke(
                main, ["register-domain", "example.com", "--config-file", "config.yaml"]
            )

            assert result.exit_code == 0
            assert "test-123" in result.output
            mock_run.assert_called_once()

            # Verify AWS CLI command construction
            call_args = mock_run.call_args[0][0]
            assert "aws" in call_args
            assert "route53domains" in call_args
            assert "register-domain" in call_args
            assert "--domain-name" in call_args
            assert "example.com" in call_args


@pytest.mark.unit
def test_register_domain_invalid_yaml():
    """Test register-domain command with invalid YAML config."""
    runner = CliRunner()
    with runner.isolated_filesystem():
        # Create invalid YAML file
        with open("invalid.yaml", "w") as f:
            f.write("invalid: yaml: content: [")

        result = runner.invoke(
            main, ["register-domain", "example.com", "--config-file", "invalid.yaml"]
        )

        assert result.exit_code == 1
        assert "Error parsing YAML config file" in result.output


@pytest.mark.unit
def test_argument_parsing_edge_cases():
    """Test various argument parsing edge cases."""
    runner = CliRunner()

    # Test missing domain name for check-domain
    result = runner.invoke(main, ["check-domain"])
    assert result.exit_code != 0

    # Test missing domain name for register-domain
    result = runner.invoke(main, ["register-domain"])
    assert result.exit_code != 0
