#!/usr/bin/env python3
"""
Time-based Pipeline Scheduler
Monitors time and runs the pipeline at 11:30 AM
"""

import time
import subprocess
import os
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_pipeline():
    """Run the complete racing pipeline."""
    console.print(
        Panel("🏇 Starting Scheduled Horse Racing Pipeline", style="bold green")
    )

    # Change to project directory
    os.chdir("/home/jc/Documents/Horse-race-ai-v2.0")

    # Run the pipeline using full Python path
    try:
        import sys

        python_path = sys.executable
        result = subprocess.run(
            [python_path, "demos/complete_racing_pipeline.py"],
            capture_output=False,
            text=True,
            cwd="/home/jc/Documents/Horse-race-ai-v2.0",
        )
        return result.returncode == 0
    except Exception as e:
        console.print(f"❌ Pipeline failed: {e}")
        return False


def main():
    """Monitor time and run at 11:30."""
    console.print(Panel("⏰ Time-based Pipeline Scheduler", style="bold blue"))

    target_hour = 11
    target_minute = 30

    while True:
        now = datetime.now()
        current_time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

        console.print(f"🕐 Current time: {current_time} - Waiting for 11:30:00...")

        # Check if it's 11:30
        if now.hour == target_hour and now.minute == target_minute:
            console.print("🚀 Time reached! Starting pipeline...")
            success = run_pipeline()

            if success:
                console.print("✅ Pipeline completed successfully!")
            else:
                console.print("❌ Pipeline completed with errors!")

            console.print("📋 Scheduler finished. Exiting...")
            break

        # Check every 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    main()
