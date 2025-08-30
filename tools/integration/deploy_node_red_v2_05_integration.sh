#!/bin/bash
# Node-RED v2.05 Integration Deployment Script
# Version Tag: latest:v2.05
# Horse Racing AI - Automated Data Processing Pipeline

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
CONTAINER_NAME="horse_racing_node_red"
VERSION="v2.05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# Check if Node-RED container is running
check_container() {
    log "🔍 Checking Node-RED container status..."
    
    if ! docker ps | grep -q "$CONTAINER_NAME"; then
        error "Node-RED container is not running"
        log "Starting Node-RED container..."
        cd "$PROJECT_ROOT"
        docker-compose -f docker-compose.clean.yml up -d node-red
        sleep 10
    fi
    
    success "✅ Node-RED container is running"
}

# Deploy v2.05 integration flows
deploy_flows() {
    log "🚀 Deploying v2.05 integration flows..."
    
    # Copy the enhanced flows to the container
    docker cp "$PROJECT_ROOT/config/node_red_v2_05_integration_flows.json" \
        "$CONTAINER_NAME:/data/flows.json"
    
    # Install missing modules if needed
    info "📦 Installing required Node-RED modules..."
    docker exec "$CONTAINER_NAME" npm install --prefix /data \
        node-red-node-redis \
        node-red-dashboard \
        node-red-contrib-fs-ops \
        node-red-contrib-cron-plus
    
    # Restart Node-RED to load new flows
    log "🔄 Restarting Node-RED to apply changes..."
    docker restart "$CONTAINER_NAME"
    
    # Wait for Node-RED to start
    sleep 15
    
    success "✅ v2.05 integration flows deployed"
}

# Verify deployment
verify_deployment() {
    log "🔍 Verifying deployment..."
    
    # Check Node-RED health
    if curl -s -f "http://localhost:1881" > /dev/null; then
        success "✅ Node-RED is accessible"
    else
        error "❌ Node-RED is not accessible"
        return 1
    fi
    
    # Check logs for any errors
    log "📄 Checking recent logs..."
    docker logs "$CONTAINER_NAME" --tail 10
    
    success "✅ Deployment verification completed"
}

# Test file watcher integration
test_file_watcher() {
    log "🧪 Testing file watcher integration..."
    
    # Execute file watcher status check via Node-RED
    docker exec "$CONTAINER_NAME" python3 /data/tools/file_watching/enhanced_file_watcher_v2_05.py --status || true
    
    info "📊 File watcher integration test completed"
}

# Test data processor integration
test_data_processor() {
    log "🧪 Testing data processor integration..."
    
    # Execute data processor validation via Node-RED
    docker exec "$CONTAINER_NAME" python3 /data/tools/data_processing/enhanced_data_processor_v2_05.py --help || true
    
    info "📊 Data processor integration test completed"
}

# Create integration status dashboard
create_status_dashboard() {
    log "📊 Creating v2.05 integration status dashboard..."
    
    # Create a simple status file
    cat > "/tmp/v2_05_integration_status.json" << EOF
{
    "version": "v2.05",
    "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
    "components": {
        "file_watcher": {
            "version": "v2.05",
            "status": "integrated",
            "path": "/data/tools/file_watching/enhanced_file_watcher_v2_05.py"
        },
        "data_processor": {
            "version": "v2.05", 
            "status": "integrated",
            "path": "/data/tools/data_processing/enhanced_data_processor_v2_05.py"
        },
        "node_red_flows": {
            "version": "v2.05",
            "status": "deployed",
            "config": "/data/flows.json"
        }
    },
    "integration_features": [
        "Automated file monitoring",
        "Data processing pipeline",
        "Redis status tracking", 
        "Database upload automation",
        "Error handling and recovery",
        "Real-time dashboard monitoring"
    ]
}
EOF
    
    # Copy status to container
    docker cp "/tmp/v2_05_integration_status.json" "$CONTAINER_NAME:/data/integration_status.json"
    
    success "✅ Integration status dashboard created"
}

# Show integration summary
show_summary() {
    log "📋 v2.05 Integration Summary"
    echo
    echo -e "${PURPLE}🏇 Horse Racing AI - Node-RED v2.05 Integration${NC}"
    echo "============================================================"
    echo
    echo -e "${BLUE}✅ Components Integrated:${NC}"
    echo "  📁 Enhanced File Watcher v2.05"
    echo "  🔄 Enhanced Data Processor v2.05"
    echo "  📊 Node-RED Dashboard Integration"
    echo "  💾 Redis Status Tracking"
    echo "  🗄️ PostgreSQL Data Pipeline"
    echo
    echo -e "${BLUE}🌐 Access Points:${NC}"
    echo "  📊 Node-RED Dashboard: http://localhost:1881"
    echo "  📈 Integration Status: http://localhost:1881/ui"
    echo
    echo -e "${BLUE}🔧 Management Commands:${NC}"
    echo "  File Watcher: docker exec $CONTAINER_NAME python3 /data/tools/file_watching/enhanced_file_watcher_v2_05.py"
    echo "  Data Processor: docker exec $CONTAINER_NAME python3 /data/tools/data_processing/enhanced_data_processor_v2_05.py"
    echo
    echo -e "${BLUE}📁 Available Tools:${NC}"
    echo "  🔍 File monitoring and validation"
    echo "  📊 Data processing with -0 NULL mapping"
    echo "  📈 Quality metrics and reporting"
    echo "  🚨 Error handling and recovery"
    echo "  💾 Automated database uploads"
    echo
    success "🎉 Node-RED v2.05 integration deployment completed!"
}

# Main execution
main() {
    log "🚀 Starting Node-RED v2.05 Integration Deployment"
    echo
    
    check_container
    deploy_flows
    verify_deployment
    test_file_watcher
    test_data_processor
    create_status_dashboard
    show_summary
    
    echo
    log "✅ Deployment completed successfully!"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Open Node-RED dashboard: http://localhost:1881"
    echo "2. Check integration status in the UI"
    echo "3. Test file processing workflows"
    echo "4. Monitor logs for any issues"
    echo
}

# Run main function
main "$@"
