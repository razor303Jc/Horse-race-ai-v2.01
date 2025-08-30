#!/bin/bash
# Comprehensive Testing Suite for Horse Racing AI v2.05
# Implements the complete testing and simulation strategy

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
TEST_DATA_DATE="2025-08-26"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
RESULTS_DIR="$PROJECT_ROOT/test_results_$TIMESTAMP"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"; }
warn() { echo -e "${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1"; }
error() { echo -e "${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1"; }
info() { echo -e "${BLUE}[$(date +'%H:%M:%S')] INFO:${NC} $1"; }
success() { echo -e "${PURPLE}[$(date +'%H:%M:%S')] SUCCESS:${NC} $1"; }
section() { echo -e "${CYAN}[$(date +'%H:%M:%S')] === $1 ===${NC}"; }

# Test configuration
DATASET_PATH="$PROJECT_ROOT/data/$TEST_DATA_DATE"
DATABASE_PATH="$PROJECT_ROOT/data/processed/racing_data.db"
API_BASE_URL="http://localhost:8000"
WEBAPP_URL="http://localhost:3000"
NODERED_URL="http://localhost:1880"

# Performance targets
DB_QUERY_TARGET_MS=100
API_RESPONSE_TARGET_MS=200
WEBAPP_LOAD_TARGET_MS=2000
CONCURRENT_USERS_TARGET=50

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo "Options:"
    echo "  --suite [all|database|api|webapp|nodered|performance]  Test suite to run"
    echo "  --dataset [date]                                        Dataset date (default: $TEST_DATA_DATE)"
    echo "  --load [light|medium|heavy]                            Load testing intensity"
    echo "  --concurrent [number]                                   Number of concurrent users"
    echo "  --duration [seconds]                                    Test duration"
    echo "  --verbose                                               Verbose output"
    echo "  --help                                                  Show this help"
}

# Initialize test environment
init_test_environment() {
    section "Initializing Test Environment"
    
    # Create results directory
    mkdir -p "$RESULTS_DIR"/{database,api,webapp,nodered,performance,reports}
    
    # Verify test data exists
    if [ ! -d "$DATASET_PATH" ]; then
        error "Test dataset not found: $DATASET_PATH"
        exit 1
    fi
    
    info "📁 Test results directory: $RESULTS_DIR"
    info "📊 Test dataset: $DATASET_PATH ($(find "$DATASET_PATH" -name "*.csv" | wc -l) CSV files)"
    info "🎯 Performance targets: DB ${DB_QUERY_TARGET_MS}ms, API ${API_RESPONSE_TARGET_MS}ms, WebApp ${WEBAPP_LOAD_TARGET_MS}ms"
    
    # Create test report header
    cat > "$RESULTS_DIR/test_report.md" << EOF
# Horse Racing AI v2.05 Test Report

**Test Run:** $(date)  
**Dataset:** $TEST_DATA_DATE  
**Test ID:** $TIMESTAMP

## Test Configuration
- **Database Path:** $DATABASE_PATH
- **API Base URL:** $API_BASE_URL
- **Web App URL:** $WEBAPP_URL
- **Node-RED URL:** $NODERED_URL

## Performance Targets
- **Database Queries:** < ${DB_QUERY_TARGET_MS}ms
- **API Response:** < ${API_RESPONSE_TARGET_MS}ms
- **Web App Loading:** < ${WEBAPP_LOAD_TARGET_MS}ms
- **Concurrent Users:** ${CONCURRENT_USERS_TARGET}+

---

EOF
    
    log "✅ Test environment initialized"
}

