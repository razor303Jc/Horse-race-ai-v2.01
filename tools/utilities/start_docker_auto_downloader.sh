#!/bin/bash

# Start Docker Auto Downloader Script
# ==================================

echo "🐳 Starting Horse Racing Auto Downloader in Docker"

# Set proper permissions for data directories
chmod -R 777 ./data/daily_downloads/ 2>/dev/null || true
chmod -R 777 ./logs/ 2>/dev/null || true

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env file with your horseracedatabase.com credentials:"
    echo "HORSERACE_DB_USERNAME=your_username"
    echo "HORSERACE_DB_PASSWORD=your_password"
    echo "HORSERACE_DB_RESULTS_URL=your_results_url"
    echo "HORSERACE_DB_CARDS_URL=your_cards_url"
    exit 1
fi

# Load environment variables
set -a
source .env
set +a

echo "✅ Environment loaded"

# Run the auto downloader
echo "🚀 Starting auto downloader..."
docker-compose -f docker-compose.auto-downloader.yml run --rm auto-downloader python run_docker_auto_downloader.py --mode once

echo "🏁 Auto downloader completed"
