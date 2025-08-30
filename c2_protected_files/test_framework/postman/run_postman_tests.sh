#!/bin/bash

# 🎯 C2 Command Center Postman API Test Runner
# =============================================
# Run Postman API tests using Newman CLI

echo "🎯 C2 Command Center Postman API Tests"
echo "======================================="
echo "Starting at $(date)"
echo ""

# Check if Newman is installed
if ! command -v newman &> /dev/null; then
    echo "❌ Newman (Postman CLI) not found"
    echo "📦 Install Newman: npm install -g newman"
    echo "📦 Or use Postman GUI to import the collection"
    echo ""
    echo "Collection: tests/postman/C2_Command_Center_API_Tests.postman_collection.json"
    echo "Environment: tests/postman/C2_Environment.postman_environment.json"
    exit 1
fi

# Check if services are available
echo "🔍 Checking Services..."

if curl -s http://localhost:1881/c2-dashboard > /dev/null; then
    echo "✅ Node-RED (http://localhost:1881)"
else
    echo "❌ Node-RED not accessible"
    NODE_RED_DOWN=1
fi

if curl -s http://localhost:3000/health > /dev/null; then
    echo "✅ Web App (http://localhost:3000)"
else
    echo "❌ Web App not accessible"
    WEB_APP_DOWN=1
fi

echo ""

# Run Postman tests
echo "🧪 Running Postman API Tests..."
echo "================================"

COLLECTION_FILE="tests/postman/C2_Command_Center_API_Tests.postman_collection.json"
ENVIRONMENT_FILE="tests/postman/C2_Environment.postman_environment.json"

if [[ ! -f "$COLLECTION_FILE" ]]; then
    echo "❌ Collection file not found: $COLLECTION_FILE"
    exit 1
fi

if [[ ! -f "$ENVIRONMENT_FILE" ]]; then
    echo "❌ Environment file not found: $ENVIRONMENT_FILE"
    exit 1
fi

# Newman command with options
newman run "$COLLECTION_FILE" \
    --environment "$ENVIRONMENT_FILE" \
    --reporters cli,json \
    --reporter-json-export "tests/postman/results/newman-results-$(date +%Y%m%d-%H%M%S).json" \
    --timeout-request 10000 \
    --timeout-script 5000 \
    --delay-request 500 \
    --color on \
    --verbose

NEWMAN_EXIT_CODE=$?

echo ""
echo "🏁 Postman API Tests completed at $(date)"
echo "Exit code: $NEWMAN_EXIT_CODE"

if [[ $NEWMAN_EXIT_CODE -eq 0 ]]; then
    echo "✅ All API tests passed!"
else
    echo "❌ Some API tests failed"
fi

echo ""
echo "📊 Results saved in: tests/postman/results/"
echo ""
echo "To run in Postman GUI:"
echo "1. Import collection: $COLLECTION_FILE"
echo "2. Import environment: $ENVIRONMENT_FILE" 
echo "3. Run collection with environment"

exit $NEWMAN_EXIT_CODE
