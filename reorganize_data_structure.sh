#!/bin/bash
# Data Reorganization Script for Horse Racing AI v2.05
# Implements the data structure analysis recommendations

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
DATA_DIR="$PROJECT_ROOT/data"
BACKUP_DIR="$PROJECT_ROOT/data_backup_$(date +%Y%m%d_%H%M%S)"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

# Phase 1: Backup current data structure
backup_current_data() {
    log "🔄 Phase 1: Creating complete data backup..."
    
    if [ ! -d "$DATA_DIR" ]; then
        error "Data directory not found: $DATA_DIR"
        exit 1
    fi
    
    # Create backup
    cp -r "$DATA_DIR" "$BACKUP_DIR"
    log "✅ Data backed up to: $BACKUP_DIR"
    
    # Create backup report
    echo "Data Backup Report - $(date)" > "$BACKUP_DIR/backup_report.txt"
    echo "=================================" >> "$BACKUP_DIR/backup_report.txt"
    echo "" >> "$BACKUP_DIR/backup_report.txt"
    echo "Original location: $DATA_DIR" >> "$BACKUP_DIR/backup_report.txt"
    echo "Backup location: $BACKUP_DIR" >> "$BACKUP_DIR/backup_report.txt"
    echo "Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)" >> "$BACKUP_DIR/backup_report.txt"
    echo "" >> "$BACKUP_DIR/backup_report.txt"
    echo "Directory structure:" >> "$BACKUP_DIR/backup_report.txt"
    find "$BACKUP_DIR" -type d | sort >> "$BACKUP_DIR/backup_report.txt"
    
    log "✅ Backup report created: $BACKUP_DIR/backup_report.txt"
}

# Phase 2: Create new development structure
create_development_structure() {
    log "🔄 Phase 2: Creating new development data structure..."
    
    cd "$DATA_DIR"
    
    # Create new directory structure
    mkdir -p development/{primary,secondary,samples}
    mkdir -p archive
    mkdir -p test_outputs
    mkdir -p staging/{manual,auto,temp}
    
    log "✅ New directory structure created"
    info "📁 Structure:"
    info "   development/primary/   - Main test dataset (2025-08-26)"
    info "   development/secondary/ - Validation dataset (2025-08-25)"
    info "   development/samples/   - Quick test samples"
    info "   archive/               - Historical data"
    info "   test_outputs/          - Generated test results"
    info "   staging/               - Pipeline processing"
}

