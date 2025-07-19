#!/bin/bash

# Development helper script for code quality and formatting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Help function
show_help() {
    echo "Development Helper Script for Expense Tracker"
    echo ""
    echo "Usage: ./scripts/dev.sh [COMMAND]"
    echo ""
    echo "Code Quality Commands:"
    echo "  lint      - Run ruff linter (check only)"
    echo "  lint-fix  - Run ruff linter and fix issues"
    echo "  format    - Format code with ruff formatter"
    echo "  check     - Run all checks (lint + format check)"
    echo "  fix       - Fix all issues (lint-fix + format)"
    echo ""
    echo "Testing Commands:"
    echo "  test      - Run pytest with coverage"
    echo "  test-fast - Run pytest without coverage"
    echo "  test-watch - Run pytest in watch mode"
    echo ""
    echo "Development Commands:"
    echo "  clean     - Clean up cache files and temporary files"
    echo "  install   - Install all dependencies"
    echo "  install-dev - Install development dependencies"
    echo "  setup     - Setup development environment"
    echo ""
    echo "Docker Commands:"
    echo "  docker-lint - Run ruff inside Docker container"
    echo "  docker-test - Run tests inside Docker container"
    echo ""
    echo "Other:"
    echo "  help      - Show this help"
    echo ""
}

# Code quality functions
run_lint() {
    print_status "Running ruff linter..."
    if ruff check app/ scripts/ start.py; then
        print_success "Linting passed!"
    else
        print_error "Linting failed!"
        exit 1
    fi
}

run_lint_fix() {
    print_status "Running ruff linter with auto-fix..."
    ruff check --fix app/ scripts/ start.py
    print_success "Linting with fixes completed!"
}

run_format() {
    print_status "Running ruff formatter..."
    ruff format app/ scripts/ start.py
    print_success "Code formatting completed!"
}

run_format_check() {
    print_status "Checking code formatting..."
    if ruff format --check app/ scripts/ start.py; then
        print_success "Code formatting is correct!"
    else
        print_error "Code formatting issues found!"
        exit 1
    fi
}

run_check() {
    print_status "Running all code quality checks..."
    run_lint
    run_format_check
    print_success "All checks passed!"
}

run_fix() {
    print_status "Fixing all code quality issues..."
    run_lint_fix
    run_format
    print_success "All fixes applied!"
}

# Testing functions
run_test() {
    print_status "Running tests with coverage..."
    pytest --cov=app --cov-report=term-missing --cov-report=html
}

run_test_fast() {
    print_status "Running tests (fast mode)..."
    pytest -x
}

run_test_watch() {
    print_status "Running tests in watch mode..."
    pytest-watch
}

# Development functions
clean_cache() {
    print_status "Cleaning cache and temporary files..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    find . -type f -name "*.pyo" -delete 2>/dev/null || true
    find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
    find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
    rm -rf htmlcov/ .coverage coverage.xml 2>/dev/null || true
    print_success "Cache cleaned!"
}

install_deps() {
    print_status "Installing project dependencies..."
    pip install -r requirements.txt
    print_success "Dependencies installed!"
}

install_dev_deps() {
    print_status "Installing development dependencies..."
    pip install -e ".[dev]"
    print_success "Development dependencies installed!"
}

setup_dev() {
    print_status "Setting up development environment..."
    install_deps
    install_dev_deps
    print_success "Development environment setup complete!"
}

# Docker functions
docker_lint() {
    print_status "Running linter in Docker container..."
    docker-compose exec api ruff check app/
}

docker_test() {
    print_status "Running tests in Docker container..."
    docker-compose exec api pytest -v
}

# Main script logic
case "${1:-help}" in
    lint)
        run_lint
        ;;
    lint-fix)
        run_lint_fix
        ;;
    format)
        run_format
        ;;
    format-check)
        run_format_check
        ;;
    check)
        run_check
        ;;
    fix)
        run_fix
        ;;
    test)
        run_test
        ;;
    test-fast)
        run_test_fast
        ;;
    test-watch)
        run_test_watch
        ;;
    clean)
        clean_cache
        ;;
    install)
        install_deps
        ;;
    install-dev)
        install_dev_deps
        ;;
    setup)
        setup_dev
        ;;
    docker-lint)
        docker_lint
        ;;
    docker-test)
        docker_test
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac 