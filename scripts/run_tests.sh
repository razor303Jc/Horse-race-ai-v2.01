#!/bin/bash

# 🧪 Comprehensive Test Suite for Horse Racing AI v2.03
# Runs both frontend (Playwright) and backend (pytest) tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.03"
WEB_DIR="$PROJECT_ROOT/src/web"
API_URL="http://localhost:8000"
WEB_URL="http://localhost:5003"
TEST_RESULTS_DIR="$PROJECT_ROOT/test-results"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Function to check if a service is running
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1

    print_status "Checking if $service_name is running at $url..."
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            print_success "$service_name is running"
            return 0
        fi
        
        print_status "Waiting for $service_name... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    
    print_error "$service_name is not running at $url"
    return 1
}

# Function to start API server if not running
start_api_server() {
    if ! check_service "$API_URL/health" "API Server"; then
        print_status "Starting API server..."
        cd "$PROJECT_ROOT/api"
        
        # Start API server in background
        python prediction_api.py &
        API_PID=$!
        echo $API_PID > "$TEST_RESULTS_DIR/api_server.pid"
        
        # Wait for it to start
        sleep 10
        
        if check_service "$API_URL/health" "API Server"; then
            print_success "API server started successfully"
        else
            print_error "Failed to start API server"
            return 1
        fi
    fi
}

# Function to start web server if not running
start_web_server() {
    if ! check_service "$WEB_URL" "Web Server"; then
        print_status "Starting web server..."
        cd "$WEB_DIR"
        
        # Start web server in background
        npm run dev &
        WEB_PID=$!
        echo $WEB_PID > "$TEST_RESULTS_DIR/web_server.pid"
        
        # Wait for it to start
        sleep 15
        
        if check_service "$WEB_URL" "Web Server"; then
            print_success "Web server started successfully"
        else
            print_error "Failed to start web server"
            return 1
        fi
    fi
}

# Function to run backend tests
run_backend_tests() {
    print_status "🐍 Running Backend (API) Tests..."
    
    cd "$PROJECT_ROOT"
    
    # Install required packages if not present
    if ! python -c "import requests" 2>/dev/null; then
        print_status "Installing required Python packages..."
        pip install requests pytest
    fi
    
    # Run comprehensive backend tests
    if python run_backend_tests.py; then
        print_success "Backend tests completed successfully"
        return 0
    else
        print_error "Backend tests failed"
        return 1
    fi
}

# Function to run frontend tests
run_frontend_tests() {
    print_status "🎭 Running Frontend (Playwright) Tests..."
    
    cd "$WEB_DIR"
    
    # Install Playwright if not present
    if [ ! -d "node_modules/@playwright" ]; then
        print_status "Installing Playwright..."
        npm install @playwright/test
        npx playwright install chromium
    fi
    
    # Run Playwright tests
    if npm run test; then
        print_success "Frontend tests completed successfully"
        return 0
    else
        print_error "Frontend tests failed"
        return 1
    fi
}

