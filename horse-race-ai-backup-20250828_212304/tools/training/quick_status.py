#!/usr/bin/env python3
"""
Quick Training Status Check
==========================
Check training progress without interrupting the process
"""
import json
import os
from datetime import datetime
from pathlib import Path


def check_training_status():
    """Check the current training status"""
    base_dir = Path(__file__).parent.parent.parent
    reports_dir = base_dir / "reports"

    print("🚀 Enhanced AI Training Status Check")
    print("=" * 40)

    # Find all progress files
    progress_files = list(reports_dir.glob("simplified_training_progress_*.json"))
    if not progress_files:
        print("❌ No training progress files found")
        return

    # Get the most recent file
    latest_file = max(progress_files, key=lambda f: f.stat().st_mtime)
    file_time = datetime.fromtimestamp(latest_file.stat().st_mtime)

    print(f"📄 Latest Report: {latest_file.name}")
    print(f"⏰ Last Updated: {file_time.strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        with open(latest_file, "r") as f:
            data = json.load(f)

        session = data.get("training_session", {})
        stats = data.get("overall_statistics", {})
        levels = data.get("level_results", [])

        # Session duration
        if "total_duration_hours" in session:
            hours = session["total_duration_hours"]
            duration_str = f"{hours:.2f}h" if hours >= 1 else f"{hours*60:.1f}m"
            print(f"⏱️  Training Duration: {duration_str}")

        # Overall progress
        total_successful = stats.get("total_successful_runs", 0)
        total_planned = stats.get("total_planned_runs", 0)
        success_rate = stats.get("overall_success_rate", 0)

        print(
            f"📊 Overall Progress: {total_successful}/{total_planned} runs ({success_rate:.1f}%)"
        )
        print(f"🏁 Levels Completed: {session.get('levels_completed', 0)}/5")

        # Level details
        if levels:
            print("\n📈 Level Details:")
            for level in levels:
                level_num = level.get("level", "?")
                successful = level.get("successful_runs", 0)
                planned = level.get("planned_runs", 0)
                rate = level.get("success_rate", 0)
                status = level.get("status", "unknown")

                status_emoji = {
                    "completed": "✅",
                    "running": "🔄",
                    "pending": "⏳",
                }.get(status, "❓")

                print(
                    f"   Level {level_num}: {status_emoji} {successful}/{planned} ({rate:.1f}%)"
                )

    except Exception as e:
        print(f"❌ Error reading progress: {e}")

    print("\n" + "=" * 40)
    print("💡 Training continues autonomously in background")
    print("💡 Run this script anytime to check progress")


if __name__ == "__main__":
    check_training_status()
