#!/usr/bin/env python3
"""
Monitor Progressive Training Status
===================================
Quick monitoring script to check training progress
"""
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def find_latest_progress_file(reports_dir: Path) -> Optional[Path]:
    """Find the most recent training progress file"""
    pattern = "simplified_training_progress_*.json"
    files = list(reports_dir.glob(pattern))
    if not files:
        return None
    return max(files, key=lambda f: f.stat().st_mtime)


def format_duration(seconds: float) -> str:
    """Format duration in a human-readable way"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def display_training_status():
    """Display current training status"""
    base_dir = Path(__file__).parent.parent.parent
    reports_dir = base_dir / "reports"

    print("🧠 Enhanced AI Progressive Training Monitor")
    print("=" * 45)

    # Find latest progress file
    progress_file = find_latest_progress_file(reports_dir)
    if not progress_file:
        print("❌ No training progress files found")
        return

    try:
        with open(progress_file, "r") as f:
            data = json.load(f)

        session_info = data.get("session_info", {})
        levels = data.get("training_levels", [])
        stats = data.get("overall_statistics", {})

        # Session info
        start_time = session_info.get("start_time", "Unknown")
        current_time = session_info.get("current_time", "Unknown")

        print(f"📅 Session Start: {start_time}")
        print(f"⏰ Last Update:   {current_time}")

        if "total_duration_seconds" in session_info:
            duration = format_duration(session_info["total_duration_seconds"])
            print(f"⏱️  Duration:      {duration}")

        print()

        # Training progress by level
        print("📊 Training Progress by Level:")
        print("-" * 40)

        total_successful = 0
        total_planned = 0

        for level in levels:
            level_num = level.get("level", "?")
            successful = level.get("successful_runs", 0)
            planned = level.get("planned_runs", 0)
            success_rate = level.get("success_rate", 0)
            status = level.get("status", "unknown")

            total_successful += successful
            total_planned += planned

            status_emoji = {
                "completed": "✅",
                "running": "🔄",
                "pending": "⏳",
                "failed": "❌",
            }.get(status, "❓")

            print(
                f"Level {level_num}: {status_emoji} {successful}/{planned} runs ({success_rate:.1f}%)"
            )

        print("-" * 40)

        # Overall statistics
        if total_planned > 0:
            overall_rate = (total_successful / total_planned) * 100
            print(
                f"🎯 Overall: {total_successful}/{total_planned} runs ({overall_rate:.1f}%)"
            )

        if "average_level_duration" in stats:
            avg_duration = format_duration(stats["average_level_duration"] * 60)
            print(f"⏱️  Avg Level Duration: {avg_duration}")

        # Recent activity
        print()
        print("📋 Recent Activity:")
        recent_logs = data.get("recent_logs", [])
        for log in recent_logs[-5:]:  # Show last 5 log entries
            print(f"   {log}")

    except Exception as e:
        print(f"❌ Error reading progress file: {e}")


if __name__ == "__main__":
    display_training_status()
