#!/bin/bash
# Automated Cleanup Script for Horse Racing AI v2.05
# Safely removes redundant files and organizes project structure

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_ROOT/cleanup_backup_$TIMESTAMP"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

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

# Create safety backup
create_safety_backup() {
    log "🔄 Creating safety backup before cleanup..."
    
    # Create backup directory
    mkdir -p "$BACKUP_DIR"
    
    # Create list of files to be cleaned up
    cat > "$BACKUP_DIR/cleanup_manifest.txt" << EOF
Cleanup Backup Manifest - $(date)
========================================

Files backed up before cleanup:

DUPLICATE FLOWS:
$(find . -maxdepth 1 -name "*flow*.json" -o -name "*flows*.json" | sort)

DEVELOPMENT TEST FILES:
$(find . -maxdepth 1 -name "test_*exec*" -o -name "test_*c2*" | sort)

EMPTY/TEMP FILES:
$(find . -maxdepth 1 -name "merged_flows.json" -o -name "working-c2-flows.json" | sort)

TEMP DIRECTORIES:
$(find . -type d -name "temp_*" | sort)

Total files/directories in scope: $(find . -maxdepth 1 -name "*flow*.json" -o -name "*flows*.json" -o -name "test_*exec*" -o -name "test_*c2*" -o -name "merged_flows.json" -o -name "working-c2-flows.json" | wc -l)
EOF
    
    # Copy important files to backup
    for file in *flow*.json *flows*.json test_*exec* test_*c2* merged_flows.json working-c2-flows.json; do
        if [ -f "$file" ]; then
            cp "$file" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done
    
    # Backup temp directories
    for temp_dir in temp_*; do
        if [ -d "$temp_dir" ]; then
            cp -r "$temp_dir" "$BACKUP_DIR/" 2>/dev/null || true
        fi
    done
    
    log "✅ Safety backup created: $BACKUP_DIR"
}

# Create archive structure
create_archive_structure() {
    log "🔄 Creating archive directory structure..."
    
    cd "$PROJECT_ROOT"
    
    # Create main archive directories
    mkdir -p archive/{node_red_development,development_tests,temp_data_backup,old_reports}
    
    info "📁 Created archive structure:"
    info "   archive/node_red_development/   - Old Node-RED flows"
    info "   archive/development_tests/      - Development test files"
    info "   archive/temp_data_backup/       - Temporary data backups"
    info "   archive/old_reports/            - Historical reports"
    
    # Create protected directories list
    cat > "$PROJECT_ROOT/PROTECTED_DIRECTORIES.txt" << EOF
# Protected Directories - DO NOT CLEAN
# These directories contain critical data and should be preserved

CRITICAL DATA DIRECTORIES:
- data/raw_csv_archives/     # ZIP archives of raw CSV racing data
- data/2025-08-*/           # Daily racing data directories
- data/processed/           # Processed racing data
- data/daily_downloads/     # Daily download tracking

CRITICAL SCHEMA FILES:
- AI_SCHEMA.sql            # Database schema definition

ACTIVE NODE-RED FLOWS (KEEP):
- clean_working_flows.json          # Clean working version
- deploy_ready_pipeline_automation.json  # Production ready flows
- database_config_flows.json        # Database configuration
- simple_test_flows.json           # Simple test flows
- test_flows.json                  # Core test flows

CRITICAL JSON DATA:
- api_load_test_results_*.json     # Performance test results

Note: Only duplicate/development flows will be archived, not active production flows.
EOF
    
    log "✅ Archive structure created with protection list"
}

