#!/bin/bash
# Enhanced File Watcher v2.05 - Latest Version
# Startup and Management Script
# 
# Features:
# - System environment validation
# - Docker container health checks
# - Service management (start/stop/restart/status)
# - Log monitoring and rotation
# - Configuration validation
# - Backup and recovery operations

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
WATCHER_SCRIPT="$PROJECT_ROOT/tools/automation/enhanced_file_watcher_v2_05.py"
PID_FILE="$PROJECT_ROOT/logs/watcher_v2_05.pid"
LOG_FILE="$PROJECT_ROOT/logs/enhanced_file_watcher_v2_05.log"
CONFIG_FILE="$PROJECT_ROOT/config/enhanced_watcher_config_v2_05.json"
VERSION="v2.05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

check_dependencies() {
    log "🔍 Checking system dependencies..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        error "Docker is not installed"
        exit 1
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
        exit 1
    fi
    
    log "✅ All dependencies are available"
}

check_docker_containers() {
    log "🐳 Checking Docker containers..."
    
    required_containers=("redis" "postgres" "horse_racing_data_pipeline_clean")
    
    for container in "${required_containers[@]}"; do
        if ! docker ps --format "table {{.Names}}" | grep -q "^${container}$"; then
            warn "Container '$container' is not running"
            
            # Try to start it
            if docker ps -a --format "table {{.Names}}" | grep -q "^${container}$"; then
                info "Starting container '$container'..."
                docker start "$container"
            else
                error "Container '$container' does not exist"
                return 1
            fi
        else
            log "✅ Container '$container' is running"
        fi
    done
    
    # Check container health
    sleep 5
    for container in "${required_containers[@]}"; do
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        if [ "$status" != "running" ]; then
            error "Container '$container' is not healthy (status: $status)"
            return 1
        fi
    done
    
    log "✅ All required containers are running and healthy"
}

validate_configuration() {
    log "📋 Validating configuration..."
    
    if [ ! -f "$CONFIG_FILE" ]; then
        error "Configuration file not found: $CONFIG_FILE"
        exit 1
    fi
    
    # Validate JSON syntax
    if ! python3 -m json.tool "$CONFIG_FILE" > /dev/null 2>&1; then
        error "Invalid JSON in configuration file"
        exit 1
    fi
    
    # Check required directories
    directories=(
        "$PROJECT_ROOT/data/daily_downloads/manual_download"
        "$PROJECT_ROOT/data/daily_downloads/auto_download"
        "$PROJECT_ROOT/data/external_feeds"
        "$PROJECT_ROOT/logs"
        "$PROJECT_ROOT/config"
    )
    
    for dir in "${directories[@]}"; do
        if [ ! -d "$dir" ]; then
            info "Creating directory: $dir"
            mkdir -p "$dir"
        fi
    done
    
    log "✅ Configuration validated"
}

check_watcher_status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # Running
        else
            # Stale PID file
            rm -f "$PID_FILE"
            return 1  # Not running
        fi
    else
        return 1  # Not running
    fi
}

start_watcher() {
    log "🚀 Starting Enhanced File Watcher $VERSION..."
    
    if check_watcher_status; then
        warn "File watcher is already running (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    # Pre-flight checks
    check_dependencies
    check_docker_containers
    validate_configuration
    
    # Ensure log directory exists
    mkdir -p "$(dirname "$LOG_FILE")"
    
    # Start the watcher
    cd "$PROJECT_ROOT"
    nohup python3 "$WATCHER_SCRIPT" > "$LOG_FILE" 2>&1 &
    watcher_pid=$!
    
    # Save PID
    echo "$watcher_pid" > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 3
    if ps -p "$watcher_pid" > /dev/null 2>&1; then
        log "✅ Enhanced File Watcher $VERSION started successfully (PID: $watcher_pid)"
        info "📄 Log file: $LOG_FILE"
        info "🔧 Configuration: $CONFIG_FILE"
        
        # Show initial status
        sleep 2
        show_status
    else
        error "Failed to start file watcher"
        rm -f "$PID_FILE"
        exit 1
    fi
}

stop_watcher() {
    log "🛑 Stopping Enhanced File Watcher $VERSION..."
    
    if ! check_watcher_status; then
        warn "File watcher is not running"
        return 0
    fi
    
    pid=$(cat "$PID_FILE")
    
    # Try graceful shutdown first
    kill "$pid" 2>/dev/null || true
    
    # Wait for graceful shutdown
    for i in {1..10}; do
        if ! ps -p "$pid" > /dev/null 2>&1; then
            log "✅ File watcher stopped gracefully"
            rm -f "$PID_FILE"
            return 0
        fi
        sleep 1
    done
    
    # Force kill if still running
    warn "Forcing stop..."
    kill -9 "$pid" 2>/dev/null || true
    rm -f "$PID_FILE"
    
    log "✅ File watcher stopped"
}

restart_watcher() {
    log "🔄 Restarting Enhanced File Watcher $VERSION..."
    stop_watcher
    sleep 2
    start_watcher
}

