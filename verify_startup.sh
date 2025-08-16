#!/bin/bash

echo "🚀 VERIFYING DOCKER SYSTEM STARTUP"
echo "=================================="

# Function to check service health
check_service() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    echo "Checking $service..."
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f docker-compose.clean.yml ps $service | grep -q "Up"; then
            echo "✅ $service is up (attempt $attempt)"
            return 0
        fi
        
        echo "⏳ Waiting for $service... (attempt $attempt/$max_attempts)"
        sleep 5
        ((attempt++))
    done
    
    echo "❌ $service failed to start after $max_attempts attempts"
    return 1
}

# Check each service
services=("postgres" "redis" "web-app" "data-pipeline" "ml-trainer")

echo "Starting all services..."
docker-compose -f docker-compose.clean.yml up -d

echo -e "\nWaiting for services to start..."
sleep 10

# Check each service
for service in "${services[@]}"; do
    check_service $service
done

echo -e "\n📊 Final Status:"
docker-compose -f docker-compose.clean.yml ps

echo -e "\n🔍 Quick Health Check:"
echo "======================="

# Test database connection
echo "Testing database connection..."
if docker-compose -f docker-compose.clean.yml exec -T postgres pg_isready -h localhost -p 5432; then
    echo "✅ PostgreSQL is ready"
else
    echo "❌ PostgreSQL not ready"
fi

# Test Redis connection  
echo "Testing Redis connection..."
if docker-compose -f docker-compose.clean.yml exec -T redis redis-cli ping; then
    echo "✅ Redis is ready"
else
    echo "❌ Redis not ready"
fi

echo -e "\n🎯 Startup verification complete!"
