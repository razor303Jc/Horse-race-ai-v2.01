#!/usr/bin/env python3
"""
Fixed Pipeline Scheduler
Monitors time and runs the pipeline at specified times with proper Python paths
"""

import time
import subprocess
import os
import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel

console = Console()


def send_notification(title, message, priority="default"):
    """Send NTFY notification using correct topic."""
    try:
        import requests

        url = "http://localhost:8081/horse_racing_alerts"
        headers = {
            "Title": title,
            "Priority": priority,
            "Tags": "horse,racing,scheduler",
        }
        response = requests.post(url, data=message, headers=headers)
        return response.status_code == 200
    except Exception as e:
        console.print(f"[yellow]⚠️ Notification failed: {e}[/yellow]")
        return False


def run_pipeline():
    """Run the complete racing pipeline with proper Python path."""
    console.print(
        Panel("🏇 Starting Scheduled Horse Racing Pipeline", style="bold green")
    )

    # Send start notification
    send_notification(
        "🏇 Pipeline Started",
        f"Automated horse racing pipeline started at "
        f"{datetime.now().strftime('%H:%M:%S')}",
        "high",
    )

    # Change to project directory
    os.chdir("/home/jc/Documents/Horse-race-ai-v2.0")

    # Use the current Python executable (not just 'python')
    python_path = sys.executable

    try:
        console.print(f"[cyan]Using Python: {python_path}[/cyan]")

        # Run the pipeline with proper Python path and output capture
        result = subprocess.run(
            [python_path, "demos/complete_racing_pipeline.py"],
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )

        if result.returncode == 0:
            console.print("✅ [green]Pipeline completed successfully![/green]")
            send_notification(
                "✅ Pipeline Success",
                f"Horse racing pipeline completed successfully at "
                f"{datetime.now().strftime('%H:%M:%S')}",
                "high",
            )
            return True
        else:
            console.print(
                f"❌ [red]Pipeline failed with return code: "
                f"{result.returncode}[/red]"
            )
            console.print(f"[red]Error output: {result.stderr}[/red]")
            send_notification(
                "❌ Pipeline Failed",
                f"Pipeline failed with error: {result.stderr[:100]}...",
                "max",
            )
            return False

    except subprocess.TimeoutExpired:
        console.print("❌ [red]Pipeline timed out after 10 minutes[/red]")
        send_notification(
            "⏰ Pipeline Timeout", "Pipeline exceeded 10 minute timeout limit", "max"
        )
        return False
    except Exception as e:
        console.print(f"❌ [red]Pipeline failed: {e}[/red]")
        send_notification(
            "❌ Pipeline Error", f"Pipeline failed with exception: {str(e)}", "max"
        )
        return False


def main():
    """Monitor time and run at specified intervals."""
    console.print(Panel("⏰ Fixed Horse Racing Pipeline Scheduler", style="bold blue"))

    # Send scheduler start notification
    send_notification(
        "⏰ Scheduler Started",
        "Pipeline scheduler started and monitoring for scheduled runs",
        "default",
    )

    target_hour = 11
    target_minute = 52  # Set for 11:52 for immediate testing

    console.print(
        f"[cyan]🎯 Waiting for {target_hour:02d}:{target_minute:02d}:00..." f"[/cyan]"
    )

    while True:
        now = datetime.now()
        current_time = f"{now.hour:02d}:{now.minute:02d}:{now.second:02d}"

        console.print(
            f"🕐 Current time: {current_time} - "
            f"Waiting for {target_hour:02d}:{target_minute:02d}:00..."
        )

        # Check if it's the target time
        if now.hour == target_hour and now.minute == target_minute:
            console.print(
                "🚀 [bold green]Time reached! Starting pipeline..." "[/bold green]"
            )
            success = run_pipeline()

            if success:
                console.print(
                    "✅ [bold green]Pipeline completed successfully!" "[/bold green]"
                )
            else:
                console.print("❌ [bold red]Pipeline completed with errors![/bold red]")

            console.print("📋 Scheduler finished. Exiting...")
            break

        # Check every 30 seconds
        time.sleep(30)


if __name__ == "__main__":
    main()
