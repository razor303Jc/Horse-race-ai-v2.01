#!/bin/bash
# Enable ML Service Script
# ========================

echo "🧠 ENABLING ML SERVICE"
echo "====================="

echo "📋 Starting ML trainer service..."
docker-compose -f docker-compose.clean.yml up -d ml-trainer

echo "⏳ Waiting 30 seconds for ML service to start..."
sleep 30

echo "📊 Checking ML service status..."
docker-compose -f docker-compose.clean.yml ps ml-trainer

echo "🔍 Checking ML service logs..."
docker-compose -f docker-compose.clean.yml logs --tail=10 ml-trainer

echo "✅ ML service startup attempted - check logs above for status"