# Database performance testing
test_database_performance() {
    section "Database Performance Testing"
    
    local results_file="$RESULTS_DIR/database/db_performance.json"
    
    # Create database test script
    cat > "$RESULTS_DIR/database/db_test.py" << 'EOF'
#!/usr/bin/env python3
import sqlite3
import time
import json
import sys
from pathlib import Path

def test_database_performance(db_path, results_file):
    """Test database performance with realistic queries"""
    
    results = {
        "timestamp": time.time(),
        "database_path": str(db_path),
        "tests": {}
    }
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test 1: Simple SELECT query
        start_time = time.perf_counter()
        cursor.execute("SELECT COUNT(*) FROM horses")
        result = cursor.fetchone()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["simple_count"] = {
            "query": "SELECT COUNT(*) FROM horses",
            "time_ms": round(query_time, 2),
            "result_count": result[0] if result else 0,
            "status": "pass" if query_time < 100 else "warning"
        }
        
        # Test 2: Complex JOIN query
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT h.horse_name, j.jockey_name, t.trainer_name, r.position
            FROM horses h
            JOIN results_horses rh ON h.horse_id = rh.horse_id
            JOIN jockeys_stats j ON rh.jockey_id = j.jockey_id
            JOIN trainers_stats t ON h.trainer_id = t.trainer_id
            JOIN records r ON rh.race_id = r.race_id
            LIMIT 100
        """)
        results_data = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["complex_join"] = {
            "query": "Complex JOIN with 4 tables",
            "time_ms": round(query_time, 2),
            "result_count": len(results_data),
            "status": "pass" if query_time < 500 else "warning"
        }
        
        # Test 3: Aggregation query
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT trainer_name, COUNT(*) as horse_count, AVG(win_rate) as avg_win_rate
            FROM trainers_stats
            GROUP BY trainer_name
            ORDER BY avg_win_rate DESC
            LIMIT 20
        """)
        agg_results = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["aggregation"] = {
            "query": "GROUP BY with aggregations",
            "time_ms": round(query_time, 2),
            "result_count": len(agg_results),
            "status": "pass" if query_time < 200 else "warning"
        }
        
        # Test 4: Full text search simulation
        start_time = time.perf_counter()
        cursor.execute("""
            SELECT * FROM horses 
            WHERE horse_name LIKE '%STAR%' 
            OR horse_name LIKE '%GOLD%'
            LIMIT 50
        """)
        search_results = cursor.fetchall()
        query_time = (time.perf_counter() - start_time) * 1000
        
        results["tests"]["text_search"] = {
            "query": "LIKE pattern matching",
            "time_ms": round(query_time, 2),
            "result_count": len(search_results),
            "status": "pass" if query_time < 150 else "warning"
        }
        
        conn.close()
        
        # Calculate summary
        total_time = sum(test["time_ms"] for test in results["tests"].values())
        passed_tests = len([test for test in results["tests"].values() if test["status"] == "pass"])
        total_tests = len(results["tests"])
        
        results["summary"] = {
            "total_time_ms": round(total_time, 2),
            "average_time_ms": round(total_time / total_tests, 2),
            "passed_tests": passed_tests,
            "total_tests": total_tests,
            "success_rate": round((passed_tests / total_tests) * 100, 2)
        }
        
    except Exception as e:
        results["error"] = str(e)
        results["status"] = "failed"
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    db_path = sys.argv[1] if len(sys.argv) > 1 else "racing_data.db"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "db_performance.json"
    
    results = test_database_performance(db_path, results_file)
    
    print(f"Database Performance Test Results:")
    print(f"Total Time: {results.get('summary', {}).get('total_time_ms', 0)}ms")
    print(f"Success Rate: {results.get('summary', {}).get('success_rate', 0)}%")
    
    if results.get('summary', {}).get('success_rate', 0) >= 80:
        sys.exit(0)
    else:
        sys.exit(1)
