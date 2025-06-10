#!/bin/bash
set -e

echo "🚀 Kreatisite Pre-Build Pipeline (Phase 5: CI/CD Integration)"
echo "============================================================="

# Run pre-commit checks on all files (includes Black, isort, flake8, mypy, etc.)
echo ""
echo "📋 Stage 1: Code Quality Checks (pre-commit hooks)"
echo "---------------------------------------------------"
poetry run pre-commit run --all-files || { 
    echo "❌ Pre-commit checks failed. Please fix issues before building."; 
    exit 1; 
}
echo "✅ Code quality checks passed!"

echo ""
find . -type f -name "*.sh" -exec shellcheck {} + || {
    echo "❌ shellcheck failed. Please fix issues before building."; 
    exit 1;
}
echo "✅ shellcheck passed!"

# Run comprehensive test suite (unit, integration, e2e with coverage)
echo ""
echo "📋 Stage 2: Comprehensive Test Suite"
echo "------------------------------------"
poetry run comprehensive-tests || { 
    echo "❌ Comprehensive tests failed. Please fix issues before building."; 
    exit 1; 
}

echo ""
echo "📋 Stage 3: Package Build"
echo "-------------------------"
echo "Building package..."
poetry build || {
    echo "❌ Package build failed.";
    exit 1;
}

echo ""
echo "============================================================="
echo "✅ PRE-BUILD PIPELINE COMPLETED SUCCESSFULLY!"
echo "   - Code Quality: ✅ (Black, isort, flake8, mypy)"
echo "   - Unit Tests: ✅ (with 80% coverage requirement)"
echo "   - Integration Tests: ✅"
echo "   - E2E Smoke Tests: ✅"
echo "   - Package Build: ✅"
echo "============================================================="
