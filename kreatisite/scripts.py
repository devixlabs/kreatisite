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


def run_unit_tests() -> int:
    """Run unit tests with coverage reporting.

    Returns:
        int: 0 if tests pass, 1 if they fail
    """
    print("🧪 Running Unit Tests (fast, mocked)...")
    print("=" * 50)

    # Run unit tests with coverage
    result = subprocess.run(
        [
            "pytest",
            "-v",
            "-m",
            "unit",
            "--cov=kreatisite",
            "--cov-report=term-missing",
            "--cov-fail-under=80",
        ],
        check=False,
    )

    if result.returncode != 0:
        print("❌ Unit tests failed!", file=sys.stderr)
        return result.returncode

    print("✅ Unit tests passed!")
    return 0


def run_integration_tests() -> int:
    """Run integration tests.

    Returns:
        int: 0 if tests pass, 1 if they fail
    """
    print("🔗 Running Integration Tests (installed package)...")
    print("=" * 50)

    # Run integration tests
    result = subprocess.run(["pytest", "-v", "-m", "integration"], check=False)

    if result.returncode != 0:
        print("❌ Integration tests failed!", file=sys.stderr)
        return result.returncode

    print("✅ Integration tests passed!")
    return 0


def run_comprehensive_tests() -> int:
    """Run comprehensive test suite: unit, integration, and e2e tests.

    Returns:
        int: 0 if all tests pass, non-zero if any test fails
    """
    print("🚀 Running Comprehensive Test Suite...")
    print("=" * 60)

    # Phase 1: Unit Tests with Coverage
    print("\n📋 Phase 1: Unit Tests with Coverage Requirements")
    unit_result = run_unit_tests()
    if unit_result != 0:
        print("❌ Comprehensive tests failed at Phase 1 (Unit Tests)")
        return unit_result

    # Phase 2: Integration Tests
    print("\n📋 Phase 2: Integration Tests")
    integration_result = run_integration_tests()
    if integration_result != 0:
        print("❌ Comprehensive tests failed at Phase 2 (Integration Tests)")
        return integration_result

    # Phase 3: E2E Smoke Tests
    print("\n📋 Phase 3: E2E Smoke Tests")
    e2e_result = run_smoke_tests()
    if e2e_result != 0:
        print("❌ Comprehensive tests failed at Phase 3 (E2E Tests)")
        return e2e_result

    print("\n" + "=" * 60)
    print("✅ ALL COMPREHENSIVE TESTS PASSED!")
    print("   - Unit Tests: ✅ (with 80% coverage requirement)")
    print("   - Integration Tests: ✅")
    print("   - E2E Smoke Tests: ✅")
    print("=" * 60)
    return 0


def check_all() -> int:
    """Run all checks (linting, type checking, tests, etc.).

    Returns:
        int: 0 if all checks pass, non-zero if any check fails
    """
    print("🔍 Running All Checks...")
    print("=" * 60)

    # Run linting
    print("\n📋 Step 1: Linting")
    lint_result = lint()
    if lint_result != 0:
        return lint_result

    # Run comprehensive tests (unit, integration, e2e)
    print("\n📋 Step 2: Comprehensive Test Suite")
    test_result = run_comprehensive_tests()
    if test_result != 0:
        return test_result

    print("\n" + "=" * 60)
    print("✅ ALL CHECKS PASSED!")
    print("   - Linting: ✅")
    print("   - Comprehensive Tests: ✅")
    print("=" * 60)
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
