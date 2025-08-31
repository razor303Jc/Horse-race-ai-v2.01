#!/bin/bash
# Enhanced Data Pipeline v2.05 - Integration Startup Script
# Version Tag: latest:v2.05
# Integrated File Watcher and Data Processor with Node-RED Pipeline
#
# This script integrates the Enhanced File Watcher v2.05 and Enhanced Data Processor v2.05
# into the Node-RED pipeline for complete automated data processing workflow.

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
DOCKER_COMPOSE_FILE="$PROJECT_ROOT/docker-compose.node-red.yml"
FLOWS_FILE="$PROJECT_ROOT/config/enhanced_data_pipeline_v2_05_flows.json"
NODE_RED_DATA_DIR="$PROJECT_ROOT/node_red_data"
VERSION="v2.05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function definitions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

success() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

check_prerequisites() {
    log "🔍 Checking prerequisites for v2.05 integration..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if required files exist
    local required_files=(
        "$PROJECT_ROOT/tools/file_monitoring/enhanced_file_watcher_v2_05.py"
        "$PROJECT_ROOT/tools/data_processing/enhanced_data_processor_v2_05.py"
        "$PROJECT_ROOT/tools/data_processing/manage_data_processor_v2_05.sh"
        "$PROJECT_ROOT/config/data_processor_config_v2_05.json"
        "$FLOWS_FILE"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            error "Required file not found: $file"
            exit 1
        fi
    done
    
    # Check Python requirements
    if ! python3 -c "import pandas, numpy, redis, psycopg2, watchdog" &> /dev/null; then
        warn "Some Python dependencies may be missing"
        info "Run: pip install pandas numpy redis psycopg2-binary watchdog"
    fi
    
    log "✅ Prerequisites check completed"
}

prepare_node_red_environment() {
    log "🏗️ Preparing Node-RED environment for v2.05 integration..."
    
    # Create Node-RED data directory if it doesn't exist
    mkdir -p "$NODE_RED_DATA_DIR"
    
    # Create necessary subdirectories
    mkdir -p "$NODE_RED_DATA_DIR/node_modules"
    mkdir -p "$NODE_RED_DATA_DIR/lib"
    mkdir -p "$NODE_RED_DATA_DIR/flows"
    
    # Set proper permissions
    chmod 755 "$NODE_RED_DATA_DIR"
    
    # Copy the enhanced flows to Node-RED data directory
    if [ -f "$FLOWS_FILE" ]; then
        cp "$FLOWS_FILE" "$NODE_RED_DATA_DIR/flows.json"
        log "✅ Enhanced v2.05 flows installed"
    else
        warn "Enhanced flows file not found, using default configuration"
    fi
    
    log "✅ Node-RED environment prepared"
}

start_supporting_services() {
    log "🚀 Starting supporting services..."
    
    # Start Redis and PostgreSQL if not running
    if ! docker ps | grep -q redis; then
        log "Starting Redis container..."
        cd "$PROJECT_ROOT"
        docker-compose -f docker-compose.clean.yml up -d redis
    fi
    
    if ! docker ps | grep -q postgres; then
        log "Starting PostgreSQL container..."
        cd "$PROJECT_ROOT"
        docker-compose -f docker-compose.clean.yml up -d postgres
    fi
    
    # Wait for services to be ready
    log "⏳ Waiting for services to be ready..."
    sleep 10
    
    # Check Redis connection
    if docker exec redis redis-cli ping | grep -q PONG; then
        success "✅ Redis is ready"
    else
        warn "Redis may not be fully ready"
    fi
    
    # Check PostgreSQL connection
    if docker exec postgres pg_isready -U horse_racing | grep -q "accepting connections"; then
        success "✅ PostgreSQL is ready"
    else
        warn "PostgreSQL may not be fully ready"
    fi
}

deploy_node_red_pipeline() {
    log "🚀 Deploying Node-RED pipeline with v2.05 integration..."
    
    cd "$PROJECT_ROOT"
    
    # Stop existing Node-RED if running
    if docker ps | grep -q horse_racing_node_red; then
        log "Stopping existing Node-RED container..."
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
    fi
    
    # Start Node-RED with enhanced configuration
    log "Starting Node-RED with v2.05 data pipeline..."
    docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
    
    # Wait for Node-RED to start
    log "⏳ Waiting for Node-RED to initialize..."
    sleep 15
    
    # Check if Node-RED is accessible
    local max_attempts=12
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:1881 > /dev/null; then
            success "✅ Node-RED is accessible at http://localhost:1881"
            break
        else
            info "Attempt $attempt/$max_attempts: Waiting for Node-RED..."
            sleep 5
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "Node-RED failed to start or is not accessible"
        return 1
    fi
}

install_node_red_dependencies() {
    log "📦 Installing Node-RED dependencies for v2.05..."
    
    # Required Node-RED modules for the enhanced pipeline
    local required_modules=(
        "node-red-contrib-redis"
        "node-red-node-postgres"
        "node-red-dashboard"
        "node-red-contrib-fs"
        "node-red-contrib-cron"
    )
    
    for module in "${required_modules[@]}"; do
        info "Installing $module..."
        docker exec horse_racing_node_red npm install "$module" || warn "Failed to install $module"
    done
    
    # Restart Node-RED to load new modules
    log "🔄 Restarting Node-RED to load new modules..."
    docker restart horse_racing_node_red
    sleep 10
}

initialize_redis_status() {
    log "🔧 Initializing Redis status for v2.05 components..."
    
    # Initialize watcher status
    docker exec redis redis-cli set "watcher:status" '{
        "status": "stopped",
        "last_check": "'$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)'",
        "files_found": 0,
        "files_processed": 0,
        "errors": 0,
        "version": "v2.05"
    }'
    
    # Initialize processor status
    docker exec redis redis-cli set "processor:status" '{
        "status": "ready",
        "last_run": null,
        "files_processed": 0,
        "errors": 0,
        "version": "v2.05"
    }'
    
    # Set status expiration (24 hours)
    docker exec redis redis-cli expire "watcher:status" 86400
    docker exec redis redis-cli expire "processor:status" 86400
    
    success "✅ Redis status initialized"
}

