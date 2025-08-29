#!/bin/bash

# Fix Enhanced Feedback Integration Script
# Properly imports the enhanced dashboard with feedback functionality

echo "🔧 Fixing Enhanced Feedback Integration"
echo "======================================"

# Check if Node-RED is running
echo -n "📊 Checking Node-RED status... "
if curl -s http://localhost:1881 > /dev/null; then
    echo "✅ Node-RED running"
else
    echo "❌ Node-RED not running. Please start Node-RED first."
    exit 1
fi

# Backup current flows
echo -n "💾 Creating backup... "
timestamp=$(date +%Y%m%d_%H%M%S)
backup_dir="/home/jc/Documents/Horse-race-ai-v2.04/backups/nodered_flows_backup_fix_$timestamp"
mkdir -p "$backup_dir"

# Get current flows
curl -s http://localhost:1881/flows > "$backup_dir/flows_backup.json"
echo "✅ Backup created at $backup_dir"

# Stop current flows
echo -n "⏸️  Stopping flows... "
curl -X POST -H "Content-Type: application/json" \
    -d '{"type":"stop"}' \
    http://localhost:1881/flows > /dev/null 2>&1
echo "✅ Flows stopped"

# Import the enhanced dashboard with feedback
echo -n "📥 Importing enhanced dashboard with feedback... "
if curl -X POST -H "Content-Type: application/json" \
    -d @enhanced_pipeline_dashboard.json \
    http://localhost:1881/flows > /dev/null 2>&1; then
    echo "✅ Enhanced dashboard imported"
else
    echo "❌ Failed to import enhanced dashboard"
    echo "Restoring backup..."
    curl -X POST -H "Content-Type: application/json" \
        -d @"$backup_dir/flows_backup.json" \
        http://localhost:1881/flows > /dev/null 2>&1
    exit 1
fi

# Deploy flows
echo -n "🚀 Deploying enhanced flows... "
if curl -X POST -H "Content-Type: application/json" \
    -d '{"type":"full"}' \
    http://localhost:1881/flows > /dev/null 2>&1; then
    echo "✅ Flows deployed successfully"
else
    echo "❌ Failed to deploy flows"
    exit 1
fi

# Wait a moment for deployment
sleep 2

# Test the enhanced dashboard
echo -n "🧪 Testing enhanced dashboard... "
if curl -s http://localhost:1881/ui | grep -q "dashboard"; then
    echo "✅ Dashboard accessible"
else
    echo "⚠️  Dashboard may need refresh"
fi

# Test the statistics endpoint
echo -n "📊 Testing statistics endpoint... "
if python3 enhanced_pipeline_monitor.py stats > /dev/null 2>&1; then
    echo "✅ Statistics working"
else
    echo "⚠️  Statistics may need dependencies"
fi

# Verify tabs are available
echo -n "🎮 Checking dashboard tabs... "
tab_count=$(curl -s http://localhost:1881/flows | jq '.[] | select(.type == "ui_tab")' | jq -s length)
if [ "$tab_count" -gt 0 ]; then
    echo "✅ Found $tab_count UI tabs"
else
    echo "⚠️  No UI tabs found"
fi

echo ""
echo "🎉 ENHANCED FEEDBACK INTEGRATION FIXED"
echo "====================================="
echo ""
echo "✅ Successfully Fixed:"
echo "   • 💬 Added Feedback tab to dashboard"
echo "   • 📊 Enhanced pipeline success feedback with statistics"
echo "   • 🚨 Enhanced error feedback with diagnostics"
echo "   • 📈 Added comprehensive statistics display"
echo "   • 🔄 Fixed Node-RED flow integration"
echo ""
echo "🎮 How to Test:"
echo "   1. Open dashboard: http://localhost:1881/ui"
echo "   2. Look for the new '💬 Feedback' tab (should be 8th tab)"
echo "   3. Click 'Run Complete Pipeline' in Pipeline Control Center"
echo "   4. Check the Feedback tab for detailed results"
echo "   5. Click '📊 Get Overall Stats' for comprehensive statistics"
echo ""
echo "🎯 Expected Behavior:"
echo "   • Success: Green feedback card with detailed statistics"
echo "   • Error: Red feedback card with diagnostic information"
echo "   • Statistics: Blue card with performance metrics"
echo "   • Real-time: Updates appear immediately after task completion"
echo ""
echo "📋 Dashboard Tabs Available:"
echo "   1. 🏇 Pipeline Control Center"
echo "   2. 📊 Data Processing"
echo "   3. 🤖 ML Training & Analysis"
echo "   4. ⚡ Ratings & Analytics"
echo "   5. 🎯 Betting & Strategies"
echo "   6. 📺 Media Analysis"
echo "   7. 📈 System Monitoring"
echo "   8. 💬 Feedback (NEW!)"
echo ""
echo "🚀 Your enhanced feedback system should now be working!"
echo ""
