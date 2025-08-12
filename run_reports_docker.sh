#!/bin/bash
# Quick setup script to run comprehensive reports with Docker

echo "🚀 Horse Racing AI Pipeline - Reports Setup"
echo "============================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "📊 Setting up comprehensive reporting environment..."

# Build the reports service specifically
echo "🔨 Building reports container..."
docker build -f Dockerfile.reports -t horse-racing-reports .

# Run the reports container
echo "📈 Running comprehensive pipeline reports..."
docker run --rm \
    --name horse-racing-reports-run \
    --network horse_racing_network \
    -v "$(pwd)/reports:/app/reports" \
    -v "$(pwd)/data:/app/data" \
    -v "$(pwd)/tools:/app/tools" \
    -v "$(pwd)/experiments:/app/experiments" \
    -e DATABASE_URL="postgresql://horse_racing:secure_password_123@horse_racing_postgres:5432/horse_racing_db" \
    -e PYTHONPATH="/app" \
    horse-racing-reports python reports/comprehensive_pipeline_report.py

echo "✅ Reports generation complete!"
echo "📁 Check the reports/ directory for generated files"

# Optional: Start a simple HTTP server to view reports
read -p "🌐 Start web server to view reports? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌐 Starting web server at http://localhost:8888"
    echo "💡 Press Ctrl+C to stop the server"
    cd reports && python -m http.server 8888
fi