# Clean duplicate Node-RED flows
clean_duplicate_flows() {
    log "🔄 Cleaning duplicate Node-RED flow files (preserving active flows)..."
    
    cd "$PROJECT_ROOT"
    
    # Protected flows to keep (critical for operation)
    local protected_flows=(
        "clean_working_flows.json"
        "deploy_ready_pipeline_automation.json"
        "database_config_flows.json"
        "simple_test_flows.json"
        "test_flows.json"
        "AI_SCHEMA.sql"
    )
    
    # List of duplicate/development flow files to archive
    local flow_files=(
        "backup_flows_20250830_200940.json"
        "c2_enhanced_flows.json"
        "current_flows.json" 
        "current_flows_backup.json"
        "current_flows_before_redis.json"
        "flows_c2_with_ml_trainer.json"
        "flows_c2_with_pipeline.json"
        "flows_c2_with_redis.json"
        "flows_c2_with_web_app_20250830_192658.json"
        "flows_redis_health_fixed.json"
        "flows_with_redis_health.json"
        "flows_with_redis_tab.json"
        "merged_flows.json"
        "merged_flows_with_debug.json"
        "new_health_flows.json"
        "pipeline_automation_flows.json"
        "updated_flows.json"
        "working-c2-flows.json"
        "working_flows_from_dev.json"
        "debug_flows.json"
    )
    
    info "🛡️ Protected files (will NOT be cleaned):"
    for protected in "${protected_flows[@]}"; do
        if [ -f "$protected" ]; then
            info "   ✓ $protected"
        fi
    done
    
    local moved_count=0
    local total_size=0
    
    for file in "${flow_files[@]}"; do
        if [ -f "$file" ]; then
            # Double-check it's not in protected list
            local is_protected=false
            for protected in "${protected_flows[@]}"; do
                if [ "$file" = "$protected" ]; then
                    is_protected=true
                    break
                fi
            done
            
            if [ "$is_protected" = false ]; then
                # Get file size for reporting
                local size
                size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo 0)
                total_size=$((total_size + size))
                
                # Move to archive
                mv "$file" "archive/node_red_development/"
                info "📦 Archived: $file"
                ((moved_count++))
            else
                warn "Skipped protected file: $file"
            fi
        fi
    done
    
    # Create archive index
    cat > "archive/node_red_development/ARCHIVE_INDEX.md" << EOF
# Node-RED Development Files Archive

**Archived:** $(date)  
**Reason:** Cleanup duplicate/development flow files (protected active flows)

## Protected Files (NOT archived):
$(for protected in "${protected_flows[@]}"; do [ -f "$protected" ] && echo "- $protected ✓" || echo "- $protected (not found)"; done)

