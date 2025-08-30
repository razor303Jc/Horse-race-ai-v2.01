#!/bin/bash
# Enhanced Data Processor v2.05 - Management Script
# Version Tag: latest:v2.05
# Latest Version Data Processing Management System
#
# This script provides easy management and execution of the 
# Enhanced Data Processor v2.05 for Horse Racing AI system
#
# Features:
# - File processing with validation
# - Batch processing capabilities  
# - Database upload management
# - Report generation and monitoring
# - Error handling and recovery
# - Standardized -0 NULL mapping for ML model compatibility

set -e

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
PROCESSOR_SCRIPT="$PROJECT_ROOT/tools/data_processing/enhanced_data_processor_v2_05.py"
DATA_DIR="$PROJECT_ROOT/data"
LOG_DIR="$PROJECT_ROOT/logs"
VERSION="v2.05"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function definitions
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING:${NC} $1"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR:${NC} $1"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO:${NC} $1"
}

success() {
    echo -e "${PURPLE}[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS:${NC} $1"
}

check_prerequisites() {
    log "🔍 Checking prerequisites..."
    
    # Check if processor script exists
    if [ ! -f "$PROCESSOR_SCRIPT" ]; then
        error "Data processor script not found: $PROCESSOR_SCRIPT"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        error "Python3 is not installed"
        exit 1
    fi
    
    # Check required Python modules
    if ! python3 -c "import pandas, numpy, redis, psycopg2" &> /dev/null; then
        warn "Some required Python modules may be missing"
        info "Install with: pip install pandas numpy redis psycopg2-binary"
    fi
    
    # Create necessary directories
    mkdir -p "$LOG_DIR/processing_reports"
    mkdir -p "$DATA_DIR/processed"
    mkdir -p "$DATA_DIR/quarantine"
    
    log "✅ Prerequisites check completed"
}

extract_date_from_filename() {
    local filename="$1"
    # Extract YYYY-MM-DD pattern from filename
    if [[ $filename =~ ([0-9]{4}-[0-9]{2}-[0-9]{2}) ]]; then
        echo "${BASH_REMATCH[1]}"
    else
        echo ""
    fi
}

