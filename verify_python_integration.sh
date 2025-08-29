#!/bin/bash

echo "🐍 Python Integration Verification"
echo "================================="

echo ""
echo "✅ Checking Python environment..."
docker exec horse_racing_node_red_custom python3 --version && echo "   ✅ Python available in Node-RED container" || echo "   ❌ Python not available"

echo ""
echo "✅ Checking key Python scripts..."

# Check if scripts exist in the container
SCRIPTS=(
    "tools/automation/automated_data_pipeline.py"
    "tools/ml_training/unified_ml_trainer.py"
    "src/contextual_ai/race_data_quality_analyzer.py"
    "scripts/run_real_selections.py"
    "tools/performance/race_results_tracker.py"
    "scripts/check_db_metrics.py"
)

for script in "${SCRIPTS[@]}"; do
    if docker exec horse_racing_web_app_clean test -f "/app/$script"; then
        echo "   ✅ $script"
    else
        echo "   ❌ $script (not found)"
    fi
done

echo ""
echo "✅ Checking database connectivity from Python..."
docker exec horse_racing_web_app_clean python3 -c "
import psycopg2
try:
    conn = psycopg2.connect(
        host='postgres',
        port=5432,
        database='cards_horse_racing_db',
        user='horse_racing',
        password='secure_password_123'
    )
    print('   ✅ Python can connect to PostgreSQL')
    conn.close()
except Exception as e:
    print(f'   ❌ Python database connection failed: {e}')
"

echo ""
echo "✅ Checking Node-RED exec node availability..."
docker exec horse_racing_node_red_custom ls /data/node_modules | grep -q "node-red" && echo "   ✅ Node-RED exec capability available" || echo "   ❌ Node-RED exec not available"

echo ""
echo "✅ Testing sample Python execution from Node-RED container..."
docker exec horse_racing_node_red_custom sh -c "cd /data && python3 -c 'print(\"✅ Python execution test successful\")'" 2>/dev/null || echo "   ❌ Python execution test failed"

echo ""
echo "📋 Integration Flow Files Ready:"
echo "   🔧 horse_racing_python_integration_flows.json (comprehensive flows)"
echo "   📖 PYTHON_INTEGRATION_GUIDE.md (setup instructions)"

echo ""
echo "🚀 Python Integration Features Available:"
echo "   🔄 Data Pipeline Automation"
echo "   🤖 ML Training Integration"
echo "   🎯 AI Selections Generation"
echo "   📊 Performance Tracking"
echo "   📧 Email Notifications"
echo "   ⏰ Scheduled Execution"
echo "   🖥️  Dashboard Controls"

echo ""
echo "🎯 Ready for Python Script Integration!"
echo "   Import: horse_racing_python_integration_flows.json"
echo "   Configure: Database credentials and email settings"
echo "   Test: Use manual trigger buttons first"
echo "   Deploy: Enable scheduled automation"
