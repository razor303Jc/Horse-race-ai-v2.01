#!/bin/bash

# Quick Demo: Weekly Race Cards with Daily Release
# This demonstrates the 7-day progressive race card system

echo "🏁 WEEKLY RACE CARDS DEMO"
echo "========================="
echo ""
echo "This demo shows how we can generate and release a full week's worth"
echo "of race cards, with each day's races being released progressively."
echo ""

# Set up environment
export DATABASE_URL="postgresql://postgres:password@postgres:5432/horse_racing_test_db"

# Check database
echo "🔍 Checking test database..."
if ! docker-compose -f docker-compose.test.yml ps | grep -q postgres; then
    echo "🚀 Starting test database..."
    docker-compose -f docker-compose.test.yml up -d postgres
    sleep 8
fi

echo "✅ Database ready"
echo ""

# Demo 1: Quick weekly generation (instant)
echo "📊 DEMO 1: Quick Weekly Generation"
echo "===================================="
echo "Generating a complete week of race cards instantly..."

python3 tests/weekly_race_cards_generator.py --days 7

echo ""
echo "✅ Complete week generated!"
echo ""

# Demo 2: Daily progressive release simulation
echo "📅 DEMO 2: Daily Progressive Release Simulation"
echo "==============================================="
echo "Simulating daily race card releases over 7 days (with 2-second delays)..."
echo ""

python3 tests/daily_race_simulator.py \
    --week-start $(date +%Y-%m-%d) \
    --simulate-days 7 \
    --delay 2

echo ""
echo "✅ Progressive simulation complete!"
echo ""

# Demo 3: Status and summary
echo "📈 DEMO 3: Status and Summary"
echo "============================="

echo "Current week status:"
python3 tests/daily_race_simulator.py --status

echo ""
echo "Released races summary:"
python3 tests/daily_race_simulator.py --summary

echo ""
echo "🎯 DEMO COMPLETE!"
echo "================"
echo ""
echo "What was demonstrated:"
echo "1. ✅ Complete weekly race card generation (50+ races per day)"
echo "2. ✅ Progressive daily race release simulation"
echo "3. ✅ Realistic UK/Irish racing data with proper scheduling"
echo "4. ✅ Status tracking and progress monitoring"
echo "5. ✅ Full integration with test database"
echo ""
echo "The system is now ready for comprehensive testing with:"
echo "- Realistic racing schedules (Monday-Sunday patterns)"
echo "- Progressive data availability testing"
echo "- Daily processing workflow validation"
echo "- Monte Carlo + Fast Results + NTFY integration testing"
echo ""
echo "Database: postgresql://postgres:password@postgres:5432/horse_racing_test_db"