## Archived Files:
$(ls -la archive/node_red_development/*.json 2>/dev/null | awk '{print "- " $9 " (" $5 " bytes)"}' || echo "No files")

## Usage:
These files are preserved for reference but are not actively used:
- Development versions of Node-RED flows
- Backup files from various development stages
- Experimental flow configurations

## Restoration:
To restore any file: \`cp archive/node_red_development/[filename] ./\`

Total archived: $moved_count files ($(echo "scale=2; $total_size/1024" | bc 2>/dev/null || echo "unknown") KB)
EOF
    
    log "✅ Archived $moved_count duplicate flow files ($(echo "scale=1; $total_size/1024" | bc 2>/dev/null || echo "unknown") KB)"
    log "🛡️ Protected $(echo "${protected_flows[@]}" | wc -w) critical flow files"
}
            
            # Move to archive
            mv "$file" "archive/node_red_development/"
            info "📦 Archived: $file"
            ((moved_count++))
        fi
    done
    
    # Create archive index
    cat > "archive/node_red_development/ARCHIVE_INDEX.md" << EOF
# Node-RED Development Files Archive

**Archived:** $(date)  
**Reason:** Cleanup duplicate/development flow files

## Archived Files:
$(ls -la archive/node_red_development/*.json 2>/dev/null | awk '{print "- " $9 " (" $5 " bytes)"}' || echo "No files")

## Usage:
These files are preserved for reference but are not actively used:
- Development versions of Node-RED flows
- Backup files from various development stages
- Experimental flow configurations

## Restoration:
To restore any file: \`cp archive/node_red_development/[filename] ./\`

Total archived: $moved_count files ($(echo "scale=2; $total_size/1024" | bc 2>/dev/null || echo "unknown") KB)
EOF
    
    log "✅ Archived $moved_count duplicate flow files ($(echo "scale=1; $total_size/1024" | bc 2>/dev/null || echo "unknown") KB)"
}

# Clean development test files
clean_development_tests() {
    log "🔄 Cleaning development test files..."
    
    cd "$PROJECT_ROOT"
    
    # Development test files to archive
    local test_patterns=(
        "test_direct_exec.py"
        "test_exec_node.json"
        "test_exec_node_readiness.py"
        "test_ml_trainer_c2_integration.py"
        "test_pipeline_c2_integration.py"
        "test_redis_c2_integration.py"
        "test_web_app_c2_integration.py"
    )
    
    local moved_count=0
    
    for pattern in "${test_patterns[@]}"; do
        if [ -f "$pattern" ]; then
            mv "$pattern" "archive/development_tests/"
            info "📦 Archived: $pattern"
            ((moved_count++))
        fi
    done
    
    # Archive any remaining test_*c2* files
    for file in test_*c2*; do
        if [ -f "$file" ] && [ ! -f "archive/development_tests/$file" ]; then
            mv "$file" "archive/development_tests/"
            info "📦 Archived: $file"
            ((moved_count++))
        fi
    done
    
    # Create archive index
    cat > "archive/development_tests/ARCHIVE_INDEX.md" << EOF
# Development Test Files Archive

**Archived:** $(date)  
**Reason:** Cleanup old development test files

## Archived Files:
$(ls -la archive/development_tests/*.py archive/development_tests/*.json 2>/dev/null | awk '{print "- " $9 " (" $5 " bytes)"}' || echo "No files")

## Usage:
These are development test files no longer in active use:
- C2 integration tests (superseded by automation tests)
- Exec node testing files  
- Development validation scripts

## Notes:
- Current testing uses tests/automation/ directory
- These files preserved for reference only

Total archived: $moved_count files
EOF
    
    log "✅ Archived $moved_count development test files"
}

# Clean temporary data directories
clean_temp_data() {
    log "🔄 Cleaning temporary data directories..."
    
    cd "$PROJECT_ROOT"
    
    local cleaned_size=0
    local cleaned_dirs=0
    
    # Handle temp_extract
    if [ -d "temp_extract" ]; then
        # Check if contains unique data
        if [ "$(find temp_extract -name "*.csv" | wc -l)" -gt 0 ]; then
            warn "Found CSV files in temp_extract - archiving before cleanup"
            cp -r temp_extract archive/temp_data_backup/
            info "📦 Archived temp_extract/ data"
        fi
        
        local size
        size=$(du -sb temp_extract 2>/dev/null | cut -f1 || echo 0)
        cleaned_size=$((cleaned_size + size))
        rm -rf temp_extract
        info "🗑️ Removed temp_extract/"
        ((cleaned_dirs++))
    fi
    
    # Handle temp_card_processing
    if [ -d "temp_card_processing" ]; then
        if [ "$(find temp_card_processing -name "*.csv" | wc -l)" -gt 0 ]; then
            warn "Found CSV files in temp_card_processing - archiving before cleanup"
            cp -r temp_card_processing archive/temp_data_backup/
            info "📦 Archived temp_card_processing/ data"
        fi
        
        local size
        size=$(du -sb temp_card_processing 2>/dev/null | cut -f1 || echo 0)
        cleaned_size=$((cleaned_size + size))
        rm -rf temp_card_processing
        info "🗑️ Removed temp_card_processing/"
        ((cleaned_dirs++))
    fi
    
    # Create archive index if we archived anything
    if [ -d "archive/temp_data_backup/temp_extract" ] || [ -d "archive/temp_data_backup/temp_card_processing" ]; then
        cat > "archive/temp_data_backup/ARCHIVE_INDEX.md" << EOF
# Temporary Data Backup Archive

**Archived:** $(date)  
**Reason:** Cleanup temporary processing directories

## Archived Directories:
$(for dir in archive/temp_data_backup/*/; do [ -d "$dir" ] && echo "- $(basename "$dir")" || true; done)

## Contents:
- CSV data files from temporary processing
- Intermediate pipeline processing files
- Data extracted during development

## Usage:
These are temporary files that were preserved in case they contain unique data:
- Check contents before permanent deletion
- May contain test data from development phases

Total directories cleaned: $cleaned_dirs ($(echo "scale=1; $cleaned_size/1024/1024" | bc 2>/dev/null || echo "unknown") MB)
EOF
    fi
    
    log "✅ Cleaned $cleaned_dirs temporary directories ($(echo "scale=1; $cleaned_size/1024/1024" | bc 2>/dev/null || echo "unknown") MB)"
}

