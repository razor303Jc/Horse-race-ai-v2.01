#!/bin/bash
#
# Auto Downloader Management Script
# Horse Racing AI v2.0
#
# Simple script to manage the respectful auto downloader service.
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project paths
PROJECT_DIR="/home/jc/Documents/Horse-race-ai-v2.01"
SERVICE_FILE="scripts/horse-racing-auto-downloader.service"
LOGS_DIR="$PROJECT_DIR/logs"
DATA_DIR="$PROJECT_DIR/data/daily_downloads"

# Function to print colored messages
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if service is installed
is_service_installed() {
    systemctl list-unit-files | grep -q "horse-racing-auto-downloader.service"
}

# Function to check if service is running
is_service_running() {
    systemctl is-active --quiet horse-racing-auto-downloader.service 2>/dev/null
}

# Function to install the service
install_service() {
    print_message $BLUE "Installing Auto Downloader Service..."
    
    # Copy service file to systemd directory
    sudo cp "$PROJECT_DIR/$SERVICE_FILE" /etc/systemd/system/
    
    # Reload systemd daemon
    sudo systemctl daemon-reload
    
    # Enable the service
    sudo systemctl enable horse-racing-auto-downloader.service
    
    print_message $GREEN "✅ Service installed and enabled"
}

# Function to start the service
start_service() {
    print_message $BLUE "Starting Auto Downloader Service..."
    
    # Create necessary directories
    mkdir -p "$LOGS_DIR"
    mkdir -p "$DATA_DIR"
    
    # Start the service
    sudo systemctl start horse-racing-auto-downloader.service
    
    if is_service_running; then
        print_message $GREEN "✅ Auto Downloader Service started successfully"
        print_message $YELLOW "Next download scheduled for: 00:01 daily"
    else
        print_message $RED "❌ Failed to start service"
        exit 1
    fi
}

# Function to stop the service
stop_service() {
    print_message $BLUE "Stopping Auto Downloader Service..."
    
    sudo systemctl stop horse-racing-auto-downloader.service
    
    if ! is_service_running; then
        print_message $GREEN "✅ Auto Downloader Service stopped"
    else
        print_message $RED "❌ Failed to stop service"
        exit 1
    fi
}

# Function to check service status
check_status() {
    print_message $BLUE "Auto Downloader Service Status:"
    echo
    
    if is_service_installed; then
        print_message $GREEN "📦 Service: Installed"
    else
        print_message $RED "📦 Service: Not Installed"
        return
    fi
    
    if is_service_running; then
        print_message $GREEN "🟢 Status: Running"
    else
        print_message $RED "🔴 Status: Stopped"
    fi
    
    echo
    print_message $BLUE "Service Details:"
    systemctl status horse-racing-auto-downloader.service --no-pager -l
    
    echo
    print_message $BLUE "Recent Logs (last 20 lines):"
    sudo journalctl -u horse-racing-auto-downloader.service -n 20 --no-pager
    
    # Check last download status
    if [ -f "$DATA_DIR/last_success.json" ]; then
        echo
        print_message $BLUE "Last Successful Download:"
        cat "$DATA_DIR/last_success.json" | python3 -m json.tool
    fi
    
    if [ -f "$DATA_DIR/last_failure.json" ]; then
        echo
        print_message $YELLOW "Last Failed Download:"
        cat "$DATA_DIR/last_failure.json" | python3 -m json.tool
    fi
}

# Function to show logs
show_logs() {
    local lines=${1:-50}
    print_message $BLUE "Auto Downloader Service Logs (last $lines lines):"
    sudo journalctl -u horse-racing-auto-downloader.service -n "$lines" --no-pager -f
}

# Function to run download manually
run_manual() {
    print_message $BLUE "Running manual download..."
    cd "$PROJECT_DIR"
    python3 src/automation/daily_scheduler.py --run-now
}

# Function to test configuration
test_config() {
    print_message $BLUE "Testing configuration..."
    cd "$PROJECT_DIR"
    
    if [ -f "config/respectful_downloader_config.json" ]; then
        print_message $GREEN "✅ Configuration file found"
        python3 -c "import json; json.load(open('config/respectful_downloader_config.json'))"
        print_message $GREEN "✅ Configuration file is valid JSON"
    else
        print_message $RED "❌ Configuration file not found"
        exit 1
    fi
    
    # Test Python dependencies
    python3 -c "import playwright, schedule, aiofiles, structlog" 2>/dev/null
    if [ $? -eq 0 ]; then
        print_message $GREEN "✅ Required Python packages available"
    else
        print_message $RED "❌ Missing required Python packages"
        print_message $YELLOW "Run: pip install playwright schedule aiofiles structlog"
        exit 1
    fi
}

# Function to uninstall the service
uninstall_service() {
    print_message $BLUE "Uninstalling Auto Downloader Service..."
    
    # Stop service if running
    if is_service_running; then
        stop_service
    fi
    
    # Disable and remove service
    if is_service_installed; then
        sudo systemctl disable horse-racing-auto-downloader.service
        sudo rm -f /etc/systemd/system/horse-racing-auto-downloader.service
        sudo systemctl daemon-reload
        print_message $GREEN "✅ Service uninstalled"
    else
        print_message $YELLOW "Service was not installed"
    fi
}

# Function to show help
show_help() {
    cat << EOF
Auto Downloader Management Script
Horse Racing AI v2.0

Usage: $0 [COMMAND]

Commands:
    install     Install the auto downloader service
    start       Start the auto downloader service
    stop        Stop the auto downloader service
    restart     Restart the auto downloader service
    status      Show service status and recent logs
    logs        Show recent logs (default: 50 lines)
    logs [N]    Show last N lines of logs
    manual      Run download manually (for testing)
    test        Test configuration and dependencies
    uninstall   Uninstall the service
    help        Show this help message

The auto downloader runs at 00:01 daily and downloads race data respectfully
from horseracedatabase.com. It stops when successful or after maximum runtime.

This is a temporary solution until horseracedatabase.com releases their official API.
EOF
}

# Main script logic
case "${1:-help}" in
    install)
        if is_service_installed; then
            print_message $YELLOW "Service is already installed"
        else
            install_service
        fi
        ;;
    start)
        if ! is_service_installed; then
            print_message $YELLOW "Installing service first..."
            install_service
        fi
        
        if is_service_running; then
            print_message $YELLOW "Service is already running"
        else
            start_service
        fi
        ;;
    stop)
        if is_service_running; then
            stop_service
        else
            print_message $YELLOW "Service is not running"
        fi
        ;;
    restart)
        if is_service_running; then
            stop_service
            sleep 2
        fi
        start_service
        ;;
    status)
        check_status
        ;;
    logs)
        show_logs ${2:-50}
        ;;
    manual)
        run_manual
        ;;
    test)
        test_config
        ;;
    uninstall)
        uninstall_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_message $RED "Unknown command: $1"
        echo
        show_help
        exit 1
        ;;
esac