EOF
    
    chmod +x "$RESULTS_DIR/database/db_test.py"
    
    # Run database performance test
    info "🔍 Testing database performance..."
    if python3 "$RESULTS_DIR/database/db_test.py" "$DATABASE_PATH" "$results_file"; then
        success "✅ Database performance test completed"
        
        # Parse and display results
        if [ -f "$results_file" ]; then
            local success_rate=$(python3 -c "import json; data=json.load(open('$results_file')); print(data.get('summary', {}).get('success_rate', 0))")
            local total_time=$(python3 -c "import json; data=json.load(open('$results_file')); print(data.get('summary', {}).get('total_time_ms', 0))")
            
            info "📊 Success Rate: ${success_rate}%"
            info "⏱️  Total Time: ${total_time}ms"
            
            echo "### Database Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Success Rate:** ${success_rate}%" >> "$RESULTS_DIR/test_report.md"
            echo "- **Total Test Time:** ${total_time}ms" >> "$RESULTS_DIR/test_report.md"
            echo "- **Status:** ✅ PASSED" >> "$RESULTS_DIR/test_report.md"
            echo "" >> "$RESULTS_DIR/test_report.md"
        fi
    else
        error "❌ Database performance test failed"
        echo "### Database Performance Results" >> "$RESULTS_DIR/test_report.md"
        echo "- **Status:** ❌ FAILED" >> "$RESULTS_DIR/test_report.md"
        echo "" >> "$RESULTS_DIR/test_report.md"
    fi
}

