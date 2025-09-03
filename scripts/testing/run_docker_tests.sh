#!/bin/bash

# =============================================================================
# Docker Test Runner for Horse Racing AI v2.05
# =============================================================================
# Comprehensive test runner for Docker-related tests including:
# - Service-specific dockerignore validation
# - Build optimization tests
# - Performance benchmarks
# - System integration tests
# - Security and production readiness checks
# =============================================================================

set -euo pipefail

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
TEST_DIR="$PROJECT_ROOT/tests"
DOCKER_TEST_DIR="$TEST_DIR/integration/docker_integration"
PERFORMANCE_TEST_DIR="$TEST_DIR/performance"
SYSTEM_TEST_DIR="$TEST_DIR/system"

# Test categories
declare -A TEST_CATEGORIES=(
    ["dockerignore"]="Service-specific dockerignore file tests"
    ["optimization"]="Docker build optimization tests"
    ["performance"]="Container performance and benchmarks"
    ["system"]="System integration and deployment tests"
    ["security"]="Security and production readiness tests"
    ["smoke"]="Quick smoke tests for Docker setup"
    ["all"]="Run all Docker-related tests"
)

# Test execution options
PYTEST_ARGS=""
VERBOSE=false
COVERAGE=false
PARALLEL=false
SLOW_TESTS=false
INTEGRATION_TESTS=false
STRESS_TESTS=false

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_test() {
    echo -e "${PURPLE}[TEST]${NC} $1"
}

log_result() {
    echo -e "${CYAN}[RESULT]${NC} $1"
}

print_header() {
    echo "============================================================================="
    echo "                 Horse Racing AI v2.05 - Docker Test Suite"
    echo "============================================================================="
    echo "Running Docker-related tests for optimized service architecture"
    echo "Project root: $PROJECT_ROOT"
    echo "Test directory: $TEST_DIR"
    echo "============================================================================="
    echo
}

print_usage() {
    echo "Usage: $0 [CATEGORY] [OPTIONS]"
    echo
    echo "Test Categories:"
    for category in "${!TEST_CATEGORIES[@]}"; do
        printf "  %-15s %s\n" "$category" "${TEST_CATEGORIES[$category]}"
    done
    echo
    echo "Options:"
    echo "  --verbose, -v       Enable verbose output"
    echo "  --coverage, -c      Enable coverage reporting"
    echo "  --parallel, -p      Run tests in parallel"
    echo "  --slow             Include slow tests"
    echo "  --integration      Include integration tests"
    echo "  --stress           Include stress tests"
    echo "  --help, -h         Show this help message"
    echo
    echo "Examples:"
    echo "  $0 smoke                    # Quick smoke tests"
    echo "  $0 dockerignore --verbose   # Dockerignore tests with verbose output"
    echo "  $0 performance --slow       # Performance tests including slow ones"
    echo "  $0 all --coverage           # All tests with coverage"
    echo
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "$PROJECT_ROOT/docker-compose.clean.yml" ]]; then
        log_error "Not in correct project directory. Missing docker-compose.clean.yml"
        exit 1
    fi
    
    # Check pytest is available
    if ! command -v pytest &> /dev/null; then
        log_error "pytest not found. Please install: pip install pytest"
        exit 1
    fi
    
    # Check Docker is available
    if ! command -v docker &> /dev/null; then
        log_warning "Docker not found. Some tests may be skipped."
    fi
    
    # Check test directories exist
    local missing_dirs=()
    for dir in "$DOCKER_TEST_DIR" "$PERFORMANCE_TEST_DIR" "$SYSTEM_TEST_DIR"; do
        if [[ ! -d "$dir" ]]; then
            missing_dirs+=("$dir")
        fi
    done
    
    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        log_error "Missing test directories:"
        printf '%s\n' "${missing_dirs[@]}"
        exit 1
    fi
    
    log_success "Prerequisites check passed"
}

