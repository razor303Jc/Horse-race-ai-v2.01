#!/bin/bash

# Test Data Generation Script for Horse Racing AI v2.0
# Generates 50,000 races with complete test data in Docker test environment

set -e

echo "🚀 Horse Racing AI v2.0 - Test Data Generation"
echo "============================================="
echo "🎯 Target: 50,000 races with complete racing data"
echo "📦 Environment: Docker test containers"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start test database containers
echo "🐳 Starting test database containers..."
docker-compose -f docker-compose.test.yml up -d postgres-test

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check database connection
echo "🔍 Checking database connection..."
DB_URL="postgresql://horse_racing_test:test_password_123@localhost:5434/horse_racing_test_db"

# Test connection
if python3 -c "import psycopg2; psycopg2.connect('$DB_URL'); print('✅ Database connection successful')" 2>/dev/null; then
    echo "✅ Database is ready"
else
    echo "❌ Database connection failed. Waiting longer..."
    sleep 20
    if ! python3 -c "import psycopg2; psycopg2.connect('$DB_URL')" 2>/dev/null; then
        echo "❌ Database still not ready. Check Docker logs:"
        docker-compose -f docker-compose.test.yml logs postgres-test
        exit 1
    fi
fi

# Install required Python packages if not already installed
echo "📦 Installing required Python packages..."
pip install psycopg2-binary > /dev/null 2>&1 || echo "⚠️ psycopg2-binary may already be installed"

# Generate test data
echo ""
echo "🎲 Starting massive test data generation..."
echo "📊 This will create:"
echo "   • 50,000 races across 5 years"
echo "   • 15,000 unique horses"
echo "   • 800 jockeys"
echo "   • 1,200 trainers"
echo "   • ~600,000 race entries"
echo "   • ~200,000 race results"
echo ""

# Run the data generator
python3 tests/test_data_generator.py \
    --races 50000 \
    --database-url "$DB_URL"

echo ""
echo "🎉 TEST DATA GENERATION COMPLETE!"
echo "=================================="
echo "✅ Test database is now populated with massive dataset"
echo "🔗 Database URL: $DB_URL"
echo "📊 Ready for comprehensive testing of:"
echo "   • Horse Racing AI algorithms"
echo "   • Database performance"
echo "   • Query optimization"
echo "   • Machine learning training"
echo "   • Monte Carlo simulations"
echo ""
echo "🛠️ Next steps:"
echo "   1. Run integration tests against test data"
echo "   2. Test machine learning models"
echo "   3. Validate AI performance metrics"
echo "   4. Benchmark database queries"
echo ""
echo "🐳 Test containers running:"
echo "   • PostgreSQL: localhost:5434"
echo "   • Database: horse_racing_test_db"
echo "   • User: horse_racing_test"
echo ""
echo "🧹 To stop test containers:"
echo "   docker-compose -f docker-compose.test.yml down"
