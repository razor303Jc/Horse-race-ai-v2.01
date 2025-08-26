#!/usr/bin/env bash

# 🧪 Rebuilded Test Framework - Quick Start Script
# ===============================================
# 
# Comprehensive test execution script for Horse Racing AI v2.04
# Provides easy commands for running different test categories

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test framework directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}🧪 Horse Racing AI v2.04 - Rebuilded Test Framework${NC}"
echo -e "${BLUE}=====================================================${NC}"

# Function to print usage
print_usage() {
    echo -e "${YELLOW}Usage: $0 [COMMAND] [OPTIONS]${NC}"
    echo ""
    echo -e "${YELLOW}Commands:${NC}"
    echo "  setup     - Install test dependencies and setup environment"
    echo "  unit      - Run unit tests"
    echo "  integration - Run integration tests"
    echo "  system    - Run system/end-to-end tests"
    echo "  performance - Run performance tests"
    echo "  all       - Run all test categories"
    echo "  smoke     - Run smoke tests (critical functionality)"
    echo "  coverage  - Run tests with coverage analysis"
    echo "  clean     - Clean test artifacts and reports"
    echo "  report    - Generate comprehensive test report"
    echo ""
    echo -e "${YELLOW}Options:${NC}"
    echo "  -v, --verbose     - Verbose output"
    echo "  -c, --component   - Run tests for specific component"
    echo "  -p, --parallel    - Run tests in parallel"
    echo "  -h, --help        - Show this help message"
    echo ""
    echo -e "${YELLOW}Examples:${NC}"
    echo "  $0 unit -v                    # Run unit tests with verbose output"
    echo "  $0 integration -c database    # Run database integration tests"
    echo "  $0 all -p                     # Run all tests in parallel"
    echo "  $0 smoke                      # Run smoke tests only"
    echo ""
    echo -e "${YELLOW}Components:${NC}"
    echo "  bulk_uploader, pipeline, ml, api, database, web_app"
}

# Function to setup test environment
setup_test_environment() {
    echo -e "${BLUE}🔧 Setting up test environment...${NC}"
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is required but not installed.${NC}"
        exit 1
    fi
    
    # Check if pip is available
    if ! command -v pip3 &> /dev/null; then
        echo -e "${RED}❌ pip3 is required but not installed.${NC}"
        exit 1
    fi
    
    # Install test dependencies
    echo -e "${YELLOW}📦 Installing test dependencies...${NC}"
    pip3 install pytest pytest-html pytest-cov pytest-benchmark pytest-xdist pytest-mock
    pip3 install pandas numpy scipy scikit-learn
    pip3 install requests psutil docker
    
    # Create reports directory
    mkdir -p "$SCRIPT_DIR/reports"
    mkdir -p "$SCRIPT_DIR/logs"
    mkdir -p "$SCRIPT_DIR/temp"
    
    echo -e "${GREEN}✅ Test environment setup complete${NC}"
}

# Function to run unit tests
run_unit_tests() {
    local verbose=""
    local component=""
    local parallel=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose="-v"
                shift
                ;;
            -c|--component)
                component="-k $2"
                shift 2
                ;;
            -p|--parallel)
                parallel="-n auto"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}🧪 Running Unit Tests...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/unit" \
        $verbose \
        $component \
        $parallel \
        --tb=short \
        --durations=10 \
        --html="$SCRIPT_DIR/reports/unit_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ Unit tests completed${NC}"
}

# Function to run integration tests
run_integration_tests() {
    local verbose=""
    local component=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose="-v"
                shift
                ;;
            -c|--component)
                component="-k $2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}🔗 Running Integration Tests...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/integration" \
        $verbose \
        $component \
        -m integration \
        --tb=short \
        --html="$SCRIPT_DIR/reports/integration_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ Integration tests completed${NC}"
}

# Function to run system tests
run_system_tests() {
    local verbose=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose="-v"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}🏗️ Running System Tests...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/system" \
        $verbose \
        -m system \
        --tb=short \
        --html="$SCRIPT_DIR/reports/system_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ System tests completed${NC}"
}

# Function to run performance tests
run_performance_tests() {
    local verbose=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose="-v"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}⚡ Running Performance Tests...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/performance" \
        $verbose \
        -m performance \
        --benchmark-only \
        --benchmark-sort=mean \
        --benchmark-json="$SCRIPT_DIR/reports/performance_benchmark.json" \
        --html="$SCRIPT_DIR/reports/performance_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ Performance tests completed${NC}"
}

# Function to run smoke tests
run_smoke_tests() {
    echo -e "${BLUE}💨 Running Smoke Tests...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR" \
        -m "smoke or critical" \
        --maxfail=1 \
        --tb=short \
        --html="$SCRIPT_DIR/reports/smoke_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ Smoke tests completed${NC}"
}

