#!/bin/bash

# Quick setup script for Horse Base web scraping integration
echo "🏇 Horse Race Handicapping AI - Quick Setup"
echo "=========================================="

# Navigate to the horse-bot directory
cd "$(dirname "$0")"

# Check if we're in the right place
if [ ! -f "setup_dev.sh" ]; then
    echo "❌ Error: Please run this script from the horse-bot directory"
    exit 1
fi

echo "📋 Setting up Horse Base integration with provided credentials..."

# Copy environment template with pre-filled credentials
if [ ! -f ".env" ]; then
    echo "🔧 Creating .env file with Horse Base credentials..."
    cp .env.template .env
    echo "✅ .env file created with credentials: raxor303 / horse"
else
    echo "✅ .env file already exists"
fi

# Make setup script executable and run it
echo "🔧 Running development environment setup..."
chmod +x setup_dev.sh
./setup_dev.sh

# Test the Horse Base connection
echo ""
echo "🔄 Testing Horse Base web scraping connection..."
python test_horse_base.py

# Run validation
echo ""
echo "🔍 Running code validation..."
python validate_setup.py

echo ""
echo "🎉 Setup complete! Next steps:"
echo "   1. Check that Horse Base login worked above"
echo "   2. Run: uvicorn src.main:app --reload"
echo "   3. Visit: http://localhost:8000/docs"
echo "   4. Test: curl http://localhost:8000/health/detailed"
echo ""
echo "📝 Important notes:"
echo "   - Horse Base uses web scraping (not API)"
echo "   - Test account: raxor303 / horse" 
echo "   - Rate limited to 1 request per 2 seconds"
echo "   - Check TODO/CRITICAL-TODOS.md for next tasks"
