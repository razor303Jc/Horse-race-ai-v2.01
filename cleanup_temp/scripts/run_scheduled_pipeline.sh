#!/bin/bash
# Scheduled Pipeline Runner for 11:30 AM
# This script runs the complete horseracedatabase download and ML pipeline

echo "🏇 Starting Scheduled Horse Racing Pipeline at $(date)"
echo "=============================================="

cd /home/jc/Documents/Horse-race-ai-v2.0

# Check if Docker services are running
echo "🐳 Checking Docker services..."
docker-compose ps

# Run the complete racing pipeline
echo "🚀 Starting complete racing pipeline..."
python demos/complete_racing_pipeline.py

echo "✅ Scheduled pipeline completed at $(date)"
