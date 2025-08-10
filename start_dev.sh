#!/bin/bash

# Horse Racing AI - Development Environment Startup Script
# =======================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🏇 Horse Racing AI - Development Environment${NC}"
echo -e "${BLUE}=============================================${NC}"

# Check if Docker is running
if ! docker info >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running. Please start Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose >/dev/null 2>&1; then
    echo -e "${RED}❌ Docker Compose is not installed.${NC}"
    exit 1
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null; then
        echo -e "${YELLOW}⚠️  Port $port is already in use${NC}"
        return 1
    fi
    return 0
}

# Function to wait for service
wait_for_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    echo -e "${YELLOW}⏳ Waiting for $service_name to be ready...${NC}"
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" >/dev/null 2>&1; then
            echo -e "${GREEN}✅ $service_name is ready!${NC}"
            return 0
        fi
        echo -n "."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo -e "${RED}❌ $service_name failed to start within $((max_attempts * 2)) seconds${NC}"
    return 1
}

# Parse command line arguments
MODE=${1:-"dev"}
case $MODE in
    "dev"|"development")
        echo -e "${GREEN}🚀 Starting development environment...${NC}"
        COMPOSE_FILE="src/web/docker-compose.dev.yml"
        ;;
    "prod"|"production")
        echo -e "${GREEN}🚀 Starting production environment...${NC}"
        COMPOSE_FILE="docker-compose.yml"
        ;;
    "build")
        echo -e "${GREEN}🔨 Building containers...${NC}"
        ;;
    "down")
        echo -e "${YELLOW}🛑 Stopping all services...${NC}"
        docker-compose -f docker-compose.yml down
        docker-compose -f src/web/docker-compose.dev.yml down 2>/dev/null || true
        echo -e "${GREEN}✅ All services stopped${NC}"
        exit 0
        ;;
    "clean")
        echo -e "${YELLOW}🧹 Cleaning up...${NC}"
        docker-compose -f docker-compose.yml down -v
        docker-compose -f src/web/docker-compose.dev.yml down -v 2>/dev/null || true
        docker system prune -f
        echo -e "${GREEN}✅ Cleanup complete${NC}"
        exit 0
        ;;
    "logs")
        echo -e "${BLUE}📋 Showing logs...${NC}"
        docker-compose -f docker-compose.yml logs -f --tail=100
        exit 0
        ;;
    "help"|"--help"|"-h")
        echo -e "${BLUE}Horse Racing AI Development Script${NC}"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo "Commands:"
        echo "  dev, development  Start development environment with hot reload"
        echo "  prod, production  Start production environment"
        echo "  build            Build containers only"
        echo "  down             Stop all services"
        echo "  clean            Stop services and clean up volumes"
        echo "  logs             Show service logs"
        echo "  help             Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 dev           # Start development with hot reload"
        echo "  $0 prod          # Start production environment"
        echo "  $0 down          # Stop all services"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $MODE${NC}"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac

# Check required ports
echo -e "${BLUE}🔍 Checking ports...${NC}"
if [ "$MODE" = "dev" ] || [ "$MODE" = "development" ]; then
    check_port 5003 || echo -e "${YELLOW}   Development server port 5003 in use${NC}"
    check_port 8001 || echo -e "${YELLOW}   API server port 8001 in use${NC}"
else
    check_port 8000 || echo -e "${YELLOW}   Production server port 8000 in use${NC}"
fi

# Start services based on mode
if [ "$MODE" = "build" ]; then
    echo -e "${BLUE}🔨 Building containers...${NC}"
    docker-compose build
    docker-compose -f src/web/docker-compose.dev.yml build 2>/dev/null || true
    echo -e "${GREEN}✅ Build complete${NC}"
    exit 0
fi

# Start database and supporting services first
echo -e "${BLUE}🗄️  Starting database services...${NC}"
docker-compose up -d postgres redis ntfy

# Wait for database
wait_for_service "http://localhost:5433" "PostgreSQL" || {
    echo -e "${RED}❌ Database failed to start${NC}"
    exit 1
}

# Start main application
if [ "$MODE" = "dev" ] || [ "$MODE" = "development" ]; then
    echo -e "${BLUE}⚛️  Starting development environment...${NC}"
    
    # Install NPM dependencies if needed
    if [ ! -d "src/web/node_modules" ]; then
        echo -e "${YELLOW}📦 Installing NPM dependencies...${NC}"
        cd src/web && npm install && cd ../..
    fi
    
    # Start development containers
    docker-compose -f src/web/docker-compose.dev.yml up -d horse-racing-ai-dev
    
    # Wait for services
    wait_for_service "http://localhost:5003" "React Dev Server"
    wait_for_service "http://localhost:8001/api/system_status" "API Server"
    
    echo -e "${GREEN}🎉 Development environment is ready!${NC}"
    echo ""
    echo -e "${BLUE}📱 Web Application: ${GREEN}http://localhost:5003${NC}"
    echo -e "${BLUE}🔧 API Server:      ${GREEN}http://localhost:8001${NC}"
    echo -e "${BLUE}🔔 Notifications:   ${GREEN}http://localhost:8081${NC}"
    echo -e "${BLUE}🗄️  Database:        ${GREEN}localhost:5433${NC}"
    echo ""
    echo -e "${YELLOW}💡 Tips:${NC}"
    echo -e "   • React files auto-reload on changes"
    echo -e "   • API server restarts on Python file changes"
    echo -e "   • Use 'grunt auto' in src/web/ for advanced watching"
    echo -e "   • Use '$0 logs' to view container logs"
    echo -e "   • Use '$0 down' to stop all services"
    
else
    echo -e "${BLUE}🚀 Starting production environment...${NC}"
    docker-compose up -d horse-racing-ai
    
    wait_for_service "http://localhost:8000/api/system_status" "Production Server"
    
    echo -e "${GREEN}🎉 Production environment is ready!${NC}"
    echo ""
    echo -e "${BLUE}🌐 Web Application: ${GREEN}http://localhost:8000${NC}"
    echo -e "${BLUE}🔔 Notifications:   ${GREEN}http://localhost:8081${NC}"
    echo -e "${BLUE}🗄️  Database:        ${GREEN}localhost:5433${NC}"
fi

# Show container status
echo ""
echo -e "${BLUE}📊 Container Status:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "(horse_racing|Name)"

echo ""
echo -e "${GREEN}✅ Startup complete!${NC}"
