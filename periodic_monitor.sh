#!/bin/bash
# Periodic monitoring script for database and file changes
# Run alongside the main log monitoring

echo "📊 PERIODIC MONITORING - Starting checks every 2 minutes"
echo "🎯 Baseline: 7,332 total records, 432 with dates, max_id: 100046927"
echo "============================================================"

while true; do
    current_time=$(date "+%H:%M:%S")
    echo ""
    echo "🕐 CHECK AT $current_time"
    echo "----------------------------------------"
    
    # Database check
    echo "🗄️ Database Status:"
    PGPASSWORD=secure_password_123 psql -h localhost -p 5433 -U horse_racing -d horse_racing_db -c "
    SELECT 
        COUNT(*) as total_records,
        COUNT(race_date) as with_dates,
        MAX(id) as max_id,
        COUNT(*) - 7332 as new_records
    FROM race_results;
    " 2>/dev/null || echo "   ❌ Database connection failed"
    
    # File system check
    echo ""
    echo "📁 New Files Since Test Start:"
    new_files=$(find data/daily_downloads -newer /tmp/test_marker_1231 2>/dev/null)
    if [ -z "$new_files" ]; then
        echo "   ❌ No new files found"
    else
        echo "$new_files" | while read file; do
            echo "   ✅ $file"
        done
    fi
    
    # Container health check
    echo ""
    echo "🐳 Container Status:"
    container_status=$(docker ps --filter name=horserace-auto-downloader --format "{{.Status}}")
    echo "   Status: $container_status"
    
    echo "----------------------------------------"
    
    # Wait 2 minutes before next check
    sleep 120
done