build_pytest_command() {
    local category="$1"
    local cmd="pytest"
    
    # Add base arguments
    if [[ "$VERBOSE" == "true" ]]; then
        cmd+=" -v"
    fi
    
    if [[ "$COVERAGE" == "true" ]]; then
        cmd+=" --cov=docker --cov-report=html --cov-report=term"
    fi
    
    if [[ "$PARALLEL" == "true" ]]; then
        cmd+=" -n auto"
    fi
    
    # Add test-specific options
    if [[ "$SLOW_TESTS" == "true" ]]; then
        cmd+=" --run-slow"
    fi
    
    if [[ "$INTEGRATION_TESTS" == "true" ]]; then
        cmd+=" --integration"
    fi
    
    if [[ "$STRESS_TESTS" == "true" ]]; then
        cmd+=" --run-stress"
    fi
    
    # Add category-specific paths and markers
    case "$category" in
        "dockerignore")
            cmd+=" $DOCKER_TEST_DIR/test_optimized_docker_services.py::TestServiceSpecificDockerIgnore"
            ;;
        "optimization")
            cmd+=" $DOCKER_TEST_DIR/test_optimized_docker_services.py::TestOptimizedBuilds"
            cmd+=" $DOCKER_TEST_DIR/test_optimized_docker_services.py::TestContainerSizes"
            ;;
        "performance")
            cmd+=" $PERFORMANCE_TEST_DIR/test_docker_performance.py"
            cmd+=" -m performance"
            ;;
        "system")
            cmd+=" $SYSTEM_TEST_DIR/test_docker_system.py"
            cmd+=" -m system"
            ;;
        "security")
            cmd+=" $DOCKER_TEST_DIR/test_optimized_docker_services.py::TestContainerSecurity"
            cmd+=" $SYSTEM_TEST_DIR/test_docker_system.py::TestProductionReadiness"
            ;;
        "smoke")
            cmd+=" $DOCKER_TEST_DIR/test_optimized_docker_services.py::TestDockerSetupSmoke"
            cmd+=" $SYSTEM_TEST_DIR/test_docker_system.py::TestSystemDeployment::test_compose_file_structure"
            ;;
        "all")
            cmd+=" $DOCKER_TEST_DIR $PERFORMANCE_TEST_DIR $SYSTEM_TEST_DIR"
            cmd+=" -m 'docker or performance or system'"
            ;;
        *)
            log_error "Unknown test category: $category"
            exit 1
            ;;
    esac
    
    # Add any additional pytest arguments
    cmd+=" $PYTEST_ARGS"
    
    echo "$cmd"
}

run_test_category() {
    local category="$1"
    local description="${TEST_CATEGORIES[$category]}"
    
    log_test "Running: $description"
    echo
    
    local pytest_cmd
    pytest_cmd=$(build_pytest_command "$category")
    
    log_info "Executing: $pytest_cmd"
    echo
    
    # Change to project root for test execution
    cd "$PROJECT_ROOT"
    
    local start_time
    start_time=$(date +%s)
    
    # Execute tests
    if eval "$pytest_cmd"; then
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_success "Test category '$category' completed successfully in ${duration}s"
        return 0
    else
        local end_time
        end_time=$(date +%s)
        local duration=$((end_time - start_time))
        
        log_error "Test category '$category' failed after ${duration}s"
        return 1
    fi
}

run_docker_environment_check() {
    log_info "Checking Docker environment..."
    
    # Check Docker daemon
    if docker info &>/dev/null; then
        log_success "Docker daemon is running"
    else
        log_warning "Docker daemon not accessible. Some tests may be skipped."
    fi
    
    # Check docker-compose
    if command -v docker-compose &>/dev/null; then
        local compose_version
        compose_version=$(docker-compose --version)
        log_success "Docker Compose available: $compose_version"
    else
        log_warning "Docker Compose not found. Some tests may be skipped."
    fi
    
    # Check for existing containers
    local running_containers
    running_containers=$(docker ps -q | wc -l)
    if [[ "$running_containers" -gt 0 ]]; then
        log_info "Found $running_containers running containers"
    fi
    
    # Check available space
    local available_space
    available_space=$(df -h . | awk 'NR==2 {print $4}')
    log_info "Available disk space: $available_space"
}