# Generate cleanup report
generate_cleanup_report() {
    log "📊 Generating cleanup completion report..."
    
    cat > "$PROJECT_ROOT/CLEANUP_COMPLETION_REPORT.md" << EOF
# Project Cleanup Completion Report

**Date:** $(date)  
**Project:** Horse Racing AI v2.05  
**Operation:** Automated file cleanup and organization

## ✅ **Completed Operations**

### **Safety Backup Created ✅**
- Backup location: \`$(basename "$BACKUP_DIR")\`
- All cleaned files preserved before removal
- Complete cleanup manifest generated

### **Archive Structure ✅**
- \`archive/node_red_development/\` - Duplicate Node-RED flows
- \`archive/development_tests/\` - Old development test files
- \`archive/temp_data_backup/\` - Archived temporary data
- \`archive/old_reports/\` - Ready for future use

### **Duplicate Flows Cleaned ✅**
$(if [ -d "archive/node_red_development" ]; then
    echo "- Archived: $(ls archive/node_red_development/*.json 2>/dev/null | wc -l) flow files"
    echo "- Location: \`archive/node_red_development/\`"
else
    echo "- No duplicate flows found to clean"
fi)

### **Development Tests Cleaned ✅**
$(if [ -d "archive/development_tests" ]; then
    echo "- Archived: $(ls archive/development_tests/*.py archive/development_tests/*.json 2>/dev/null | wc -l) test files"
    echo "- Location: \`archive/development_tests/\`"
else
    echo "- No development tests found to clean"
fi)

### **Temporary Data Cleaned ✅**
$(if [ -d "archive/temp_data_backup" ]; then
    echo "- Cleaned temporary directories with data preservation"
    echo "- Archive: \`archive/temp_data_backup/\`"
else
    echo "- No temporary directories found to clean"
fi)

## 📊 **Current Project Structure**

\`\`\`
$(find . -maxdepth 2 -type d | grep -E "^\./(data|tests|tools|config|docs|archive)" | sort || echo "Basic structure maintained")
\`\`\`

## 🎯 **Benefits Achieved**

### **Organization Improvements:**
- 🗂️ Clear separation of active vs. archived files
- 📁 Logical archive structure for future reference
- 🔍 Easier navigation of project files

### **Performance Benefits:**
- ⚡ Reduced file count in root directory
- 💾 Cleaned unnecessary temporary data
- 📊 Optimized for development workflows

### **Maintenance Benefits:**
- 📝 All cleanup actions documented
- 💾 Complete backup preserved
- 🔄 Reversible operations if needed

## 🚀 **Next Steps**

1. **Execute data reorganization:** \`./reorganize_data_structure.sh\`
2. **Verify critical functionality** after cleanup
3. **Update development workflows** if needed
4. **Consider data reorganization** for optimal structure

## 📁 **Key Locations After Cleanup**

- **Active Development:** Root directory (cleaned)
- **Archived Flows:** \`archive/node_red_development/\`
- **Archived Tests:** \`archive/development_tests/\`
- **Temp Data Backup:** \`archive/temp_data_backup/\`
- **Safety Backup:** \`$(basename "$BACKUP_DIR")\`

## ⚠️ **Recovery Instructions**

If any cleaned file is needed:
1. Check appropriate archive directory
2. Copy file back to root: \`cp archive/[category]/[filename] ./\`
3. Refer to safety backup: \`$(basename "$BACKUP_DIR")\`

---

**Project cleanup completed successfully. Development environment optimized for efficient Horse Racing AI v2.05 development.**
EOF
    
    log "✅ Cleanup report generated: CLEANUP_COMPLETION_REPORT.md"
}

# Main execution
main() {
    log "🚀 Starting Horse Racing AI v2.05 Automated Cleanup"
    echo
    
    warn "This will clean up duplicate and temporary files. All files will be safely archived."
    echo
    info "Operations to perform:"
    info "  1. Create safety backup of all files to be cleaned"
    info "  2. Archive duplicate Node-RED flow files"
    info "  3. Archive old development test files"
    info "  4. Clean temporary data directories (with data preservation)"
    info "  5. Generate comprehensive cleanup report"
    echo
    
    read -p "Continue with automated cleanup? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Cleanup cancelled by user"
        exit 0
    fi
    
    echo
    log "Starting cleanup process..."
    
    # Execute all cleanup phases
    create_safety_backup
    create_archive_structure
    clean_duplicate_flows
    clean_development_tests
    clean_temp_data
    generate_cleanup_report
    
    echo
    success "🎉 Automated cleanup completed successfully!"
    echo
    info "📋 Review the complete report: CLEANUP_COMPLETION_REPORT.md"
    info "💾 Safety backup preserved: $(basename "$BACKUP_DIR")"
    info "📁 Archived files preserved in: archive/"
    echo
    log "✅ Project now optimized for efficient development!"
    echo
    warn "🔄 Next step: Run ./reorganize_data_structure.sh for data organization"
}

# Execute main function
main "$@"
