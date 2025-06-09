"""Tests for the parser module."""

import argparse
from unittest.mock import Mock

import pytest

from kreatisite.parser import (
    create_check_domain_parser,
    create_parser,
    create_register_domain_parser,
)


def test_create_parser() -> None:
    """Test that create_parser returns a properly configured ArgumentParser."""
    parser = create_parser()

    assert isinstance(parser, argparse.ArgumentParser)
    assert parser.prog == "kreatisite"
    assert "Kreatisite - A command line application" in parser.description
    assert "devixlabs.com" in parser.epilog


def test_create_parser_help_command() -> None:
    """Test that help command is properly configured."""
    parser = create_parser()

    # Test help command parsing
    args = parser.parse_args(["help"])
    assert args.command == "help"


def test_create_parser_check_domain_command() -> None:
    """Test that check-domain command is properly configured."""
    parser = create_parser()

    # Test check-domain command parsing
    args = parser.parse_args(["check-domain", "example.com"])
    assert args.command == "check-domain"
    assert args.domain_name == "example.com"


def test_create_parser_register_domain_defaults() -> None:
    """Test register-domain command with default values."""
    parser = create_parser()

    # Test register-domain command parsing with defaults
    args = parser.parse_args(["register-domain", "example.com"])
    assert args.command == "register-domain"
    assert args.domain_name == "example.com"
    assert args.config_file == "aws-register-domain.yaml"
    assert args.duration_in_years == 1
    assert args.auto_renew is True


def test_create_parser_register_domain_custom_config() -> None:
    """Test register-domain command with custom config file."""
    parser = create_parser()

    args = parser.parse_args(
        ["register-domain", "example.com", "--config-file", "custom-config.yaml"]
    )
    assert args.config_file == "custom-config.yaml"


def test_create_parser_register_domain_custom_duration() -> None:
    """Test register-domain command with custom duration."""
    parser = create_parser()

    args = parser.parse_args(["register-domain", "example.com", "--duration-in-years", "3"])
    assert args.duration_in_years == 3


def test_create_parser_register_domain_no_auto_renew() -> None:
    """Test register-domain command with auto-renew disabled."""
    parser = create_parser()

    args = parser.parse_args(["register-domain", "example.com", "--no-auto-renew"])
    assert args.auto_renew is False


def test_create_parser_register_domain_all_options() -> None:
    """Test register-domain command with all options."""
    parser = create_parser()

    args = parser.parse_args(
        [
            "register-domain",
            "example.com",
            "--config-file",
            "my-config.yaml",
            "--duration-in-years",
            "5",
            "--no-auto-renew",
        ]
    )
    assert args.command == "register-domain"
    assert args.domain_name == "example.com"
    assert args.config_file == "my-config.yaml"
    assert args.duration_in_years == 5
    assert args.auto_renew is False


def test_create_check_domain_parser() -> None:
    """Test create_check_domain_parser function."""
    # Create a mock subparsers object
    subparsers = Mock()
    mock_parser = Mock()
    subparsers.add_parser.return_value = mock_parser

    create_check_domain_parser(subparsers)

    # Verify the parser was added with correct parameters
    subparsers.add_parser.assert_called_once_with(
        "check-domain",
        help="Check domain availability using AWS Route53",
    )

    # Verify domain_name argument was added
    mock_parser.add_argument.assert_called_once_with(
        "domain_name",
        help="Domain name to check (e.g., example.com)",
    )


def test_create_register_domain_parser() -> None:
    """Test create_register_domain_parser function."""
    # Create a mock subparsers object
    subparsers = Mock()
    mock_parser = Mock()
    subparsers.add_parser.return_value = mock_parser

    create_register_domain_parser(subparsers)

    # Verify the parser was added
    subparsers.add_parser.assert_called_once_with(
        "register-domain",
        help="Register a domain using AWS Route53",
    )

    # Verify all arguments were added (4 calls expected)
    assert mock_parser.add_argument.call_count == 4

    # Check that all expected arguments were added by examining call args
    call_args = [call[0][0] for call in mock_parser.add_argument.call_args_list]
    assert "domain_name" in call_args
    assert "--config-file" in call_args
    assert "--duration-in-years" in call_args
    assert "--no-auto-renew" in call_args


def test_parser_error_handling() -> None:
    """Test parser error handling for invalid arguments."""
    parser = create_parser()

    # Test missing required argument for check-domain
    with pytest.raises(SystemExit):
        parser.parse_args(["check-domain"])

    # Test missing required argument for register-domain
    with pytest.raises(SystemExit):
        parser.parse_args(["register-domain"])


def test_parser_invalid_duration_type() -> None:
    """Test parser handles invalid duration type."""
    parser = create_parser()

    # Test invalid duration (non-integer)
    with pytest.raises(SystemExit):
        parser.parse_args(["register-domain", "example.com", "--duration-in-years", "not-a-number"])
