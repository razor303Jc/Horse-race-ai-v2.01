#!/bin/bash

# =============================================================================
# Horse Racing AI v2.05 - Optimized Service Builder
# =============================================================================
# Builds all services using service-specific .dockerignore files for
# optimal container sizes and enhanced security
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_VERSION="v2.05"
DOCKER_BUILDKIT=1

# Service configurations: service_name:dockerfile:tag_suffix
declare -a SERVICES=(
    "web-app:Dockerfile.web-optimized:web-app"
    "data-pipeline:Dockerfile.pipeline-optimized:pipeline"
    "ml-trainer:Dockerfile.ml-models:ml-trainer"
    "node-red:node-red/Dockerfile.enhanced:node-red"
    "docs:Dockerfile.mkdocs:docs"
    "production:Dockerfile.production:production"
    "alerts:Dockerfile.alerts:alerts"
)

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
    echo "           Horse Racing AI $PROJECT_VERSION - Optimized Service Builder"
    echo "============================================================================="
    echo "Building ${#SERVICES[@]} services with service-specific optimizations"
    echo "Build mode: Production-optimized with minimal dependencies"
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
    
    # Check Docker Buildkit
    export DOCKER_BUILDKIT=1
    
    # Check service directories
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service dockerfile tag <<< "$service_config"
        
        if [[ ! -f "docker/$service/.dockerignore" ]]; then
            log_error "Service-specific .dockerignore not found: docker/$service/.dockerignore"
            exit 1
        fi
        
        if [[ ! -f "docker/dockerfiles/$dockerfile" ]]; then
            log_error "Dockerfile not found: docker/dockerfiles/$dockerfile"
            exit 1
        fi
    done
    
    log_success "Prerequisites check passed"
}

backup_existing_dockerignore() {
    if [[ -f ".dockerignore" ]]; then
        log_info "Backing up existing .dockerignore"
        cp .dockerignore .dockerignore.backup
    fi
}

restore_dockerignore() {
    if [[ -f ".dockerignore.backup" ]]; then
        log_info "Restoring original .dockerignore"
        mv .dockerignore.backup .dockerignore
    elif [[ -f ".dockerignore" ]]; then
        rm .dockerignore
    fi
}

build_service() {
    local service=$1
    local dockerfile=$2
    local tag=$3
    
    log_info "Building service: $service"
    
    # Copy service-specific dockerignore
    log_info "Using optimized .dockerignore for $service"
    cp "docker/$service/.dockerignore" .dockerignore
    
    # Show dockerignore stats
    local excluded_count=$(wc -l < .dockerignore)
    log_info "Excluding $excluded_count patterns for $service"
    
    # Build the service
    local image_name="horse-racing-$tag:$PROJECT_VERSION"
    log_info "Building image: $image_name"
    
    if docker build -f "docker/dockerfiles/$dockerfile" -t "$image_name" .; then
        log_success "Built $service successfully"
        
        # Show image size
        local image_size=$(docker images "$image_name" --format "{{.Size}}")
        log_success "Image size: $image_size"
        
        return 0
    else
        log_error "Failed to build $service"
        return 1
    fi
}