# Function to generate combined test report
generate_combined_report() {
    print_status "📊 Generating combined test report..."
    
    cd "$PROJECT_ROOT"
    
    # Create combined report HTML
    cat > "$TEST_RESULTS_DIR/combined-test-report.html" << 'EOF'
<!DOCTYPE html>
<html>
<head>
    <title>Horse Racing AI v2.03 - Complete Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                  color: white; padding: 30px; border-radius: 12px; text-align: center; }
        .section { margin: 20px 0; padding: 20px; border: 1px solid #ddd; 
                   border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .success { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); 
                   border-color: #90ee90; }
        .failure { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); 
                   border-color: #ffcccb; }
        .stats { display: flex; justify-content: space-around; margin: 20px 0; }
        .stat-box { background: white; padding: 15px; border-radius: 8px; 
                    text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .links { margin: 20px 0; }
        .links a { display: inline-block; margin: 5px; padding: 10px 20px; 
                   background: #007bff; color: white; text-decoration: none; 
                   border-radius: 5px; }
        .timestamp { font-size: 14px; color: #666; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏇 Horse Racing AI v2.03</h1>
        <h2>Complete Test Suite Report</h2>
        <p>Frontend (Playwright) + Backend (pytest) Test Results</p>
    </div>
    
    <div class="stats">
        <div class="stat-box">
            <h3>🎭 Frontend Tests</h3>
            <p id="frontend-status">Check individual reports</p>
        </div>
        <div class="stat-box">
            <h3>🐍 Backend Tests</h3>
            <p id="backend-status">Check individual reports</p>
        </div>
        <div class="stat-box">
            <h3>📊 Overall Status</h3>
            <p id="overall-status">Tests Completed</p>
        </div>
    </div>
    
    <div class="section">
        <h2>📋 Test Reports</h2>
        <div class="links">
            <a href="playwright-report/index.html" target="_blank">📱 Frontend Test Report</a>
            <a href="backend-test-report.html" target="_blank">🔧 Backend Test Report</a>
            <a href="backend-test-results.json" target="_blank">📄 Raw Test Data</a>
        </div>
    </div>
    
    <div class="section">
        <h2>🚀 Test Coverage</h2>
        <ul>
            <li><strong>Frontend Tests:</strong> Dashboard, Race Cards, API Integration, E2E User Journeys</li>
            <li><strong>Backend Tests:</strong> API Endpoints, Performance, Security, Error Handling</li>
            <li><strong>Integration Tests:</strong> Frontend-Backend Communication, WebSocket, Real-time Updates</li>
            <li><strong>Cross-Browser:</strong> Chrome, Firefox, Safari, Mobile Browsers</li>
        </ul>
    </div>
    
    <div class="section">
        <h2>📸 Screenshots & Videos</h2>
        <p>Visual test evidence and failure recordings are available in:</p>
        <ul>
            <li><code>test-results/</code> - Individual test screenshots</li>
            <li><code>playwright-report/</code> - Complete Playwright report with videos</li>
        </ul>
    </div>
    
    <div class="timestamp">
        Generated: $(date)
    </div>
</body>
</html>
EOF

    print_success "Combined test report generated"
}

# Function to cleanup processes
cleanup() {
    print_status "🧹 Cleaning up test processes..."
    
    # Kill API server if we started it
    if [ -f "$TEST_RESULTS_DIR/api_server.pid" ]; then
        local api_pid=$(cat "$TEST_RESULTS_DIR/api_server.pid")
        if kill -0 $api_pid 2>/dev/null; then
            kill $api_pid
            print_status "Stopped API server (PID: $api_pid)"
        fi
        rm -f "$TEST_RESULTS_DIR/api_server.pid"
    fi
    
    # Kill web server if we started it
    if [ -f "$TEST_RESULTS_DIR/web_server.pid" ]; then
        local web_pid=$(cat "$TEST_RESULTS_DIR/web_server.pid")
        if kill -0 $web_pid 2>/dev/null; then
            kill $web_pid
            print_status "Stopped web server (PID: $web_pid)"
        fi
        rm -f "$TEST_RESULTS_DIR/web_server.pid"
    fi
}

# Trap to cleanup on exit
trap cleanup EXIT

# Main execution
main() {
    print_status "🚀 Starting Comprehensive Test Suite for Horse Racing AI v2.03"
    
    # Create test results directory
    mkdir -p "$TEST_RESULTS_DIR"
    
    # Start services
    start_api_server
    start_web_server
    
    # Run tests
    local backend_success=true
    local frontend_success=true
    
    # Run backend tests
    if ! run_backend_tests; then
        backend_success=false
    fi
    
    # Run frontend tests
    if ! run_frontend_tests; then
        frontend_success=false
    fi
    
    # Generate combined report
    generate_combined_report
    
    # Print final summary
    echo ""
    echo "================================================================"
    print_status "🏁 Test Suite Complete!"
    echo "================================================================"
    
    if $backend_success; then
        print_success "Backend Tests: PASSED"
    else
        print_error "Backend Tests: FAILED"
    fi
    
    if $frontend_success; then
        print_success "Frontend Tests: PASSED"
    else
        print_error "Frontend Tests: FAILED"
    fi
    
    if $backend_success && $frontend_success; then
        print_success "Overall Result: ALL TESTS PASSED! 🎉"
        echo ""
        print_status "📊 View complete reports at:"
        echo "   🌐 Combined Report: file://$TEST_RESULTS_DIR/combined-test-report.html"
        echo "   🎭 Frontend Report: file://$WEB_DIR/playwright-report/index.html"
        echo "   🐍 Backend Report: file://$TEST_RESULTS_DIR/backend-test-report.html"
        return 0
    else
        print_error "Overall Result: SOME TESTS FAILED"
        return 1
    fi
}

# Parse command line arguments
case "${1:-all}" in
    "backend")
        print_status "Running backend tests only..."
        mkdir -p "$TEST_RESULTS_DIR"
        start_api_server
        run_backend_tests
        ;;
    "frontend")
        print_status "Running frontend tests only..."
        mkdir -p "$TEST_RESULTS_DIR"
        start_api_server
        start_web_server
        run_frontend_tests
        ;;
    "all"|*)
        main
        ;;
esac
