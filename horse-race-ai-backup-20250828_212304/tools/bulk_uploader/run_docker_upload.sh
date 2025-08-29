#!/bin/bash
# Run bulk uploader inside Docker container

echo "🚀 Running Bulk Uploader inside Docker Container"
echo "=================================================="

# Copy the uploader script to the container
echo "📋 Copying bulk uploader to container..."
docker cp /home/jc/Documents/Horse-race-ai-v2.04/tools/bulk_uploader/docker_uploader.py \
    horse_racing_ml_trainer_clean:/app/tools/bulk_uploader/

# Make it executable
docker exec horse_racing_ml_trainer_clean chmod +x /app/tools/bulk_uploader/docker_uploader.py

# Run the bulk uploader
echo "🚀 Starting bulk upload process..."
docker exec -it horse_racing_ml_trainer_clean python /app/tools/bulk_uploader/docker_uploader.py

echo "✅ Bulk upload process completed"
