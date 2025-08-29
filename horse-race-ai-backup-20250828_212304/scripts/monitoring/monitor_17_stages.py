#!/usr/bin/env python3
"""
🚀 17-Stage Pipeline Real-Time Monitor
=====================================

Comprehensive monitoring of all 17 pipeline stages with real-time updates.
Updated for 15:45 schedule time.

Author: AI Assistant
Date: August 18, 2025
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


class Stage17Monitor:
    """Real-time monitor for all 17 pipeline stages"""

    def __init__(self):
        self.project_root = Path.cwd()
        self.logs_dir = self.project_root / "logs"

        # 17-Stage Pipeline Definition
        self.stages = [
            # Phase 1: Data Acquisition (28 minutes)
            {
                "id": 1,
                "name": "data_download",
                "phase": "Data Acquisition",
                "duration": 5,
                "status": "pending",
            },
            {
                "id": 2,
                "name": "data_validation",
                "phase": "Data Acquisition",
                "duration": 3,
                "status": "pending",
            },
            {
                "id": 3,
                "name": "data_ingestion",
                "phase": "Data Acquisition",
                "duration": 8,
                "status": "pending",
            },
            {
                "id": 4,
                "name": "data_cleanup",
                "phase": "Data Acquisition",
                "duration": 12,
                "status": "pending",
            },
            # Phase 2: Feature Engineering (45 minutes)
            {
                "id": 5,
                "name": "feature_extraction",
                "phase": "Feature Engineering",
                "duration": 15,
                "status": "pending",
            },
            {
                "id": 6,
                "name": "feature_transformation",
                "phase": "Feature Engineering",
                "duration": 12,
                "status": "pending",
            },
            {
                "id": 7,
                "name": "feature_selection",
                "phase": "Feature Engineering",
                "duration": 10,
                "status": "pending",
            },
            {
                "id": 8,
                "name": "feature_validation",
                "phase": "Feature Engineering",
                "duration": 8,
                "status": "pending",
            },
            # Phase 3: Advanced Analytics (120 minutes)
            {
                "id": 9,
                "name": "statistical_analysis",
                "phase": "Advanced Analytics",
                "duration": 30,
                "status": "pending",
            },
            {
                "id": 10,
                "name": "pattern_recognition",
                "phase": "Advanced Analytics",
                "duration": 35,
                "status": "pending",
            },
            {
                "id": 11,
                "name": "trend_analysis",
                "phase": "Advanced Analytics",
                "duration": 25,
                "status": "pending",
            },
            {
                "id": 12,
                "name": "correlation_analysis",
                "phase": "Advanced Analytics",
                "duration": 30,
                "status": "pending",
            },
            # Phase 4: Simulation (50 minutes)
            {
                "id": 13,
                "name": "monte_carlo_simulation",
                "phase": "Simulation",
                "duration": 25,
                "status": "pending",
            },
            {
                "id": 14,
                "name": "scenario_modeling",
                "phase": "Simulation",
                "duration": 25,
                "status": "pending",
            },
            # Phase 5: Strategy (35 minutes)
            {
                "id": 15,
                "name": "strategy_optimization",
                "phase": "Strategy",
                "duration": 20,
                "status": "pending",
            },
            {
                "id": 16,
                "name": "risk_assessment",
                "phase": "Strategy",
                "duration": 15,
                "status": "pending",
            },
            # Phase 6: Pre-Race (15 minutes)
            {
                "id": 17,
                "name": "pre_race_updates",
                "phase": "Pre-Race",
                "duration": 15,
                "status": "pending",
            },
        ]

        # Calculate timing for 15:45 schedule
        self.schedule_time = "15:45"
        self.calculate_stage_timing()

    def calculate_stage_timing(self):
        """Calculate timing for each stage based on 15:45 schedule"""
        # Assume first race at 14:00 for now (will be dynamic later)
        first_race_time = datetime.now().replace(
            hour=14, minute=0, second=0, microsecond=0
        )
        if first_race_time < datetime.now():
            first_race_time += timedelta(days=1)

        # Calculate pipeline end time (15 minutes before first race)
        pipeline_end = first_race_time - timedelta(minutes=15)

        # Total pipeline duration
        total_duration = sum(stage["duration"] for stage in self.stages)

        # Calculate start time
        pipeline_start = pipeline_end - timedelta(minutes=total_duration)

        # Assign start times to each stage
        current_time = pipeline_start
        for stage in self.stages:
            stage["start_time"] = current_time
            stage["end_time"] = current_time + timedelta(minutes=stage["duration"])
            current_time = stage["end_time"]

    def check_container_status(self):
        """Check Docker container status"""
        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "json"],
                capture_output=True,
                text=True,
                check=True,
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
            return []

    def check_file_activity(self):
        """Check for recent file activity"""
        data_dir = self.project_root / "data" / "daily_downloads"
        if not data_dir.exists():
            return {"files": 0, "latest": "No data directory"}

        try:
            # Count files modified in last hour
            cutoff = datetime.now() - timedelta(hours=1)
            recent_files = []

            for file_path in data_dir.rglob("*"):
                if file_path.is_file():
                    mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if mtime > cutoff:
                        recent_files.append(file_path)

            latest_file = "None"
            if recent_files:
                latest_file = max(recent_files, key=lambda f: f.stat().st_mtime).name

            return {"files": len(recent_files), "latest": latest_file}
        except Exception as e:
            return {"files": 0, "latest": f"Error: {e}"}

    def check_pipeline_logs(self):
        """Check recent pipeline logs"""
        try:
            result = subprocess.run(
                ["docker", "logs", "horse_racing_data_pipeline_clean", "--tail", "5"],
                capture_output=True,
                text=True,
            )

            lines = result.stdout.strip().split("\n") if result.stdout else []
            # Look for stage indicators
            stage_activities = []
            for line in lines:
                if any(
                    keyword in line.lower()
                    for keyword in [
                        "stage",
                        "phase",
                        "completed",
                        "started",
                        "processing",
                    ]
                ):
                    stage_activities.append(line.strip())

            return stage_activities[-3:] if stage_activities else ["No recent activity"]
        except Exception as e:
            return [f"Error reading logs: {e}"]

    def update_stage_status(self):
        """Update stage status based on current time and activity"""
        current_time = datetime.now()
        next_scheduled = datetime.now().replace(
            hour=15, minute=45, second=0, microsecond=0
        )

        if next_scheduled < current_time:
            next_scheduled += timedelta(days=1)

        # Check if we're in an active pipeline window
        time_to_schedule = (next_scheduled - current_time).total_seconds() / 60

        # Update stages based on timing
        for stage in self.stages:
            if hasattr(stage, "start_time") and hasattr(stage, "end_time"):
                if (
                    current_time >= stage["start_time"]
                    and current_time <= stage["end_time"]
                ):
                    stage["status"] = "running"
                elif current_time > stage["end_time"]:
                    stage["status"] = "completed"
                else:
                    stage["status"] = "pending"
            else:
                # Default status logic
                if time_to_schedule <= 0:
                    stage["status"] = "running" if stage["id"] <= 2 else "pending"
                else:
                    stage["status"] = "scheduled"

    def create_display(self):
        """Create the monitoring display"""
        # Update stage status
        self.update_stage_status()

        # Header
        current_time = datetime.now().strftime("%H:%M:%S")
        next_run = datetime.now().replace(hour=15, minute=45, second=0)
        if next_run < datetime.now():
            next_run += timedelta(days=1)

        time_to_next = next_run - datetime.now()

        layout = Layout()

        # Title panel
        title = Text("🏇 17-Stage Pipeline Monitor", style="bold blue")
        subtitle = Text(
            f"Schedule: 15:45 | Next Run: {time_to_next} | Current: {current_time}",
            style="dim",
        )
        title_panel = Panel(f"{title}\n{subtitle}", border_style="blue")

        # Container status
        containers = self.check_container_status()
        container_table = Table(
            title="🐳 Container Status", show_header=True, header_style="bold magenta"
        )
        container_table.add_column("Service", style="cyan")
        container_table.add_column("Status", style="green")
        container_table.add_column("Health", style="yellow")

        for container in containers:
            name = (
                container.get("Names", "Unknown")
                .replace("horse_racing_", "")
                .replace("_clean", "")
            )
            status = container.get("State", "Unknown")
            health_info = container.get("Status", "Unknown")
            health = (
                "🟢"
                if "healthy" in health_info
                else "🔴" if "unhealthy" in health_info else "🟡"
            )
            container_table.add_row(name, status, health)

        # Stage status
        stage_table = Table(
            title="🚀 Pipeline Stages Status",
            show_header=True,
            header_style="bold green",
        )
        stage_table.add_column("Stage", style="cyan", width=20)
        stage_table.add_column("Phase", style="blue", width=18)
        stage_table.add_column("Duration", style="yellow", width=8)
        stage_table.add_column("Status", style="green", width=12)
        stage_table.add_column("Progress", style="magenta", width=20)

        for stage in self.stages:
            # Status emoji
            status_emoji = {
                "completed": "✅",
                "running": "🔄",
                "pending": "⏳",
                "scheduled": "📅",
            }.get(stage["status"], "❓")

            # Progress bar
            progress = (
                "████████████████████"
                if stage["status"] == "completed"
                else (
                    "████████░░░░░░░░░░░░"
                    if stage["status"] == "running"
                    else "░░░░░░░░░░░░░░░░░░░░"
                )
            )

            stage_table.add_row(
                f"{stage['id']:2d}. {stage['name']}",
                stage["phase"],
                f"{stage['duration']}min",
                f"{status_emoji} {stage['status']}",
                progress,
            )

        # File activity
        file_activity = self.check_file_activity()
        activity_panel = Panel(
            f"📁 Files: {file_activity['files']} recent\n"
            f"📄 Latest: {file_activity['latest']}",
            title="📥 Data Activity",
            border_style="green",
        )

        # Pipeline logs
        logs = self.check_pipeline_logs()
        log_text = "\n".join(logs) if logs else "No recent activity"
        log_panel = Panel(log_text, title="📊 Recent Activity", border_style="yellow")

        # Layout
        layout.split_column(
            Layout(title_panel, size=3),
            Layout().split_row(
                Layout(container_table), Layout(activity_panel), Layout(log_panel)
            ),
            Layout(stage_table),
        )

        return layout

    def run_monitor(self):
        """Run the real-time monitor"""
        console.print("🚀 Starting 17-Stage Pipeline Monitor", style="bold blue")
        console.print("Press Ctrl+C to stop\n")

        try:
            with Live(self.create_display(), refresh_per_second=1, screen=True) as live:
                while True:
                    live.update(self.create_display())
                    time.sleep(5)  # Update every 5 seconds
        except KeyboardInterrupt:
            console.print("\n🛑 Monitor stopped", style="bold red")


def main():
    """Main entry point"""
    monitor = Stage17Monitor()
    monitor.run_monitor()


if __name__ == "__main__":
    main()
