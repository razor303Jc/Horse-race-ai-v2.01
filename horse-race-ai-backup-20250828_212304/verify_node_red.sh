#!/bin/bash

# 🏇 Node-RED Package Verification Script
echo "🚀 Verifying Node-RED packages and connections..."

echo "📦 Checking installed Node-RED packages..."
docker exec horse_racing_node_red_custom ls /data/node_modules | grep -E "(dashboard|cron|email|postgres|moment|ui-led)" | while read package; do
    echo "  ✅ $package"
done

echo ""
echo "🔌 Testing database connectivity from Node-RED..."
docker exec horse_racing_node_red_custom sh -c "
echo 'Testing PostgreSQL connection...'
nc -z host.docker.internal 5432 && echo '✅ PostgreSQL reachable' || echo '❌ PostgreSQL not reachable'
"

echo ""
echo "🌐 Checking Node-RED service status..."
curl -s http://localhost:1881/red/nodes | grep -q "node-red-dashboard" && echo "✅ Dashboard package loaded" || echo "❌ Dashboard package not loaded"

echo ""
echo "📊 Opening Node-RED interfaces..."
echo "🔗 Node-RED Editor: http://localhost:1881"
echo "🔗 Node-RED Dashboard: http://localhost:1881/ui"

echo ""
echo "🎯 Ready to import automation flows!"
echo "   File to import: horse_racing_automation_flows.json"
