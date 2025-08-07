#!/usr/bin/env python3
"""
Pipeline Process Monitor
========================

Monitors the running pipeline processes and provides status updates
"""

import subprocess
import time
import os
from datetime import datetime


def get_process_info(pid):
    """Get detailed info about a process."""
    try:
        cmd = f"ps -p {pid} -o pid,ppid,command,start,etime,pcpu,pmem --no-headers"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None


def count_recent_files():
    """Count files created since 12:30."""
    try:
        cmd = 'find /home/jc/Documents/Horse-race-ai-v2.0/data -type f -newermt "12:30" | wc -l'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        return 0
    except Exception:
        return 0


def get_playwright_processes():
    """Count active Playwright/Chrome processes."""
    try:
        cmd = 'ps aux | grep -E "(playwright|chrome|headless)" | grep -v grep | wc -l'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            return int(result.stdout.strip())
        return 0
    except Exception:
        return 0


def send_monitoring_alert(message):
    """Send monitoring alert via NTFY."""
    try:
        import requests

        url = "http://localhost:8081/horse-racing-alerts"
        headers = {
            "Title": "Pipeline Monitor",
            "Priority": "default",
            "Tags": "monitoring,pipeline",
        }
        response = requests.post(url, data=message, headers=headers)
        return response.status_code == 200
    except Exception:
        return False


def main():
    """Monitor pipeline processes."""
    print("🔍 Pipeline Process Monitor")
    print("=" * 40)

    pipeline_pid = 1053047  # Our main pipeline process
    scheduler_pid = 1021334  # Our scheduler process

    start_time = datetime.now()
    last_file_count = 0

    while True:
        current_time = datetime.now()
        elapsed = current_time - start_time

        print(f"\n📊 Status Update - {current_time.strftime('%H:%M:%S')}")
        print("-" * 40)

        # Check main pipeline process
        pipeline_info = get_process_info(pipeline_pid)
        if pipeline_info:
            print(f"✅ Pipeline Process {pipeline_pid}: RUNNING")
            print(f"   Details: {pipeline_info}")
        else:
            print(f"❌ Pipeline Process {pipeline_pid}: NOT FOUND")
            send_monitoring_alert(
                f"⚠️ Pipeline process {pipeline_pid} has stopped or completed!"
            )

        # Check scheduler process
        scheduler_info = get_process_info(scheduler_pid)
        if scheduler_info:
            print(f"✅ Scheduler Process {scheduler_pid}: RUNNING")
        else:
            print(f"❌ Scheduler Process {scheduler_pid}: NOT FOUND")

        # Check file activity
        file_count = count_recent_files()
        new_files = file_count - last_file_count
        print(f"📁 Files created since 12:30: {file_count} (+{new_files} new)")
        last_file_count = file_count

        # Check browser activity
        browser_count = get_playwright_processes()
        print(f"🌐 Active browser processes: {browser_count}")

        # Overall status
        if pipeline_info and file_count > 0:
            print(f"🟢 Overall Status: HEALTHY - Running for {elapsed}")
        elif pipeline_info:
            print(f"🟡 Overall Status: RUNNING - No new files recently")
        else:
            print(f"🔴 Overall Status: STOPPED or COMPLETED")
            break

        # Wait 60 seconds before next check
        print(f"\n⏱️ Next check in 60 seconds...")
        time.sleep(60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped by user")
    except Exception as e:
        print(f"\n❌ Monitor error: {e}")
