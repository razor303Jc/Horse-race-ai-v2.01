#!/usr/bin/env python3
"""
🔍 Auto-Downloader Monitor
=========================

Real-time monitoring dashboard for the auto-downloader process.
Tracks schedule triggers, downloads, processing, and data validation.
"""

import json
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path


class AutoDownloaderMonitor:
    def __init__(self):
        self.base_path = Path("/home/jc/Documents/Horse-race-ai-v2.02")
        self.container_name = "horse_racing_auto_downloader_clean"
        self.data_paths = {
            "results": self.base_path / "data" / "results_data",
            "cards": self.base_path / "data" / "cards_data",
            "archived": self.base_path / "data" / "archived",
        }

    def get_current_time(self):
        """Get current time formatted"""
        return datetime.now().strftime("%H:%M:%S")

    def get_container_status(self):
        """Get Docker container status"""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={self.container_name}",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.returncode == 0 else "Not running"
        except:
            return "Error checking"

    def get_container_logs(self, tail=5):
        """Get recent container logs"""
        try:
            result = subprocess.run(
                ["docker", "logs", self.container_name, "--tail", str(tail)],
                capture_output=True,
                text=True,
            )
            return result.stdout.strip() if result.returncode == 0 else "No logs"
        except:
            return "Error getting logs"

    def check_file_counts(self):
        """Check file counts in data directories"""
        counts = {}
        for name, path in self.data_paths.items():
            if path.exists():
                counts[name] = len([f for f in path.iterdir() if f.is_file()])
            else:
                counts[name] = 0
        return counts

    def get_latest_files(self):
        """Get latest files in each directory"""
        latest = {}
        for name, path in self.data_paths.items():
            if path.exists():
                files = [f for f in path.iterdir() if f.is_file()]
                if files:
                    latest_file = max(files, key=lambda f: f.stat().st_mtime)
                    latest[name] = {
                        "file": latest_file.name,
                        "modified": datetime.fromtimestamp(
                            latest_file.stat().st_mtime
                        ).strftime("%H:%M:%S"),
                    }
                else:
                    latest[name] = {"file": "None", "modified": "N/A"}
            else:
                latest[name] = {"file": "Directory not found", "modified": "N/A"}
        return latest

    def time_until_trigger(self, target_time="15:15"):
        """Calculate time until next trigger"""
        now = datetime.now()
        target = datetime.strptime(target_time, "%H:%M").replace(
            year=now.year, month=now.month, day=now.day
        )

        if target < now:
            target += timedelta(days=1)

        diff = target - now
        return str(diff).split(".")[0]  # Remove microseconds

    def display_status(self):
        """Display current monitoring status"""
        print(f"\n🔍 Auto-Downloader Monitor - {self.get_current_time()}")
        print("=" * 60)

        # Schedule info
        print(f"⏰ Next trigger: 15:15 (in {self.time_until_trigger()})")

        # Container status
        status = self.get_container_status()
        status_emoji = "✅" if "Up" in status else "❌"
        print(f"🐳 Container: {status_emoji} {status}")

        # File counts
        counts = self.check_file_counts()
        print(
            f"📁 File counts: Results: {counts['results']}, Cards: {counts['cards']}, Archived: {counts['archived']}"
        )

        # Latest files
        latest = self.get_latest_files()
        print("\n📄 Latest files:")
        for name, info in latest.items():
            print(f"   {name.title()}: {info['file']} (modified: {info['modified']})")

        # Recent logs
        print(f"\n📋 Recent logs:")
        logs = self.get_container_logs(3)
        for line in logs.split("\n")[-3:]:
            if line.strip():
                print(f"   {line}")

    def monitor_continuous(self, interval=30):
        """Continuous monitoring with refresh interval"""
        print("🚀 Starting Auto-Downloader Monitoring...")
        print("Press Ctrl+C to stop")

        try:
            while True:
                os.system("clear")  # Clear screen
                self.display_status()
                print(f"\n🔄 Refreshing in {interval} seconds...")
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped.")


def main():
    monitor = AutoDownloaderMonitor()

    # Show initial status
    monitor.display_status()

    print(f"\n🎯 Options:")
    print("1. Continuous monitoring (30s refresh)")
    print("2. Single status check")
    print("3. Watch logs live")

    choice = input("\nSelect option (1-3): ").strip()

    if choice == "1":
        monitor.monitor_continuous()
    elif choice == "2":
        monitor.display_status()
    elif choice == "3":
        print("🔍 Watching logs live (Ctrl+C to stop)...")
        subprocess.run(["docker", "logs", "-f", monitor.container_name])
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
