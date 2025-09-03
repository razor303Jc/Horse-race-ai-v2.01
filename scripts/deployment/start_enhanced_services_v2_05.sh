#!/bin/bash

# =============================================================================
# Enhanced Horse Racing AI v2.05 Services Deployment
# =============================================================================
# This script deploys the complete Horse Racing AI system with:
# - Core services (postgres, redis, web-app, data-pipeline, ml-trainer)
# - Enhanced Node-RED with v2.05 flow automation
# - Documentation service (mkdocs)
# - Notification service (ntfy)
# - Admin interface (pgadmin)
#
# Author: Horse Racing AI Team
# Version: v2.05
# Created: $(date +"%Y-%m-%d %H:%M:%S")
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.clean.yml"
PROJECT_NAME="horse-racing-ai-v205"
DOCKER_BUILDKIT=1

# Services to deploy
CORE_SERVICES=(
    "postgres"
    "redis" 
    "web-app"
    "data-pipeline"
    "ml-trainer"
)

ENHANCED_SERVICES=(
    "node-red"
    "docs"
    "ntfy"
    "pgadmin"
)

ALL_SERVICES=("${CORE_SERVICES[@]}" "${ENHANCED_SERVICES[@]}")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_header() {
    echo "============================================================================="
    echo "               Horse Racing AI v2.05 Enhanced Deployment"
    echo "============================================================================="
    echo "Deploying services: ${ALL_SERVICES[*]}"
    echo "Compose file: $COMPOSE_FILE"
    echo "Project name: $PROJECT_NAME"
    echo "============================================================================="
    echo
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed or not in PATH"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed or not in PATH"
        exit 1
    fi
    
    # Check compose file exists
    if [[ ! -f "$COMPOSE_FILE" ]]; then
        log_error "Compose file $COMPOSE_FILE not found"
        exit 1
    fi
    
    # Validate compose file
    log_info "Validating compose file..."
    if ! docker-compose -f "$COMPOSE_FILE" config --quiet; then
        log_error "Compose file validation failed"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

check_enhanced_dockerfile() {
    log_info "Checking enhanced Node-RED Dockerfile..."
    
    if [[ ! -f "docker/node-red/Dockerfile.enhanced" ]]; then
        log_warning "Enhanced Node-RED Dockerfile not found"
        log_info "Creating basic enhanced Dockerfile..."
        
        mkdir -p docker/node-red
        cat > docker/node-red/Dockerfile.enhanced << 'EOF'
FROM nodered/node-red:latest

# Install additional Node.js packages for JSON processing
USER root
RUN apk add --no-cache python3 py3-pip nodejs npm

# Install Node.js packages globally
RUN npm install -g @json-tools/cli

# Copy enhanced entrypoint script
COPY docker/node-red/entrypoint-enhanced.sh /usr/local/bin/entrypoint-enhanced.sh
RUN chmod +x /usr/local/bin/entrypoint-enhanced.sh

# Copy flow sources
COPY flows/ /app/flow_sources/

USER node-red

# Use enhanced entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint-enhanced.sh"]
EOF
        log_success "Created basic enhanced Dockerfile"
    else
        log_success "Enhanced Node-RED Dockerfile found"
    fi
}

check_enhanced_entrypoint() {
    log_info "Checking enhanced Node-RED entrypoint..."
    
    if [[ ! -f "docker/node-red/entrypoint-enhanced.sh" ]]; then
        log_warning "Enhanced Node-RED entrypoint not found"
        log_info "Creating basic enhanced entrypoint..."
        
        mkdir -p docker/node-red
        cat > docker/node-red/entrypoint-enhanced.sh << 'EOF'
#!/bin/bash
set -euo pipefail

echo "[INFO] Starting enhanced Node-RED v2.05..."

# Check if flow sources exist
if [[ -d "/app/flow_sources" ]]; then
    echo "[INFO] Flow sources found, building flows..."
    
    # Simple flow copy for basic setup
    if [[ -f "/app/flow_sources/active/main_flow.json" ]]; then
        echo "[INFO] Copying main flow..."
        cp /app/flow_sources/active/main_flow.json /data/flows.json
    fi
fi

echo "[INFO] Starting Node-RED..."
exec node-red
EOF
        chmod +x docker/node-red/entrypoint-enhanced.sh
        log_success "Created basic enhanced entrypoint"
    else
        log_success "Enhanced Node-RED entrypoint found"
    fi
}

prepare_environment() {
    log_info "Preparing environment..."
    
    # Set Docker Buildkit
    export DOCKER_BUILDKIT=1
    
    # Create .env file if it doesn't exist
    if [[ ! -f ".env" ]]; then
        log_info "Creating .env file from example..."
        if [[ -f "example.env" ]]; then
            cp example.env .env
            log_success "Created .env from example.env"
        else
            log_warning "No example.env found, using defaults"
            cat > .env << 'EOF'
# Basic configuration
POSTGRES_PASSWORD=secure_password_123
REDIS_PASSWORD=redis_password_123
PGADMIN_PASSWORD=admin_password_123
USER_NAME=jc
USER_ID=1000
GROUP_ID=1000
EOF
        fi
    fi
    
    # Check Docker files
    check_enhanced_dockerfile
    check_enhanced_entrypoint
    
    log_success "Environment preparation completed"
}

build_services() {
    log_info "Building required services..."
    
    # Build services that need building
    for service in "${ALL_SERVICES[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" config | grep -A 10 "^  $service:" | grep -q "build:"; then
            log_info "Building service: $service"
            if ! docker-compose -f "$COMPOSE_FILE" build "$service"; then
                log_error "Failed to build service: $service"
                return 1
            fi
        fi
    done
    
    log_success "Service building completed"
}

start_core_services() {
    log_info "Starting core services first..."
    
    # Start core services in dependency order
    docker-compose -f "$COMPOSE_FILE" up -d "${CORE_SERVICES[@]}"
    
    # Wait for core services to be healthy
    log_info "Waiting for core services to be ready..."
    sleep 30
    
    log_success "Core services started"
}

start_enhanced_services() {
    log_info "Starting enhanced services..."
    
    # Start enhanced services
    docker-compose -f "$COMPOSE_FILE" up -d "${ENHANCED_SERVICES[@]}"
    
    log_success "Enhanced services started"
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check service status
    for service in "${ALL_SERVICES[@]}"; do
        if docker-compose -f "$COMPOSE_FILE" ps "$service" | grep -q "Up"; then
            log_success "Service $service is running"
        else
            log_warning "Service $service is not running properly"
        fi
    done
    
    # Show service URLs
    echo
    log_info "Service URLs:"
    echo "  - Web App: http://localhost:5000"
    echo "  - Node-RED: http://localhost:1880"
    echo "  - Documentation: http://localhost:8000 (if docs service is running)"
    echo "  - Notifications: http://localhost:8082"
    echo "  - PgAdmin: http://localhost:8083"
    echo
    
    # Show Traefik URLs (if available)
    if docker network ls | grep -q traefik-dev; then
        log_info "Traefik URLs (if Traefik is running):"
        echo "  - Web App: http://horserace.local"
        echo "  - Node-RED: http://node-red.horserace.local"
        echo "  - Documentation: http://horserace-docs.local"
        echo "  - Notifications: http://ntfy.horserace.local"
        echo "  - PgAdmin: http://pgadmin.horserace.local"
    fi
}

show_logs() {
    log_info "Recent logs from enhanced services:"
    echo
    for service in "${ENHANCED_SERVICES[@]}"; do
        echo "--- $service logs ---"
        docker-compose -f "$COMPOSE_FILE" logs --tail=5 "$service" || true
        echo
    done
}

cleanup_on_error() {
    log_error "Deployment failed, cleaning up..."
    docker-compose -f "$COMPOSE_FILE" down
    exit 1
}

# Main execution
main() {
    print_header
    
    # Set error handling
    trap cleanup_on_error ERR
    
    # Execute deployment steps
    check_prerequisites
    prepare_environment
    build_services
    start_core_services
    start_enhanced_services
    verify_deployment
    
    log_success "Enhanced Horse Racing AI v2.05 deployment completed successfully!"
    echo
    log_info "Use the following commands for management:"
    echo "  - View logs: docker-compose -f $COMPOSE_FILE logs -f [service_name]"
    echo "  - Stop services: docker-compose -f $COMPOSE_FILE down"
    echo "  - Restart service: docker-compose -f $COMPOSE_FILE restart [service_name]"
    echo
    
    # Option to show logs
    read -p "Show recent logs from enhanced services? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        show_logs
    fi
}

# Execute main function
main "$@"
