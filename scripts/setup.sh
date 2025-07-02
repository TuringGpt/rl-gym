#!/bin/bash

# API Mock Gym Setup Script
# This script sets up the development environment for the API Mock Gym project

set -e

echo "🚀 Setting up API Mock Gym..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if required tools are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "All dependencies are available."
}

# Generate environment files
generate_env_files() {
    print_status "Generating environment files..."
    
    # Generate main .env file
    if [ ! -f .env ]; then
        cp .env.template .env
        print_success "Created .env file from template"
    else
        print_warning ".env file already exists, skipping..."
    fi
    
    # Generate service-specific .env files
    ./scripts/generate-env.sh
}

# Create necessary directories
create_directories() {
    print_status "Creating project directories..."
    
    directories=(
        "logs"
        "data/backups"
        "docs"
        "shared/utils"
        "shared/models"
        "services/amazon/app/api/v0"
        "services/amazon/app/api/2021-06-30"
        "services/amazon/app/api/2021-08-01"
        "services/amazon/app/models"
        "services/amazon/app/database"
        "services/amazon/app/services"
        "services/amazon/tests"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            mkdir -p "$dir"
            print_success "Created directory: $dir"
        fi
    done
}

# Set proper permissions
set_permissions() {
    print_status "Setting file permissions..."
    
    # Make scripts executable
    chmod +x scripts/*.sh
    
    # Set proper permissions for data directories
    chmod -R 755 data/ 2>/dev/null || true
    chmod -R 755 logs/ 2>/dev/null || true
    
    print_success "Permissions set correctly."
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build Amazon service image
    if [ -f "services/amazon/Dockerfile" ]; then
        docker-compose build amazon-api
        print_success "Built Amazon API service image"
    else
        print_warning "Amazon service Dockerfile not found, will be built later"
    fi
}

# Initialize databases
init_databases() {
    print_status "Initializing databases..."
    
    # Start database services
    docker-compose up -d amazon-db redis
    
    print_status "Waiting for databases to be ready..."
    sleep 15
    
    # Check database health
    if docker-compose exec -T amazon-db pg_isready -U amazon_user -d amazon_sp_db; then
        print_success "Amazon database is ready"
    else
        print_warning "Amazon database may not be fully ready, continue anyway..."
    fi
    
    print_success "Database initialization complete"
}

# Run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Check if all required files exist
    required_files=(
        "docker-compose.yml"
        ".env"
        "services/amazon/.env.template"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            print_error "Required file missing: $file"
            exit 1
        fi
    done
    
    print_success "All health checks passed"
}

# Main setup function
main() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║                     API Mock Gym Setup                       ║"
    echo "║               Setting up development environment              ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    check_dependencies
    create_directories
    generate_env_files
    set_permissions
    
    # Only build and init if services are implemented
    if [ -f "services/amazon/main.py" ]; then
        build_images
        init_databases
    else
        print_warning "Service implementations not found, skipping Docker setup"
    fi
    
    run_health_checks
    
    echo ""
    echo -e "${GREEN}🎉 Setup completed successfully!${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Review and update .env file with your configuration"
    echo "2. Run 'docker-compose up -d' to start all services"
    echo "3. Visit http://localhost:8001/docs for Amazon API documentation"
    echo "4. Visit http://localhost:8080 for database administration (dev profile)"
    echo ""
    echo "For development with pgAdmin:"
    echo "  docker-compose --profile dev up -d"
    echo ""
}

# Run main function
main "$@"