#!/bin/bash

# Horse Racing AI v2.0 - Enhanced Web Application Startup Script
# Comprehensive web GUI with ALL system integrations

echo "🏇 ============================================================"
echo "   HORSE RACING AI v2.0 - ENHANCED WEB APPLICATION"
echo "=============================================================="
echo ""
echo "🤖 SYSTEM FEATURES:"
echo "   ✅ Advanced ML Models (76.5% AUC)"
echo "   ✅ 4-Model Ensemble (RF, GB, LR, NN)"
echo "   ✅ 32-Factor Contextual AI Enhancement"
echo "   ✅ Professional BETDAQ Integration"
echo "   ✅ Real-time Performance Tracking"
echo "   ✅ Comprehensive Analytics Dashboard"
echo "   ✅ Live Race Analysis & Predictions"
echo "   ✅ Advanced Betting Strategies"
echo "   ✅ Risk Management & Bankroll Protection"
echo ""
echo "🌐 STARTING ENHANCED WEB APPLICATION..."
echo "   📍 URL: http://localhost:5002"
echo "   📊 Dashboard: Real-time system monitoring"
echo "   🔄 Auto-refresh: 30-second updates"
echo ""

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if required packages are installed
echo "🔍 Checking dependencies..."
python3 -c "import flask, pandas, numpy, sklearn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing required packages..."
    pip3 install -r requirements.txt
fi

echo "🚀 Launching application..."
echo ""

# Start the enhanced web application
python3 app.py

echo ""
echo "🏁 Application has stopped."
echo "Thank you for using Horse Racing AI v2.0!"