build_all_services() {
    log_info "Starting service builds..."
    
    local failed_services=()
    local successful_services=()
    
    for service_config in "${SERVICES[@]}"; do
        IFS=':' read -r service dockerfile tag <<< "$service_config"
        
        echo
        log_info "========================================="
        log_info "Building: $service"
        log_info "Dockerfile: docker/dockerfiles/$dockerfile"
        log_info "Dockerignore: docker/$service/.dockerignore"
        log_info "========================================="
        
        if build_service "$service" "$dockerfile" "$tag"; then
            successful_services+=("$service")
        else
            failed_services+=("$service")
        fi
        
        # Cleanup dockerignore after each build
        rm -f .dockerignore
    done
    
    echo
    log_info "Build Summary:"
    log_success "Successful builds (${#successful_services[@]}): ${successful_services[*]}"
    
    if [[ ${#failed_services[@]} -gt 0 ]]; then
        log_error "Failed builds (${#failed_services[@]}): ${failed_services[*]}"
        return 1
    else
        log_success "All services built successfully!"
        return 0
    fi
}

show_image_sizes() {
    log_info "Final image sizes:"
    echo
    echo "Repository                    Tag      Size"
    echo "----------------------------------------------"
    docker images | grep "horse-racing-.*:$PROJECT_VERSION" | awk '{printf "%-25s %-8s %s\n", $1, $2, $7}'
    echo
    
    # Calculate total size (approximate)
    local total_size=$(docker images | grep "horse-racing-.*:$PROJECT_VERSION" | awk '{print $7}' | sed 's/MB//g' | awk '{sum += $1} END {print sum "MB"}')
    log_info "Approximate total size: $total_size"
}

cleanup_on_error() {
    log_error "Build failed, cleaning up..."
    restore_dockerignore
    exit 1
}

main() {
    print_header
    
    # Set error handling
    trap cleanup_on_error ERR
    
    # Execute build steps
    check_prerequisites
    backup_existing_dockerignore
    
    if build_all_services; then
        restore_dockerignore
        show_image_sizes
        
        log_success "Optimized Horse Racing AI $PROJECT_VERSION services build completed!"
        echo
        log_info "Next steps:"
        echo "  1. Deploy services: docker-compose -f docker-compose.clean.yml up -d"
        echo "  2. Check service health: docker-compose -f docker-compose.clean.yml ps"
        echo "  3. View logs: docker-compose -f docker-compose.clean.yml logs -f [service]"
        echo
        log_info "Service-specific benefits:"
        echo "  - Reduced attack surface (minimal file inclusion)"
        echo "  - Faster builds (smaller contexts)"
        echo "  - Better security (no sensitive files)"
        echo "  - Optimized for production deployment"
        
    else
        restore_dockerignore
        log_error "Some services failed to build. Check logs above."
        exit 1
    fi
}

# Handle script arguments
case "${1:-}" in
    --help|-h)
        echo "Usage: $0 [options]"
        echo
        echo "Options:"
        echo "  --help, -h     Show this help message"
        echo "  --list, -l     List available services"
        echo "  --single, -s   Build single service (interactive)"
        echo
        echo "This script builds all Horse Racing AI services with optimized"
        echo "service-specific .dockerignore files for minimal container sizes."
        exit 0
        ;;
    --list|-l)
        echo "Available services:"
        for service_config in "${SERVICES[@]}"; do
            IFS=':' read -r service dockerfile tag <<< "$service_config"
            echo "  - $service (docker/dockerfiles/$dockerfile)"
        done
        exit 0
        ;;
    --single|-s)
        echo "Available services:"
        for i in "${!SERVICES[@]}"; do
            IFS=':' read -r service dockerfile tag <<< "${SERVICES[$i]}"
            echo "  $((i+1)). $service"
        done
        echo
        read -p "Select service number (1-${#SERVICES[@]}): " selection
        
        if [[ "$selection" -ge 1 && "$selection" -le "${#SERVICES[@]}" ]]; then
            selected_service="${SERVICES[$((selection-1))]}"
            IFS=':' read -r service dockerfile tag <<< "$selected_service"
            
            print_header
            check_prerequisites
            backup_existing_dockerignore
            
            if build_service "$service" "$dockerfile" "$tag"; then
                restore_dockerignore
                show_image_sizes
                log_success "Service $service built successfully!"
            else
                restore_dockerignore
                log_error "Failed to build service $service"
                exit 1
            fi
        else
            log_error "Invalid selection"
            exit 1
        fi
        exit 0
        ;;
    "")
        # No arguments, run main build
        main "$@"
        ;;
    *)
        log_error "Unknown option: $1"
        echo "Use --help for usage information"
        exit 1
        ;;
esac