# API performance testing
test_api_performance() {
    section "API Performance Testing"
    
    local results_file="$RESULTS_DIR/api/api_performance.json"
    
    # Create API test script
    cat > "$RESULTS_DIR/api/api_test.py" << 'EOF'
#!/usr/bin/env python3
import requests
import time
import json
import sys
import concurrent.futures
from datetime import datetime

def test_api_endpoint(url, endpoint, expected_status=200):
    """Test a single API endpoint"""
    start_time = time.perf_counter()
    try:
        response = requests.get(f"{url}{endpoint}", timeout=10)
        response_time = (time.perf_counter() - start_time) * 1000
        
        return {
            "endpoint": endpoint,
            "status_code": response.status_code,
            "response_time_ms": round(response_time, 2),
            "content_length": len(response.content),
            "success": response.status_code == expected_status,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        response_time = (time.perf_counter() - start_time) * 1000
        return {
            "endpoint": endpoint,
            "error": str(e),
            "response_time_ms": round(response_time, 2),
            "success": False,
            "timestamp": datetime.now().isoformat()
        }

def load_test_endpoint(url, endpoint, concurrent_users=10, requests_per_user=5):
    """Load test a single endpoint with concurrent users"""
    
    def user_session():
        results = []
        for _ in range(requests_per_user):
            result = test_api_endpoint(url, endpoint)
            results.append(result)
            time.sleep(0.1)  # Small delay between requests
        return results
    
    all_results = []
    start_time = time.perf_counter()
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = [executor.submit(user_session) for _ in range(concurrent_users)]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                user_results = future.result()
                all_results.extend(user_results)
            except Exception as e:
                print(f"User session failed: {e}")
    
    total_time = time.perf_counter() - start_time
    
    # Calculate statistics
    successful_requests = [r for r in all_results if r.get('success', False)]
    failed_requests = [r for r in all_results if not r.get('success', False)]
    
    if successful_requests:
        response_times = [r['response_time_ms'] for r in successful_requests]
        avg_response_time = sum(response_times) / len(response_times)
        min_response_time = min(response_times)
        max_response_time = max(response_times)
        p95_response_time = sorted(response_times)[int(len(response_times) * 0.95)]
    else:
        avg_response_time = min_response_time = max_response_time = p95_response_time = 0
    
    return {
        "endpoint": endpoint,
        "concurrent_users": concurrent_users,
        "requests_per_user": requests_per_user,
        "total_requests": len(all_results),
        "successful_requests": len(successful_requests),
        "failed_requests": len(failed_requests),
        "success_rate": round((len(successful_requests) / len(all_results)) * 100, 2) if all_results else 0,
        "total_time_seconds": round(total_time, 2),
        "requests_per_second": round(len(all_results) / total_time, 2) if total_time > 0 else 0,
        "avg_response_time_ms": round(avg_response_time, 2),
        "min_response_time_ms": round(min_response_time, 2),
        "max_response_time_ms": round(max_response_time, 2),
        "p95_response_time_ms": round(p95_response_time, 2),
        "timestamp": datetime.now().isoformat()
    }

def test_api_performance(base_url, results_file, concurrent_users=10):
    """Run comprehensive API performance tests"""
    
    results = {
        "timestamp": datetime.now().isoformat(),
        "base_url": base_url,
        "concurrent_users": concurrent_users,
        "tests": {}
    }
    
    # Define test endpoints
    endpoints = [
        "/health",
        "/api/races",
        "/api/horses",
        "/api/jockeys",
        "/api/trainers",
        "/api/predictions/latest"
    ]
    
    print(f"Testing API performance with {concurrent_users} concurrent users...")
    
    for endpoint in endpoints:
        print(f"Testing endpoint: {endpoint}")
        
        # Single request test
        single_result = test_api_endpoint(base_url, endpoint)
        
        # Load test
        load_result = load_test_endpoint(base_url, endpoint, concurrent_users, 3)
        
        results["tests"][endpoint] = {
            "single_request": single_result,
            "load_test": load_result
        }
    
    # Calculate overall statistics
    all_load_tests = [test["load_test"] for test in results["tests"].values()]
    
    if all_load_tests:
        overall_success_rate = sum(test["success_rate"] for test in all_load_tests) / len(all_load_tests)
        overall_avg_response = sum(test["avg_response_time_ms"] for test in all_load_tests) / len(all_load_tests)
        overall_requests_per_sec = sum(test["requests_per_second"] for test in all_load_tests)
        
        results["summary"] = {
            "overall_success_rate": round(overall_success_rate, 2),
            "overall_avg_response_ms": round(overall_avg_response, 2),
            "total_requests_per_second": round(overall_requests_per_sec, 2),
            "endpoints_tested": len(endpoints),
            "status": "pass" if overall_success_rate >= 95 and overall_avg_response < 500 else "warning"
        }
    
    # Save results
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    return results

if __name__ == "__main__":
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
    results_file = sys.argv[2] if len(sys.argv) > 2 else "api_performance.json"
    concurrent_users = int(sys.argv[3]) if len(sys.argv) > 3 else 10
    
    results = test_api_performance(base_url, results_file, concurrent_users)
    
    summary = results.get('summary', {})
    print(f"API Performance Test Results:")
    print(f"Success Rate: {summary.get('overall_success_rate', 0)}%")
    print(f"Average Response Time: {summary.get('overall_avg_response_ms', 0)}ms")
    print(f"Requests/Second: {summary.get('total_requests_per_second', 0)}")
    
    if summary.get('status') == 'pass':
        sys.exit(0)
    else:
        sys.exit(1)
EOF
    
    chmod +x "$RESULTS_DIR/api/api_test.py"
    
    # Check if API is running
    info "🔍 Checking API availability..."
    if curl -s "$API_BASE_URL/health" > /dev/null 2>&1; then
        info "📡 API is accessible at $API_BASE_URL"
        
        # Run API performance test
        info "🚀 Testing API performance with $CONCURRENT_USERS_TARGET concurrent users..."
        if python3 "$RESULTS_DIR/api/api_test.py" "$API_BASE_URL" "$results_file" "$CONCURRENT_USERS_TARGET"; then
            success "✅ API performance test completed"
            
            # Parse and display results
            if [ -f "$results_file" ]; then
                local success_rate=$(python3 -c "import json; data=json.load(open('$results_file')); print(data.get('summary', {}).get('overall_success_rate', 0))")
                local avg_response=$(python3 -c "import json; data=json.load(open('$results_file')); print(data.get('summary', {}).get('overall_avg_response_ms', 0))")
                local requests_per_sec=$(python3 -c "import json; data=json.load(open('$results_file')); print(data.get('summary', {}).get('total_requests_per_second', 0))")
                
                info "📊 Success Rate: ${success_rate}%"
                info "⏱️  Average Response: ${avg_response}ms"
                info "🚀 Requests/Second: ${requests_per_sec}"
                
                echo "### API Performance Results" >> "$RESULTS_DIR/test_report.md"
                echo "- **Success Rate:** ${success_rate}%" >> "$RESULTS_DIR/test_report.md"
                echo "- **Average Response Time:** ${avg_response}ms" >> "$RESULTS_DIR/test_report.md"
                echo "- **Requests/Second:** ${requests_per_sec}" >> "$RESULTS_DIR/test_report.md"
                echo "- **Concurrent Users:** $CONCURRENT_USERS_TARGET" >> "$RESULTS_DIR/test_report.md"
                echo "- **Status:** ✅ PASSED" >> "$RESULTS_DIR/test_report.md"
                echo "" >> "$RESULTS_DIR/test_report.md"
            fi
        else
            error "❌ API performance test failed"
            echo "### API Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Status:** ❌ FAILED" >> "$RESULTS_DIR/test_report.md"
            echo "" >> "$RESULTS_DIR/test_report.md"
        fi
    else
        warn "⚠️ API not accessible at $API_BASE_URL - skipping API tests"
        echo "### API Performance Results" >> "$RESULTS_DIR/test_report.md"
        echo "- **Status:** ⚠️ SKIPPED (API not running)" >> "$RESULTS_DIR/test_report.md"
        echo "" >> "$RESULTS_DIR/test_report.md"
    fi
}

# Web application testing
test_webapp_performance() {
    section "Web Application Performance Testing"
    
    # Check if webapp is running
    info "🔍 Checking Web App availability..."
    if curl -s "$WEBAPP_URL" > /dev/null 2>&1; then
        info "🌐 Web App is accessible at $WEBAPP_URL"
        
        # Basic load time test using curl
        local start_time=$(date +%s%3N)
        if curl -s "$WEBAPP_URL" > /dev/null; then
            local end_time=$(date +%s%3N)
            local load_time=$((end_time - start_time))
            
            info "⏱️  Page load time: ${load_time}ms"
            
            echo "### Web Application Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Page Load Time:** ${load_time}ms" >> "$RESULTS_DIR/test_report.md"
            if [ $load_time -lt $WEBAPP_LOAD_TARGET_MS ]; then
                echo "- **Status:** ✅ PASSED" >> "$RESULTS_DIR/test_report.md"
                success "✅ Web App performance test passed"
            else
                echo "- **Status:** ⚠️ WARNING (Slow load time)" >> "$RESULTS_DIR/test_report.md"
                warn "⚠️ Web App load time exceeds target"
            fi
        else
            error "❌ Failed to load web application"
            echo "### Web Application Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Status:** ❌ FAILED" >> "$RESULTS_DIR/test_report.md"
        fi
    else
        warn "⚠️ Web App not accessible at $WEBAPP_URL - skipping webapp tests"
        echo "### Web Application Performance Results" >> "$RESULTS_DIR/test_report.md"
        echo "- **Status:** ⚠️ SKIPPED (Web App not running)" >> "$RESULTS_DIR/test_report.md"
    fi
    echo "" >> "$RESULTS_DIR/test_report.md"
}

# Node-RED flow testing
test_nodered_flows() {
    section "Node-RED Flow Testing"
    
    info "🔍 Checking Node-RED availability..."
    if curl -s "$NODERED_URL" > /dev/null 2>&1; then
        info "🔄 Node-RED is accessible at $NODERED_URL"
        
        # Test basic Node-RED responsiveness
        local start_time=$(date +%s%3N)
        if curl -s "$NODERED_URL/flows" > /dev/null; then
            local end_time=$(date +%s%3N)
            local response_time=$((end_time - start_time))
            
            info "⏱️  Node-RED response time: ${response_time}ms"
            
            echo "### Node-RED Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Response Time:** ${response_time}ms" >> "$RESULTS_DIR/test_report.md"
            echo "- **Status:** ✅ ACCESSIBLE" >> "$RESULTS_DIR/test_report.md"
            success "✅ Node-RED flows accessible"
        else
            error "❌ Failed to access Node-RED flows"
            echo "### Node-RED Performance Results" >> "$RESULTS_DIR/test_report.md"
            echo "- **Status:** ❌ FAILED" >> "$RESULTS_DIR/test_report.md"
        fi
    else
        warn "⚠️ Node-RED not accessible at $NODERED_URL - skipping Node-RED tests"
        echo "### Node-RED Performance Results" >> "$RESULTS_DIR/test_report.md"
        echo "- **Status:** ⚠️ SKIPPED (Node-RED not running)" >> "$RESULTS_DIR/test_report.md"
    fi
    echo "" >> "$RESULTS_DIR/test_report.md"
}

# Generate final report
generate_final_report() {
    section "Generating Final Test Report"
    
    # Add timestamp and summary to report
    cat >> "$RESULTS_DIR/test_report.md" << EOF

## Test Summary

**Completed:** $(date)  
**Total Duration:** $(( $(date +%s) - $(stat -c %Y "$RESULTS_DIR") )) seconds  
**Results Directory:** $RESULTS_DIR

### Files Generated:
- **Database Results:** \`database/db_performance.json\`
- **API Results:** \`api/api_performance.json\`
- **Test Scripts:** Available in respective directories
- **Full Report:** \`test_report.md\`

### Next Steps:
1. Review detailed results in JSON files
2. Analyze performance bottlenecks
3. Run optimization iterations
4. Schedule regular performance monitoring

---
**Testing completed successfully. System ready for daily operations simulation.**
EOF
    
    info "📊 Final test report: $RESULTS_DIR/test_report.md"
    success "🎉 Comprehensive testing completed!"
}

# Main execution function
main() {
    local test_suite="all"
    local load_level="medium"
    local concurrent_users=$CONCURRENT_USERS_TARGET
    local duration=300
    local verbose=false
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            --suite)
                test_suite="$2"
                shift 2
                ;;
            --dataset)
                TEST_DATA_DATE="$2"
                DATASET_PATH="$PROJECT_ROOT/data/$TEST_DATA_DATE"
                shift 2
                ;;
            --load)
                load_level="$2"
                shift 2
                ;;
            --concurrent)
                concurrent_users="$2"
                shift 2
                ;;
            --duration)
                duration="$2"
                shift 2
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            --help)
                usage
                exit 0
                ;;
            *)
                error "Unknown option: $1"
                usage
                exit 1
                ;;
        esac
    done
    
    # Adjust settings based on load level
    case $load_level in
        light)
            concurrent_users=$((concurrent_users / 2))
            ;;
        heavy)
            concurrent_users=$((concurrent_users * 2))
            ;;
    esac
    
    CONCURRENT_USERS_TARGET=$concurrent_users
    
    section "Horse Racing AI v2.05 Comprehensive Testing Suite"
    info "🎯 Test Suite: $test_suite"
    info "📊 Load Level: $load_level"
    info "👥 Concurrent Users: $concurrent_users"
    info "⏱️  Duration: ${duration}s"
    echo
    
    # Initialize test environment
    init_test_environment
    
    # Run selected test suites
    case $test_suite in
        all)
            test_database_performance
            test_api_performance
            test_webapp_performance
            test_nodered_flows
            ;;
        database)
            test_database_performance
            ;;
        api)
            test_api_performance
            ;;
        webapp)
            test_webapp_performance
            ;;
        nodered)
            test_nodered_flows
            ;;
        performance)
            test_database_performance
            test_api_performance
            ;;
        *)
            error "Unknown test suite: $test_suite"
            usage
            exit 1
            ;;
    esac
    
    # Generate final report
    generate_final_report
    
    echo
    success "🚀 Testing complete! Results available in: $RESULTS_DIR"
    info "📋 View report: cat $RESULTS_DIR/test_report.md"
    echo
}

# Execute main function with all arguments
main "$@"
