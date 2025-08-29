#!/bin/bash
# Horse Racing AI - Project Audit Runner
# Quick start script for project audit and cleanup

set -e

# Configuration
PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.04"
PYTHON_CMD="python3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_header() {
    echo -e "${BLUE}🔍 Horse Racing AI - Project Audit${NC}"
    echo "======================================"
}

print_success() {
    echo -e "${GREEN}✅${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️${NC} $1"
}

print_error() {
    echo -e "${RED}❌${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ️${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v $PYTHON_CMD &> /dev/null; then
        print_error "Python 3 not found"
        exit 1
    fi
    
    # Check if we're in the right directory
    if [ ! -f "$PROJECT_ROOT/tools/versioning/project_auditor.py" ]; then
        print_error "Audit tools not found. Please run from project root."
        exit 1
    fi
    
    # Check required Python packages
    $PYTHON_CMD -c "import json, pathlib, subprocess" 2>/dev/null || {
        print_error "Required Python packages not available"
        exit 1
    }
    
    print_success "Prerequisites check passed"
}

# Main menu
show_menu() {
    echo
    echo "📋 Available Audit Operations:"
    echo "1. 🔍 Run Dependency Analysis Only"
    echo "2. 📊 Run Usage Tracking Only" 
    echo "3. 🧹 Run Complete Audit (Dry Run)"
    echo "4. ⚡ Run Complete Audit with Cleanup"
    echo "5. 🔧 Run System Validation Only"
    echo "6. 📄 Generate Reports Only"
    echo "7. ❓ Show Help"
    echo "0. ❌ Exit"
    echo
}

# Run dependency analysis only
run_dependency_analysis() {
    print_info "Running dependency analysis..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD tools/versioning/dependency_mapper.py --project-root "$PROJECT_ROOT"
    print_success "Dependency analysis complete"
}

# Run usage tracking only
run_usage_tracking() {
    print_info "Running usage tracking..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD tools/versioning/usage_tracker.py --project-root "$PROJECT_ROOT" --scan --report
    print_success "Usage tracking complete"
}

# Run complete audit (dry run)
run_complete_audit_dry() {
    print_info "Running complete audit (dry run - no files will be modified)..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD tools/versioning/project_auditor.py --project-root "$PROJECT_ROOT"
    print_success "Complete audit (dry run) finished"
}

# Run complete audit with cleanup
run_complete_audit_execute() {
    print_warning "This will modify files in your project!"
    echo "A backup will be created before any changes."
    echo
    read -p "Are you sure you want to proceed? [y/N]: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Running complete audit with cleanup execution..."
        cd "$PROJECT_ROOT"
        $PYTHON_CMD tools/versioning/project_auditor.py --project-root "$PROJECT_ROOT" --execute
        print_success "Complete audit with cleanup finished"
    else
        print_info "Audit cancelled by user"
    fi
}

# Run system validation only
run_system_validation() {
    print_info "Running system validation..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD tools/versioning/cleanup_validator.py --project-root "$PROJECT_ROOT"
    print_success "System validation complete"
}

# Generate reports only
generate_reports() {
    print_info "Generating audit reports..."
    
    # Create output directory
    mkdir -p "$PROJECT_ROOT/data/audit"
    
    echo "📊 Generating dependency analysis report..."
    cd "$PROJECT_ROOT"
    $PYTHON_CMD tools/versioning/dependency_mapper.py --project-root "$PROJECT_ROOT" >/dev/null 2>&1 || true
    
    echo "📈 Generating usage tracking report..."
    $PYTHON_CMD tools/versioning/usage_tracker.py --project-root "$PROJECT_ROOT" --export >/dev/null 2>&1 || true
    
    echo "🔧 Running quick system validation..."
    $PYTHON_CMD tools/versioning/cleanup_validator.py --project-root "$PROJECT_ROOT" --quick >/dev/null 2>&1 || true
    
    print_success "Reports generated in data/audit/"
    
    # List generated files
    echo
    echo "📄 Generated files:"
    find "$PROJECT_ROOT/data/audit" -name "*.json" -o -name "*.md" | sort | tail -10 | while read file; do
        echo "  $(basename "$file")"
    done
}

# Show help
show_help() {
    echo
    echo "🔍 Horse Racing AI Project Audit Help"
    echo "====================================="
    echo
    echo "This tool helps you audit and clean up the Horse Racing AI project by:"
    echo "• Analyzing file dependencies and relationships"
    echo "• Tracking which files are actually used by the system"
    echo "• Identifying safe candidates for removal"
    echo "• Creating backups before any changes"
    echo "• Validating system integrity after cleanup"
    echo
    echo "📁 File Locations:"
    echo "• Audit reports: data/audit/"
    echo "• Backups: data/backups/"
    echo "• Version tracking: data/versions/"
    echo
    echo "🛡️ Safety Features:"
    echo "• Dry run mode by default"
    echo "• Automatic backups before changes"
    echo "• Comprehensive system validation"
    echo "• Rollback capabilities"
    echo
    echo "⚡ Quick Start:"
    echo "1. Run option 3 (Complete Audit Dry Run) first"
    echo "2. Review the generated reports"
    echo "3. If satisfied, run option 4 (Execute Cleanup)"
    echo
}

# Main execution
main() {
    print_header
    check_prerequisites
    
    while true; do
        show_menu
        read -p "Select an option [0-7]: " choice
        
        case $choice in
            1)
                run_dependency_analysis
                ;;
            2)
                run_usage_tracking
                ;;
            3)
                run_complete_audit_dry
                ;;
            4)
                run_complete_audit_execute
                ;;
            5)
                run_system_validation
                ;;
            6)
                generate_reports
                ;;
            7)
                show_help
                ;;
            0)
                print_info "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid option. Please select 0-7."
                ;;
        esac
        
        echo
        read -p "Press Enter to continue..."
    done
}

# Run main function
main "$@"
