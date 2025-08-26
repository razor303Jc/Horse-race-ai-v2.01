#!/bin/bash
# 🔧 PIPELINE DAILY UPLOAD FIX DEPLOYMENT SCRIPT
# ==============================================
# 
# This script deploys the fixed pipeline daily uploader to resolve
# all critical issues from CRITICAL_PIPELINE_FINDINGS_REPORT.md
#
# FIXES DEPLOYED:
# ✅ Column mapping mismatches (horses "id" issue)
# ✅ Case sensitivity problems (UptoDate vs uptodate)  
# ✅ Data cleaning for "-" strings in integer fields
# ✅ Multi-database support enhancement
#
# Usage: ./deploy_pipeline_fix.sh

cd /home/jc/Documents/Horse-race-ai-v2.04

echo "🚀 DEPLOYING PIPELINE DAILY UPLOAD FIX"
echo "======================================"
echo ""

# Step 1: Backup the problematic original script
echo "📦 Step 1: Backing up original problematic script..."
if [ -f "tools/data_processing/upload_results_data_container.py" ]; then
    cp tools/data_processing/upload_results_data_container.py \
       tools/data_processing/upload_results_data_container.py.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ Original script backed up"
else
    echo "⚠️ Original script not found (may already be replaced)"
fi

# Step 2: Deploy the fixed script
echo ""
echo "🔧 Step 2: Deploying fixed pipeline uploader..."
if [ -f "tools/data_processing/fixed_pipeline_daily_uploader.py" ]; then
    cp tools/data_processing/fixed_pipeline_daily_uploader.py \
       tools/data_processing/upload_results_data_container.py
    echo "✅ Fixed script deployed"
else
    echo "❌ Fixed script not found!"
    exit 1
fi

# Step 3: Validate the deployment
echo ""
echo "🧪 Step 3: Validating deployment..."
if python tools/data_processing/test_pipeline_uploader_fixes.py; then
    echo "✅ Validation passed - fix deployed successfully"
else
    echo "❌ Validation failed - deployment issue detected"
    exit 1
fi

# Step 4: Show deployment summary
echo ""
echo "📊 DEPLOYMENT SUMMARY"
echo "===================="
echo "✅ Original script backed up"
echo "✅ Fixed script deployed as upload_results_data_container.py"
echo "✅ All validation tests passed"
echo ""
echo "CRITICAL ISSUES RESOLVED:"
echo "  • Fix 1: horses 'id' -> 'horse_id' column mapping"
echo "  • Fix 2: jockeys_stats 'UptoDate' -> 'uptodate' case sensitivity"
echo "  • Fix 3: trainers_stats 'UptoDate' -> 'uptodate' case sensitivity"  
echo "  • Fix 4: records '-' string cleaning for integer fields"
echo "  • Enhanced: Multi-database support and data validation"
echo ""
echo "RECOVERY PROJECTION:"
echo "  • horses: 574 records recoverable"
echo "  • jockeys_stats: 6,605 records recoverable"
echo "  • trainers_stats: 4,260 records recoverable"
echo "  • records: 534 records recoverable"
echo "  • TOTAL: 11,973 records recoverable"
echo ""
echo "🎯 PIPELINE DAILY UPLOAD SYSTEM: READY FOR PRODUCTION"
echo "Next: Run pipeline with latest data to recover lost records"
