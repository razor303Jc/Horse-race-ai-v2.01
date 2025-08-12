#!/bin/bash
# Live Test Monitoring Script - Track Auto-Downloader and Data Flow
# Run this script to monitor the 12:31 auto-downloader execution

echo "🔍 LIVE TEST MONITORING - Starting at $(date)"
echo "⏰ Target Time: 12:31 UTC"
echo "📊 Monitoring auto-downloader, data flow, and database changes"
echo "============================================================"

# Function to check container status
check_containers() {
    echo "📦 Container Status:"
    docker ps --filter name=horserace-auto-downloader --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
}

# Function to check database record counts
check_database() {
    echo "🗄️ Database Status:"
    PGPASSWORD=secure_password_123 psql -h localhost -p 5433 -U horse_racing -d horse_racing_db -c "
    SELECT 
        'race_results' as table_name, 
        COUNT(*) as total_records,
        COUNT(race_date) as records_with_dates,
        COUNT(*) - COUNT(race_date) as null_dates
    FROM race_results
    UNION ALL
    SELECT 
        'races_cards' as table_name,
        COUNT(*) as total_records, 
        COUNT(date) as records_with_dates,
        COUNT(*) - COUNT(date) as null_dates
    FROM races_cards;
    "
    echo ""
}

# Function to check downloaded files
check_downloads() {
    echo "📁 Downloaded Files:"
    if [ -d "data/daily_downloads" ]; then
        find data/daily_downloads -name "*.csv" -mtime -1 2>/dev/null | while read file; do
            echo "  📄 $file"
            if [ -f "$file" ]; then
                # Check first data row for dates
                first_date=$(head -2 "$file" | tail -1 | grep -oE "2025-[0-9]{2}-[0-9]{2}" | head -1)
                if [ ! -z "$first_date" ]; then
                    echo "     📅 Contains date: $first_date"
                fi
                record_count=$(wc -l < "$file")
                echo "     📊 Records: $((record_count - 1))"
            fi
        done
    else
        echo "  ❌ No downloads directory found"
    fi
    echo ""
}

# Function to monitor auto-downloader logs
monitor_logs() {
    echo "📋 Recent Auto-Downloader Logs:"
    docker logs horserace-auto-downloader --tail 10
    echo ""
}

# Initial baseline check
echo "🏁 BASELINE CHECK (Pre-Test):"
check_containers
check_database
check_downloads
monitor_logs

echo "⏳ Waiting for 12:31 auto-downloader execution..."
echo "🔄 Will check every 30 seconds starting at 12:30"

# Wait until 12:30 to start intensive monitoring
while [ $(date +%H:%M) != "12:30" ]; do
    sleep 10
done

echo "🚨 12:30 REACHED - Starting intensive monitoring..."

# Monitor every 30 seconds from 12:30 to 12:35
for i in {1..10}; do
    current_time=$(date +%H:%M:%S)
    echo "============================================================"
    echo "🕐 CHECK #$i at $current_time"
    
    check_containers
    check_database
    check_downloads
    monitor_logs
    
    if [ $i -lt 10 ]; then
        echo "⏱️ Waiting 30 seconds for next check..."
        sleep 30
    fi
done

echo "============================================================"
echo "✅ MONITORING COMPLETE - Final Analysis:"
echo "📊 Check the above logs for:"
echo "  1. Auto-downloader execution at 12:31"
echo "  2. New CSV files created"
echo "  3. Database record count changes"
echo "  4. Date population in database"
echo "  5. Any error messages or failures"
echo ""
echo "🎯 Use this data to identify where the data pipeline breaks"