show_status() {
    echo
    echo "==============================================="
    echo "  Enhanced File Watcher $VERSION - Status"
    echo "==============================================="
    
    # Service status
    if check_watcher_status; then
        pid=$(cat "$PID_FILE")
        echo -e "Status: ${GREEN}RUNNING${NC} (PID: $pid)"
        
        # Check process details
        if ps -p "$pid" -o pid,etime,pcpu,pmem,cmd --no-headers 2>/dev/null; then
            echo
        fi
    else
        echo -e "Status: ${RED}STOPPED${NC}"
    fi
    
    # Docker containers status
    echo
    echo "Docker Containers:"
    required_containers=("redis" "postgres" "horse_racing_data_pipeline_clean")
    for container in "${required_containers[@]}"; do
        status=$(docker inspect --format='{{.State.Status}}' "$container" 2>/dev/null || echo "not_found")
        if [ "$status" = "running" ]; then
            echo -e "  $container: ${GREEN}RUNNING${NC}"
        else
            echo -e "  $container: ${RED}$status${NC}"
        fi
    done
    
    # Log file info
    echo
    if [ -f "$LOG_FILE" ]; then
        log_size=$(du -h "$LOG_FILE" | cut -f1)
        log_lines=$(wc -l < "$LOG_FILE")
        echo "Log file: $LOG_FILE ($log_size, $log_lines lines)"
        
        # Show last few log entries
        echo
        echo "Recent log entries:"
        tail -5 "$LOG_FILE" | while IFS= read -r line; do
            echo "  $line"
        done
    else
        echo "Log file: Not created yet"
    fi
    
    # Configuration info
    echo
    if [ -f "$CONFIG_FILE" ]; then
        echo "Configuration: $CONFIG_FILE"
        config_version=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE')).get('version', 'unknown'))" 2>/dev/null || echo "unknown")
        echo "Config version: $config_version"
    else
        echo -e "Configuration: ${RED}MISSING${NC}"
    fi
    
    echo "==============================================="
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        if [ "$1" = "-f" ]; then
            log "📄 Following log file (Ctrl+C to stop)..."
            tail -f "$LOG_FILE"
        else
            lines=${1:-50}
            log "📄 Last $lines lines from log file:"
            tail -n "$lines" "$LOG_FILE"
        fi
    else
        warn "Log file does not exist: $LOG_FILE"
    fi
}

cleanup_logs() {
    log "🧹 Cleaning up old log files..."
    
    # Rotate log if it's too large (>50MB)
    if [ -f "$LOG_FILE" ]; then
        size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE" 2>/dev/null || echo 0)
        if [ "$size" -gt 52428800 ]; then  # 50MB
            timestamp=$(date +%Y%m%d_%H%M%S)
            mv "$LOG_FILE" "${LOG_FILE}.${timestamp}"
            log "📄 Log file rotated: ${LOG_FILE}.${timestamp}"
        fi
    fi
    
    # Clean old rotated logs (keep last 5)
    log_dir=$(dirname "$LOG_FILE")
    if [ -d "$log_dir" ]; then
        find "$log_dir" -name "enhanced_file_watcher_v2_05.log.*" -type f | sort -r | tail -n +6 | xargs rm -f 2>/dev/null || true
    fi
    
    log "✅ Log cleanup completed"
}

validate_system() {
    log "🔍 Running system validation..."
    
    check_dependencies
    check_docker_containers
    validate_configuration
    
    # Check Python modules
    python3 -c "
import sys
modules = ['watchdog', 'redis', 'psycopg2', 'pandas', 'asyncio']
missing = []
for module in modules:
    try:
        __import__(module)
    except ImportError:
        missing.append(module)

if missing:
    print(f'Missing Python modules: {missing}')
    sys.exit(1)
else:
    print('All Python modules are available')
" || {
        error "Some Python modules are missing. Install with: pip install -r requirements.txt"
        exit 1
    }
    
    # Test Redis connection
    if ! python3 -c "
import redis
try:
    r = redis.Redis(host='redis', port=6379, password='redis_password_123')
    r.ping()
    print('Redis connection: OK')
except Exception as e:
    print(f'Redis connection failed: {e}')
    exit(1)
"; then
        exit 1
    fi
    
    # Test database connection
    if ! python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres',
        port=5432,
        dbname='cards_horse_racing_db',
        user='horse_racing',
        password='secure_password_123'
    )
    conn.close()
    print('Database connection: OK')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
"; then
        exit 1
    fi
    
    log "✅ System validation completed successfully"
}

show_help() {
    echo
    echo "Enhanced File Watcher $VERSION - Management Script"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo "Commands:"
    echo "  start           Start the file watcher service"
    echo "  stop            Stop the file watcher service"
    echo "  restart         Restart the file watcher service"
    echo "  status          Show service status and information"
    echo "  logs [lines]    Show log file (default: 50 lines)"
    echo "  logs -f         Follow log file in real-time"
    echo "  validate        Run system validation checks"
    echo "  cleanup         Clean up old log files"
    echo "  help            Show this help message"
    echo
    echo "Examples:"
    echo "  $0 start                 # Start the service"
    echo "  $0 status                # Check status"
    echo "  $0 logs 100              # Show last 100 log lines"
    echo "  $0 logs -f               # Follow logs in real-time"
    echo "  $0 validate              # Validate system setup"
    echo
}

# Main command handling
case "${1:-help}" in
    start)
        start_watcher
        ;;
    stop)
        stop_watcher
        ;;
    restart)
        restart_watcher
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    validate)
        validate_system
        ;;
    cleanup)
        cleanup_logs
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
