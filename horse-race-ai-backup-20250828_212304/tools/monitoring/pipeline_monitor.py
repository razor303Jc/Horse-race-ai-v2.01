#!/usr/bin/env python3
"""
🎯 Complete Pipeline Monitor
============================

Real-time monitoring of the horse racing data pipeline from auto-download
through database upload with comprehensive logging and status tracking.

Features:
- Container status monitoring
- File system monitoring
- Database state tracking
- Pipeline progression analysis
- Real-time log streaming
"""

import json
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

console = Console()


class PipelineMonitor:
    """Complete pipeline monitoring system."""

    def __init__(self):
        """Initialize the monitor."""
        self.project_root = Path(__file__).parent.parent.parent
        self.downloads_dir = self.project_root / "data" / "daily_downloads"
        self.start_time = datetime.now()

    def get_container_status(self) -> dict:
        """Get auto-downloader container status."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horse_racing_auto_downloader_clean",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            status = result.stdout.strip()
            if "Up" in status:
                return {"status": "running", "details": status}
            else:
                return {"status": "stopped", "details": "Container not running"}

        except subprocess.CalledProcessError:
            return {"status": "error", "details": "Cannot check container"}

    def get_file_counts(self) -> dict:
        """Get current file counts in downloads directory."""
        if not self.downloads_dir.exists():
            return {"error": "Downloads directory not found"}

        counts = {
            "original_csv": 0,
            "mapped_csv": 0,
            "cleaned_csv": 0,
            "manifest_json": 0,
            "other_json": 0,
            "zip_files": 0,
            "html_files": 0,
            "sql_files": 0,
        }

        for file_path in self.downloads_dir.rglob("*"):
            if file_path.is_file():
                name = file_path.name

                if name.startswith("mapped_") and name.endswith(".csv"):
                    counts["mapped_csv"] += 1
                elif name.startswith("cleaned_") and name.endswith(".csv"):
                    counts["cleaned_csv"] += 1
                elif name.endswith(".csv"):
                    counts["original_csv"] += 1
                elif "manifest" in name and name.endswith(".json"):
                    counts["manifest_json"] += 1
                elif name.endswith(".json"):
                    counts["other_json"] += 1
                elif name.endswith(".zip"):
                    counts["zip_files"] += 1
                elif name.endswith(".html"):
                    counts["html_files"] += 1
                elif name.endswith(".sql"):
                    counts["sql_files"] += 1

        return counts

    def get_database_counts(self) -> dict:
        """Get current database row counts."""
        try:
            cmd = [
                "docker",
                "exec",
                "horse_racing_postgres",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "horse_racing_db",
                "-t",
                "-c",
                """
                SELECT 'races:' || COUNT(*) FROM races
                UNION ALL SELECT 'records:' || COUNT(*) FROM records
                UNION ALL SELECT 'horses:' || COUNT(*) FROM horses
                UNION ALL SELECT 'jockeys_stats:' || COUNT(*) FROM jockeys_stats
                UNION ALL SELECT 'trainers_stats:' || COUNT(*) FROM trainers_stats
                UNION ALL SELECT 'race_results:' || COUNT(*) FROM race_results
                UNION ALL SELECT 'racecard_details:' || COUNT(*) FROM racecard_details;
                """,
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

            counts = {}
            for line in result.stdout.strip().split("\n"):
                if ":" in line:
                    table, count = line.strip().split(":")
                    counts[table] = int(count)

            return counts

        except subprocess.CalledProcessError as e:
            return {"error": f"Database query failed: {e}"}

    def get_latest_logs(self, lines: int = 10) -> list:
        """Get latest container logs."""
        try:
            result = subprocess.run(
                [
                    "docker",
                    "logs",
                    "horse_racing_auto_downloader_clean",
                    "--tail",
                    str(lines),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            return result.stdout.strip().split("\n")[-lines:]

        except subprocess.CalledProcessError:
            return ["Unable to fetch logs"]

    def create_status_display(self) -> Layout:
        """Create the status display layout."""
        layout = Layout()

        # Container status
        container_info = self.get_container_status()
        container_panel = Panel(
            f"Status: {container_info['status'].upper()}\n{container_info['details']}",
            title="🐳 Container Status",
            border_style="green" if container_info["status"] == "running" else "red",
        )

        # File counts
        file_counts = self.get_file_counts()
        file_table = Table(title="📁 File System Status")
        file_table.add_column("File Type", style="cyan")
        file_table.add_column("Count", style="green")

        for file_type, count in file_counts.items():
            if isinstance(count, int):
                file_table.add_row(file_type.replace("_", " ").title(), str(count))

        # Database counts
        db_counts = self.get_database_counts()
        db_table = Table(title="🗄️ Database Status")
        db_table.add_column("Table", style="cyan")
        db_table.add_column("Rows", style="green")

        total_rows = 0
        for table, count in db_counts.items():
            if isinstance(count, int):
                db_table.add_row(table, str(count))
                total_rows += count

        db_table.add_row("TOTAL", str(total_rows), style="bold yellow")

        # Recent logs
        logs = self.get_latest_logs(8)
        log_text = Text()
        for log_line in logs:
            if log_line.strip():
                log_text.append(log_line + "\n")

        log_panel = Panel(log_text, title="📜 Recent Logs", border_style="blue")

        # Runtime info
        runtime = datetime.now() - self.start_time
        runtime_panel = Panel(
            f"Started: {self.start_time.strftime('%H:%M:%S')}\n"
            f"Runtime: {str(runtime).split('.')[0]}\n"
            f"Next Check: {(datetime.now().replace(second=0, microsecond=0) + timedelta(seconds=60)).strftime('%H:%M:%S')}",
            title="⏱️ Monitor Status",
            border_style="yellow",
        )

        # Create layout
        layout.split_column(
            Layout(container_panel, name="container"),
            Layout(ratio=2, name="main"),
            Layout(log_panel, name="logs", size=10),
        )

        layout["main"].split_row(Layout(file_table, name="files"), Layout(name="right"))

        layout["main"]["right"].split_column(
            Layout(db_table, name="database"), Layout(runtime_panel, name="runtime")
        )

        return layout

    def run_monitor(self):
        """Run the monitoring loop."""
        console.print("🎯 [bold green]Starting Complete Pipeline Monitor[/bold green]")
        console.print(f"📂 Monitoring: {self.downloads_dir}")
        console.print(f"⏰ Schedule: 10:31 daily")
        console.print("🔄 Press Ctrl+C to stop\n")

        try:
            with Live(self.create_status_display(), refresh_per_second=1) as live:
                while True:
                    live.update(self.create_status_display())
                    time.sleep(5)  # Update every 5 seconds

        except KeyboardInterrupt:
            console.print("\n🛑 [bold red]Monitor stopped by user[/bold red]")
        except Exception as e:
            console.print(f"\n❌ [bold red]Monitor error: {e}[/bold red]")


def main():
    """Main entry point."""
    monitor = PipelineMonitor()
    monitor.run_monitor()


if __name__ == "__main__":
    main()