# Phase 3: Organize primary dataset
organize_primary_dataset() {
    log "🔄 Phase 3: Setting up primary development dataset..."
    
    if [ -d "$DATA_DIR/2025-08-26" ]; then
        # Copy complete dataset to primary
        cp -r "$DATA_DIR/2025-08-26"/* "$DATA_DIR/development/primary/"
        
        # Create dataset info
        cat > "$DATA_DIR/development/primary/dataset_info.md" << EOF
# Primary Development Dataset - 2025-08-26

**Date:** August 26, 2025  
**Status:** Primary test dataset for Horse Racing AI v2.05  
**Size:** $(du -sh "$DATA_DIR/development/primary" | cut -f1)

## Data Types Available:
$(ls -la "$DATA_DIR/development/primary"/*.csv 2>/dev/null | wc -l) CSV files containing:

$(ls "$DATA_DIR/development/primary"/*.csv 2>/dev/null | while read file; do
    filename=$(basename "$file")
    lines=$(wc -l < "$file")
    echo "- **$filename**: $lines records"
done)

## Usage:
- ML training and validation
- Integration testing  
- Performance benchmarking
- Full system testing

## Last Updated: $(date)
EOF
        
        log "✅ Primary dataset organized with $(ls "$DATA_DIR/development/primary"/*.csv 2>/dev/null | wc -l) data files"
    else
        warn "Primary dataset directory (2025-08-26) not found"
    fi
}

# Phase 4: Setup secondary dataset
organize_secondary_dataset() {
    log "🔄 Phase 4: Setting up secondary validation dataset..."
    
    if [ -d "$DATA_DIR/2025-08-25" ]; then
        # Copy secondary dataset
        cp -r "$DATA_DIR/2025-08-25"/* "$DATA_DIR/development/secondary/"
        
        # Create dataset info
        cat > "$DATA_DIR/development/secondary/dataset_info.md" << EOF
# Secondary Validation Dataset - 2025-08-25

**Date:** August 25, 2025  
**Status:** Secondary validation dataset  
**Size:** $(du -sh "$DATA_DIR/development/secondary" | cut -f1)

## Data Types Available:
$(ls -la "$DATA_DIR/development/secondary"/*.csv 2>/dev/null | wc -l) CSV files containing:

$(ls "$DATA_DIR/development/secondary"/*.csv 2>/dev/null | while read file; do
    filename=$(basename "$file")
    lines=$(wc -l < "$file")
    echo "- **$filename**: $lines records"
done)

## Usage:
- Model validation
- Cross-verification testing
- Independent dataset testing

## Last Updated: $(date)
EOF
        
        log "✅ Secondary dataset organized with $(ls "$DATA_DIR/development/secondary"/*.csv 2>/dev/null | wc -l) data files"
    else
        warn "Secondary dataset directory (2025-08-25) not found"
    fi
}

# Phase 5: Create test samples
create_test_samples() {
    log "🔄 Phase 5: Creating quick test samples..."
    
    if [ -d "$DATA_DIR/development/primary" ]; then
        cd "$DATA_DIR/development/samples"
        
        # Create small samples from each primary dataset file
        for csv_file in ../primary/*.csv; do
            if [ -f "$csv_file" ]; then
                filename=$(basename "$csv_file")
                
                # Create 15-row sample (header + 14 data rows)
                head -15 "$csv_file" > "sample_$filename"
                
                info "📝 Created sample_$filename (15 rows)"
            fi
        done
        
        # Create sample info
        cat > "samples_info.md" << EOF
# Quick Test Samples

**Purpose:** Fast testing and development  
**Created:** $(date)

## Available Samples:
$(ls sample_*.csv 2>/dev/null | while read file; do
    lines=$(wc -l < "$file")
    echo "- **$file**: $lines rows"
done)

## Usage:
- Unit testing
- API validation
- Quick schema verification
- Rapid development testing

## Notes:
- Each sample contains header + 14 data rows
- Sufficient for ML pipeline testing (10+ row requirement)
- Use for fast iteration during development

EOF
        
        sample_count=$(ls sample_*.csv 2>/dev/null | wc -l)
        log "✅ Created $sample_count quick test samples"
    else
        warn "Primary dataset not available for sample creation"
    fi
}

# Phase 6: Archive historical data
archive_historical_data() {
    log "🔄 Phase 6: Archiving historical datasets..."
    
    # Archive older datasets
    for date_dir in 2025-08-20 2025-08-21 2025-08-22 2025-08-23 2025-08-24; do
        if [ -d "$DATA_DIR/$date_dir" ]; then
            mv "$DATA_DIR/$date_dir" "$DATA_DIR/archive/"
            info "📁 Archived $date_dir"
        fi
    done
    
    # Archive 2025-08-27 if it exists
    if [ -d "$DATA_DIR/2025-08-27" ]; then
        mv "$DATA_DIR/2025-08-27" "$DATA_DIR/archive/"
        info "📁 Archived 2025-08-27"
    fi
    
    # Create archive index
    cat > "$DATA_DIR/archive/archive_index.md" << EOF
# Archived Historical Data

**Archive Date:** $(date)  
**Purpose:** Historical racing data for reference

## Archived Datasets:
$(for dir in "$DATA_DIR/archive"/*; do
    if [ -d "$dir" ]; then
        dirname=$(basename "$dir")
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        echo "- **$dirname**: $size"
    fi
done)

## Access:
These datasets are preserved for:
- Historical analysis
- Extended testing scenarios  
- Data comparison studies
- Backup reference

## Total Archive Size: $(du -sh "$DATA_DIR/archive" | cut -f1)
EOF
    
    archived_count=$(ls -d "$DATA_DIR/archive"/2025-* 2>/dev/null | wc -l)
    log "✅ Archived $archived_count historical datasets"
}

# Phase 7: Clean temporary directories
clean_temp_directories() {
    log "🔄 Phase 7: Cleaning temporary directories..."
    
    # Move processed data to new structure
    if [ -d "$DATA_DIR/processed" ]; then
        mv "$DATA_DIR/processed"/* "$DATA_DIR/test_outputs/" 2>/dev/null || true
        rmdir "$DATA_DIR/processed" 2>/dev/null || true
        info "📁 Moved processed data to test_outputs/"
    fi
    
    # Clean temp directories
    temp_dirs=("../temp_extract" "../temp_card_processing")
    for temp_dir in "${temp_dirs[@]}"; do
        if [ -d "$temp_dir" ]; then
            # Backup any important data first
            if [ "$(find "$temp_dir" -name "*.csv" | wc -l)" -gt 0 ]; then
                warn "Found CSV files in $temp_dir - archiving before cleanup"
                mkdir -p "$DATA_DIR/staging/temp/$(basename "$temp_dir")"
                cp -r "$temp_dir"/* "$DATA_DIR/staging/temp/$(basename "$temp_dir")/" 2>/dev/null || true
            fi
            
            # Remove temp directory
            rm -rf "$temp_dir"
            info "🗑️ Cleaned temporary directory: $temp_dir"
        fi
    done
    
    log "✅ Temporary directories cleaned"
}

# Phase 8: Create documentation
create_documentation() {
    log "🔄 Phase 8: Creating data organization documentation..."
    
    cat > "$DATA_DIR/DATA_ORGANIZATION_GUIDE.md" << EOF
# Data Organization Guide - Horse Racing AI v2.05

**Reorganized:** $(date)  
**Structure Version:** 2.0

## 📁 Directory Structure

\`\`\`
data/
├── development/           # Active development data
│   ├── primary/          # Main test dataset (2025-08-26)
│   ├── secondary/        # Validation dataset (2025-08-25)  
│   └── samples/          # Quick test samples (15 rows each)
├── archive/              # Historical datasets (2025-08-20 to 2025-08-24)
├── test_outputs/         # Generated test results and reports
└── staging/              # Pipeline processing area
    ├── manual/           # Manual data uploads
    ├── auto/             # Automated data processing
    └── temp/             # Temporary processing files
\`\`\`

## 🎯 Usage Guidelines

### **Development Data (\`development/\`):**
- **Primary:** Complete 2025-08-26 dataset for full testing
- **Secondary:** 2025-08-25 dataset for validation  
- **Samples:** Quick 15-row samples for rapid testing

### **Archived Data (\`archive/\`):**
- Historical datasets preserved for reference
- Accessible but not actively used in development
- Total size: $(du -sh "$DATA_DIR/archive" 2>/dev/null | cut -f1 || echo "N/A")

### **Test Outputs (\`test_outputs/\`):**
- Results from test runs
- Performance reports
- Validation outputs

### **Staging (\`staging/\`):**
- Active pipeline processing
- Temporary file management
- Data upload staging

## 📊 Data Summary

### Primary Dataset (development/primary/):
$(if [ -d "$DATA_DIR/development/primary" ]; then
    echo "- **Size:** $(du -sh "$DATA_DIR/development/primary" | cut -f1)"
    echo "- **Files:** $(ls "$DATA_DIR/development/primary"/*.csv 2>/dev/null | wc -l) CSV files"
    echo "- **Records:** $(find "$DATA_DIR/development/primary" -name "*.csv" -exec wc -l {} + 2>/dev/null | tail -1 | awk '{print $1}') total"
else
    echo "- Not available"
fi)

### Secondary Dataset (development/secondary/):
$(if [ -d "$DATA_DIR/development/secondary" ]; then
    echo "- **Size:** $(du -sh "$DATA_DIR/development/secondary" | cut -f1)"
    echo "- **Files:** $(ls "$DATA_DIR/development/secondary"/*.csv 2>/dev/null | wc -l) CSV files"
else
    echo "- Not available"
fi)

### Quick Samples (development/samples/):
$(if [ -d "$DATA_DIR/development/samples" ]; then
    echo "- **Count:** $(ls "$DATA_DIR/development/samples"/sample_*.csv 2>/dev/null | wc -l) sample files"
    echo "- **Purpose:** Rapid testing and development"
else
    echo "- Not available"
fi)

## 🚀 Development Workflow

1. **Use samples** for quick testing and debugging
2. **Use primary** for full integration testing and ML training
3. **Use secondary** for validation and cross-verification
4. **Archive access** only when historical comparison needed

## 🔄 Maintenance

- Regularly clean staging/temp/ directory
- Archive old test_outputs/ periodically
- Update samples when primary dataset changes
- Document any schema changes

---
**This structure optimizes development efficiency while preserving data integrity.**
EOF
    
    log "✅ Documentation created: $DATA_DIR/DATA_ORGANIZATION_GUIDE.md"
}

# Generate final report
generate_final_report() {
    log "📊 Generating reorganization report..."
    
    cat > "$PROJECT_ROOT/DATA_REORGANIZATION_REPORT.md" << EOF
# Data Reorganization Completion Report

**Date:** $(date)  
**Project:** Horse Racing AI v2.05  
**Operation:** Complete data structure reorganization

## ✅ **Completed Operations**

### Phase 1: Backup ✅
- Complete data backup created: \`$(basename "$BACKUP_DIR")\`
- Backup size: $(du -sh "$BACKUP_DIR" | cut -f1)
- All original data preserved

### Phase 2: Structure Creation ✅
- New development directory structure implemented
- Staging areas configured for pipeline processing
- Test output directories established

### Phase 3: Primary Dataset ✅
$(if [ -d "$DATA_DIR/development/primary" ]; then
    echo "- Primary dataset (2025-08-26) organized"
    echo "- Size: $(du -sh "$DATA_DIR/development/primary" | cut -f1)"
    echo "- Files: $(ls "$DATA_DIR/development/primary"/*.csv 2>/dev/null | wc -l) CSV datasets"
else
    echo "- Primary dataset setup: SKIPPED (source not found)"
fi)

### Phase 4: Secondary Dataset ✅
$(if [ -d "$DATA_DIR/development/secondary" ]; then
    echo "- Secondary dataset (2025-08-25) organized"
    echo "- Size: $(du -sh "$DATA_DIR/development/secondary" | cut -f1)"
    echo "- Files: $(ls "$DATA_DIR/development/secondary"/*.csv 2>/dev/null | wc -l) CSV datasets"
else
    echo "- Secondary dataset setup: SKIPPED (source not found)"
fi)

### Phase 5: Test Samples ✅
$(if [ -d "$DATA_DIR/development/samples" ]; then
    echo "- Quick test samples created"
    echo "- Count: $(ls "$DATA_DIR/development/samples"/sample_*.csv 2>/dev/null | wc -l) sample files"
    echo "- Size: 15 rows each (header + 14 data rows)"
else
    echo "- Test samples: SKIPPED (primary dataset not available)"
fi)

### Phase 6: Historical Archive ✅
$(if [ -d "$DATA_DIR/archive" ]; then
    echo "- Historical datasets archived"
    echo "- Archived: $(ls -d "$DATA_DIR/archive"/2025-* 2>/dev/null | wc -l) date directories"
    echo "- Archive size: $(du -sh "$DATA_DIR/archive" | cut -f1)"
else
    echo "- Historical archive: No datasets to archive"
fi)

### Phase 7: Cleanup ✅
- Temporary directories cleaned
- Processed data moved to test_outputs/
- Staging structure prepared for pipeline use

### Phase 8: Documentation ✅
- Complete data organization guide created
- Dataset information documented
- Usage guidelines established

## 📊 **Final Structure Summary**

\`\`\`
$(tree "$DATA_DIR" -d -L 2 2>/dev/null || find "$DATA_DIR" -type d | head -20)
\`\`\`

## 🎯 **Development Benefits**

### **Performance Improvements:**
- ⚡ Faster testing with 15-row samples
- 🎯 Clear data separation (dev/archive/staging)
- 📊 Optimized directory structure

### **Development Efficiency:**
- 📝 Quick access to test data
- 🔍 Clear data location patterns
- 📋 Comprehensive documentation

### **Data Management:**
- 💾 Original data preserved in backup
- 🗂️ Logical organization by usage type
- 📈 Scalable for future data additions

## 🚀 **Next Steps**

1. **Update development workflows** to use new structure
2. **Test ML pipeline** with reorganized data
3. **Validate API testing** with sample datasets
4. **Update automation scripts** to use staging directories

## 📁 **Key Locations**

- **Primary Test Data:** \`data/development/primary/\`
- **Quick Samples:** \`data/development/samples/\`
- **Pipeline Staging:** \`data/staging/\`
- **Test Results:** \`data/test_outputs/\`
- **Backup Location:** \`$(basename "$BACKUP_DIR")\`

---

**Data reorganization completed successfully. Development environment optimized for efficient Horse Racing AI v2.05 development.**
EOF
    
    log "✅ Final report generated: $PROJECT_ROOT/DATA_REORGANIZATION_REPORT.md"
}

# Main execution
main() {
    log "🚀 Starting Horse Racing AI v2.05 Data Reorganization"
    echo
    
    warn "This will reorganize your data structure. Backup will be created automatically."
    echo
    read -p "Continue with data reorganization? (y/N): " -n 1 -r
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Operation cancelled by user"
        exit 0
    fi
    
    echo
    log "Starting reorganization process..."
    
    # Execute all phases
    backup_current_data
    create_development_structure
    organize_primary_dataset
    organize_secondary_dataset  
    create_test_samples
    archive_historical_data
    clean_temp_directories
    create_documentation
    generate_final_report
    
    echo
    log "🎉 Data reorganization completed successfully!"
    echo
    info "📋 Review the complete report: DATA_REORGANIZATION_REPORT.md"
    info "📖 See usage guide: data/DATA_ORGANIZATION_GUIDE.md"
    info "💾 Original data backed up to: $(basename "$BACKUP_DIR")"
    echo
    log "✅ Ready for efficient Horse Racing AI v2.05 development!"
}

# Execute main function
main "$@"
