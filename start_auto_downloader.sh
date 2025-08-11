#!/bin/bash
#
# 🏇 HORSE RACING AUTO DOWNLOADER - SIMPLE LAUNCHER
# =================================================
#
# This script simplifies starting the auto downloader.
# All the complexity is hidden - just run this script!
#

set -e

# Colors for pretty output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🏇 Horse Racing Auto Downloader${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  No .env file found. Creating template...${NC}"
    cat > .env << 'EOF'
# WooCommerce Database Credentials
HORSERACE_DB_USERNAME=your_username
HORSERACE_DB_PASSWORD=your_password
HORSERACE_DB_RESULTS_URL=https://your-site.com/wp-json/wc/v3/products
HORSERACE_DB_CARDS_URL=https://your-site.com/wp-json/wc/v3/products

# Optional: Notification settings
NTFY_TOPIC=horse-racing-alerts
EOF
    echo -e "${YELLOW}📝 Please edit .env with your actual credentials${NC}"
    echo ""
fi

# Function to start the auto downloader
start_auto_downloader() {
    echo -e "${BLUE}🚀 Starting Auto Downloader...${NC}"
    echo -e "${BLUE}📅 Scheduled to run daily at 00:01 UTC${NC}"
    echo ""
    
    # Build and start the container
    docker-compose -f docker-compose.auto-downloader.yml up -d --build
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Auto Downloader started successfully!${NC}"
        echo ""
        echo -e "${BLUE}📊 To view logs: ./start_auto_downloader.sh logs${NC}"
        echo -e "${BLUE}🛑 To stop: ./start_auto_downloader.sh stop${NC}"
        echo -e "${BLUE}📋 To check status: ./start_auto_downloader.sh status${NC}"
    else
        echo -e "${RED}❌ Failed to start Auto Downloader${NC}"
        exit 1
    fi
}

# Function to show logs
show_logs() {
    echo -e "${BLUE}📊 Showing Auto Downloader logs...${NC}"
    docker-compose -f docker-compose.auto-downloader.yml logs -f auto-downloader
}

# Function to stop the auto downloader
stop_auto_downloader() {
    echo -e "${YELLOW}🛑 Stopping Auto Downloader...${NC}"
    docker-compose -f docker-compose.auto-downloader.yml down
    echo -e "${GREEN}✅ Auto Downloader stopped${NC}"
}

# Function to show status
show_status() {
    echo -e "${BLUE}📋 Auto Downloader Status:${NC}"
    echo ""
    
    if docker ps | grep -q "horserace-auto-downloader"; then
        echo -e "${GREEN}✅ Running${NC}"
        docker ps | grep horserace-auto-downloader
        echo ""
        echo -e "${BLUE}📊 Recent logs:${NC}"
        docker-compose -f docker-compose.auto-downloader.yml logs --tail=10 auto-downloader
    else
        echo -e "${RED}❌ Not running${NC}"
    fi
}

# Function to run a test download
test_download() {
    echo -e "${BLUE}🧪 Running test download...${NC}"
    docker-compose -f docker-compose.auto-downloader.yml run --rm auto-downloader python run_docker_auto_downloader.py --mode once --log-level DEBUG
}

# Main menu
case "${1:-start}" in
    "start"|"")
        start_auto_downloader
        ;;
    "stop")
        stop_auto_downloader
        ;;
    "logs")
        show_logs
        ;;
    "status")
        show_status
        ;;
    "test")
        test_download
        ;;
    "restart")
        stop_auto_downloader
        sleep 2
        start_auto_downloader
        ;;
    *)
        echo -e "${BLUE}Usage: $0 {start|stop|restart|logs|status|test}${NC}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the scheduled auto downloader (default)"
        echo "  stop    - Stop the auto downloader"
        echo "  restart - Stop and start the auto downloader"
        echo "  logs    - Show live logs"
        echo "  status  - Show current status"
        echo "  test    - Run a one-time test download"
        ;;
esac
