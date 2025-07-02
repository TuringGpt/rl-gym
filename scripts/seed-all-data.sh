#!/bin/bash

# Seed All Data Script
# Seeds mock data into all service databases

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Docker services are running
check_services() {
    print_status "Checking if services are running..."
    
    if ! docker-compose ps | grep -q "amazon-db.*Up"; then
        print_error "Amazon database service is not running. Start it with: docker-compose up -d amazon-db"
        exit 1
    fi
    
    if ! docker-compose ps | grep -q "redis.*Up"; then
        print_warning "Redis service is not running. Some features may not work properly."
    fi
    
    print_success "Required services are running"
}

# Wait for database to be ready
wait_for_database() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    
    print_status "Waiting for $service_name database to be ready..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose exec -T $service_name pg_isready -U amazon_user -d amazon_sp_db 2>/dev/null; then
            print_success "$service_name database is ready"
            return 0
        fi
        
        print_status "Attempt $attempt/$max_attempts: Database not ready, waiting..."
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name database failed to become ready after $max_attempts attempts"
    exit 1
}

# Seed Amazon database
seed_amazon_database() {
    print_status "Seeding Amazon Selling Partner API database..."
    
    # Check if feed_data.sql exists
    if [ ! -f "services/amazon/feed_data.sql" ]; then
        print_error "Amazon feed_data.sql not found. Please create it first."
        return 1
    fi
    
    # Execute the SQL file
    if docker-compose exec -T amazon-db psql -U amazon_user -d amazon_sp_db -f /docker-entrypoint-initdb.d/01-feed_data.sql; then
        print_success "Amazon database seeded successfully"
    else
        print_warning "Amazon database seeding may have failed or was already completed"
    fi
    
    # Verify data was inserted
    local count=$(docker-compose exec -T amazon-db psql -U amazon_user -d amazon_sp_db -t -c "SELECT COUNT(*) FROM sellers;" 2>/dev/null | tr -d ' \n' || echo "0")
    if [ "$count" -gt "0" ]; then
        print_success "Verified: $count sellers found in database"
    else
        print_warning "No sellers found in database - seeding may have failed"
    fi
}

# Generate additional mock data using Python
generate_additional_data() {
    print_status "Generating additional mock data..."
    
    # Check if the Amazon service is running
    if docker-compose ps | grep -q "amazon-api.*Up"; then
        print_status "Amazon API service is running, generating data via API..."
        
        # Try to generate data via API endpoint
        if curl -s -X POST "http://localhost:8001/admin/generate-mock-data" \
           -H "Content-Type: application/json" \
           -d '{"orders": 100, "products": 50, "inventory_items": 200}' > /dev/null 2>&1; then
            print_success "Additional mock data generated via API"
        else
            print_warning "Could not generate additional data via API - service may not be fully ready"
        fi
    else
        print_warning "Amazon API service is not running, skipping additional data generation"
    fi
}

# Backup seed data
backup_seed_data() {
    print_status "Creating backup of seed data..."
    
    local backup_dir="data/backups"
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    
    mkdir -p "$backup_dir"
    
    # Backup Amazon database
    if docker-compose exec -T amazon-db pg_dump -U amazon_user amazon_sp_db > "$backup_dir/amazon_sp_db_$timestamp.sql"; then
        print_success "Amazon database backed up to $backup_dir/amazon_sp_db_$timestamp.sql"
    else
        print_warning "Failed to backup Amazon database"
    fi
}

# Display seeding summary
show_summary() {
    print_status "Seeding Summary:"
    echo ""
    
    # Amazon database stats
    echo "Amazon Selling Partner API Database:"
    local sellers_count=$(docker-compose exec -T amazon-db psql -U amazon_user -d amazon_sp_db -t -c "SELECT COUNT(*) FROM sellers;" 2>/dev/null | tr -d ' \n' || echo "0")
    local orders_count=$(docker-compose exec -T amazon-db psql -U amazon_user -d amazon_sp_db -t -c "SELECT COUNT(*) FROM orders;" 2>/dev/null | tr -d ' \n' || echo "0")
    local inventory_count=$(docker-compose exec -T amazon-db psql -U amazon_user -d amazon_sp_db -t -c "SELECT COUNT(*) FROM inventory;" 2>/dev/null | tr -d ' \n' || echo "0")
    
    echo "  - Sellers: $sellers_count"
    echo "  - Orders: $orders_count"
    echo "  - Inventory Items: $inventory_count"
    echo ""
    
    print_success "Database seeding completed!"
    echo ""
    echo "You can now:"
    echo "1. Start the API services: docker-compose up -d"
    echo "2. Access Amazon API docs: http://localhost:8001/docs"
    echo "3. View database: http://localhost:8080 (pgAdmin)"
    echo ""
}

# Clean existing data (optional)
clean_data() {
    if [ "$1" = "--clean" ]; then
        print_warning "Cleaning existing data..."
        
        # Stop services
        docker-compose down
        
        # Remove volumes
        docker volume rm api-mock-gym_amazon_db_data 2>/dev/null || true
        docker volume rm api-mock-gym_redis_data 2>/dev/null || true
        
        print_success "Existing data cleaned"
        
        # Restart services
        docker-compose up -d amazon-db redis
        sleep 10
    fi
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "╔═══════════════════════════════════════════════════════════════════╗"
    echo "║                        Data Seeding Process                      ║"
    echo "║              Populating databases with mock data                 ║"
    echo "╚═══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    # Handle clean flag
    clean_data "$@"
    
    check_services
    wait_for_database "amazon-db"
    seed_amazon_database
    generate_additional_data
    backup_seed_data
    show_summary
}

# Show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --clean    Clean existing data before seeding"
    echo "  --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Seed data normally"
    echo "  $0 --clean        # Clean and reseed all data"
    echo ""
}

# Handle command line arguments
case "${1:-}" in
    --help|-h)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac