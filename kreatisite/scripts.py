"""Scripts for development and build processes."""

import subprocess
import sys


def lint() -> int:
    """Run flake8 linting on the codebase.

    Returns:
        int: 0 if linting passes, 1 if it fails
    """
    print("Running flake8 linter...")
    result = subprocess.run(["flake8", "kreatisite"], capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1
    print("Linting passed!")
    return 0


def test() -> int:
    """Run pytest on the codebase.

    Returns:
        int: 0 if tests pass, 1 if they fail
    """
    print("Running tests...")
    # Run pytest with output going directly to the console
    result = subprocess.run(["pytest", "-v"], check=False)
    if result.returncode != 0:
        print("Tests failed!", file=sys.stderr)
        return 1
    print("All tests passed!")
    return 0


def check_all() -> int:
    """Run all checks (linting, type checking, tests, etc.).

    Returns:
        int: 0 if all checks pass, non-zero if any check fails
    """
    print("Running all checks...")
    # Run linting
    lint_result = lint()
    if lint_result != 0:
        return lint_result
    # Run tests
    print()  # Empty line for better output formatting
    test_result = test()
    if test_result != 0:
        return test_result
    print("All checks passed!")
    return 0


def setup_hooks() -> int:
    """Set up pre-commit hooks.

    Returns:
        int: 0 if successful, 1 if failed
    """
    print("Setting up pre-commit hooks...")
    try:
        # Get the project root directory
        result = subprocess.run(
            ["pre-commit", "install"], check=True, capture_output=True, text=True
        )
        print(result.stdout)
        print("Pre-commit hooks installed successfully!")
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error installing pre-commit hooks: {e}", file=sys.stderr)
        print(e.stdout)
        print(e.stderr, file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(check_all())
