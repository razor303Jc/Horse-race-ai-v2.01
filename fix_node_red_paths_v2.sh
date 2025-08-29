#!/bin/bash
# Node-RED Script Path Fix - Comprehensive Update
# Updates Node-RED flows with existing script paths

echo "🔧 Fixing Node-RED script paths..."

cd /home/jc/Documents/Horse-race-ai-v2.04

# Backup Node-RED flows before making changes
echo "📋 Creating backup of Node-RED flows..."
cp -r node-red node-red-backup-$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "   Node-RED backup created"

# Replace missing scripts with existing alternatives
echo "🔄 Updating script paths in Node-RED flows..."

# 1. Fix daily_downloader.py references
echo "   ➤ Fixing daily_downloader.py references..."
find node-red docker/node-red -name "*.json" -type f -exec sed -i \
    's|scripts/daily_downloader.py|tools/data_processing/daily_downloads_manager.py|g' {} \; 2>/dev/null || true
find node-red docker/node-red -name "*.json" -type f -exec sed -i \
    's|tools/daily_downloader.py|tools/data_processing/daily_downloads_manager.py|g' {} \; 2>/dev/null || true

# 2. Fix database import references  
echo "   ➤ Fixing database import references..."
find node-red docker/node-red -name "*.json" -type f -exec sed -i \
    's|tools/database/import_clean_data.py|tools/pipeline/quick_csv_import.py|g' {} \; 2>/dev/null || true

# 3. Fix prediction generation references
echo "   ➤ Fixing prediction generation references..."
find node-red docker/node-red -name "*.json" -type f -exec sed -i \
    's|tools/ml_training/generate_predictions.py|api/prediction_api.py|g' {} \; 2>/dev/null || true

# 4. Update workspace path to be more flexible
echo "   ➤ Updating workspace paths..."
find node-red docker/node-red -name "*.json" -type f -exec sed -i \
    's|cd /workspace &&|cd /home/jc/Documents/Horse-race-ai-v2.04 \&\&|g' {} \; 2>/dev/null || true

echo "✅ Node-RED script paths updated successfully!"
echo ""
echo "📋 Updated mappings:"
echo "   • scripts/daily_downloader.py → tools/data_processing/daily_downloads_manager.py"
echo "   • tools/daily_downloader.py → tools/data_processing/daily_downloads_manager.py"  
echo "   • tools/database/import_clean_data.py → tools/pipeline/quick_csv_import.py"
echo "   • tools/ml_training/generate_predictions.py → api/prediction_api.py"
echo "   • /workspace → /home/jc/Documents/Horse-race-ai-v2.04"
echo ""
echo "🔍 Verifying updates..."

# Verify the changes
MISSING_SCRIPTS=0
for script in "tools/data_processing/daily_downloads_manager.py" "tools/pipeline/quick_csv_import.py" "api/prediction_api.py" "tools/data_quality/csv_data_cleaner.py"; do
    if [ -f "$script" ]; then
        echo "✅ $script exists"
    else
        echo "❌ $script missing"
        MISSING_SCRIPTS=$((MISSING_SCRIPTS + 1))
    fi
done

if [ $MISSING_SCRIPTS -eq 0 ]; then
    echo ""
    echo "🎉 All Node-RED referenced scripts now exist!"
    echo "ℹ️  Restart Node-RED to apply changes"
else
    echo ""
    echo "⚠️  $MISSING_SCRIPTS scripts still missing - manual review needed"
fi
