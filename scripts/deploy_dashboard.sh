#!/bin/bash

# Simple Flow Deployment Script
echo "🚀 Deploying Enhanced Dashboard Flows"
echo "=================================="

# Check Node-RED status
echo -n "📊 Checking Node-RED... "
if curl -s http://localhost:1881 > /dev/null; then
    echo "✅ Running"
else
    echo "❌ Not running"
    exit 1
fi

# Deploy flows
echo -n "📥 Deploying flows... "
response=$(curl -s -X POST -H "Content-Type: application/json" \
    --data-binary @enhanced_pipeline_dashboard.json \
    http://localhost:1881/flows)

if echo "$response" | grep -q "error"; then
    echo "❌ Failed"
    echo "Error: $response"
    exit 1
else
    echo "✅ Success"
fi

# Test dashboard
echo -n "🎮 Testing dashboard... "
sleep 2
dashboard_content=$(curl -s http://localhost:1881/ui/)
if echo "$dashboard_content" | grep -q "Node-RED Dashboard"; then
    echo "✅ Accessible"
else
    echo "⚠️  May need refresh"
fi

# Check tabs
echo -n "📋 Checking tabs... "
tabs=$(curl -s http://localhost:1881/flows | jq '.[] | select(.type == "ui_tab") | .name' | wc -l)
echo "✅ Found $tabs tabs"

echo ""
echo "🎉 DEPLOYMENT COMPLETE"
echo "===================="
echo "Dashboard: http://localhost:1881/ui/"
echo "Tabs available: $tabs"
echo ""
