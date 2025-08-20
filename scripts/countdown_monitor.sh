#!/bin/bash
echo "🚀 Horse Racing AI v2.03 - 00:01 COUNTDOWN MONITOR"
echo "=================================================="

while true; do
    current_time=$(date +"%H:%M:%S")
    target_time="2025-08-20 00:01:00"
    current_epoch=$(date +%s)
    target_epoch=$(date -d "$target_time" +%s)
    
    diff_seconds=$((target_epoch - current_epoch))
    
    if [ $diff_seconds -gt 0 ]; then
        hours=$((diff_seconds / 3600))
        minutes=$(((diff_seconds % 3600) / 60))
        seconds=$((diff_seconds % 60))
        
        clear
        echo "🏇 HORSE RACING AI v2.03 - 00:01 COUNTDOWN"
        echo "Current Time: $current_time"
        printf "⏰ TIME UNTIL 00:01: %02d:%02d:%02d\n" $hours $minutes $seconds
        
        if [ $diff_seconds -le 300 ]; then
            echo "🔥 FINAL COUNTDOWN - AUTO-DOWNLOAD IMMINENT!"
        else
            echo "🕐 WAITING FOR 00:01 AUTO-DOWNLOAD SCHEDULE"
        fi
        
        echo ""
        echo "📦 Container Status:"
        docker ps --format "{{.Names}}: {{.Status}}" | grep horse_racing
        
        echo ""
        echo "🤖 Latest Auto-Downloader Log:"
        docker logs --tail 1 horse_racing_auto_downloader_clean 2>/dev/null || echo "   No recent activity"
    else
        echo "🚀 00:01 PASSED - CHECKING PIPELINE ACTIVITY"
        docker logs --tail 5 horse_racing_auto_downloader_clean
    fi
    
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 10
done