test_integration() {
    log "🧪 Testing v2.05 integration..."
    
    # Test file watcher script
    if python3 "$PROJECT_ROOT/tools/file_monitoring/enhanced_file_watcher_v2_05.py" --help > /dev/null 2>&1; then
        success "✅ File Watcher v2.05 is executable"
    else
        error "File Watcher v2.05 test failed"
        return 1
    fi
    
    # Test data processor script
    if python3 "$PROJECT_ROOT/tools/data_processing/enhanced_data_processor_v2_05.py" --help > /dev/null 2>&1; then
        success "✅ Data Processor v2.05 is executable"
    else
        error "Data Processor v2.05 test failed"
        return 1
    fi
    
    # Test management script
    if "$PROJECT_ROOT/tools/data_processing/manage_data_processor_v2_05.sh" help > /dev/null 2>&1; then
        success "✅ Management Script v2.05 is executable"
    else
        error "Management Script v2.05 test failed"
        return 1
    fi
    
    # Test Redis connection from containers
    if docker exec horse_racing_node_red sh -c "echo 'ping' | nc redis 6379" | grep -q PONG; then
        success "✅ Node-RED can connect to Redis"
    else
        warn "Node-RED Redis connection test failed"
    fi
    
    success "✅ Integration tests completed"
}

