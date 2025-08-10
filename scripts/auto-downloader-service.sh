#!/bin/bash
# Auto Downloader Service Manager
# Manages the horserace auto downloader Docker container

set -euo pipefail

# Configuration
COMPOSE_FILE="/home/jc/Documents/Horse-race-ai-v2.01/docker-compose.auto-downloader.yml"
CONTAINER_NAME="horserace-auto-downloader"
LOG_FILE="/home/jc/Documents/Horse-race-ai-v2.01/logs/auto-downloader-service.log"
PID_FILE="/home/jc/Documents/Horse-race-ai-v2.01/logs/auto-downloader.pid"

# Ensure log directory exists
mkdir -p "$(dirname "$LOG_FILE")"

# Logging function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

# Function to check if container is running
is_container_running() {
    docker ps --filter "name=$CONTAINER_NAME" --filter "status=running" --quiet | grep -q .
}

# Function to check if container is healthy
is_container_healthy() {
    if is_container_running; then
        health_status=$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo "none")
        [ "$health_status" = "healthy" ] || [ "$health_status" = "none" ]
    else
        false
    fi
}

# Function to start the auto downloader
start_service() {
    log "🚀 Starting auto downloader service..."
    
    if is_container_running; then
        log "⚠️  Container is already running"
        return 0
    fi
    
    # Navigate to project directory
    cd "/home/jc/Documents/Horse-race-ai-v2.01" || {
        log "❌ Failed to navigate to project directory"
        return 1
    }
    
    # Start the container
    if docker-compose -f "$COMPOSE_FILE" up -d auto-downloader; then
        echo $! > "$PID_FILE"
        log "✅ Auto downloader container started successfully"
        
        # Wait for container to be ready
        for i in {1..30}; do
            if is_container_running; then
                log "✅ Container is running and ready"
                return 0
            fi
            sleep 2
        done
        
        log "⚠️  Container started but may not be fully ready"
        return 0
    else
        log "❌ Failed to start auto downloader container"
        return 1
    fi
}

# Function to stop the auto downloader
stop_service() {
    log "🛑 Stopping auto downloader service..."
    
    if ! is_container_running; then
        log "⚠️  Container is not running"
        return 0
    fi
    
    cd "/home/jc/Documents/Horse-race-ai-v2.01" || {
        log "❌ Failed to navigate to project directory"
        return 1
    }
    
    if docker-compose -f "$COMPOSE_FILE" down auto-downloader; then
        rm -f "$PID_FILE"
        log "✅ Auto downloader container stopped successfully"
        return 0
    else
        log "❌ Failed to stop auto downloader container"
        return 1
    fi
}

# Function to restart the service
restart_service() {
    log "🔄 Restarting auto downloader service..."
    stop_service
    sleep 5
    start_service
}

# Function to check service status
status_service() {
    if is_container_running; then
        if is_container_healthy; then
            log "✅ Auto downloader is running and healthy"
            return 0
        else
            log "⚠️  Auto downloader is running but may not be healthy"
            return 1
        fi
    else
        log "❌ Auto downloader is not running"
        return 1
    fi
}

# Function to monitor and ensure service is running
monitor_service() {
    while true; do
        if ! is_container_running; then
            log "🔧 Auto downloader not running, attempting to start..."
            start_service
        elif ! is_container_healthy; then
            log "🔧 Auto downloader unhealthy, attempting restart..."
            restart_service
        fi
        
        # Check every 5 minutes
        sleep 300
    done
}

# Main script logic
case "${1:-}" in
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    monitor)
        log "🔍 Starting monitoring mode..."
        monitor_service
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|monitor}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the auto downloader container"
        echo "  stop    - Stop the auto downloader container"
        echo "  restart - Restart the auto downloader container"
        echo "  status  - Check the status of the auto downloader"
        echo "  monitor - Monitor and maintain the auto downloader"
        exit 1
        ;;
esac
