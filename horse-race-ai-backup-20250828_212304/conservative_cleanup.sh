#!/bin/bash

# Conservative Project Cleanup Script
# Removes only the safest, most obvious unused files
# Created: 2025-08-26

echo "🧹 Starting Conservative Project Cleanup"
echo "======================================="

PROJECT_ROOT="/home/jc/Documents/Horse-race-ai-v2.04"
CLEANUP_LOG="$PROJECT_ROOT/data/audit/cleanup_log_$(date +%Y%m%d_%H%M%S).txt"
BACKUP_DIR="$PROJECT_ROOT/data/versions/cleanup_backup_$(date +%Y%m%d_%H%M%S)"

# Create backup directory
mkdir -p "$BACKUP_DIR"

echo "📁 Backup directory: $BACKUP_DIR"
echo "📝 Cleanup log: $CLEANUP_LOG"

# Start logging
echo "Conservative Cleanup Log - $(date)" > "$CLEANUP_LOG"
echo "=================================" >> "$CLEANUP_LOG"

removed_count=0
backed_up_count=0

# Function to safely remove file
safe_remove() {
    local file="$1"
    local full_path="$PROJECT_ROOT/$file"
    
    if [[ -f "$full_path" ]]; then
        # Create backup
        local backup_path="$BACKUP_DIR/$file"
        mkdir -p "$(dirname "$backup_path")"
        cp "$full_path" "$backup_path" 2>/dev/null
        
        if [[ $? -eq 0 ]]; then
            echo "✅ Backed up: $file" | tee -a "$CLEANUP_LOG"
            backed_up_count=$((backed_up_count + 1))
            
            # Remove original
            rm "$full_path"
            if [[ $? -eq 0 ]]; then
                echo "🗑️  Removed: $file" | tee -a "$CLEANUP_LOG"
                removed_count=$((removed_count + 1))
            else
                echo "❌ Failed to remove: $file" | tee -a "$CLEANUP_LOG"
            fi
        else
            echo "❌ Failed to backup: $file" | tee -a "$CLEANUP_LOG"
        fi
    else
        echo "⚠️  File not found: $file" | tee -a "$CLEANUP_LOG"
    fi
}

echo "🔍 Phase 1: Removing Empty __init__.py Files"
echo "============================================"

# Empty __init__.py files that aren't imported
safe_remove "src/horse_racing_ai/__init__.py"
safe_remove "src/horse_racing_ai/simulation/__init__.py"
safe_remove "src/horse_racing_ai/orchestration/__init__.py" 
safe_remove "src/horse_racing_ai/core/__init__.py"
safe_remove "src/horse_racing_ai/automation/__init__.py"
safe_remove "src/feeds/__init__.py"
safe_remove "src/horse_racing_ai/integration/__init__.py"
safe_remove "src/horse_racing_ai/deployment/__init__.py"
safe_remove "src/horse_racing_ai/ml/__init__.py"
safe_remove "src/horse_racing_ai/analytics/__init__.py"
safe_remove "src/horse_racing_ai/production/__init__.py"
safe_remove "src/horse_racing_ai/notifications/__init__.py"
safe_remove "src/horse_racing_ai/scoring/__init__.py"
safe_remove "src/betdaq/__init__.py"
safe_remove "docker/ml_training/__init__.py"

echo ""
echo "🐎 Phase 2: Removing Horse-bot Experimental Modules"
echo "=================================================="

# Horse-bot experimental/unused modules  
safe_remove "horse-bot/src/api/routes/betting.py"
safe_remove "horse-bot/src/services/market_simulator.py"
safe_remove "horse-bot/src/core/__init__.py"
safe_remove "horse-bot/src/api/routes/participants.py"
safe_remove "horse-bot/tools/development_summary.py"
safe_remove "horse-bot/src/database/__init__.py"
safe_remove "horse-bot/src/api/routes/__init__.py"
safe_remove "horse-bot/src/api/routes/races.py"
safe_remove "horse-bot/src/services/betdaq_client.py"
safe_remove "horse-bot/src/core/config.py"
safe_remove "horse-bot/src/services/paper_trading.py"
safe_remove "horse-bot/setup.py"
safe_remove "horse-bot/src/api/__init__.py"
safe_remove "horse-bot/src/services/betting_engine.py"

echo ""
echo "📊 Phase 3: Removing Duplicate Monitoring Scripts"
echo "=============================================="

# Duplicate/obsolete monitoring scripts
safe_remove "monitoring/script_instrumenter.py"
safe_remove "monitoring/test_analysis_system.py"
safe_remove "monitoring/analyzed_pipeline_coordinator.py"
safe_remove "monitoring/enhanced_pipeline_trigger.py"
safe_remove "monitoring/setup_and_run.py"
safe_remove "monitoring/script_function_analyzer.py"

echo ""
echo "🔧 Phase 4: Removing Duplicate Utility Scripts"
echo "==========================================="

# Duplicate utility scripts
safe_remove "scripts/utility/fix_csv_for_db.py"
safe_remove "scripts/fix_csv_for_db.py"  
safe_remove "scripts/create_db_csv.py"
safe_remove "scripts/utility/create_db_csv.py"
safe_remove "scripts/check_tables.py"
safe_remove "scripts/utility/check_schema.py"

echo ""
echo "📈 Cleanup Summary"
echo "=================="
echo "🗂️  Files backed up: $backed_up_count"
echo "🗑️  Files removed: $removed_count"
echo "📁 Backup location: $BACKUP_DIR"
echo "📝 Full log: $CLEANUP_LOG"

echo ""
echo "Cleanup completed successfully!" | tee -a "$CLEANUP_LOG"
echo "Summary: Removed $removed_count files, backed up $backed_up_count files" >> "$CLEANUP_LOG"
echo "Backup location: $BACKUP_DIR" >> "$CLEANUP_LOG"
echo "$(date)" >> "$CLEANUP_LOG"

echo ""
echo "🔄 Next Steps:"
echo "1. Test system functionality"
echo "2. If issues occur, restore from: $BACKUP_DIR"
echo "3. Git commit the changes if everything works"
