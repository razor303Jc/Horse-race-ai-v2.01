#!/bin/bash
# Docker Test Runner for Race Card Upload Success
# Runs the test inside Docker container with proper database access

echo "🐳 Running Race Card Upload Test in Docker Container"
echo "=================================================="

# Run the test inside the ML trainer container where it has database access
docker exec -it horse_racing_ml_trainer_clean python /app/tests/test_race_card_upload_success.py
