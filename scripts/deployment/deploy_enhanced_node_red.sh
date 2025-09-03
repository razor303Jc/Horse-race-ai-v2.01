#!/bin/bash

# 🏇 Horse Racing AI v2.05 - Enhanced Node-RED Deployment Script
# ==============================================================
# Builds and deploys Node-RED container with automatic flow building

set -e

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
DOCKER_COMPOSE_FILE="docker-compose.node-red-enhanced.yml"
CONTAINER_NAME="horse_racing_node_red_enhanced_v205"
IMAGE_NAME="horse-race-ai-v205-node-red-enhanced"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# Logging functions
log_info() {
    echo -e "${BLUE}[DEPLOY]${NC} $1"
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

log_header() {
    echo -e "${PURPLE}[ENHANCED-NODE-RED]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_header "Checking prerequisites..."
    
    # Check if docker is running
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running"
        exit 1
    fi
    log_success "Docker is running"
    
    # Check if docker-compose is available
    if ! command -v docker-compose > /dev/null 2>&1; then
        log_error "docker-compose is not available"
        exit 1
    fi
    log_success "docker-compose is available"
    
    # Check if flows directory exists
    if [ ! -d "$PROJECT_ROOT/flows" ]; then
        log_error "Flows directory not found: $PROJECT_ROOT/flows"
        exit 1
    fi
    log_success "Flows directory found with $(find "$PROJECT_ROOT/flows" -name "*.json" | wc -l) flow files"
    
    # Check if network exists
    if ! docker network ls | grep -q horse_racing_network; then
        log_warning "Creating horse_racing_network..."
        docker network create horse_racing_network
        log_success "Network created"
    else
        log_success "horse_racing_network exists"
    fi
}

# Stop existing container
stop_existing_container() {
    log_info "Stopping existing Node-RED containers..."
    
    # Stop enhanced container if running
    if docker ps -q -f name=$CONTAINER_NAME | grep -q .; then
        log_info "Stopping $CONTAINER_NAME..."
        docker stop $CONTAINER_NAME
        docker rm $CONTAINER_NAME
        log_success "Stopped enhanced container"
    fi
    
    # Stop any other Node-RED containers
    local other_containers=$(docker ps -q -f name=horse_racing_node_red)
    if [ -n "$other_containers" ]; then
        log_info "Stopping other Node-RED containers..."
        echo "$other_containers" | xargs docker stop
        echo "$other_containers" | xargs docker rm
        log_success "Stopped other Node-RED containers"
    fi
}

# Prepare build context
prepare_build_context() {
    log_info "Preparing build context..."
    
    # Create data directories
    mkdir -p "$PROJECT_ROOT/data/node-red"
    mkdir -p "$PROJECT_ROOT/logs/node-red"
    
    # Ensure proper permissions
    sudo chown -R 1000:1000 "$PROJECT_ROOT/data/node-red" "$PROJECT_ROOT/logs/node-red"
    
    # Copy build script to docker context
    cp "$PROJECT_ROOT/build_final_flows_v2_05.sh" "$PROJECT_ROOT/docker/node-red/"
    
    log_success "Build context prepared"
}

# Build enhanced Node-RED image
build_enhanced_image() {
    log_header "Building enhanced Node-RED image..."
    
    cd "$PROJECT_ROOT"
    
    # Build the enhanced image
    docker-compose -f "$DOCKER_COMPOSE_FILE" build --no-cache
    
    if [ $? -eq 0 ]; then
        log_success "Enhanced Node-RED image built successfully"
    else
        log_error "Failed to build enhanced Node-RED image"
        exit 1
    fi
}

# Deploy enhanced container
deploy_enhanced_container() {
    log_header "Deploying enhanced Node-RED container..."
    
    cd "$PROJECT_ROOT"
    
    # Start the enhanced container
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    if [ $? -eq 0 ]; then
        log_success "Enhanced Node-RED container deployed"
    else
        log_error "Failed to deploy enhanced Node-RED container"
        exit 1
    fi
}

# Monitor deployment
monitor_deployment() {
    log_info "Monitoring deployment progress..."
    
    # Wait for container to be running
    local max_wait=120
    local wait_time=0
    
    while [ $wait_time -lt $max_wait ]; do
        if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -q "$CONTAINER_NAME.*Up"; then
            log_success "Container is running"
            break
        fi
        
        log_info "Waiting for container to start... ($wait_time/${max_wait}s)"
        sleep 5
        wait_time=$((wait_time + 5))
    done
    
    if [ $wait_time -ge $max_wait ]; then
        log_error "Container failed to start within timeout"
        docker logs "$CONTAINER_NAME" --tail 20
        exit 1
    fi
    
    # Monitor container logs for build completion
    log_info "Monitoring flow build process..."
    
    # Follow logs for build indicators
    timeout 300 docker logs -f "$CONTAINER_NAME" &
    LOGS_PID=$!
    
    # Wait for flow build completion or timeout
    local build_wait=0
    local max_build_wait=300
    
    while [ $build_wait -lt $max_build_wait ]; do
        if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "Flow build process completed"; then
            log_success "Flow build completed successfully"
            kill $LOGS_PID 2>/dev/null || true
            break
        fi
        
        if docker logs "$CONTAINER_NAME" 2>&1 | grep -q "Using default Node-RED flows"; then
            log_warning "Using default flows - no source flows processed"
            kill $LOGS_PID 2>/dev/null || true
            break
        fi
        
        sleep 5
        build_wait=$((build_wait + 5))
    done
    
    if [ $build_wait -ge $max_build_wait ]; then
        log_warning "Build monitoring timed out - check container logs manually"
        kill $LOGS_PID 2>/dev/null || true
    fi
}

# Verify deployment
verify_deployment() {
    log_header "Verifying deployment..."
    
    # Wait a moment for services to be ready
    sleep 10
    
    # Test container health
    if docker ps --format "table {{.Names}}\t{{.Status}}" | grep "$CONTAINER_NAME" | grep -q "healthy"; then
        log_success "Container health check passed"
    else
        log_warning "Container health check not yet passing"
    fi
    
    # Test Node-RED accessibility
    local max_attempts=20
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:1880 > /dev/null; then
            log_success "Node-RED is accessible at http://localhost:1880"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_error "Node-RED is not accessible after $max_attempts attempts"
            return 1
        fi
        
        log_info "Attempt $attempt/$max_attempts - waiting for Node-RED..."
        sleep 3
        ((attempt++))
    done
    
    # Test dashboard endpoints
    if curl -s http://localhost:1880/c2 > /dev/null; then
        log_success "Main dashboard is accessible at http://localhost:1880/c2"
    else
        log_warning "Main dashboard not yet accessible"
    fi
    
    if curl -s http://localhost:1880/c2/status > /dev/null; then
        log_success "Status API is accessible at http://localhost:1880/c2/status"
    else
        log_warning "Status API not yet accessible"
    fi
}

# Show deployment summary
show_deployment_summary() {
    log_header "🎉 Enhanced Node-RED Deployment Complete!"
    
    echo ""
    echo "📊 Container Information:"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "$CONTAINER_NAME"
    
    echo ""
    echo "🌐 Access Points:"
    echo "   • Main Dashboard: http://localhost:1880/c2"
    echo "   • Advanced Metrics: http://localhost:1880/c2/metrics"
    echo "   • Node-RED Editor: http://localhost:1880"
    echo "   • Status API: http://localhost:1880/c2/status"
    
    echo ""
    echo "🔧 Management Commands:"
    echo "   • View logs: docker logs $CONTAINER_NAME"
    echo "   • Enter container: docker exec -it $CONTAINER_NAME /bin/bash"
    echo "   • Restart: docker restart $CONTAINER_NAME"
    echo "   • Stop: docker stop $CONTAINER_NAME"
    
    echo ""
    echo "📁 Data Directories:"
    echo "   • Node-RED data: $PROJECT_ROOT/data/node-red"
    echo "   • Flow builds: $PROJECT_ROOT/data/node-red/flows-build"
    echo "   • Logs: $PROJECT_ROOT/logs/node-red"
    
    echo ""
    echo "🚀 Next Steps:"
    echo "   1. Verify dashboard functionality"
    echo "   2. Test advanced metrics calculation"
    echo "   3. Review container logs for any issues"
    echo "   4. Configure automation as needed"
    
    echo ""
    log_success "🏇 Horse Racing AI v2.05 Enhanced Node-RED is ready!"
}

# Main deployment process
main() {
    log_header "🏇 Horse Racing AI v2.05 - Enhanced Node-RED Deployment Starting..."
    
    cd "$PROJECT_ROOT"
    
    check_prerequisites
    stop_existing_container
    prepare_build_context
    build_enhanced_image
    deploy_enhanced_container
    monitor_deployment
    verify_deployment
    show_deployment_summary
    
    echo ""
    log_success "Deployment completed successfully!"
}

# Execute main function
main "$@"
