#!/bin/bash

# 🎯 C2 Command Center Quick Test Suite
# ====================================
# Quick validation of C2 system functionality

echo "🎯 C2 Command Center Quick Test Suite"
echo "======================================"
echo "Starting at $(date)"
echo ""

echo "📱 Testing Dashboard Accessibility..."
if python3 -m pytest system/test_c2_command_center.py::TestC2Dashboard::test_c2_dashboard_accessible -q; then
    echo "✅ Dashboard accessible"
else
    echo "❌ Dashboard test failed"
fi

# Test 2: Container Communication
echo ""
echo "🐳 Testing Container Communication..."
if python3 -m pytest system/test_c2_command_center.py::TestContainerCommunication::test_container_status_endpoint -q; then
    echo "✅ Container communication working"
else
    echo "❌ Container communication test failed"
fi

# Test 3: NTFY Integration
echo ""
echo "📢 Testing NTFY Integration..."
if python3 -m pytest system/test_c2_command_center.py::TestNTFYIntegration::test_ntfy_send_endpoint -q; then
    echo "✅ NTFY integration working"
else
    echo "❌ NTFY integration test failed"
fi

# Test 4: API Performance
echo ""
echo "⚡ Testing API Performance..."
if python3 -m pytest performance/test_c2_performance.py::TestC2PerformanceBaseline::test_api_response_time_baseline -q; then
    echo "✅ API performance acceptable"
else
    echo "❌ API performance test failed"
fi

echo ""
echo "🏁 Quick test suite completed at $(date)"
echo ""
echo "For comprehensive testing, run:"
echo "  python3 run_c2_tests.py all -v"
