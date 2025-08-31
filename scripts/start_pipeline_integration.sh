#!/bin/bash
# Integrated Daily File Watcher & Pipeline Startup
# Horse Racing AI v2.04 - Pipeline Integration

set -e

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.04"
INTEGRATION_SCRIPT="$PROJECT_ROOT/tools/pipeline/daily_file_watcher_integration.py"
LOG_FILE="$PROJECT_ROOT/logs/pipeline_integration.log"
PID_FILE="$PROJECT_ROOT/data/pipeline_integration.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Print colored output
print_status() {
    echo -e "${BLUE}🔗 Pipeline Integration${NC} - $1"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

# Create required directories
create_directories() {
    print_status "Creating required directories..."
    
    mkdir -p "$PROJECT_ROOT/logs"
    mkdir -p "$PROJECT_ROOT/data"
    mkdir -p "$PROJECT_ROOT/data/daily_downloads/manual_download"
    mkdir -p "$PROJECT_ROOT/data/daily_downloads/cards_data"
    mkdir -p "$PROJECT_ROOT/data/daily_downloads/results_data"
    mkdir -p "$PROJECT_ROOT/data/daily_downloads/processed"
    
    print_success "Directories created"
}

# Check if integration is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Pipeline Integration is already running (PID: $PID)"
            echo "Use './start_pipeline_integration.sh stop' to stop it first"
            exit 1
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

# Start the pipeline integration
start_integration() {
    print_status "Starting Pipeline Integration..."
    
    # Check dependencies
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check if script exists
    if [ ! -f "$INTEGRATION_SCRIPT" ]; then
        print_error "Integration script not found: $INTEGRATION_SCRIPT"
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Check if already running
    check_running
    
    # Start the integration
    log "Starting Pipeline Integration"
    cd "$PROJECT_ROOT"
    
    # Start in background and capture PID
    nohup python3 "$INTEGRATION_SCRIPT" >> "$LOG_FILE" 2>&1 &
    INTEGRATION_PID=$!
    
    # Save PID
    echo "$INTEGRATION_PID" > "$PID_FILE"
    
    # Wait a moment to see if it starts successfully
    sleep 3
    
    if ps -p "$INTEGRATION_PID" > /dev/null 2>&1; then
        print_success "Pipeline Integration started successfully (PID: $INTEGRATION_PID)"
        log "Pipeline Integration started with PID: $INTEGRATION_PID"
        
        # Show status
        show_status
    else
        print_error "Failed to start Pipeline Integration"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the pipeline integration
stop_integration() {
    print_status "Stopping Pipeline Integration..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Pipeline Integration is not running (no PID file found)"
        return
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        log "Stopping Pipeline Integration (PID: $PID)"
        kill "$PID"
        
        # Wait for process to stop
        for i in {1..15}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Force killing Pipeline Integration..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        print_success "Pipeline Integration stopped"
        log "Pipeline Integration stopped"
    else
        print_warning "Pipeline Integration process not found, removing PID file"
        rm -f "$PID_FILE"
    fi
}

# Show current status
show_status() {
    print_status "Current Status"
    echo "===================="
    
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_success "Pipeline Integration is running (PID: $PID)"
            
            # Show integration status
            STATUS_FILE="$PROJECT_ROOT/data/pipeline_integration_status.json"
            if [ -f "$STATUS_FILE" ]; then
                echo ""
                echo "🔗 Integration Status:"
                python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        status = json.load(f)
    
    integration = status.get('integration_status', {})
    print(f\"   Target Date: {integration.get('current_target_date', 'Unknown')}\")
    
    files_status = integration.get('files_status', {})
    if files_status.get('cards', False):
        print('   📋 Race Cards: ✅ Received')
    else:
        print('   📋 Race Cards: ⏳ Waiting')
    
    if files_status.get('results', False):
        print('   🏁 Results: ✅ Received')
    else:
        print('   🏁 Results: ⏳ Waiting')
    
    completed = integration.get('completed_days', [])
    print(f\"   Completed Days: {len(completed)}\")
    
    pipeline_config = integration.get('pipeline_config', {})
    auto_trigger = pipeline_config.get('auto_trigger', False)
    print(f\"   Auto Pipeline: {'✅ Enabled' if auto_trigger else '❌ Disabled'}\")
    
    events = integration.get('event_log_count', 0)
    print(f\"   Events Logged: {events}\")
    
except Exception as e:
    print(f'   Status file error: {e}')
"
            fi
            
            # Show file watcher status
            WATCHER_STATUS="$PROJECT_ROOT/data/daily_watcher_status.json"
            if [ -f "$WATCHER_STATUS" ]; then
                echo ""
                echo "👁️ File Watcher Status:"
                python3 -c "
import json
try:
    with open('$WATCHER_STATUS', 'r') as f:
        status = json.load(f)
    
    print(f\"   Watcher: {status.get('watcher_status', 'Unknown')}\")
    
    files_needed = status.get('files_needed', {})
    if files_needed.get('cards', False) or files_needed.get('results', False):
        print('   Status: ⏳ Waiting for files')
    else:
        print('   Status: ✅ All files received')
    
except:
    print('   Watcher status not available')
"
            fi
        else
            print_error "Pipeline Integration is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "Pipeline Integration is not running"
    fi
    
    echo ""
    echo "📂 Watch Directory: $PROJECT_ROOT/data/daily_downloads/manual_download"
    echo "📄 Log File: $LOG_FILE"
    echo "📊 Status Files:"
    echo "   - Pipeline: $PROJECT_ROOT/data/pipeline_integration_status.json"
    echo "   - Watcher: $PROJECT_ROOT/data/daily_watcher_status.json"
}

# Show help
show_help() {
    echo "Daily File Watcher Pipeline Integration Control Script"
    echo "Horse Racing AI v2.04"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the integrated pipeline system"
    echo "  stop     - Stop the integrated pipeline system"
    echo "  restart  - Restart the integrated pipeline system"
    echo "  status   - Show current status and file monitoring"
    echo "  help     - Show this help message"
    echo ""
    echo "Features:"
    echo "  • Daily file monitoring with automatic pipeline triggering"
    echo "  • Event-driven data processing pipeline"
    echo "  • Automatic validation and database upload"
    echo "  • ML model retraining on new data"
    echo "  • Contextual analysis and reporting"
    echo ""
    echo "File Placement:"
    echo "  Place ZIP files in: $PROJECT_ROOT/data/daily_downloads/manual_download/"
    echo "  Naming convention: Include date (YYYY-MM-DD) and type (cards/results)"
    echo "  Examples:"
    echo "    - racecards_2025-08-23.zip"
    echo "    - results_2025-08-23.zip"
}

# Test integration
test_integration() {
    print_status "Testing Pipeline Integration..."
    
    # Check Python environment
    if ! python3 -c "import asyncio, pathlib, json" 2>/dev/null; then
        print_error "Python environment missing required modules"
        exit 1
    fi
    
    # Check project structure
    REQUIRED_DIRS=(
        "$PROJECT_ROOT/tools/pipeline"
        "$PROJECT_ROOT/tools/automation"
        "$PROJECT_ROOT/data"
        "$PROJECT_ROOT/logs"
    )
    
    for dir in "${REQUIRED_DIRS[@]}"; do
        if [ ! -d "$dir" ]; then
            print_error "Required directory missing: $dir"
            exit 1
        fi
    done
    
    # Test integration script
    if python3 "$INTEGRATION_SCRIPT" --help >/dev/null 2>&1; then
        print_success "Integration script test passed"
    else
        print_warning "Integration script may have issues - check dependencies"
    fi
    
    print_success "Integration test completed"
}

# Main script logic
case "${1:-}" in
    start)
        start_integration
        ;;
    stop)
        stop_integration
        ;;
    restart)
        stop_integration
        sleep 3
        start_integration
        ;;
    status)
        show_status
        ;;
    test)
        test_integration
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|test|help}"
        echo "Run '$0 help' for more information"
        exit 1
        ;;
esac
