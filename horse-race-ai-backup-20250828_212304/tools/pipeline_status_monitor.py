#!/usr/bin/env python3
"""
Pipeline Status Monitor
Shows real-time status of the complete pipeline integration
"""

import json
import subprocess
from datetime import datetime


def get_container_status():
    """Check container status"""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "json"], capture_output=True, text=True
        )
        containers = []
        for line in result.stdout.strip().split("\n"):
            if line:
                containers.append(json.loads(line))

        horse_containers = [
            c for c in containers if "horse_racing" in c.get("Names", "")
        ]
        return horse_containers
    except Exception as e:
        return f"Error checking containers: {e}"


def get_pipeline_logs():
    """Get latest pipeline activity"""
    try:
        result = subprocess.run(
            ["docker", "logs", "horse_racing_data_pipeline_clean", "--tail", "10"],
            capture_output=True,
            text=True,
        )
        return result.stdout
    except Exception as e:
        return f"Error getting logs: {e}"


def get_download_status():
    """Check latest downloads"""
    try:
        result = subprocess.run(
            [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "find",
                "/app/data/daily_downloads",
                "-type",
                "f",
                "-newer",
                "/app/data/racing_data_tracking.db",
            ],
            capture_output=True,
            text=True,
        )
        files = result.stdout.strip().split("\n") if result.stdout.strip() else []
        return len([f for f in files if f])
    except Exception as e:
        return f"Error checking downloads: {e}"


def main():
    print("🏇 Horse Racing AI Pipeline Status Monitor")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Container Status
    print("🐳 Container Status:")
    containers = get_container_status()
    if isinstance(containers, list):
        for container in containers:
            name = container.get("Names", "Unknown")
            status = container.get("Status", "Unknown")
            state = container.get("State", "Unknown")
            print(f"   {name}: {state} ({status})")
    else:
        print(f"   {containers}")
    print()

    # Download Status
    print("📥 Recent Downloads:")
    download_count = get_download_status()
    if isinstance(download_count, int):
        print(f"   {download_count} files processed since last pipeline run")
    else:
        print(f"   {download_count}")
    print()

    # Pipeline Activity
    print("🚀 Latest Pipeline Activity:")
    logs = get_pipeline_logs()
    if logs:
        # Extract key pipeline messages
        lines = logs.split("\n")
        pipeline_lines = [
            line
            for line in lines
            if any(
                keyword in line
                for keyword in ["Stage", "Pipeline", "Health", "✅", "🚀", "📊", "💚"]
            )
        ]

        for line in pipeline_lines[-8:]:  # Show last 8 relevant lines
            if line.strip():
                # Clean up the timestamp and show just the message
                parts = line.split(" - ")
                if len(parts) >= 3:
                    message = parts[-1]
                    print(f"   {message}")
    else:
        print("   No recent activity")

    print()
    print("=" * 50)


if __name__ == "__main__":
    main()
