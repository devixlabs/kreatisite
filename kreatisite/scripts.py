"""Scripts for development and build processes."""

import subprocess
import sys


def lint():
    """Run flake8 linting on the codebase."""
    print("Running flake8 linter...")
    result = subprocess.run(
        ["flake8", "kreatisite"], capture_output=True, text=True
    )
    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        return 1
    print("Linting passed!")
    return 0


def test():
    """Run pytest on the codebase."""
    print("Running tests...")
    # Run pytest with output going directly to the console
    result = subprocess.run(["pytest", "-v"], check=False)
    if result.returncode != 0:
        print("Tests failed!", file=sys.stderr)
        return 1
    print("All tests passed!")
    return 0


def check_all():
    """Run all checks (linting, type checking, tests, etc.)."""
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


if __name__ == "__main__":
    sys.exit(check_all())