validate_date_format() {
    local date_str="$1"
    if [[ $date_str =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
        return 0
    else
        return 1
    fi
}

process_single_file() {
    local file_path="$1"
    local expected_date="$2"
    local upload_flag="$3"
    
    if [ ! -f "$file_path" ]; then
        error "File not found: $file_path"
        return 1
    fi
    
    log "🔄 Processing file: $(basename "$file_path")"
    
    # Extract date from filename if not provided
    if [ -z "$expected_date" ]; then
        expected_date=$(extract_date_from_filename "$(basename "$file_path")")
        if [ -n "$expected_date" ]; then
            info "📅 Extracted date from filename: $expected_date"
        fi
    fi
    
    # Validate date format
    if [ -n "$expected_date" ] && ! validate_date_format "$expected_date"; then
        error "Invalid date format: $expected_date (expected YYYY-MM-DD)"
        return 1
    fi
    
    # Build command
    local cmd="python3 $PROCESSOR_SCRIPT '$file_path'"
    
    if [ -n "$expected_date" ]; then
        cmd="$cmd --expected-date '$expected_date'"
    fi
    
    if [ "$upload_flag" = "true" ]; then
        cmd="$cmd --upload"
        info "📤 Database upload enabled"
    else
        cmd="$cmd --report-only"
        info "📄 Report-only mode"
    fi
    
    # Execute processing
    log "⚙️ Executing: $cmd"
    
    if eval "$cmd"; then
        success "✅ Processing completed successfully"
        
        # Move processed file to processed directory
        local processed_dir="$DATA_DIR/processed/$(date +%Y-%m-%d)"
        mkdir -p "$processed_dir"
        cp "$file_path" "$processed_dir/"
        
        return 0
    else
        error "❌ Processing failed"
        
        # Move failed file to quarantine
        local quarantine_dir="$DATA_DIR/quarantine/$(date +%Y-%m-%d)"
        mkdir -p "$quarantine_dir"
        cp "$file_path" "$quarantine_dir/"
        
        return 1
    fi
}

process_directory() {
    local dir_path="$1"
    local expected_date="$2"
    local upload_flag="$3"
    
    if [ ! -d "$dir_path" ]; then
        error "Directory not found: $dir_path"
        return 1
    fi
    
    log "📁 Processing directory: $dir_path"
    
    # Find ZIP files
    local zip_files=()
    while IFS= read -r -d '' file; do
        zip_files+=("$file")
    done < <(find "$dir_path" -name "*.zip" -type f -print0)
    
    if [ ${#zip_files[@]} -eq 0 ]; then
        warn "No ZIP files found in directory"
        return 1
    fi
    
    log "📦 Found ${#zip_files[@]} ZIP files"
    
    # Process each file
    local success_count=0
    local failure_count=0
    
    for zip_file in "${zip_files[@]}"; do
        log "Processing: $(basename "$zip_file")"
        
        if process_single_file "$zip_file" "$expected_date" "$upload_flag"; then
            ((success_count++))
        else
            ((failure_count++))
        fi
        
        echo # Add blank line for readability
    done
    
    # Summary
    log "📊 Batch processing summary:"
    success "  ✅ Successful: $success_count"
    if [ $failure_count -gt 0 ]; then
        error "  ❌ Failed: $failure_count"
    fi
    
    return $failure_count
}

list_available_files() {
    log "📋 Available files for processing:"
    
    local count=0
    for date_dir in "$DATA_DIR"/20*; do
        if [ -d "$date_dir" ]; then
            local date_name=$(basename "$date_dir")
            echo -e "${CYAN}📅 $date_name:${NC}"
            
            for zip_file in "$date_dir"/*.zip; do
                if [ -f "$zip_file" ]; then
                    local size=$(du -h "$zip_file" | cut -f1)
                    echo "  📦 $(basename "$zip_file") ($size)"
                    ((count++))
                fi
            done
        fi
    done
    
    if [ $count -eq 0 ]; then
        warn "No ZIP files found in data directory"
    else
        log "Total files found: $count"
    fi
}

show_processing_reports() {
    local reports_dir="$LOG_DIR/processing_reports"
    
    if [ ! -d "$reports_dir" ]; then
        warn "No processing reports directory found"
        return 1
    fi
    
    log "📄 Recent processing reports:"
    
    # Show last 10 text reports
    find "$reports_dir" -name "processing_report_*.txt" -type f | \
        sort -r | head -10 | while read -r report; do
        local report_name=$(basename "$report")
        local report_date=$(echo "$report_name" | grep -o '[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}')
        local report_time=$(echo "$report_name" | grep -o '[0-9]\{8\}_[0-9]\{6\}')
        local size=$(du -h "$report" | cut -f1)
        
        echo "  📄 $report_date $report_time ($size)"
    done
}

view_latest_report() {
    local reports_dir="$LOG_DIR/processing_reports"
    
    local latest_report=$(find "$reports_dir" -name "processing_report_*.txt" -type f | sort -r | head -1)
    
    if [ -z "$latest_report" ]; then
        warn "No processing reports found"
        return 1
    fi
    
    log "📄 Latest processing report:"
    echo
    cat "$latest_report"
}

monitor_processing() {
    log "📊 Starting processing monitor..."
    
    local log_file="$LOG_DIR/data_processor_v2_05.log"
    
    if [ ! -f "$log_file" ]; then
        warn "Log file not found: $log_file"
        return 1
    fi
    
    log "📄 Following log file (Press Ctrl+C to stop):"
    tail -f "$log_file"
}

validate_system() {
    log "🔍 Running system validation..."
    
    check_prerequisites
    
    # Test with a sample file if available
    local sample_file=$(find "$DATA_DIR" -name "*.zip" -type f | head -1)
    
    if [ -n "$sample_file" ]; then
        log "🧪 Testing with sample file: $(basename "$sample_file")"
        
        # Run in report-only mode for validation
        if python3 "$PROCESSOR_SCRIPT" "$sample_file" --report-only > /tmp/validation_test.log 2>&1; then
            success "✅ System validation passed"
            return 0
        else
            error "❌ System validation failed"
            echo "Error details:"
            cat /tmp/validation_test.log
            return 1
        fi
    else
        warn "No sample files available for testing"
        log "✅ Basic system validation completed"
        return 0
    fi
}

show_help() {
    echo
    echo -e "${PURPLE}Enhanced Data Processor $VERSION - Management Script${NC}"
    echo
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo
    echo -e "${CYAN}Commands:${NC}"
    echo "  process <file> [date] [--upload]    Process a single ZIP file"
    echo "  batch <directory> [date] [--upload] Process all ZIP files in directory"
    echo "  list                                List available files"
    echo "  reports                             Show recent processing reports"
    echo "  latest                              View latest processing report"
    echo "  monitor                             Monitor processing in real-time"
    echo "  validate                            Validate system setup"
    echo "  help                                Show this help message"
    echo
    echo -e "${CYAN}Options:${NC}"
    echo "  [date]        Expected date in YYYY-MM-DD format"
    echo "  --upload      Upload processed data to database"
    echo
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 process data/2025-08-20/results_*.zip"
    echo "  $0 process data/2025-08-20/results_*.zip 2025-08-19"
    echo "  $0 process data/2025-08-20/results_*.zip 2025-08-19 --upload"
    echo "  $0 batch data/2025-08-20/ --upload"
    echo "  $0 list"
    echo "  $0 latest"
    echo
}

# Main command handling
case "${1:-help}" in
    process)
        if [ $# -lt 2 ]; then
            error "Usage: $0 process <file> [date] [--upload]"
            exit 1
        fi
        
        check_prerequisites
        
        file_path="$2"
        expected_date="$3"
        upload_flag="false"
        
        # Check for --upload flag
        if [[ "$3" == "--upload" ]] || [[ "$4" == "--upload" ]]; then
            upload_flag="true"
        fi
        
        # If third argument is date and fourth is --upload
        if [[ "$3" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            expected_date="$3"
        fi
        
        process_single_file "$file_path" "$expected_date" "$upload_flag"
        ;;
        
    batch)
        if [ $# -lt 2 ]; then
            error "Usage: $0 batch <directory> [date] [--upload]"
            exit 1
        fi
        
        check_prerequisites
        
        dir_path="$2"
        expected_date="$3"
        upload_flag="false"
        
        # Check for --upload flag
        if [[ "$3" == "--upload" ]] || [[ "$4" == "--upload" ]]; then
            upload_flag="true"
        fi
        
        # If third argument is date and fourth is --upload
        if [[ "$3" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
            expected_date="$3"
        fi
        
        process_directory "$dir_path" "$expected_date" "$upload_flag"
        ;;
        
    list)
        list_available_files
        ;;
        
    reports)
        show_processing_reports
        ;;
        
    latest)
        view_latest_report
        ;;
        
    monitor)
        monitor_processing
        ;;
        
    validate)
        validate_system
        ;;
        
    help|--help|-h)
        show_help
        ;;
        
    *)
        error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
