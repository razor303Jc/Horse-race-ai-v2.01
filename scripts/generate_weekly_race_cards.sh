#!/bin/bash

# Weekly Race Cards Generation Script
# Generates a full week's worth of race cards with daily release simulation

echo "🏁 Starting Weekly Race Cards Generation"
echo "======================================="

# Set up environment
export DATABASE_URL="postgresql://postgres:password@localhost:5434/horse_racing_test_db"

# Check if test database is running
echo "🔍 Checking test database connection..."
docker-compose -f docker-compose.test.yml ps | grep postgres

if [ $? -ne 0 ]; then
    echo "⚠️ Test database not running. Starting..."
    docker-compose -f docker-compose.test.yml up -d postgres
    echo "⏳ Waiting for database to be ready..."
    sleep 10
fi

# Default to today's date for the week start
START_DATE=${1:-$(date +%Y-%m-%d)}
DAYS=${2:-7}

echo "📅 Generating weekly race cards starting: $START_DATE"
echo "🗓️ Days to simulate: $DAYS"

# Run the weekly race cards generator
python3 tests/weekly_race_cards_generator.py \
    --start-date "$START_DATE" \
    --days "$DAYS"

echo ""
echo "✅ Weekly race cards generation complete!"
echo ""
echo "To check status of the week:"
echo "python3 tests/weekly_race_cards_generator.py --start-date $START_DATE --status-only"
echo ""
echo "Database available at: postgresql://postgres:password@localhost:5434/horse_racing_test_db"
