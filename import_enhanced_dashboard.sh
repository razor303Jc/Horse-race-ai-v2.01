#!/bin/bash

echo "🚀 Importing Enhanced Pipeline Dashboard with Comprehensive Logging"
echo "=================================================================="

# Create logs directory if it doesn't exist
mkdir -p /home/jc/Documents/Horse-race-ai-v2.04/logs

# Set up log files with proper permissions
touch /home/jc/Documents/Horse-race-ai-v2.04/logs/nodered_pipeline.log
touch /home/jc/Documents/Horse-race-ai-v2.04/logs/data_processing.log
touch /home/jc/Documents/Horse-race-ai-v2.04/logs/ml_training.log
touch /home/jc/Documents/Horse-race-ai-v2.04/logs/betting_analysis.log
touch /home/jc/Documents/Horse-race-ai-v2.04/logs/performance_tracking.log

echo "✅ Log files created and configured"

# Check if Node-RED is running
if ! curl -s http://localhost:1881 > /dev/null; then
    echo "❌ Node-RED is not running on port 1881"
    echo "   Please start Node-RED first"
    exit 1
fi

echo "✅ Node-RED is running"

# Import the enhanced dashboard flows
echo "📤 Importing enhanced pipeline dashboard flows..."

if [ -f "enhanced_pipeline_dashboard.json" ]; then
    curl -X POST http://localhost:1881/flows \
        -H "Content-Type: application/json" \
        -d @enhanced_pipeline_dashboard.json
    
    if [ $? -eq 0 ]; then
        echo "✅ Enhanced dashboard imported successfully!"
        echo ""
        echo "🎯 Enhanced Dashboard Features:"
        echo "==============================================="
        echo "🏇 Pipeline Control Center - Complete pipeline automation"
        echo "📊 Data Processing - Validation, processing, uploading"
        echo "🤖 ML Training & Analysis - Model training, Monte Carlo, AI selections"
        echo "⚡ Ratings & Analytics - Power ratings, speed ratings, form scoring"
        echo "🎯 Betting & Strategies - Live betting, strategies, staking, risk assessment"
        echo "📺 Media Analysis - News integration, sentiment analysis"
        echo "📈 System Monitoring - Real-time logs, performance metrics"
        echo ""
        echo "🔧 Advanced Features Included:"
        echo "- Comprehensive logging to files"
        echo "- Real-time pipeline monitoring"
        echo "- Error handling and alerts"
        echo "- Performance tracking"
        echo "- Emergency stop functionality"
        echo "- Advanced mathematical models integration"
        echo ""
        echo "📋 Next Steps:"
        echo "1. Go to Node-RED: http://localhost:1881"
        echo "2. Click 'Deploy' (red button)"
        echo "3. Visit Enhanced Dashboard: http://localhost:1881/ui"
        echo "4. Test individual pipeline components"
        echo "5. Monitor logs in real-time"
        echo ""
        echo "🎉 Your enhanced Horse Racing AI pipeline dashboard is ready!"
    else
        echo "❌ Import failed - try manual import"
    fi
else
    echo "❌ enhanced_pipeline_dashboard.json not found"
    exit 1
fi
