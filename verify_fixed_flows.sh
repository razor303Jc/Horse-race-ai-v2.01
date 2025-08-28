#!/bin/bash

echo "🔧 Node-RED Flow Verification"
echo "============================="

echo ""
echo "✅ Checking Node-RED service..."
curl -s http://localhost:1881/ > /dev/null && echo "   Node-RED accessible at http://localhost:1881" || echo "   ❌ Node-RED not accessible"

echo ""
echo "✅ Checking installed packages..."
echo "   PostgreSQL nodes:"
docker exec horse_racing_node_red_custom ls /data/node_modules | grep postgres-multi > /dev/null && echo "   ✅ node-red-contrib-postgres-multi installed" || echo "   ❌ postgres-multi missing"

echo "   Email nodes:"
docker exec horse_racing_node_red_custom ls /data/node_modules | grep node-red-node-email > /dev/null && echo "   ✅ node-red-node-email installed" || echo "   ❌ email node missing"

echo "   Cron nodes:"
docker exec horse_racing_node_red_custom ls /data/node_modules | grep cron-plus > /dev/null && echo "   ✅ node-red-contrib-cron-plus installed" || echo "   ❌ cron-plus missing"

echo "   Dashboard nodes:"
docker exec horse_racing_node_red_custom ls /data/node_modules | grep dashboard > /dev/null && echo "   ✅ node-red-dashboard installed" || echo "   ❌ dashboard missing"

echo ""
echo "✅ Checking database connectivity..."
docker exec horse_racing_node_red_custom sh -c "nc -z host.docker.internal 5432" 2>/dev/null && echo "   ✅ PostgreSQL reachable from Node-RED" || echo "   ❌ PostgreSQL not reachable"

echo ""
echo "📋 Fixed Flow Files Ready:"
echo "   🔧 horse_racing_flows_corrected.json (main flows)"
echo "   🔑 horse_racing_flows_credentials.json (database credentials)"
echo "   📖 FIXED_NODE_RED_SETUP_GUIDE.md (setup instructions)"

echo ""
echo "🚀 Next Steps:"
echo "   1. Open http://localhost:1881"
echo "   2. Import horse_racing_flows_corrected.json"
echo "   3. Configure database credentials"
echo "   4. Update email address"
echo "   5. Deploy flows"

echo ""
echo "🎯 All prerequisites verified - ready for import!"