create_monitoring_dashboard() {
    log "📊 Creating monitoring dashboard URLs..."
    
    cat << EOF

🚀 Enhanced Data Pipeline v2.05 - Integration Complete!

📊 Access Points:
  🏠 Node-RED Editor:     http://localhost:1881
  📋 Dashboard:           http://localhost:1881/ui
  📈 Redis Status:        redis://localhost:6379
  🗄️  PostgreSQL:         postgresql://localhost:5432

🔧 Management Commands:
  File Watcher:    ./tools/file_monitoring/enhanced_file_watcher_v2_05.py
  Data Processor:  ./tools/data_processing/manage_data_processor_v2_05.sh
  System Status:   docker ps

📁 Key Directories:
  Data Input:      ./data/
  Logs:           ./logs/
  Processing:     ./logs/processing_reports/
  Node-RED Data:  ./node_red_data/

🏗️ Pipeline Flow:
  1. File Watcher monitors ./data/ directory
  2. New files added to Redis processing queue
  3. Node-RED triggers Data Processor
  4. Files processed with -0 NULL mapping
  5. Results uploaded to PostgreSQL database
  6. Status updates tracked in Redis
  7. Dashboard displays real-time status

📋 Next Steps:
  1. Visit http://localhost:1881 to configure flows
  2. Deploy flows to activate automation
  3. Add data files to ./data/ directory
  4. Monitor processing via dashboard

EOF
}

show_help() {
    echo
    echo -e "${PURPLE}Enhanced Data Pipeline v2.05 - Integration Script${NC}"
    echo
    echo "Usage: $0 [COMMAND]"
    echo
    echo -e "${CYAN}Commands:${NC}"
    echo "  deploy      Deploy complete v2.05 integration"
    echo "  start       Start Node-RED pipeline"
    echo "  stop        Stop Node-RED pipeline"  
    echo "  restart     Restart Node-RED pipeline"
    echo "  status      Check system status"
    echo "  test        Run integration tests"
    echo "  logs        Show Node-RED logs"
    echo "  help        Show this help message"
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 deploy   # Full deployment of v2.05 integration"
    echo "  $0 start    # Start the pipeline"
    echo "  $0 status   # Check system status"
    echo
}

# Main command handling
case "${1:-deploy}" in
    deploy)
        log "🚀 Starting Enhanced Data Pipeline v2.05 Integration Deployment"
        check_prerequisites
        prepare_node_red_environment
        start_supporting_services
        deploy_node_red_pipeline
        install_node_red_dependencies
        initialize_redis_status
        test_integration
        create_monitoring_dashboard
        success "🎉 Enhanced Data Pipeline v2.05 Integration Complete!"
        ;;
        
    start)
        log "🚀 Starting Node-RED pipeline..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        success "✅ Node-RED pipeline started"
        ;;
        
    stop)
        log "🛑 Stopping Node-RED pipeline..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        success "✅ Node-RED pipeline stopped"
        ;;
        
    restart)
        log "🔄 Restarting Node-RED pipeline..."
        cd "$PROJECT_ROOT"
        docker-compose -f "$DOCKER_COMPOSE_FILE" down
        sleep 5
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d
        success "✅ Node-RED pipeline restarted"
        ;;
        
    status)
        log "📊 Checking system status..."
        echo
        echo "🐳 Docker Containers:"
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        echo
        echo "🔍 v2.05 Components:"
        if [ -f "$PROJECT_ROOT/tools/file_monitoring/enhanced_file_watcher_v2_05.py" ]; then
            echo "  ✅ File Watcher v2.05 - Available"
        else
            echo "  ❌ File Watcher v2.05 - Missing"
        fi
        
        if [ -f "$PROJECT_ROOT/tools/data_processing/enhanced_data_processor_v2_05.py" ]; then
            echo "  ✅ Data Processor v2.05 - Available"
        else
            echo "  ❌ Data Processor v2.05 - Missing"
        fi
        
        echo
        echo "🌐 Service Endpoints:"
        echo "  Node-RED: http://localhost:1881"
        echo "  Dashboard: http://localhost:1881/ui"
        ;;
        
    test)
        log "🧪 Running integration tests..."
        test_integration
        ;;
        
    logs)
        log "📄 Showing Node-RED logs..."
        docker logs -f horse_racing_node_red
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
