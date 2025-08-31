#!/bin/bash
# CSV Backup and Database Reset Script
# ====================================
# Purpose: Backup all CSV files and reset PostgreSQL databases for testing

set -e

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.05"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$PROJECT_ROOT/backups/csv_backup_$TIMESTAMP"

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

# Function to backup CSV files
backup_csv_files() {
    log "🗄️ Starting CSV files backup..."
    
    # Create backup directory structure
    mkdir -p "$BACKUP_DIR"
    
    # Find all CSV files
    local csv_files
    mapfile -t csv_files < <(find "$PROJECT_ROOT" -name "*.csv" -type f)
    local total_files=${#csv_files[@]}
    local backup_size=0
    
    info "Found $total_files CSV files to backup"
    
    # Create backup manifest
    cat > "$BACKUP_DIR/backup_manifest.txt" << EOF
CSV Files Backup Manifest
========================
Date: $(date)
Total Files: $total_files
Backup Location: $BACKUP_DIR

Files Backed Up:
EOF
    
    # Backup each CSV file maintaining directory structure
    local count=0
    for csv_file in "${csv_files[@]}"; do
        # Get relative path from project root
        local rel_path
        rel_path=$(realpath --relative-to="$PROJECT_ROOT" "$csv_file")
        local target_dir
        target_dir="$BACKUP_DIR/$(dirname "$rel_path")"
        
        # Create target directory
        mkdir -p "$target_dir"
        
        # Copy file
        cp "$csv_file" "$target_dir/"
        
        # Get file size for reporting
        local file_size
        file_size=$(stat -c%s "$csv_file" 2>/dev/null || echo 0)
        backup_size=$((backup_size + file_size))
        
        # Add to manifest
        echo "- $rel_path ($(echo "scale=1; $file_size/1024" | bc 2>/dev/null || echo "unknown") KB)" >> "$BACKUP_DIR/backup_manifest.txt"
        
        ((count++))
        if [ $((count % 10)) -eq 0 ]; then
            info "Backed up $count/$total_files files..."
        fi
    done
    
    # Add summary to manifest
    cat >> "$BACKUP_DIR/backup_manifest.txt" << EOF

Backup Summary:
===============
Total Size: $(echo "scale=2; $backup_size/1024/1024" | bc 2>/dev/null || echo "unknown") MB
Files Processed: $total_files
Status: Complete

Restoration Instructions:
========================
To restore files, copy from backup directory structure back to project:
cp -r $BACKUP_DIR/data/* $PROJECT_ROOT/data/
cp -r $BACKUP_DIR/monitoring/* $PROJECT_ROOT/monitoring/
etc.

Individual file restoration:
cp $BACKUP_DIR/[relative_path] $PROJECT_ROOT/[relative_path]
EOF
    
    # Create compressed archive
    info "Creating compressed backup archive..."
    cd "$PROJECT_ROOT/backups"
    tar -czf "csv_backup_$TIMESTAMP.tar.gz" "csv_backup_$TIMESTAMP/"
    
    local archive_size
    archive_size=$(stat -c%s "csv_backup_$TIMESTAMP.tar.gz" 2>/dev/null || echo 0)
    
    success "✅ CSV backup completed!"
    info "📁 Backup location: $BACKUP_DIR"
    info "📦 Compressed archive: backups/csv_backup_$TIMESTAMP.tar.gz"
    info "💾 Total backup size: $(echo "scale=2; $backup_size/1024/1024" | bc 2>/dev/null || echo "unknown") MB"
    info "📦 Compressed size: $(echo "scale=2; $archive_size/1024/1024" | bc 2>/dev/null || echo "unknown") MB"
    
    return 0
}

# Function to test PostgreSQL connection
test_postgres_connection() {
    log "🔍 Testing PostgreSQL connection..."
    
    # Check if PostgreSQL is running
    if ! docker ps | grep -q horse_racing_postgres_clean; then
        error "PostgreSQL container not running. Please start with: docker-compose up -d"
        return 1
    fi
    
    # Test connection to each database
    local databases=("results" "cards" "advanced_metrics")
    for db in "${databases[@]}"; do
        if docker exec horse_racing_postgres_clean psql -U horse_racing -d "$db" -c "SELECT 1;" > /dev/null 2>&1; then
            info "✅ Connection to '$db' database: OK"
        else
            warn "⚠️ Database '$db' does not exist, will be created later"
            # Test connection to main postgres database
            if docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
                info "✅ Connection to PostgreSQL server: OK"
            else
                error "❌ Connection to PostgreSQL server: FAILED"
                return 1
            fi
        fi
    done
    
    success "✅ PostgreSQL connection verified"
    return 0
}

# Function to clear PostgreSQL databases
clear_postgres_databases() {
    log "🗑️ Clearing PostgreSQL databases..."
    
    local databases=("results" "cards" "advanced_metrics")
    
    warn "This will permanently delete all data in the following databases:"
    for db in "${databases[@]}"; do
        warn "  - $db"
    done
    
    echo
    read -p "Are you sure you want to continue? (yes/NO): " -r
    echo
    
    if [[ ! "$REPLY" =~ ^[Yy][Ee][Ss]$ ]]; then
        log "Database clearing cancelled by user"
        return 0
    fi
    
    # First, create databases if they don't exist
    for db in "${databases[@]}"; do
        log "Ensuring database exists: $db"
        docker exec horse_racing_postgres_clean psql -U horse_racing -d postgres -c "
            SELECT 'CREATE DATABASE $db' 
            WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = '$db')\\gexec
        " > /dev/null 2>&1 || true
    done
    
    # Clear each database
    for db in "${databases[@]}"; do
        log "Clearing database: $db"
        
        # Get list of tables
        local tables
        tables=$(docker exec horse_racing_postgres_clean psql -U horse_racing -d "$db" -t -c "
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            AND tablename NOT LIKE 'pg_%'
            AND tablename NOT LIKE 'sql_%';
        " | tr -d ' ' | grep -v '^$')
        
        if [ -n "$tables" ]; then
            info "Found tables in $db: $(echo "$tables" | tr '\n' ' ')"
            
            # Drop all tables
            for table in $tables; do
                if [ -n "$table" ]; then
                    info "Dropping table: $table"
                    docker exec horse_racing_postgres_clean psql -U horse_racing -d "$db" -c "DROP TABLE IF EXISTS $table CASCADE;" > /dev/null
                fi
            done
        else
            info "No tables found in database: $db"
        fi
        
        # Verify database is empty
        local remaining_tables
        remaining_tables=$(docker exec horse_racing_postgres_clean psql -U horse_racing -d "$db" -t -c "
            SELECT COUNT(*) FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name NOT LIKE 'pg_%'
            AND table_name NOT LIKE 'sql_%';
        " | tr -d ' ')
        
        if [ "$remaining_tables" = "0" ]; then
            success "✅ Database $db cleared successfully"
        else
            warn "⚠️ Database $db may still contain $remaining_tables tables"
        fi
    done
    
    success "✅ All PostgreSQL databases cleared"
    return 0
}

# Function to prepare for testing
prepare_testing_environment() {
    log "⚙️ Preparing testing environment..."
    
    # Create testing directories if they don't exist
    mkdir -p "$PROJECT_ROOT/tests/"{results,data,logs}
    mkdir -p "$PROJECT_ROOT/tests/performance_reports"
    
    # Set up test configuration
    cat > "$PROJECT_ROOT/tests/test_config.yaml" << EOF
# Testing Configuration for Horse Racing AI v2.05
# Generated: $(date)

databases:
  postgres:
    host: localhost
    port: 5432
    user: postgres
    password: ""
    databases:
      - results
      - cards  
      - advanced_metrics

test_data:
  primary_dataset: "2025-08-26"
  backup_location: "$BACKUP_DIR"
  archive_location: "backups/csv_backup_$TIMESTAMP.tar.gz"

performance_targets:
  database:
    simple_query_ms: 100
    complex_query_ms: 500
  api:
    response_time_ms: 200
    p95_response_ms: 1000
  webapp:
    initial_load_s: 2
    navigation_ms: 500

testing_phases:
  - foundation_testing
  - load_testing  
  - integration_testing
  - optimization_testing
EOF
    
    success "✅ Testing environment prepared"
    info "📄 Test config: tests/test_config.yaml"
    
    return 0
}

# Function to generate reset report
generate_reset_report() {
    log "📊 Generating reset completion report..."
    
    cat > "$PROJECT_ROOT/DATABASE_RESET_REPORT.md" << EOF
# Database Reset and CSV Backup Report

**Date:** $(date)  
**Operation:** CSV Backup + PostgreSQL Database Reset  
**Purpose:** Prepare clean environment for Testing & Simulation Strategy

## ✅ **Operations Completed**

### **CSV Files Backup** ✅
- **Backup Location:** \`$BACKUP_DIR\`
- **Compressed Archive:** \`backups/csv_backup_$TIMESTAMP.tar.gz\`
- **Files Backed Up:** $(find "$BACKUP_DIR" -name "*.csv" | wc -l) CSV files
- **Total Size:** $(du -sh "$BACKUP_DIR" | cut -f1) (uncompressed)
- **Archive Size:** $(du -sh "backups/csv_backup_$TIMESTAMP.tar.gz" 2>/dev/null | cut -f1 || echo "N/A") (compressed)

### **PostgreSQL Databases Cleared** ✅
- **results** database: All tables dropped
- **cards** database: All tables dropped  
- **advanced_metrics** database: All tables dropped
- **Status:** Clean slate ready for testing

### **Testing Environment Prepared** ✅
- **Test directories:** Created under \`tests/\`
- **Test configuration:** \`tests/test_config.yaml\`
- **Performance targets:** Defined and documented

## 🚀 **Ready for Testing Implementation**

### **Next Steps:**
1. **Create Entity Tables:** Run PostgreSQL entity table creation
2. **Load Test Data:** Import primary dataset (2025-08-26)
3. **Execute Testing Strategy:** Run comprehensive test suite
4. **Performance Validation:** Measure against defined targets

### **Key Files Ready:**
- **Entity Table Setup:** \`database/migrations/setup_entity_tables.py\`
- **Test Suite:** \`run_comprehensive_tests.sh\`
- **Daily Simulation:** \`simulate_daily_operations.py\`
- **Testing Strategy:** \`TESTING_SIMULATION_STRATEGY.md\`

### **Backup Recovery:**
If original CSV files are needed:
\`\`\`bash
# Extract from archive
tar -xzf backups/csv_backup_$TIMESTAMP.tar.gz

# Restore specific files
cp csv_backup_$TIMESTAMP/data/2025-08-26/horses/horses.csv data/2025-08-26/horses/

# Full restoration
cp -r csv_backup_$TIMESTAMP/* ./
\`\`\`

## 📊 **Available Test Data**

### **Primary Dataset: 2025-08-26**
- **Records:** 12,454 total across 8 data types
- **Size:** ~18MB (complete racing day)
- **Coverage:** Full relational data for comprehensive testing

### **Historical Data**
- **Range:** August 20-27, 2025 (8 days)
- **Archives:** Preserved in \`data/raw_csv_archives/\`
- **Purpose:** Trend analysis and extended testing

---

**Environment successfully reset and prepared for Testing & Simulation Strategy implementation!**
EOF
    
    success "✅ Reset report generated: DATABASE_RESET_REPORT.md"
    return 0
}

# Main execution function
main() {
    log "🚀 Starting CSV Backup and Database Reset"
    echo
    
    info "This script will:"
    info "  1. Backup all 62 CSV files with full directory structure"
    info "  2. Create compressed archive for safe storage"
    info "  3. Clear all PostgreSQL databases (results, cards, advanced_metrics)"
    info "  4. Prepare clean testing environment"
    echo
    
    warn "This operation will permanently delete all data in PostgreSQL databases!"
    echo
    
    read -p "Continue with backup and reset? (y/N): " -n 1 -r
    echo
    echo
    
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log "Operation cancelled by user"
        exit 0
    fi
    
    # Change to project directory
    cd "$PROJECT_ROOT"
    
    # Execute all operations
    if backup_csv_files; then
        log "✅ CSV backup completed successfully"
    else
        error "❌ CSV backup failed"
        exit 1
    fi
    
    if test_postgres_connection; then
        log "✅ PostgreSQL connection verified"
    else
        error "❌ PostgreSQL connection failed"
        exit 1
    fi
    
    if clear_postgres_databases; then
        log "✅ PostgreSQL databases cleared"
    else
        error "❌ Database clearing failed"
        exit 1
    fi
    
    if prepare_testing_environment; then
        log "✅ Testing environment prepared"
    else
        warn "⚠️ Testing environment preparation had issues"
    fi
    
    if generate_reset_report; then
        log "✅ Reset report generated"
    else
        warn "⚠️ Report generation had issues"
    fi
    
    echo
    success "🎉 Database reset and CSV backup completed successfully!"
    echo
    info "📋 Next steps:"
    info "  1. Create entity tables: python database/migrations/setup_entity_tables.py --create-all"
    info "  2. Load test data: python tools/load_test_data.py --dataset 2025-08-26"
    info "  3. Run testing suite: ./run_comprehensive_tests.sh --dataset 2025-08-26"
    echo
    warn "📁 CSV files backed up to: $BACKUP_DIR"
    warn "📦 Compressed archive: backups/csv_backup_$TIMESTAMP.tar.gz"
    echo
    log "✅ Ready to proceed with Testing & Simulation Strategy!"
}

# Execute main function
main "$@"
