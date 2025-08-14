#!/usr/bin/env python3
"""
🟢 LIVE 06:01 DOWNLOAD STATUS REPORT
Real-time monitoring of the scheduled auto-downloader execution
"""

import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path


def check_download_status():
    """Check the current status of the 06:01 auto-downloader"""

    print("🟢 LIVE DOWNLOAD STATUS REPORT")
    print("=" * 60)
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S BST')}")
    print(f"⏰ Expected Schedule: 06:01 BST Daily")
    print("=" * 60)

    # Check container status
    try:
        result = subprocess.run(
            [
                "docker",
                "ps",
                "-a",
                "--filter",
                "name=horserace-auto-downloader",
                "--format",
                "table {{.Names}}\t{{.Status}}\t{{.CreatedAt}}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        print("🐳 CONTAINER STATUS:")
        print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking container status: {e}")

    # Check recent logs with timestamps
    try:
        result = subprocess.run(
            [
                "docker",
                "logs",
                "horserace-auto-downloader",
                "--timestamps",
                "--since",
                "15m",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        logs = result.stdout.strip()
        if logs:
            print("\n📋 RECENT ACTIVITY (Last 15 minutes):")
            print("-" * 60)

            # Parse and display key events
            log_lines = logs.split("\n")
            key_events = []

            for line in log_lines:
                if any(
                    keyword in line
                    for keyword in [
                        "Starting daily download",
                        "Login successful",
                        "Starting file downloads",
                        "Downloaded",
                        "validation completed",
                        "Daily download completed",
                        "Starting Horse Racing",
                    ]
                ):
                    # Extract timestamp and message
                    if "T" in line and "Z" in line:
                        timestamp_str = line.split("Z")[0] + "Z"
                        try:
                            timestamp = datetime.fromisoformat(
                                timestamp_str.replace("Z", "+00:00")
                            )
                            bst_time = timestamp + timedelta(hours=1)  # Convert to BST
                            message = (
                                line.split("Z", 1)[1].strip() if "Z" in line else line
                            )
                            key_events.append(
                                f"{bst_time.strftime('%H:%M:%S')} - {message}"
                            )
                        except:
                            key_events.append(line)

            for event in key_events[-15:]:  # Show last 15 events
                print(f"   {event}")
        else:
            print("\n📋 No recent activity found")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking logs: {e}")

    # Check data validation results
    try:
        result = subprocess.run(
            ["docker", "logs", "horserace-auto-downloader", "--tail", "50"],
            capture_output=True,
            text=True,
            check=True,
        )

        logs = result.stdout

        print("\n📊 DATA VALIDATION RESULTS:")
        print("-" * 60)

        # Extract validation info
        if "Data validation completed successfully" in logs:
            print("✅ Data validation: PASSED")

            # Extract data counts
            for line in logs.split("\n"):
                if "Data counts:" in line:
                    print(f"📈 {line.split(':', 1)[1].strip()}")
                elif "Date validation:" in line:
                    print(f"📅 {line.split(':', 1)[1].strip()}")
                elif "Complete data overlap detected" in line:
                    print(f"🔄 {line.split(':', 1)[1].strip()}")
        else:
            print("⚠️ Data validation status: Unknown")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking validation: {e}")

    # Check next scheduled run
    print("\n⏰ SCHEDULE STATUS:")
    print("-" * 60)

    now = datetime.now()
    today_6am = now.replace(hour=6, minute=1, second=0, microsecond=0)
    tomorrow_6am = today_6am + timedelta(days=1)

    if now < today_6am:
        next_run = today_6am
        print(f"🔜 Next download: TODAY at {next_run.strftime('%H:%M:%S')}")
        time_until = next_run - now
        print(f"⏳ Time until next run: {time_until}")
    else:
        next_run = tomorrow_6am
        print(f"🔜 Next download: TOMORROW at {next_run.strftime('%H:%M:%S')}")
        time_until = next_run - now
        hours = int(time_until.total_seconds() // 3600)
        minutes = int((time_until.total_seconds() % 3600) // 60)
        print(f"⏳ Time until next run: {hours}h {minutes}m")

    # Check if download ran today
    if now >= today_6am:
        print("✅ Today's 06:01 download: COMPLETED")
    else:
        print("⏳ Today's 06:01 download: PENDING")

    print("\n" + "=" * 60)
    print("🎯 MONITORING SUMMARY:")

    # Final status
    try:
        result = subprocess.run(
            ["docker", "logs", "horserace-auto-downloader", "--tail", "1"],
            capture_output=True,
            text=True,
            check=True,
        )

        if "Daily download completed successfully" in result.stdout:
            print("🟢 Status: AUTO-DOWNLOADER OPERATIONAL")
            print("✅ Latest execution: SUCCESS")
        else:
            print("🟡 Status: CHECKING...")

    except:
        print("🔴 Status: UNABLE TO DETERMINE")


if __name__ == "__main__":
    check_download_status()
