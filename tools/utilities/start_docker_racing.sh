#!/bin/bash

# Horse Racing AI v2.0 - Docker Container Startup
# Starts the enhanced web application with racing analyzer in Docker

echo "🏇 ============================================================"
echo "   HORSE RACING AI v2.0 - DOCKER STARTUP"
echo "=============================================================="
echo ""
echo "🐋 STARTING DOCKER CONTAINERS..."
echo "   📦 PostgreSQL Database"
echo "   📦 Redis Cache"
echo "   📦 Enhanced Web Application"
echo "   📦 Racing Media Analyzer"
echo "   📦 NTFY Notifications"
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

# Set environment variables
export POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-secure_password_123}
export REDIS_PASSWORD=${REDIS_PASSWORD:-redis_password_123}
export DEBUG=${DEBUG:-false}
export LOG_LEVEL=${LOG_LEVEL:-INFO}

# Ollama configuration (assumes Ollama is running on host)
export OLLAMA_HOST=${OLLAMA_HOST:-host.docker.internal:11434}
export OLLAMA_MODEL=${OLLAMA_MODEL:-jimscard/whiterabbit-neo:13b-q5_K_M}
export RACING_ANALYZER_TIMEOUT=${RACING_ANALYZER_TIMEOUT:-300}

echo "🔧 Environment configuration:"
echo "   🗄️  Database: PostgreSQL on port 5433"
echo "   🔴 Cache: Redis"
echo "   🤖 Ollama: ${OLLAMA_HOST}"
echo "   📊 Web App: http://localhost:5002"
echo ""

# Build and start containers
echo "🚀 Building and starting containers..."
docker-compose up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

# Check service status
echo "📊 Checking service status..."
docker-compose ps

echo ""
echo "✅ DOCKER CONTAINERS STARTED!"
echo "=============================================================="
echo "🌐 Web Application: http://localhost:5002"
echo "🐦 Racing Analyzer: http://localhost:5002/racing_analyzer"
echo "🗄️  Database Admin: http://localhost:5050"
echo "📢 Notifications: http://localhost:8081"
echo "=============================================================="
echo ""
echo "📝 To check logs:"
echo "   docker-compose logs -f horse-racing-ai"
echo ""
echo "🛑 To stop containers:"
echo "   docker-compose down"
echo ""
echo "🔄 To restart containers:"
echo "   docker-compose restart"
echo ""

# Show container logs for a few seconds
echo "📋 Recent logs from web application:"
echo "------------------------------------------------------------"
docker-compose logs --tail=20 horse-racing-ai
echo "------------------------------------------------------------"
echo ""
echo "🎉 Setup complete! The racing analyzer should work with"
echo "   Ollama running on your host system at ${OLLAMA_HOST}"
