#!/bin/bash

# Documentation Cleanup Script
# Remove redundant files while preserving essential documentation
# Date: August 31, 2025

cd /home/jc/Documents/Horse-race-ai-v2.05/docs || exit 1

echo "🧹 Starting Documentation Cleanup..."
echo "📊 Total files before cleanup: $(ls *.md | wc -l)"

# Create archive directory for removed files
ARCHIVE_DIR="archive/removed_$(date +%Y%m%d)"
mkdir -p "$ARCHIVE_DIR"

# Essential files to KEEP
KEEP_FILES=(
    "README.md"
    "CONSOLIDATED_PROJECT_SUMMARY.md"
    "ADVANCED_SYSTEM_DOCUMENTATION.md"
    "TESTING_README.md"
)

# Files to move to archive (redundant status updates and old reports)
ARCHIVE_FILES=(
    "0001_KICKOFF_PREPARATION_SUMMARY.md"
    "ADVANCED_AI_RACING_TODO_LIST.md"
    "AUTOMATED_DATA_QUALITY_INTEGRATION.md"
    "BETTING_INTEGRATION_COMPLETE.md"
    "BUY_ME_A_COFFEE_BLOG_POST.md"
    "CARDS_UPLOAD_COMPLETE_SUMMARY.md"
    "CARDS_UPLOAD_QUICK_REFERENCE.md"
    "CLEANUP_ORGANIZATION_PLAN.md"
    "COMPREHENSIVE_TODO_AUDIT.md"
    "CONTEXTUAL_AI_ENHANCEMENT_COMPLETE.md"
    "CRITICAL_ACTION_PLAN.md"
    "CRITICAL_PIPELINE_INTEGRATION_SUMMARY.md"
    "CSP_LIVE_RACE_IMPLEMENTATION_SUMMARY.md"
    "DAILY_FILE_WATCHER_PIPELINE_INTEGRATION.md"
    "DATABASE_PIPELINE_FIXES_SUMMARY.md"
    "DATABASE_UPLOAD_STATUS.md"
    "DATA_PROCESSING_ISSUES_CARDS_UPLOAD.md"
    "ENHANCED_FILE_WATCHER_V2_05_LATEST.md"
    "ENHANCED_MONITORING_IMPLEMENTATION_SUMMARY.md"
    "ENHANCED_MONTE_CARLO_INTEGRATION_SUMMARY.md"
    "FILE_WATCHER_COMPLETE.md"
    "FILE_WATCHER_PLAN.md"
    "FINAL_TESTING_RESULTS.md"
    "FORM_SCORE_INTEGRATION_COMPLETION.md"
    "HORSE_RACING_DATA_MODEL_CORRECTION.md"
    "IMPLEMENTATION_REVIEW_FINAL.md"
    "IMPORTANT_DATA_SCRIPTS.md"
    "INTEGRATED_PIPELINE_GUIDE.md"
    "MANUAL_DATA_UPLOAD_PLAN.md"
    "ML_STRATEGY_INTEGRATION_SUMMARY.md"
    "ML_TRAINING_COMPLETION_REPORT.md"
    "ML_TRAINING_SETUP_DOCUMENTATION.md"
    "NEW_COMPREHENSIVE_TODO_2025.md"
    "OPERATIONAL_TIMING_ANALYSIS.md"
    "PIPELINE_ANALYSIS.md"
    "PIPELINE_INTEGRATION_TRACKING.md"
    "POST.md"
    "PRODUCTION_DEPLOYMENT.md"
    "PRODUCTION_INTEGRATION_COMPLETE.md"
    "RACE_RESULTS_INTEGRATION_COMPLETION.md"
    "REORGANIZATION_SUMMARY.md"
    "STRATEGY_INTEGRATION_COMPLETE.md"
    "TIME_AWARE_ML_OPTIMIZATION_IMPLEMENTATION_SUMMARY.md"
    "TODO_STATUS_UPDATE.md"
    "TODO_SUMMARY.md"
    "V2.03_IMPLEMENTATION_TODO.md"
    "V2_01_Advanced_Codebase_Analysis.md"
    "V2_01_Enhancement_Analysis_Report.md"
    "V2_01_FEATURES_INTEGRATION_COMPLETE.md"
    "V2_01_Implementation_Summary.md"
    "WEB_APP_ENHANCEMENT_TODO.md"
    "AI_SELECTIONS_TRACKING_IMPLEMENTATION.md"
    "enhanced_ai_selections_integration_summary.md"
    "enhanced_data_processing_system_v2_05_summary.md"
    "enhanced_monte_carlo_integration.md"
    "ml_model_data_mapping_v2_05.md"
    "stage8_data_architecture_improvements.md"
)

# Move redundant files to archive
echo "📦 Archiving redundant files..."
for file in "${ARCHIVE_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  📝 Archiving: $file"
        mv "$file" "$ARCHIVE_DIR/"
    fi
done

# Keep essential subdirectories but clean them
echo "🗂️  Cleaning subdirectories..."

# Keep plans/ but remove old files
if [ -d "plans/" ]; then
    echo "  📋 Keeping plans/NEXT_PRIORITY_TASKS_AUG30.md"
    find plans/ -name "*.md" ! -name "NEXT_PRIORITY_TASKS_AUG30.md" -exec mv {} "$ARCHIVE_DIR/" \;
fi

# Keep reports/ but only recent ones
if [ -d "reports/" ]; then
    echo "  📊 Keeping recent reports in reports/"
    find reports/ -name "*.md" ! -newermt "3 days ago" -exec mv {} "$ARCHIVE_DIR/" \;
fi

# Clean status/ directory completely (all old status updates)
if [ -d "status/" ]; then
    echo "  🗑️  Removing status/ directory (old status updates)"
    mv status/ "$ARCHIVE_DIR/"
fi

echo "✅ Cleanup complete!"
echo "📊 Total files after cleanup: $(ls *.md | wc -l)"
echo "📦 Archived files: $(ls "$ARCHIVE_DIR/" | wc -l)"
echo "🎯 Essential documentation preserved in main docs/ directory"
echo ""
echo "📚 Essential files kept:"
for file in "${KEEP_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file"
    fi
done

echo ""
echo "📁 Subdirectories preserved:"
for dir in */; do
    if [[ "$dir" != "archive/" ]]; then
        echo "  ✅ $dir"
    fi
done
