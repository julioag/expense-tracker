#!/bin/bash

# Docker development helper script for Expense Tracker

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
    echo "Docker Development Helper for Expense Tracker"
    echo ""
    echo "Usage: ./docker-dev.sh [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     - Start all services"
    echo "  stop      - Stop all services"
    echo "  restart   - Restart all services"
    echo "  build     - Build the API image"
    echo "  rebuild   - Rebuild the API image (no cache)"
    echo "  logs      - Show API logs (follow)"
    echo "  db-logs   - Show database logs"
    echo "  shell     - Open shell in API container"
    echo "  db-shell  - Open psql shell in database"
    echo "  clean     - Remove containers and volumes"
    echo "  reset     - Full reset (clean + rebuild + start)"
    echo "  status    - Show container status"
    echo "  test      - Run API tests"
    echo "  pgadmin   - Start with pgAdmin"
    echo "  help      - Show this help"
    echo ""
}

# Start services
start_services() {
    print_status "Starting Expense Tracker services..."
    docker compose up -d
    print_success "Services started!"
    echo ""
    print_status "API will be available at: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
    print_status "Health check: http://localhost:8000/health"
}

# Stop services
stop_services() {
    print_status "Stopping Expense Tracker services..."
    docker compose down
    print_success "Services stopped!"
}

# Restart services
restart_services() {
    print_status "Restarting Expense Tracker services..."
    docker compose down
    docker compose up -d
    print_success "Services restarted!"
}

# Build image
build_image() {
    print_status "Building API image..."
    docker compose build api
    print_success "Image built successfully!"
}

# Rebuild image (no cache)
rebuild_image() {
    print_status "Rebuilding API image (no cache)..."
    docker compose build --no-cache api
    print_success "Image rebuilt successfully!"
}

# Show logs
show_logs() {
    print_status "Showing API logs (Ctrl+C to exit)..."
    docker compose logs -f api
}

# Show database logs
show_db_logs() {
    print_status "Showing database logs (Ctrl+C to exit)..."
    docker compose logs -f postgres
}

# Open shell in API container
open_shell() {
    print_status "Opening shell in API container..."
    docker compose exec api bash
}

# Open database shell
open_db_shell() {
    print_status "Opening PostgreSQL shell..."
    docker compose exec postgres psql -U expense_user -d expense_tracker
}

# Clean containers and volumes
clean_all() {
    print_warning "This will remove all containers, networks, and volumes!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Cleaning up..."
        docker compose down -v --remove-orphans
        docker system prune -f
        print_success "Cleanup complete!"
    else
        print_status "Cleanup cancelled."
    fi
}

# Full reset
full_reset() {
    print_warning "This will perform a full reset (clean + rebuild + start)!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        clean_all
        rebuild_image
        start_services
        print_success "Full reset complete!"
    else
        print_status "Reset cancelled."
    fi
}

# Show container status
show_status() {
    print_status "Container status:"
    docker compose ps
}

# Run tests
run_tests() {
    print_status "Running API tests..."
    docker compose exec api pytest -v
}

# Start with pgAdmin
start_with_pgadmin() {
    print_status "Starting services with pgAdmin..."
    docker compose --profile tools up -d
    print_success "Services started with pgAdmin!"
    echo ""
    print_status "API: http://localhost:8000"
    print_status "pgAdmin: http://localhost:8080"
    print_status "pgAdmin login: admin@expense-tracker.local / admin"
}

# Main script logic
case "${1:-help}" in
    start)
        start_services
        ;;
    stop)
        stop_services
        ;;
    restart)
        restart_services
        ;;
    build)
        build_image
        ;;
    rebuild)
        rebuild_image
        ;;
    logs)
        show_logs
        ;;
    db-logs)
        show_db_logs
        ;;
    shell)
        open_shell
        ;;
    db-shell)
        open_db_shell
        ;;
    clean)
        clean_all
        ;;
    reset)
        full_reset
        ;;
    status)
        show_status
        ;;
    test)
        run_tests
        ;;
    pgadmin)
        start_with_pgadmin
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