#!/bin/bash

# Generate Environment Files Script
# Creates .env files for each service based on templates and global configuration

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

# Load main environment variables
load_main_env() {
    if [ -f .env ]; then
        source .env
        print_status "Loaded main environment configuration"
    else
        print_error "Main .env file not found. Run setup.sh first."
        exit 1
    fi
}

# Generate Amazon service .env file
generate_amazon_env() {
    print_status "Generating Amazon service environment file..."
    
    local amazon_env_file="services/amazon/.env"
    local amazon_template="services/amazon/.env.template"
    
    # Create template if it doesn't exist
    if [ ! -f "$amazon_template" ]; then
        cat > "$amazon_template" << 'EOF'
# Amazon Selling Partner API Mock Service Configuration

# Database Configuration
DATABASE_URL=postgresql://amazon_user:${AMAZON_DB_PASSWORD}@amazon-db:5432/amazon_sp_db
AMAZON_SERVICE_PORT=8001

# Redis Configuration
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# Authentication Configuration
LWA_CLIENT_ID=${LWA_CLIENT_ID}
LWA_CLIENT_SECRET=${LWA_CLIENT_SECRET}
JWT_SECRET_KEY=${JWT_SECRET_KEY}
JWT_ALGORITHM=${JWT_ALGORITHM:-HS256}
JWT_EXPIRATION_HOURS=${JWT_EXPIRATION_HOURS:-24}

# Rate Limiting Configuration
RATE_LIMIT_REQUESTS=${RATE_LIMIT_REQUESTS:-100}
RATE_LIMIT_WINDOW=${RATE_LIMIT_WINDOW:-60}

# Application Configuration
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-development}
DEBUG=${DEBUG:-true}

# Mock Data Configuration
MOCK_DATA_SEED=${MOCK_DATA_SEED:-42}
SELLERS_COUNT=${SELLERS_COUNT:-10}
ORDERS_COUNT=${ORDERS_COUNT:-1000}
PRODUCTS_COUNT=${PRODUCTS_COUNT:-500}

# API Behavior Configuration
SIMULATE_RATE_LIMITS=${SIMULATE_RATE_LIMITS:-true}
SIMULATE_AUTH_FAILURES=${SIMULATE_AUTH_FAILURES:-false}
RESPONSE_DELAY_MS=${RESPONSE_DELAY_MS:-0}
EOF
        print_success "Created Amazon service .env template"
    fi
    
    # Generate the actual .env file with variable substitution
    envsubst < "$amazon_template" > "$amazon_env_file"
    
    # Set default values for any missing variables
    cat >> "$amazon_env_file" << EOF

# Generated on $(date)
# Service-specific defaults
AMAZON_DB_HOST=amazon-db
AMAZON_DB_PORT=5432
AMAZON_DB_NAME=amazon_sp_db
AMAZON_DB_USER=amazon_user
EOF
    
    print_success "Generated Amazon service .env file"
}

# Generate future service env files (templates for now)
generate_future_service_envs() {
    local services=("slack" "stripe" "notion" "github")
    
    for service in "${services[@]}"; do
        local service_dir="services/$service"
        local service_env_template="$service_dir/.env.template"
        
        if [ ! -d "$service_dir" ]; then
            continue
        fi
        
        print_status "Generating $service service environment template..."
        
        mkdir -p "$service_dir"
        
        # Create template based on service type
        case $service in
            "slack")
                cat > "$service_env_template" << 'EOF'
# Slack API Mock Service Configuration
DATABASE_URL=postgresql://slack_user:${SLACK_DB_PASSWORD}@slack-db:5432/slack_db
SLACK_SERVICE_PORT=8002
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/1
SLACK_BOT_TOKEN=${SLACK_BOT_TOKEN}
SLACK_SIGNING_SECRET=${SLACK_SIGNING_SECRET}
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-development}
EOF
                ;;
            "stripe")
                cat > "$service_env_template" << 'EOF'
# Stripe API Mock Service Configuration
DATABASE_URL=postgresql://stripe_user:${STRIPE_DB_PASSWORD}@stripe-db:5432/stripe_db
STRIPE_SERVICE_PORT=8003
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/2
STRIPE_API_KEY=${STRIPE_API_KEY}
STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-development}
EOF
                ;;
            "notion")
                cat > "$service_env_template" << 'EOF'
# Notion API Mock Service Configuration
DATABASE_URL=postgresql://notion_user:${NOTION_DB_PASSWORD}@notion-db:5432/notion_db
NOTION_SERVICE_PORT=8004
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/3
NOTION_API_KEY=${NOTION_API_KEY}
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-development}
EOF
                ;;
            "github")
                cat > "$service_env_template" << 'EOF'
# GitHub API Mock Service Configuration
DATABASE_URL=postgresql://github_user:${GITHUB_DB_PASSWORD}@github-db:5432/github_db
GITHUB_SERVICE_PORT=8005
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/4
GITHUB_TOKEN=${GITHUB_TOKEN}
GITHUB_WEBHOOK_SECRET=${GITHUB_WEBHOOK_SECRET}
LOG_LEVEL=${LOG_LEVEL:-INFO}
ENVIRONMENT=${ENVIRONMENT:-development}
EOF
                ;;
        esac
        
        print_success "Created $service service .env template"
    done
}

# Validate environment files
validate_env_files() {
    print_status "Validating environment files..."
    
    local required_vars=(
        "AMAZON_DB_PASSWORD"
        "REDIS_PASSWORD"
        "LWA_CLIENT_ID"
        "LWA_CLIENT_SECRET"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            print_error "Required environment variable $var is not set"
            exit 1
        fi
    done
    
    print_success "Environment validation passed"
}

# Main function
main() {
    echo -e "${GREEN}"
    echo "╔══════════════════════════════════════════════════════════════════╗"
    echo "║                  Environment Files Generation                   ║"
    echo "║         Creating service-specific configuration files           ║"
    echo "╚══════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    
    load_main_env
    validate_env_files
    
    # Ensure services directory exists
    mkdir -p services/amazon
    
    generate_amazon_env
    generate_future_service_envs
    
    echo ""
    echo -e "${GREEN}✅ Environment files generated successfully!${NC}"
    echo ""
    echo "Generated files:"
    echo "  - services/amazon/.env"
    echo "  - services/{future-services}/.env.template"
    echo ""
    echo "You can now start the services with:"
    echo "  docker-compose up -d"
    echo ""
}

# Run main function
main "$@"