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


def run_smoke_tests() -> int:
    """Run E2E smoke tests with AWS credentials checking.

    Returns:
        int: 0 if smoke tests pass, non-zero if they fail
    """
    import os

    print("Running E2E smoke tests...")

    # Check for AWS credentials
    aws_available = os.environ.get("AWS_PROFILE") or (
        os.environ.get("AWS_ACCESS_KEY_ID") and os.environ.get("AWS_SECRET_ACCESS_KEY")
    )

    if not aws_available:
        print("⚠️  WARNING: AWS credentials not detected.")
        print("   Set AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY")
        print("   Some E2E tests will be skipped.")
        print()
    else:
        print("✅ AWS credentials detected - running full E2E test suite")
        print()

    # Run only E2E marked tests with verbose output and timeout
    result = subprocess.run(
        ["pytest", "-v", "-m", "e2e", "--timeout=60", "tests/test_e2e_smoke.py"], check=False
    )

    if result.returncode != 0:
        print("❌ Smoke tests failed!", file=sys.stderr)
        return result.returncode

    print("✅ All smoke tests passed!")
    return 0


if __name__ == "__main__":
    sys.exit(check_all())
