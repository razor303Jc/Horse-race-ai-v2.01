#!/bin/bash
# Enhanced v2.05 Integration Startup Script
# Version Tag: latest:v2.05
# This script starts the integrated File Watcher and Data Processor system with Node-RED

set -e

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
DOCKER_COMPOSE_FILE="docker-compose.node-red.yml"
LOG_DIR="$PROJECT_ROOT/logs"
VERSION="v2.05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

print_header() {
    echo
    echo -e "${CYAN}============================================================${NC}"
    echo -e "${CYAN}🚀 Enhanced v2.05 Integration System Startup${NC}"
    echo -e "${CYAN}   File Watcher + Data Processor + Node-RED C2${NC}"
    echo -e "${CYAN}============================================================${NC}"
    echo
}

check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check if we're in the right directory
    if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
        error "Docker compose file not found: $DOCKER_COMPOSE_FILE"
        error "Please run this script from: $PROJECT_ROOT"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check required directories
    mkdir -p "$LOG_DIR"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/temp_extract"
    
    # Check v2.05 components
    local required_files=(
        "tools/file_monitoring/enhanced_file_watcher_v2_05.py"
        "tools/data_processing/enhanced_data_processor_v2_05.py"
        "tools/data_processing/manage_data_processor_v2_05.sh"
        "config/data_processor_config_v2_05.json"
    )
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            error "Required v2.05 component not found: $file"
            exit 1
        fi
    done
    
    success "✅ Prerequisites check completed"
}

start_base_services() {
    log "🐳 Starting base services (Redis, PostgreSQL)..."
    
    # Start base services first
    docker-compose -f docker-compose.clean.yml up -d redis postgres
    
    # Wait for services to be ready
    log "⏳ Waiting for Redis to be ready..."
    timeout 30 bash -c 'until docker exec horse_racing_redis_clean redis-cli ping; do sleep 1; done' || {
        error "Redis failed to start"
        exit 1
    }
    
    log "⏳ Waiting for PostgreSQL to be ready..."
    timeout 30 bash -c 'until docker exec horse_racing_postgres_clean pg_isready -U horse_racing; do sleep 1; done' || {
        error "PostgreSQL failed to start"
        exit 1
    }
    
    success "✅ Base services started successfully"
}

rebuild_node_red() {
    log "🔧 Rebuilding Node-RED container with v2.05 integration..."
    
    # Stop existing Node-RED if running
    docker-compose -f $DOCKER_COMPOSE_FILE down node-red 2>/dev/null || true
    
    # Remove existing image to force rebuild
    docker image rm horse-race-ai-v205_node-red 2>/dev/null || true
    
    # Build new image with updated dependencies
    docker-compose -f $DOCKER_COMPOSE_FILE build --no-cache node-red
    
    success "✅ Node-RED container rebuilt with v2.05 dependencies"
}

start_node_red() {
    log "🚀 Starting Node-RED with v2.05 integration..."
    
    # Start Node-RED
    docker-compose -f $DOCKER_COMPOSE_FILE up -d node-red
    
    # Wait for Node-RED to be ready
    log "⏳ Waiting for Node-RED to be ready..."
    local retries=30
    local count=0
    
    while [ $count -lt $retries ]; do
        if curl -f http://localhost:1881 >/dev/null 2>&1; then
            break
        fi
        sleep 2
        ((count++))
    done
    
    if [ $count -eq $retries ]; then
        error "Node-RED failed to start"
        exit 1
    fi
    
    success "✅ Node-RED started successfully on http://localhost:1881"
}

deploy_flows() {
    log "📋 Deploying v2.05 integration flows..."
    
    # The flows are already built into the container via flows.json
    # Node-RED will automatically load them on startup
    
    info "💡 Access the Node-RED dashboard at: http://localhost:1881"
    info "💡 v2.05 Integration tab should be available"
    info "💡 C2 Command Center available at: http://localhost:1881/c2"
    
    success "✅ v2.05 integration flows deployed"
}

start_file_watcher() {
    log "👁️ Starting Enhanced File Watcher v2.05..."
    
    # The file watcher will be started by Node-RED injection node
    # But we can also start it independently for backup
    
    info "💡 File watcher will be started automatically by Node-RED"
    info "💡 Manual start available via Node-RED 'Start File Watcher v2.05' button"
    
    success "✅ File watcher integration ready"
}

show_status() {
    log "📊 System Status Summary:"
    echo
    
    # Check Docker containers
    echo -e "${CYAN}🐳 Docker Containers:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(redis|postgres|node-red)"
    echo
    
    # Check Redis status
    echo -e "${CYAN}📡 Redis Status:${NC}"
    if docker exec horse_racing_redis_clean redis-cli ping >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Redis: Connected${NC}"
    else
        echo -e "  ${RED}❌ Redis: Not responding${NC}"
    fi
    
    # Check PostgreSQL status
    echo -e "${CYAN}🗄️ PostgreSQL Status:${NC}"
    if docker exec horse_racing_postgres_clean pg_isready -U horse_racing >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ PostgreSQL: Ready${NC}"
    else
        echo -e "  ${RED}❌ PostgreSQL: Not ready${NC}"
    fi
    
    # Check Node-RED status
    echo -e "${CYAN}🔴 Node-RED Status:${NC}"
    if curl -f http://localhost:1881 >/dev/null 2>&1; then
        echo -e "  ${GREEN}✅ Node-RED: Available at http://localhost:1881${NC}"
    else
        echo -e "  ${RED}❌ Node-RED: Not responding${NC}"
    fi
    
    echo
    echo -e "${CYAN}📋 Next Steps:${NC}"
    echo "1. Open Node-RED dashboard: http://localhost:1881"
    echo "2. Navigate to '🚀 v2.05 Integration' tab"
    echo "3. Click 'Start File Watcher v2.05' to begin monitoring"
    echo "4. Use 'Manual Process Test' to test data processing"
    echo "5. Monitor status via 'Check Status' every 60 seconds"
    echo
}

cleanup_on_error() {
    error "❌ Startup failed. Cleaning up..."
    docker-compose -f $DOCKER_COMPOSE_FILE down 2>/dev/null || true
    exit 1
}

# Main execution
trap cleanup_on_error ERR

print_header

# Change to project directory
cd "$PROJECT_ROOT"

# Execute startup sequence
check_prerequisites
start_base_services
rebuild_node_red
start_node_red
deploy_flows
start_file_watcher

# Show final status
show_status

success "🎉 Enhanced v2.05 Integration System started successfully!"
success "🚀 System ready for automated file processing with Node-RED C2 control"

echo
echo -e "${YELLOW}📝 Important Notes:${NC}"
echo "- File Watcher v2.05: Monitors data/ directory for new ZIP files"
echo "- Data Processor v2.05: Processes files with -0 NULL mapping"
echo "- Node-RED C2: Provides centralized control and monitoring"
echo "- Redis Integration: Status tracking and caching"
echo "- PostgreSQL: Database storage for processed data"
echo
echo -e "${GREEN}✅ All systems operational - v2.05 integration complete!${NC}"
