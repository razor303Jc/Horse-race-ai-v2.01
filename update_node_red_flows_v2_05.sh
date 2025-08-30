#!/bin/bash
# Node-RED Configuration Update for v2.05 Integration
# Version Tag: latest:v2.05
# Updates Node-RED configuration to include enhanced data pipeline flows

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
NODE_RED_CONTAINER="horse_racing_node_red"
FLOWS_FILE="$PROJECT_ROOT/config/enhanced_data_pipeline_v2_05_flows.json"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

update_node_red_flows() {
    log "🔄 Updating Node-RED flows with v2.05 integration..."
    
    # Check if Node-RED container is running
    if ! docker ps | grep -q "$NODE_RED_CONTAINER"; then
        error "Node-RED container is not running. Start it first with: docker-compose -f docker-compose.node-red.yml up -d"
        exit 1
    fi
    
    # Check if flows file exists
    if [ ! -f "$FLOWS_FILE" ]; then
        error "Enhanced flows file not found: $FLOWS_FILE"
        exit 1
    fi
    
    # Copy flows to Node-RED container
    log "📁 Copying enhanced flows to Node-RED container..."
    docker cp "$FLOWS_FILE" "$NODE_RED_CONTAINER:/data/flows.json"
    
    # Install required Node-RED modules
    log "📦 Installing required Node-RED modules..."
    
    local modules=(
        "node-red-contrib-redis"
        "node-red-node-postgres" 
        "node-red-dashboard"
        "node-red-contrib-fs"
        "node-red-contrib-cron"
        "node-red-contrib-ui-led"
    )
    
    for module in "${modules[@]}"; do
        log "Installing $module..."
        docker exec "$NODE_RED_CONTAINER" npm install "$module" || warn "Failed to install $module"
    done
    
    # Restart Node-RED to apply changes
    log "🔄 Restarting Node-RED to apply changes..."
    docker restart "$NODE_RED_CONTAINER"
    
    # Wait for restart
    sleep 15
    
    # Verify Node-RED is accessible
    local max_attempts=10
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:1881 > /dev/null; then
            log "✅ Node-RED is accessible at http://localhost:1881"
            break
        else
            log "Attempt $attempt/$max_attempts: Waiting for Node-RED..."
            sleep 3
            ((attempt++))
        fi
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "Node-RED failed to restart properly"
        return 1
    fi
    
    log "✅ Node-RED flows updated successfully!"
    
    cat << EOF

🚀 Enhanced Data Pipeline v2.05 - Node-RED Integration Complete!

📊 Access Points:
  🏠 Node-RED Editor:     http://localhost:1881
  📋 Dashboard:           http://localhost:1881/ui

🎯 Available Tabs:
  🚀 v2.05 Data Pipeline  - Main integration dashboard
  👀 File Watcher v2.05   - File monitoring controls
  ⚙️ Data Processor v2.05 - Data processing controls

🔧 Quick Actions:
  1. Open Node-RED editor at http://localhost:1881
  2. Click "Deploy" to activate the flows
  3. Navigate to dashboard at http://localhost:1881/ui
  4. Monitor file watcher and processor status

📁 Flow Features:
  ✅ Automatic file monitoring
  ✅ Redis queue management  
  ✅ Data processing with -0 NULL mapping
  ✅ Real-time status monitoring
  ✅ Manual processing controls
  ✅ System health checks

EOF
}

# Execute the update
update_node_red_flows