# Function to run all tests
run_all_tests() {
    local parallel=""
    local verbose=""
    
    # Parse options
    while [[ $# -gt 0 ]]; do
        case $1 in
            -v|--verbose)
                verbose="-v"
                shift
                ;;
            -p|--parallel)
                parallel="-n auto"
                shift
                ;;
            *)
                shift
                ;;
        esac
    done
    
    echo -e "${BLUE}🚀 Running Complete Test Suite...${NC}"
    
    # Run smoke tests first
    echo -e "${YELLOW}Step 1/5: Smoke Tests${NC}"
    run_smoke_tests
    
    # Run unit tests
    echo -e "${YELLOW}Step 2/5: Unit Tests${NC}"
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/unit" \
        $verbose \
        $parallel \
        --tb=short \
        --html="$SCRIPT_DIR/reports/unit_tests_report.html" \
        --self-contained-html
    
    # Run integration tests
    echo -e "${YELLOW}Step 3/5: Integration Tests${NC}"
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/integration" \
        $verbose \
        -m integration \
        --tb=short \
        --html="$SCRIPT_DIR/reports/integration_tests_report.html" \
        --self-contained-html
    
    # Run system tests
    echo -e "${YELLOW}Step 4/5: System Tests${NC}"
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/system" \
        $verbose \
        -m system \
        --tb=short \
        --html="$SCRIPT_DIR/reports/system_tests_report.html" \
        --self-contained-html
    
    # Run performance tests
    echo -e "${YELLOW}Step 5/5: Performance Tests${NC}"
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR/performance" \
        $verbose \
        -m performance \
        --benchmark-only \
        --benchmark-sort=mean \
        --benchmark-json="$SCRIPT_DIR/reports/performance_benchmark.json" \
        --html="$SCRIPT_DIR/reports/performance_tests_report.html" \
        --self-contained-html
    
    echo -e "${GREEN}✅ Complete test suite finished${NC}"
    
    # Generate summary
    generate_test_report
}

# Function to run coverage analysis
run_coverage_analysis() {
    echo -e "${BLUE}📊 Running Coverage Analysis...${NC}"
    
    cd "$PROJECT_ROOT"
    python -m pytest "$SCRIPT_DIR" \
        --cov=src \
        --cov=tools \
        --cov=api \
        --cov=docker \
        --cov-report=html:"$SCRIPT_DIR/reports/coverage" \
        --cov-report=json:"$SCRIPT_DIR/reports/coverage.json" \
        --cov-report=term-missing \
        --cov-branch \
        --cov-fail-under=70
    
    echo -e "${GREEN}✅ Coverage analysis completed${NC}"
    echo -e "${YELLOW}📂 Coverage report: $SCRIPT_DIR/reports/coverage/index.html${NC}"
}

# Function to clean test artifacts
clean_test_artifacts() {
    echo -e "${BLUE}🧹 Cleaning test artifacts...${NC}"
    
    # Remove test reports
    rm -rf "$SCRIPT_DIR/reports/*"
    rm -rf "$SCRIPT_DIR/logs/*"
    rm -rf "$SCRIPT_DIR/temp/*"
    
    # Remove pytest cache
    find "$SCRIPT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find "$SCRIPT_DIR" -name "*.pyc" -delete 2>/dev/null || true
    find "$SCRIPT_DIR" -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    echo -e "${GREEN}✅ Test artifacts cleaned${NC}"
}

# Function to generate test report
generate_test_report() {
    echo -e "${BLUE}📋 Generating Test Report...${NC}"
    
    cd "$PROJECT_ROOT"
    python "$SCRIPT_DIR/run_tests.py" --coverage > "$SCRIPT_DIR/reports/test_summary.txt" 2>&1 || true
    
    # Count test files and create summary
    unit_tests=$(find "$SCRIPT_DIR/unit" -name "test_*.py" | wc -l)
    integration_tests=$(find "$SCRIPT_DIR/integration" -name "test_*.py" | wc -l)
    system_tests=$(find "$SCRIPT_DIR/system" -name "test_*.py" | wc -l)
    performance_tests=$(find "$SCRIPT_DIR/performance" -name "test_*.py" | wc -l)
    
    # Create summary report
    cat > "$SCRIPT_DIR/reports/framework_summary.txt" << EOF
🧪 Rebuilded Test Framework Summary
==================================

Test Categories:
- Unit Tests: $unit_tests files
- Integration Tests: $integration_tests files  
- System Tests: $system_tests files
- Performance Tests: $performance_tests files

Total Test Files: $((unit_tests + integration_tests + system_tests + performance_tests))

Framework Features:
✅ Comprehensive pytest configuration
✅ Global test fixtures and utilities
✅ Component-specific test organization
✅ Performance benchmarking
✅ Coverage analysis
✅ HTML reporting
✅ Parallel execution support
✅ Docker integration testing
✅ API integration testing
✅ ML pipeline testing
✅ Database integration testing
✅ End-to-end workflow testing

Reports Generated:
- Unit Tests: reports/unit_tests_report.html
- Integration Tests: reports/integration_tests_report.html
- System Tests: reports/system_tests_report.html
- Performance Tests: reports/performance_tests_report.html
- Coverage: reports/coverage/index.html
- Benchmarks: reports/performance_benchmark.json

Generated: $(date)
EOF
    
    echo -e "${GREEN}✅ Test report generated: $SCRIPT_DIR/reports/framework_summary.txt${NC}"
}

# Main command processing
case "${1:-help}" in
    setup)
        setup_test_environment
        ;;
    unit)
        shift
        run_unit_tests "$@"
        ;;
    integration)
        shift
        run_integration_tests "$@"
        ;;
    system)
        shift
        run_system_tests "$@"
        ;;
    performance)
        shift
        run_performance_tests "$@"
        ;;
    smoke)
        run_smoke_tests
        ;;
    all)
        shift
        run_all_tests "$@"
        ;;
    coverage)
        run_coverage_analysis
        ;;
    clean)
        clean_test_artifacts
        ;;
    report)
        generate_test_report
        ;;
    help|--help|-h)
        print_usage
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $1${NC}"
        echo ""
        print_usage
        exit 1
        ;;
esac
