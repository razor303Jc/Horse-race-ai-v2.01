#!/usr/bin/env python3
"""
System Status Monitor - Shows current state and countdown to 11:30
"""

import os
from datetime import datetime
from pathlib import Path


def check_data_status():
    """Check the current data directory status."""
    data_dir = Path("data")
    hrdb_dir = data_dir / "horseracedatabase"

    print("📁 Data Directory Status:")
    print("=" * 40)

    if hrdb_dir.exists():
        cards_dir = hrdb_dir / "cards_data"
        results_dir = hrdb_dir / "results_data"

        print(f"✅ Horseracedatabase directory exists")
        print(
            f"📋 Cards data dir: {'✅ Ready' if cards_dir.exists() and not any(cards_dir.iterdir()) else '❌ Has data'}"
        )
        print(
            f"📊 Results data dir: {'✅ Ready' if results_dir.exists() and not any(results_dir.iterdir()) else '❌ Has data'}"
        )
    else:
        print("❌ Horseracedatabase directory missing")

    # Check for any other data files
    other_files = [f for f in data_dir.glob("*.json") if f.is_file()]
    if other_files:
        print(f"🗂️  Other data files: {len(other_files)}")
        for f in other_files:
            print(f"   - {f.name}")
    else:
        print("✅ No old data files")


def check_docker_status():
    """Check Docker services status."""
    print("\n🐳 Docker Services Status:")
    print("=" * 40)
    os.system("docker-compose ps --format 'table {{.Name}}\\t{{.State}}\\t{{.Ports}}'")


def show_time_info():
    """Show current time and countdown."""
    now = datetime.now()
    target_time = now.replace(hour=11, minute=30, second=0, microsecond=0)

    if now >= target_time:
        # Already past 11:30
        print(f"\n⏰ Current time: {now.strftime('%H:%M:%S')}")
        print("🚀 Target time (11:30) has passed!")
    else:
        # Calculate remaining time
        time_diff = target_time - now
        minutes_left = int(time_diff.total_seconds() / 60)
        seconds_left = int(time_diff.total_seconds() % 60)

        print(f"\n⏰ Current time: {now.strftime('%H:%M:%S')}")
        print(f"🎯 Target time: 11:30:00")
        print(f"⏳ Time remaining: {minutes_left} minutes, {seconds_left} seconds")


def main():
    """Main status check."""
    print("🏇 Horse Racing Pipeline Status Check")
    print("=" * 50)

    os.chdir("/home/jc/Documents/Horse-race-ai-v2.0")

    show_time_info()
    check_data_status()
    check_docker_status()

    print("\n✅ Status check complete!")
    print("\n💡 The scheduler is monitoring time and will automatically")
    print("   run the pipeline at 11:30 to download fresh data!")


if __name__ == "__main__":
    main()