generate_test_report() {
    local category="$1"
    local result="$2"
    local start_time="$3"
    local end_time="$4"
    
    local report_file
    report_file="$PROJECT_ROOT/docker_test_report_$(date +%Y%m%d_%H%M%S).md"
    
    cat > "$report_file" << EOF
# Docker Test Report - $(date)

## Test Configuration
- **Category**: $category
- **Project Root**: $PROJECT_ROOT
- **Start Time**: $(date -d "@$start_time")
- **End Time**: $(date -d "@$end_time")
- **Duration**: $((end_time - start_time)) seconds
- **Result**: $result

## Test Options
- **Verbose**: $VERBOSE
- **Coverage**: $COVERAGE
- **Parallel**: $PARALLEL
- **Slow Tests**: $SLOW_TESTS
- **Integration Tests**: $INTEGRATION_TESTS
- **Stress Tests**: $STRESS_TESTS

## Environment
- **Docker Available**: $(command -v docker &>/dev/null && echo "Yes" || echo "No")
- **Docker Compose Available**: $(command -v docker-compose &>/dev/null && echo "Yes" || echo "No")
- **Python Version**: $(python --version 2>&1)
- **Pytest Version**: $(pytest --version 2>&1)

## Files Tested
EOF

    # Add file listing based on category
    case "$category" in
        "dockerignore")
            echo "- Service-specific .dockerignore files" >> "$report_file"
            find "$PROJECT_ROOT/docker" -name ".dockerignore" >> "$report_file"
            ;;
        "all")
            echo "- All Docker test files" >> "$report_file"
            find "$TEST_DIR" -name "*docker*.py" >> "$report_file"
            ;;
        *)
            echo "- Category-specific test files" >> "$report_file"
            ;;
    esac
    
    log_info "Test report generated: $report_file"
}

# Parse command line arguments
parse_arguments() {
    local category=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --coverage|-c)
                COVERAGE=true
                shift
                ;;
            --parallel|-p)
                PARALLEL=true
                shift
                ;;
            --slow)
                SLOW_TESTS=true
                shift
                ;;
            --integration)
                INTEGRATION_TESTS=true
                shift
                ;;
            --stress)
                STRESS_TESTS=true
                shift
                ;;
            --help|-h)
                print_usage
                exit 0
                ;;
            --*)
                log_error "Unknown option: $1"
                print_usage
                exit 1
                ;;
            *)
                if [[ -z "$category" ]]; then
                    category="$1"
                else
                    log_error "Multiple categories not supported: $1"
                    exit 1
                fi
                shift
                ;;
        esac
    done
    
    # Default to smoke tests if no category specified
    if [[ -z "$category" ]]; then
        category="smoke"
    fi
    
    # Validate category
    if [[ ! -v TEST_CATEGORIES["$category"] ]]; then
        log_error "Invalid test category: $category"
        echo
        print_usage
        exit 1
    fi
    
    echo "$category"
}

# Main execution
main() {
    local category
    category=$(parse_arguments "$@")
    
    print_header
    
    check_prerequisites
    run_docker_environment_check
    
    echo
    log_test "Starting test category: $category"
    log_info "Description: ${TEST_CATEGORIES[$category]}"
    echo
    
    local start_time
    start_time=$(date +%s)
    
    local result="FAILED"
    if run_test_category "$category"; then
        result="PASSED"
    fi
    
    local end_time
    end_time=$(date +%s)
    
    echo
    log_result "Test execution completed"
    log_result "Category: $category"
    log_result "Result: $result"
    log_result "Duration: $((end_time - start_time)) seconds"
    
    # Generate report
    generate_test_report "$category" "$result" "$start_time" "$end_time"
    
    if [[ "$result" == "PASSED" ]]; then
        log_success "All tests passed! 🎉"
        exit 0
    else
        log_error "Some tests failed! ❌"
        exit 1
    fi
}

# Execute main function
main "$@"
