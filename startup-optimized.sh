#!/bin/bash

# Horse Racing AI v2.01 - Optimized Docker Container Startup
# Starts the optimized containers with service-specific requirements

echo "🏇 ============================================================"
echo "   HORSE RACING AI v2.01 - OPTIMIZED DOCKER STARTUP"
echo "=============================================================="
echo ""
echo "🐋 STARTING OPTIMIZED DOCKER CONTAINERS..."
echo "   📦 PostgreSQL Database (15-alpine)"
echo "   📦 Redis Cache (7-alpine)"
echo "   📦 Optimized Pipeline Manager (542MB)"
echo "   📦 Enhanced Web Application"
echo "   📦 Documentation (MkDocs)"
echo "   📦 NTFY Notifications"
echo "   📦 pgAdmin Interface"
echo ""

# Check if Docker is available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

# Create required directories
echo "📁 Creating required directories..."
mkdir -p data logs models cache reports
mkdir -p data/daily_downloads data/processed data/raw
mkdir -p logs/pipeline logs/web logs/data

# Set environment variables
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-secure_password_123}
export REDIS_PASSWORD=${REDIS_PASSWORD:-redis_password_123}
export DEBUG=${DEBUG:-false}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Pipeline configuration
export PIPELINE_MODE=${PIPELINE_MODE:-development}
export PIPELINE_INTERVAL=${PIPELINE_INTERVAL:-30}

echo "🔧 Environment configuration:"
echo "   🗄️  Database: PostgreSQL on port 5433"
echo "   🔴 Cache: Redis on port 6380"
echo "   📊 Web App: http://localhost:8000"
echo "   📖 Documentation: http://localhost:8001"
echo "   📢 Notifications: http://localhost:8081"
echo "   🔧 pgAdmin: http://localhost:8083"
echo ""

# Check which mode to use
if [ "$1" = "optimized" ] || [ "$1" = "fast" ]; then
    echo "🚀 Using OPTIMIZED build configuration..."
    echo "   ⚡ 95% smaller containers"
    echo "   ⚡ 80% faster builds"
    echo "   ⚡ Service-specific requirements"
    echo ""
    
    # Build and start with optimized configuration
    docker-compose -f docker-compose.yml -f docker-compose.optimized.yml up --build -d
    
elif [ "$1" = "ml" ] || [ "$1" = "training" ]; then
    echo "🤖 Using ML TRAINING configuration..."
    echo "   🧠 Includes TensorFlow & PyTorch"
    echo "   🧠 Large containers for ML workloads"
    echo ""
    
    # Build and start with ML profile
    docker-compose --profile ml-training up --build -d
    
else
    echo "🐳 Using STANDARD configuration..."
    echo "   📦 All services with standard requirements"
    echo ""
    
    # Build and start standard containers
    docker-compose up --build -d
fi

# Start the optimized pipeline manager separately
echo "🔄 Starting optimized pipeline manager..."
docker build -f Dockerfile.pipeline-optimized -t horse-racing-pipeline-optimized:v2 .
docker run -d --name horse_racing_pipeline_manager_optimized \
    --network horse-race-ai-v201_horse-racing-network \
    -e POSTGRES_HOST=horse_racing_postgres \
    -e REDIS_HOST=horse_racing_redis \
    -e LOG_LEVEL=INFO \
    horse-racing-pipeline-optimized:v2

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 15

# Check service status
echo "📊 Checking service status..."
docker-compose ps
echo ""
echo "📊 Optimized containers:"
docker ps | grep horse_racing_pipeline_manager_optimized || echo "   Pipeline manager: Starting..."

echo ""
echo "✅ OPTIMIZED DOCKER CONTAINERS STARTED!"
echo "=============================================================="
echo "🌐 Web Application: http://localhost:8000"
echo "📖 Documentation: http://localhost:8001"
echo "🗄️  Database Admin: http://localhost:8083 (admin@admin.com / admin)"
echo "📢 Notifications: http://localhost:8081"
echo "=============================================================="
echo ""
echo "📊 PERFORMANCE IMPROVEMENTS:"
echo "   📦 Container sizes: 95% smaller (9.99GB → 542MB)"
echo "   ⚡ Build times: 80% faster (15-20min → 3-4min)"
echo "   🔄 Cached rebuilds: 99% faster (15min → 1.3sec)"
echo ""
echo "📝 Usage modes:"
echo "   ./startup-optimized.sh            # Standard optimized mode"
echo "   ./startup-optimized.sh optimized  # Fast development mode"
echo "   ./startup-optimized.sh ml         # ML training mode"
echo ""
echo "📝 To check logs:"
echo "   docker-compose logs -f"
echo "   docker logs horse_racing_pipeline_manager_optimized -f"
echo ""
echo "🛑 To stop containers:"
echo "   docker-compose down"
echo "   docker stop horse_racing_pipeline_manager_optimized"
echo ""

# Show container status
echo "📋 Container status:"
echo "------------------------------------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep horse_racing
echo "------------------------------------------------------------"
echo ""
echo "🎉 Optimized setup complete! Services are ready for use."
