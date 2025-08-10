#!/bin/bash
"""
Docker Auto Downloader Management Script
========================================

Manages the Docker-based auto downloader for horse racing data.
"""

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.auto-downloader.yml"
SERVICE_NAME="auto-downloader"
TEST_SERVICE_NAME="auto-downloader-test"

# Functions
print_usage() {
    echo -e "${BLUE}Docker Auto Downloader Management${NC}"
    echo ""
    echo "Usage: $0 {start|stop|restart|test|logs|status|build}"
    echo ""
    echo "Commands:"
    echo "  start   - Start the scheduled auto downloader"
    echo "  stop    - Stop the auto downloader"
    echo "  restart - Restart the auto downloader"
    echo "  test    - Run a one-time test download"
    echo "  logs    - Show auto downloader logs"
    echo "  status  - Show auto downloader status"
    echo "  build   - Rebuild the Docker image"
    echo "  clean   - Stop and remove containers/volumes"
}

check_requirements() {
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        echo -e "${RED}❌ Docker is not running${NC}"
        exit 1
    fi
    
    # Check if docker-compose file exists
    if [ ! -f "$COMPOSE_FILE" ]; then
        echo -e "${RED}❌ Docker compose file not found: $COMPOSE_FILE${NC}"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f ".env" ]; then
        echo -e "${YELLOW}⚠️  Warning: .env file not found. Make sure environment variables are set.${NC}"
    fi
}

start_downloader() {
    echo -e "${BLUE}🚀 Starting Auto Downloader...${NC}"
    
    # Create network if it doesn't exist
    docker network create horserace-network 2>/dev/null || true
    
    # Start the service
    docker compose -f "$COMPOSE_FILE" up -d "$SERVICE_NAME"
    
    echo -e "${GREEN}✅ Auto Downloader started successfully${NC}"
    echo -e "${BLUE}📅 Scheduled to run daily at 00:01 UTC${NC}"
    echo -e "${BLUE}📊 Use '$0 logs' to monitor progress${NC}"
}

stop_downloader() {
    echo -e "${BLUE}🛑 Stopping Auto Downloader...${NC}"
    docker compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}✅ Auto Downloader stopped${NC}"
}

restart_downloader() {
    echo -e "${BLUE}🔄 Restarting Auto Downloader...${NC}"
    stop_downloader
    sleep 2
    start_downloader
}

test_downloader() {
    echo -e "${BLUE}🧪 Running Test Download...${NC}"
    
    # Create network if it doesn't exist
    docker network create horserace-network 2>/dev/null || true
    
    # Run test service
    docker compose -f "$COMPOSE_FILE" --profile test run --rm "$TEST_SERVICE_NAME"
    
    echo -e "${GREEN}✅ Test download completed${NC}"
}

show_logs() {
    echo -e "${BLUE}📄 Auto Downloader Logs:${NC}"
    docker compose -f "$COMPOSE_FILE" logs -f "$SERVICE_NAME"
}

show_status() {
    echo -e "${BLUE}📊 Auto Downloader Status:${NC}"
    
    # Check if container is running
    if docker compose -f "$COMPOSE_FILE" ps "$SERVICE_NAME" | grep -q "Up"; then
        echo -e "${GREEN}✅ Status: Running${NC}"
        
        # Show container info
        docker compose -f "$COMPOSE_FILE" ps "$SERVICE_NAME"
        
        # Show recent logs
        echo -e "\n${BLUE}Recent logs:${NC}"
        docker compose -f "$COMPOSE_FILE" logs --tail=10 "$SERVICE_NAME"
    else
        echo -e "${RED}❌ Status: Not Running${NC}"
    fi
}

build_image() {
    echo -e "${BLUE}🔨 Building Docker Image...${NC}"
    docker compose -f "$COMPOSE_FILE" build --no-cache
    echo -e "${GREEN}✅ Docker image built successfully${NC}"
}

clean_all() {
    echo -e "${BLUE}🧹 Cleaning up Docker resources...${NC}"
    
    # Stop and remove containers
    docker compose -f "$COMPOSE_FILE" down -v
    
    # Remove images
    docker compose -f "$COMPOSE_FILE" down --rmi all
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Main script
case "$1" in
    start)
        check_requirements
        start_downloader
        ;;
    stop)
        check_requirements
        stop_downloader
        ;;
    restart)
        check_requirements
        restart_downloader
        ;;
    test)
        check_requirements
        test_downloader
        ;;
    logs)
        check_requirements
        show_logs
        ;;
    status)
        check_requirements
        show_status
        ;;
    build)
        check_requirements
        build_image
        ;;
    clean)
        check_requirements
        clean_all
        ;;
    *)
        print_usage
        exit 1
        ;;
esac

exit 0
