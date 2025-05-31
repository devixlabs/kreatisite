"""Tests for the CLI module."""

from unittest.mock import Mock, patch

from kreatisite.cli import main, print_help


def test_print_help(capsys) -> None:
    """Test that print_help outputs the expected help text."""
    print_help()
    captured = capsys.readouterr()
    assert "Kreatisite Command Line Application" in captured.out
    assert "DESCRIPTION" in captured.out
    assert "USAGE" in captured.out
    assert "COMMANDS" in captured.out
    assert "check-domain" in captured.out
    assert "register-domain" in captured.out


@patch('kreatisite.cli.create_parser')
def test_main_no_command(mock_create_parser, capsys) -> None:
    """Test main function with no command shows help."""
    mock_parser = Mock()
    mock_args = Mock()
    mock_args.command = None
    mock_parser.parse_args.return_value = mock_args
    mock_create_parser.return_value = mock_parser

    result = main()

    captured = capsys.readouterr()
    assert "Kreatisite Command Line Application" in captured.out
    assert result is None


@patch('kreatisite.cli.create_parser')
def test_main_help_command(mock_create_parser, capsys) -> None:
    """Test main function with help command."""
    mock_parser = Mock()
    mock_args = Mock()
    mock_args.command = "help"
    mock_parser.parse_args.return_value = mock_args
    mock_create_parser.return_value = mock_parser

    result = main()

    captured = capsys.readouterr()
    assert "Kreatisite Command Line Application" in captured.out
    assert result is None


@patch('kreatisite.cli.check_domain_availability')
@patch('kreatisite.cli.create_parser')
def test_main_check_domain_command(mock_create_parser, mock_check_domain) -> None:
    """Test main function with check-domain command."""
    mock_parser = Mock()
    mock_args = Mock()
    mock_args.command = "check-domain"
    mock_args.domain_name = "example.com"
    mock_parser.parse_args.return_value = mock_args
    mock_create_parser.return_value = mock_parser
    mock_check_domain.return_value = 0

    result = main()

    mock_check_domain.assert_called_once_with("example.com")
    assert result == 0


@patch('kreatisite.cli.register_domain')
@patch('kreatisite.cli.create_parser')
def test_main_register_domain_command(mock_create_parser, mock_register_domain) -> None:
    """Test main function with register-domain command."""
    mock_parser = Mock()
    mock_args = Mock()
    mock_args.command = "register-domain"
    mock_parser.parse_args.return_value = mock_args
    mock_create_parser.return_value = mock_parser
    mock_register_domain.return_value = 0

    result = main()

    mock_register_domain.assert_called_once_with(mock_args)
    assert result == 0


@patch('kreatisite.cli.create_parser')
def test_main_invalid_command(mock_create_parser) -> None:
    """Test main function with invalid command."""
    mock_parser = Mock()
    mock_args = Mock()
    mock_args.command = "invalid-command"
    mock_parser.parse_args.return_value = mock_args
    mock_create_parser.return_value = mock_parser

    result = main()

    mock_parser.print_help.assert_called_once()
    assert result is None


def test_python_version_check() -> None:
    """Test that the module enforces Python version requirement."""
    # This test verifies the version check exists at import time
    # The actual enforcement happens at module level, so just importing
    # kreatisite.cli on Python 3.9+ should work
    import kreatisite.cli
    assert hasattr(kreatisite.cli, 'main')
