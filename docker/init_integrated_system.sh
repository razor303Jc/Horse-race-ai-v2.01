#!/bin/bash
# 🚀 Docker Integrated System Initialization
# Initializes all Phase 1 & 2 improvements in Docker environment

echo "🚀 Initializing Horse Racing AI - Docker Integrated System"
echo "=========================================================="

# Set working directory
cd "$(dirname "$0")"

# Install integrated requirements
echo "📦 Installing integrated requirements..."
pip install -r requirements-integrated.txt

# Verify Python path setup
echo "🐍 Setting up Python paths..."
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/ml_training"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/monitoring"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/error_handling"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/caching"
export PYTHONPATH="${PYTHONPATH}:$(pwd)/database"

# Test integration
echo "🧪 Running integration tests..."
python test_integration.py

if [ $? -eq 0 ]; then
    echo "✅ Integration tests passed!"
else
    echo "❌ Integration tests failed - check configuration"
    exit 1
fi

# Initialize Redis (if available)
echo "🔴 Checking Redis availability..."
if command -v redis-server >/dev/null 2>&1; then
    if ! pgrep redis-server > /dev/null; then
        echo "🔴 Starting Redis server..."
        redis-server --daemonize yes
    else
        echo "✅ Redis server already running"
    fi
else
    echo "⚠️ Redis not available - caching will use memory fallback"
fi

# Create log directory
mkdir -p logs

echo ""
echo "🎉 Docker Integrated System Ready!"
echo "Available components:"
echo "  ✅ ML Training (UnifiedMLTrainer)"
echo "  ✅ Advanced Performance Monitoring"
echo "  ✅ Enhanced Error Handling"
echo "  ✅ Intelligent Caching"
echo "  ✅ Database Optimization"
echo ""
echo "🚀 System is ready for pipeline execution!"
