#!/usr/bin/env python3
"""
Test the pipeline execution with proper Python paths and NTFY notifications
"""

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
        headers = {"Title": title, "Priority": priority, "Tags": "horse,racing,test"}
        response = requests.post(url, data=message, headers=headers)
        if response.status_code == 200:
            console.print(f"✅ [green]Notification sent: {title}[/green]")
            return True
        else:
            console.print(f"❌ [red]Notification failed: {response.status_code}[/red]")
            return False
    except Exception as e:
        console.print(f"⚠️ [yellow]Notification failed: {e}[/yellow]")
        return False


def test_pipeline():
    """Test the complete racing pipeline with proper Python path."""
    console.print(Panel("Testing Pipeline Execution", style="bold green"))

    # Send start notification
    send_notification(
        "Pipeline Test Started",
        f"Testing pipeline execution at {datetime.now().strftime('%H:%M:%S')}",
        "high",
    )

    # Change to project directory
    os.chdir("/home/jc/Documents/Horse-race-ai-v2.0")

    # Use the current Python executable (not just 'python')
    python_path = sys.executable

    try:
        console.print(f"[cyan]Using Python: {python_path}[/cyan]")
        console.print(f"[cyan]Working directory: {os.getcwd()}[/cyan]")

        # Test if the pipeline file exists
        pipeline_file = "demos/complete_racing_pipeline.py"
        if not os.path.exists(pipeline_file):
            console.print(f"❌ [red]Pipeline file not found: {pipeline_file}[/red]")
            # Try alternative files
            alternatives = [
                "demos/enhanced_auto_download_system.py",
                "demos/horseracedatabase_auto_downloader.py",
                "main.py",
            ]
            for alt in alternatives:
                if os.path.exists(alt):
                    console.print(f"✅ [green]Found alternative: {alt}[/green]")
                    pipeline_file = alt
                    break
            else:
                console.print("❌ [red]No suitable pipeline file found[/red]")
                return False

        console.print(f"[cyan]Running: {pipeline_file}[/cyan]")

        # Run the pipeline with proper Python path and output capture
        result = subprocess.run(
            [python_path, pipeline_file],
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout for testing
        )

        console.print(f"[cyan]Return code: {result.returncode}[/cyan]")
        if result.stdout:
            console.print(f"[blue]STDOUT:\n{result.stdout}[/blue]")
        if result.stderr:
            console.print(f"[red]STDERR:\n{result.stderr}[/red]")

        if result.returncode == 0:
            console.print("✅ [green]Pipeline completed successfully![/green]")
            send_notification(
                "Pipeline Test Success",
                f"Pipeline test completed successfully at "
                f"{datetime.now().strftime('%H:%M:%S')}",
                "high",
            )
            return True
        else:
            console.print(
                f"❌ [red]Pipeline failed with return code: "
                f"{result.returncode}[/red]"
            )
            send_notification(
                "Pipeline Test Failed",
                f"Pipeline test failed with error: {result.stderr[:100]}...",
                "max",
            )
            return False

    except subprocess.TimeoutExpired:
        console.print("❌ [red]Pipeline timed out after 2 minutes[/red]")
        send_notification(
            "Pipeline Test Timeout",
            "Pipeline test exceeded 2 minute timeout limit",
            "max",
        )
        return False
    except Exception as e:
        console.print(f"❌ [red]Pipeline failed: {e}[/red]")
        send_notification(
            "Pipeline Test Error",
            f"Pipeline test failed with exception: {str(e)}",
            "max",
        )
        return False


def main():
    """Test the pipeline execution."""
    console.print(Panel("Horse Racing Pipeline Test", style="bold blue"))

    # Send start notification
    send_notification(
        "Pipeline Test Started", "Starting pipeline execution test", "default"
    )

    success = test_pipeline()

    if success:
        console.print("✅ [bold green]Test completed successfully![/bold green]")
    else:
        console.print("❌ [bold red]Test completed with errors![/bold red]")

    console.print("📋 Test finished.")


if __name__ == "__main__":
    main()
