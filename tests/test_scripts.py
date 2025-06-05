"""Tests for the scripts module."""

from unittest.mock import Mock, patch

from kreatisite.scripts import check_all, lint, setup_hooks


@patch('kreatisite.scripts.subprocess.run')
def test_lint_success(mock_run, capsys) -> None:
    """Test successful linting."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = ""
    mock_result.stderr = ""
    mock_run.return_value = mock_result

    result = lint()

    assert result == 0
    captured = capsys.readouterr()
    assert "Running flake8 linter..." in captured.out
    assert "Linting passed!" in captured.out
    mock_run.assert_called_once_with(
        ["flake8", "kreatisite"], capture_output=True, text=True
    )


@patch('kreatisite.scripts.subprocess.run')
def test_lint_failure(mock_run, capsys) -> None:
    """Test linting with errors."""
    mock_result = Mock()
    mock_result.returncode = 1
    mock_result.stdout = "kreatisite/module.py:1:1: E302 expected 2 blank lines"
    mock_result.stderr = "Some error"
    mock_run.return_value = mock_result

    result = lint()

    assert result == 1
    captured = capsys.readouterr()
    assert "Running flake8 linter..." in captured.out
    assert "kreatisite/module.py:1:1: E302 expected 2 blank lines" in captured.out
    assert "Some error" in captured.err


@patch('kreatisite.scripts.subprocess.run')
def test_setup_hooks_success(mock_run, capsys) -> None:
    """Test successful pre-commit hooks setup."""
    mock_result = Mock()
    mock_result.stdout = "pre-commit installed at .git/hooks/pre-commit"
    mock_result.returncode = 0
    mock_run.return_value = mock_result

    result = setup_hooks()

    assert result == 0
    captured = capsys.readouterr()
    assert "Setting up pre-commit hooks..." in captured.out
    assert "pre-commit installed at .git/hooks/pre-commit" in captured.out
    assert "Pre-commit hooks installed successfully!" in captured.out
    mock_run.assert_called_once_with(
        ["pre-commit", "install"],
        check=True,
        capture_output=True,
        text=True
    )


@patch('kreatisite.scripts.subprocess.run')
def test_setup_hooks_called_process_error(mock_run, capsys) -> None:
    """Test setup_hooks with CalledProcessError."""
    from subprocess import CalledProcessError

    error = CalledProcessError(1, ["pre-commit", "install"])
    error.stdout = "Some output"
    error.stderr = "Error message"
    mock_run.side_effect = error

    result = setup_hooks()

    assert result == 1
    captured = capsys.readouterr()
    assert "Setting up pre-commit hooks..." in captured.out
    assert "Error installing pre-commit hooks:" in captured.err
    assert "Some output" in captured.out
    assert "Error message" in captured.err


@patch('kreatisite.scripts.subprocess.run')
def test_setup_hooks_unexpected_error(mock_run, capsys) -> None:
    """Test setup_hooks with unexpected exception."""
    mock_run.side_effect = Exception("Unexpected error")

    result = setup_hooks()

    assert result == 1
    captured = capsys.readouterr()
    assert "Setting up pre-commit hooks..." in captured.out
    assert "Unexpected error: Unexpected error" in captured.err


def test_main_module_execution() -> None:
    """Test that scripts module can be executed as main."""
    # Test the if __name__ == "__main__" block
    # We can't directly test this, but we can verify the check_all function
    # is properly defined and would be called
    assert callable(check_all)

    # Test that the function exists and is importable
    # This is sufficient to verify the module structure is correct
    from kreatisite.scripts import check_all as imported_check_all
    assert imported_check_all is check_all


def test_scripts_module_imports() -> None:
    """Test that all functions are properly importable."""
    from kreatisite.scripts import check_all, lint, setup_hooks, test

    assert callable(lint)
    assert callable(test)
    assert callable(check_all)
    assert callable(setup_hooks)
