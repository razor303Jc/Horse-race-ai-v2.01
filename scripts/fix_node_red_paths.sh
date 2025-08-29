#!/bin/bash
# Auto-generated Node-RED flow update script

echo "🔄 Updating Node-RED flows with correct script paths..."


# Replace scripts/daily_downloader.py with backup_auto_downloader/scripts/auto_downloader_manager.py
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|scripts/daily_downloader.py|backup_auto_downloader/scripts/auto_downloader_manager.py|g' {} \;

# Replace tools/bulk_uploader/bulk_upload_processor.py with upload_race_data.py
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|tools/bulk_uploader/bulk_upload_processor.py|upload_race_data.py|g' {} \;

# Replace tools/daily_downloader.py with backup_auto_downloader/scripts/auto_downloader_manager.py
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|tools/daily_downloader.py|backup_auto_downloader/scripts/auto_downloader_manager.py|g' {} \;

# Replace tools/database/import_clean_data.py with demo_integrated_cleanup.py
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|tools/database/import_clean_data.py|demo_integrated_cleanup.py|g' {} \;

# Replace tools/ml_training/generate_predictions.py with api/prediction_api.py
find node-red docker/node-red -name "*.json" -type f -exec sed -i 's|tools/ml_training/generate_predictions.py|api/prediction_api.py|g' {} \;

echo "✅ Node-RED flows updated successfully!"
echo "ℹ️  Please restart Node-RED to apply changes"
