#!/bin/bash
# Run Bulk Uploader in Docker Container
# Executes the bulk uploader inside the ML trainer container which has network access to postgres

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Docker Bulk Uploader Runner${NC}"
echo "=================================================="

# Check if containers are running
echo -e "${YELLOW}🔍 Checking Docker containers...${NC}"
if ! docker ps | grep -q "horse_racing_ml_trainer_clean"; then
    echo -e "${RED}❌ ML trainer container not running${NC}"
    echo "Please start the containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

if ! docker ps | grep -q "horse_racing_postgres_clean"; then
    echo -e "${RED}❌ PostgreSQL container not running${NC}"
    echo "Please start the containers first:"
    echo "  docker-compose up -d"
    exit 1
fi

echo -e "${GREEN}✅ Required containers are running${NC}"

# Copy bulk uploader files to the container
echo -e "${YELLOW}📋 Copying bulk uploader to container...${NC}"
docker exec horse_racing_ml_trainer_clean mkdir -p /app/tools/bulk_uploader

# Copy the bulk uploader files
docker cp tools/bulk_uploader/bulk_uploader.py horse_racing_ml_trainer_clean:/app/tools/bulk_uploader/
docker cp tools/bulk_uploader/cli.py horse_racing_ml_trainer_clean:/app/tools/bulk_uploader/
docker cp tools/bulk_uploader/container_runner.py horse_racing_ml_trainer_clean:/app/tools/bulk_uploader/
docker cp tools/bulk_uploader/config.yaml horse_racing_ml_trainer_clean:/app/tools/bulk_uploader/

echo -e "${GREEN}✅ Files copied to container${NC}"

# Test database connection first
echo -e "${YELLOW}🔌 Testing database connection...${NC}"
if docker exec horse_racing_ml_trainer_clean python -c "
import sys
sys.path.insert(0, '/app/tools/bulk_uploader')
from bulk_uploader import DatabaseConnectionManager
import os
os.environ['DOCKER_CONTAINER'] = 'true'
manager = DatabaseConnectionManager()
if manager.test_connection():
    print('✅ Database connection successful')
else:
    print('❌ Database connection failed')
    exit(1)
"; then
    echo -e "${GREEN}✅ Database connection verified${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi

# Parse command line arguments
COMMAND="$1"
shift

case "$COMMAND" in
    "test-connection")
        echo -e "${YELLOW}🔌 Running connection test...${NC}"
        docker exec -e DOCKER_CONTAINER=true horse_racing_ml_trainer_clean \
            python /app/tools/bulk_uploader/cli.py test-connection
        ;;
    
    "upload")
        DATA_PATH="$1"
        if [ -z "$DATA_PATH" ]; then
            echo -e "${RED}❌ Please specify data path${NC}"
            echo "Usage: $0 upload <data_path> [options]"
            exit 1
        fi
        
        echo -e "${YELLOW}📤 Running bulk upload for: $DATA_PATH${NC}"
        docker exec -e DOCKER_CONTAINER=true horse_racing_ml_trainer_clean \
            python /app/tools/bulk_uploader/cli.py upload "$DATA_PATH" "$@"
        ;;
    
    "validate")
        DATA_PATH="$1"
        if [ -z "$DATA_PATH" ]; then
            echo -e "${RED}❌ Please specify data path${NC}"
            echo "Usage: $0 validate <data_path> [options]"
            exit 1
        fi
        
        echo -e "${YELLOW}✅ Running validation for: $DATA_PATH${NC}"
        docker exec -e DOCKER_CONTAINER=true horse_racing_ml_trainer_clean \
            python /app/tools/bulk_uploader/cli.py validate "$DATA_PATH" "$@"
        ;;
    
    "status")
        echo -e "${YELLOW}📊 Checking upload status...${NC}"
        docker exec -e DOCKER_CONTAINER=true horse_racing_ml_trainer_clean \
            python /app/tools/bulk_uploader/cli.py status "$@"
        ;;
    
    "daily-processing")
        echo -e "${YELLOW}📅 Running daily data processing...${NC}"
        docker exec -e DOCKER_CONTAINER=true -e BULK_UPLOAD_MODE=daily_downloads horse_racing_ml_trainer_clean \
            python /app/tools/bulk_uploader/container_runner.py
        ;;
    
    "help"|"--help"|"-h"|"")
        echo -e "${BLUE}Bulk Uploader Docker Runner${NC}"
        echo ""
        echo "Usage: $0 <command> [options]"
        echo ""
        echo "Commands:"
        echo "  test-connection              Test database connection"
        echo "  upload <path> [options]      Upload files from path"
        echo "  validate <path> [options]    Validate files without uploading"
        echo "  status [options]             Show upload status"
        echo "  daily-processing             Process daily downloads"
        echo "  help                         Show this help"
        echo ""
        echo "Examples:"
        echo "  $0 test-connection"
        echo "  $0 upload /app/data/daily_downloads --verbose"
        echo "  $0 validate /app/data/daily_downloads --recursive"
        echo "  $0 daily-processing"
        ;;
    
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo "Use '$0 help' for available commands"
        exit 1
        ;;
esac

echo -e "${GREEN}🎉 Operation completed${NC}"
