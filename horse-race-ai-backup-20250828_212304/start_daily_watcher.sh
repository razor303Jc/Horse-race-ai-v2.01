#!/bin/bash
# Daily File Watcher Startup Script
# Horse Racing AI v2.04

set -e

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.04"
WATCHER_SCRIPT="$PROJECT_ROOT/tools/automation/daily_file_watcher.py"
LOG_FILE="$PROJECT_ROOT/logs/daily_watcher_startup.log"
PID_FILE="$PROJECT_ROOT/data/daily_watcher.pid"

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
    echo -e "${BLUE}🔍 Daily File Watcher${NC} - $1"
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

# Check if watcher is already running
check_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Daily File Watcher is already running (PID: $PID)"
            echo "Use './start_daily_watcher.sh stop' to stop it first"
            exit 1
        else
            print_warning "Stale PID file found, removing..."
            rm -f "$PID_FILE"
        fi
    fi
}

# Start the daily file watcher
start_watcher() {
    print_status "Starting Daily File Watcher..."
    
    # Check dependencies
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is required but not installed"
        exit 1
    fi
    
    # Check if script exists
    if [ ! -f "$WATCHER_SCRIPT" ]; then
        print_error "Watcher script not found: $WATCHER_SCRIPT"
        exit 1
    fi
    
    # Create directories
    create_directories
    
    # Check if already running
    check_running
    
    # Start the watcher
    log "Starting Daily File Watcher"
    cd "$PROJECT_ROOT"
    
    # Start in background and capture PID
    nohup python3 "$WATCHER_SCRIPT" >> "$LOG_FILE" 2>&1 &
    WATCHER_PID=$!
    
    # Save PID
    echo "$WATCHER_PID" > "$PID_FILE"
    
    # Wait a moment to see if it starts successfully
    sleep 2
    
    if ps -p "$WATCHER_PID" > /dev/null 2>&1; then
        print_success "Daily File Watcher started successfully (PID: $WATCHER_PID)"
        log "Daily File Watcher started with PID: $WATCHER_PID"
        
        # Show status
        show_status
    else
        print_error "Failed to start Daily File Watcher"
        rm -f "$PID_FILE"
        exit 1
    fi
}

# Stop the daily file watcher
stop_watcher() {
    print_status "Stopping Daily File Watcher..."
    
    if [ ! -f "$PID_FILE" ]; then
        print_warning "Daily File Watcher is not running (no PID file found)"
        return
    fi
    
    PID=$(cat "$PID_FILE")
    
    if ps -p "$PID" > /dev/null 2>&1; then
        log "Stopping Daily File Watcher (PID: $PID)"
        kill "$PID"
        
        # Wait for process to stop
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if ps -p "$PID" > /dev/null 2>&1; then
            print_warning "Force killing Daily File Watcher..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        print_success "Daily File Watcher stopped"
        log "Daily File Watcher stopped"
    else
        print_warning "Daily File Watcher process not found, removing PID file"
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
            print_success "Daily File Watcher is running (PID: $PID)"
            
            # Show target date and files needed
            STATUS_FILE="$PROJECT_ROOT/data/daily_watcher_status.json"
            if [ -f "$STATUS_FILE" ]; then
                echo ""
                echo "📅 Current Status:"
                python3 -c "
import json
try:
    with open('$STATUS_FILE', 'r') as f:
        status = json.load(f)
    print(f\"   Target Date: {status.get('target_date', 'Unknown')}\")
    files_needed = status.get('files_needed', {})
    if files_needed.get('cards', False):
        print('   📋 Race Cards: ⏳ Needed')
    else:
        print('   📋 Race Cards: ✅ Received')
    if files_needed.get('results', False):
        print('   🏁 Results: ⏳ Needed')
    else:
        print('   🏁 Results: ✅ Received')
    print(f\"   Completed Days: {len(status.get('completed_days', []))}\")
except:
    print('   Status file not available')
"
            fi
        else
            print_error "Daily File Watcher is not running (stale PID file)"
            rm -f "$PID_FILE"
        fi
    else
        print_warning "Daily File Watcher is not running"
    fi
    
    echo ""
    echo "📂 Watch Directory: $PROJECT_ROOT/data/daily_downloads/manual_download"
    echo "📄 Log File: $LOG_FILE"
    echo "📊 Status File: $PROJECT_ROOT/data/daily_watcher_status.json"
}

# Show help
show_help() {
    echo "Daily File Watcher Control Script"
    echo "Horse Racing AI v2.04"
    echo ""
    echo "Usage: $0 {start|stop|restart|status|help}"
    echo ""
    echo "Commands:"
    echo "  start    - Start the daily file watcher"
    echo "  stop     - Stop the daily file watcher" 
    echo "  restart  - Restart the daily file watcher"
    echo "  status   - Show current status"
    echo "  help     - Show this help message"
    echo ""
    echo "The watcher monitors: $PROJECT_ROOT/data/daily_downloads/manual_download"
    echo "For ZIP files containing race cards and results for each day."
}

# Main script logic
case "${1:-}" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    restart)
        stop_watcher
        sleep 2
        start_watcher
        ;;
    status)
        show_status
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|help}"
        echo "Run '$0 help' for more information"
        exit 1
        ;;
esac
