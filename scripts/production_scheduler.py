#!/usr/bin/env python3
"""
Production Horse Racing Pipeline Scheduler
==========================================

Monitors time and runs the complete racing pipeline at 12:30
Sends NTFY notifications for all major events
"""

import time
import subprocess
import os
import sys
from datetime import datetime
from pathlib import Path


def send_notification(title, message, priority="default"):
    """Send NTFY notification using correct topic."""
    try:
        import requests

        url = "http://localhost:8081/horse-racing-alerts"
        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": "horse,racing,production",
        }
        response = requests.post(url, data=message, headers=headers)

        if response.status_code == 200:
            print(f"✅ Notification sent: {title}")
            return True
        else:
            print(f"❌ Notification failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"⚠️ Notification error: {e}")
        return False


def run_complete_pipeline():
    """Run the complete racing pipeline."""
    print("🏇 Starting Complete Horse Racing Pipeline")

    # Send start notification
    send_notification(
        "🏇 Pipeline Started",
        f"Complete horse racing pipeline started at "
        f"{datetime.now().strftime('%H:%M:%S')}",
        "high",
    )

    # Change to project directory
    os.chdir("/home/jc/Documents/Horse-race-ai-v2.0")

    # Use the current Python executable
    python_path = sys.executable

    # Try different pipeline files in order of preference
    pipeline_files = [
        "demos/complete_racing_pipeline.py",
        "demos/enhanced_auto_download_system.py",
        "demos/horseracedatabase_auto_downloader.py",
        "main.py",
    ]

    pipeline_file = None
    for file in pipeline_files:
        if Path(file).exists():
            pipeline_file = file
            print(f"✅ Using pipeline: {pipeline_file}")
            break

    if not pipeline_file:
        error_msg = "❌ No suitable pipeline file found"
        print(error_msg)
        send_notification("❌ Pipeline Error", error_msg, "max")
        return False

    try:
        print(f"🐍 Python: {python_path}")
        print(f"📁 Directory: {os.getcwd()}")
        print(f"🚀 Running: {pipeline_file}")

        # Run the pipeline with timeout
        result = subprocess.run(
            [python_path, pipeline_file],
            capture_output=True,
            text=True,
            timeout=1800,  # 30 minute timeout
        )

        print(f"📊 Return code: {result.returncode}")

        if result.stdout:
            print("📤 STDOUT:")
            print(result.stdout[-1000:])  # Last 1000 chars

        if result.stderr:
            print("📤 STDERR:")
            print(result.stderr[-1000:])  # Last 1000 chars

        if result.returncode == 0:
            success_msg = "Pipeline completed successfully!"
            print(f"✅ {success_msg}")
            send_notification(
                "✅ Pipeline Success",
                f"{success_msg} Completed at " f"{datetime.now().strftime('%H:%M:%S')}",
                "high",
            )
            return True
        else:
            error_msg = f"Pipeline failed with return code: {result.returncode}"
            print(f"❌ {error_msg}")
            send_notification(
                "❌ Pipeline Failed",
                f"{error_msg}\nError: {result.stderr[:200]}...",
                "max",
            )
            return False

    except subprocess.TimeoutExpired:
        timeout_msg = "Pipeline timed out after 30 minutes"
        print(f"❌ {timeout_msg}")
        send_notification("⏰ Pipeline Timeout", timeout_msg, "max")
        return False
    except Exception as e:
        error_msg = f"Pipeline failed with exception: {str(e)}"
        print(f"❌ {error_msg}")
        send_notification("❌ Pipeline Error", error_msg, "max")
        return False


def main():
    """Monitor time and run at 12:30."""
    print("🏁 Production Horse Racing Pipeline Scheduler")
    print("=" * 50)

    # Send scheduler start notification
    send_notification(
        "🏁 Scheduler Active",
        "Production scheduler started - waiting for 12:30",
        "default",
    )

    target_hour = 12
    target_minute = 30

    print(f"🎯 Target time: {target_hour:02d}:{target_minute:02d}:00")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")

    # Wait for target time
    while True:
        now = datetime.now()
        current_time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

        print(
            f"🕐 Current: {current_time} | "
            f"Target: {target_hour:02d}:{target_minute:02d}:00"
        )

        # Check if we've reached the target time
        if now.hour == target_hour and now.minute == target_minute:
            print("🚀 TARGET TIME REACHED! Starting pipeline...")

            send_notification(
                "🚀 Pipeline Triggered",
                f"12:30 target time reached - starting pipeline",
                "high",
            )

            success = run_complete_pipeline()

            if success:
                print("🎉 PIPELINE COMPLETED SUCCESSFULLY!")
                final_msg = (
                    f"Complete horse racing pipeline finished successfully "
                    f"at {datetime.now().strftime('%H:%M:%S')}"
                )
                send_notification("🎉 Production Run Complete", final_msg, "high")
            else:
                print("💥 PIPELINE COMPLETED WITH ERRORS!")
                final_msg = (
                    f"Pipeline completed with errors at "
                    f"{datetime.now().strftime('%H:%M:%S')}"
                )
                send_notification("💥 Production Run Issues", final_msg, "max")

            print("📋 Scheduler finished - exiting...")
            break

        # Check every 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    main()
