#!/usr/bin/env python3
"""
Quick Pipeline Status Check
==========================
Immediate status check of all pipeline processes
"""

import datetime
import subprocess


def check_containers():
    """Check status of all containers"""
    print("🐳 CONTAINER STATUS")
    print("=" * 50)

    containers = [
        "horse_racing_auto_downloader_clean",
        "horse_racing_data_pipeline_clean",
        "horse_racing_ml_trainer_clean",
        "horse_racing_postgres_clean",
        "horse_racing_redis_clean",
        "horse_racing_web_app_clean",
    ]

    for container in containers:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    f"name={container}",
                    "--format",
                    "table {{.Names}}\t{{.Status}}\t{{.Ports}}",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0 and result.stdout.strip():
                lines = result.stdout.strip().split("\n")
                if len(lines) > 1:  # Skip header
                    print(f"🟢 {container}: RUNNING")
                    print(f"   {lines[1]}")
                else:
                    print(f"🔴 {container}: NOT RUNNING")
            else:
                print(f"🔴 {container}: NOT FOUND")

        except Exception as e:
            print(f"❌ {container}: ERROR - {e}")

    print()


def check_recent_logs():
    """Check recent activity in logs"""
    print("📋 RECENT ACTIVITY (Last 2 minutes)")
    print("=" * 50)

    processes = {
        "Auto Downloader": "horse_racing_auto_downloader_clean",
        "Data Pipeline": "horse_racing_data_pipeline_clean",
        "ML Trainer": "horse_racing_ml_trainer_clean",
    }

    for name, container in processes.items():
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", "10", "--since", "2m", container],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                logs = result.stdout.strip()
                if logs:
                    print(f"🔄 {name}:")
                    for line in logs.split("\n")[-3:]:  # Last 3 lines
                        if line.strip():
                            print(f"   {line[:80]}...")  # Truncate long lines
                else:
                    print(f"⏸️  {name}: No recent activity")
            else:
                print(f"❌ {name}: Cannot access logs")

        except Exception as e:
            print(f"❌ {name}: Error - {e}")

        print()


def check_auto_downloader_schedule():
    """Check auto downloader schedule status"""
    print("⏰ AUTO DOWNLOADER SCHEDULE")
    print("=" * 50)

    try:
        result = subprocess.run(
            ["docker", "logs", "--tail", "20", "horse_racing_auto_downloader_clean"],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            logs = result.stdout

            # Look for schedule indicators
            schedule_lines = []
            for line in logs.split("\n"):
                if any(
                    indicator in line
                    for indicator in ["19:20", "Schedule", "📅", "daily"]
                ):
                    schedule_lines.append(line.strip())

            if schedule_lines:
                print("📅 Schedule Status:")
                for line in schedule_lines[-3:]:  # Last 3 schedule lines
                    print(f"   {line}")
            else:
                print("❓ No schedule information found in recent logs")
        else:
            print("❌ Cannot access auto downloader logs")

    except Exception as e:
        print(f"❌ Error checking schedule: {e}")

    print()


def check_system_resources():
    """Check basic system resource usage"""
    print("🖥️  SYSTEM RESOURCES")
    print("=" * 50)

    try:
        # Docker stats
        result = subprocess.run(
            [
                "docker",
                "stats",
                "--no-stream",
                "--format",
                "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}",
            ],
            capture_output=True,
            text=True,
            timeout=15,
        )

        if result.returncode == 0:
            print("Docker Container Resources:")
            print(result.stdout)
        else:
            print("❌ Cannot get docker stats")

    except Exception as e:
        print(f"❌ Error checking resources: {e}")


def main():
    """Main status check"""
    print(
        f"⏱️  PIPELINE STATUS CHECK - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    print("=" * 70)
    print()

    check_containers()
    check_recent_logs()
    check_auto_downloader_schedule()
    check_system_resources()

    print("✅ Status check complete!")


if __name__ == "__main__":
    main()
