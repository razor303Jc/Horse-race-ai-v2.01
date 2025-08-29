#!/bin/bash

# Enhanced Pipeline Dashboard Verification Script
# Verifies all components are working correctly

echo "🏇 Enhanced Pipeline Dashboard Verification"
echo "=========================================="

# Check Node-RED status
echo -n "📊 Checking Node-RED status... "
if curl -s http://localhost:1881 > /dev/null; then
    echo "✅ Node-RED running on port 1881"
else
    echo "❌ Node-RED not accessible"
    exit 1
fi

# Check Dashboard UI
echo -n "🎮 Checking Dashboard UI... "
if curl -s http://localhost:1881/ui > /dev/null; then
    echo "✅ Dashboard UI accessible"
else
    echo "❌ Dashboard UI not accessible"
    exit 1
fi

# Check log directory
echo -n "📋 Checking log directories... "
if [ -d "logs" ]; then
    echo "✅ Log directory exists"
    
    # List log files
    echo "📝 Available log files:"
    for log_file in logs/*.log; do
        if [ -f "$log_file" ]; then
            echo "   ✅ $(basename $log_file)"
        fi
    done
else
    echo "❌ Log directory not found"
fi

# Check enhanced pipeline monitor
echo -n "🔍 Checking enhanced pipeline monitor... "
if [ -f "enhanced_pipeline_monitor.py" ]; then
    echo "✅ Enhanced pipeline monitor available"
    
    # Test status command
    echo "📊 Testing monitor status..."
    python3 enhanced_pipeline_monitor.py status 2>/dev/null || echo "   ⚠️  Monitor needs Python dependencies"
else
    echo "❌ Enhanced pipeline monitor not found"
fi

# Check Docker containers
echo -n "🐳 Checking Docker containers... "
if docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(nodered|postgres|redis)" > /dev/null; then
    echo "✅ Docker containers running"
    
    echo "📦 Container status:"
    docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "(nodered|postgres|redis)" | sed 's/^/   /'
else
    echo "⚠️  Some Docker containers may not be running"
fi

# Check Python environment
echo -n "🐍 Checking Python environment... "
if python3 -c "import numpy, pandas, sklearn" 2>/dev/null; then
    echo "✅ Python dependencies available"
else
    echo "⚠️  Some Python dependencies may be missing"
fi

echo ""
echo "🎉 VERIFICATION COMPLETE"
echo "======================="
echo ""
echo "🚀 Next Steps:"
echo "   1. Open dashboard: http://localhost:1881/ui"
echo "   2. Navigate through the 7 tabs to explore features"
echo "   3. Test pipeline with 'Run Complete Pipeline' button"
echo "   4. Monitor logs in real-time through dashboard"
echo "   5. Use CLI tools: python3 enhanced_pipeline_monitor.py status"
echo ""
echo "📚 Documentation: ENHANCED_PIPELINE_DASHBOARD_GUIDE.md"
echo ""

# Show final status
if curl -s http://localhost:1881/ui > /dev/null && [ -d "logs" ] && [ -f "enhanced_pipeline_monitor.py" ]; then
    echo "🎯 STATUS: ✅ Enhanced pipeline dashboard is ready for use!"
else
    echo "🎯 STATUS: ⚠️  Some components need attention"
fi

echo ""
