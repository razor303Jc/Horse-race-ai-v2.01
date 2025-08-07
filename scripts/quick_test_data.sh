#!/bin/bash

# Quick Test Data Generation - 1000 races for initial testing

set -e

echo "🚀 Horse Racing AI v2.0 - Quick Test Data Generation"
echo "=================================================="
echo "🎯 Target: 1,000 races for quick testing"
echo "📦 Environment: Docker test containers"
echo ""

# Start test database containers
echo "🐳 Starting test database containers..."
docker-compose -f docker-compose.test.yml up -d postgres-test

# Wait for database to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Check database connection
DB_URL="postgresql://horse_racing_test:test_password_123@localhost:5434/horse_racing_test_db"

echo "🔍 Testing database connection..."
python3 -c "
import psycopg2
try:
    conn = psycopg2.connect('$DB_URL')
    print('✅ Database connection successful')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

# Install required packages
echo "📦 Installing required Python packages..."
pip install psycopg2-binary

# Generate quick test data
echo ""
echo "🎲 Generating quick test dataset..."
echo "📊 Creating 1,000 races with all related data..."

python3 tests/test_data_generator.py --quick --database-url "$DB_URL"

echo ""
echo "🎉 QUICK TEST DATA READY!"
echo "========================"
echo "✅ Test database populated with sample dataset"
echo "🔗 Database: $DB_URL"
echo "📊 Ready for initial testing"
echo ""
echo "🧪 To run full 50K race generation:"
echo "   ./scripts/generate_test_data.sh"
