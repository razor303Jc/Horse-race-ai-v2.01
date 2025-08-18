#!/usr/bin/env python3
"""
⏱️ Simple Pipeline Process Monitor
================================

Monitors pipeline processes using basic system tools:
- Container status and health
- Process timing and performance
- Resource usage tracking
- Pipeline stage progress

Uses only standard library and system commands.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimplePipelineMonitor:
    """Simple pipeline monitoring using system commands"""

    def __init__(self):
        self.monitoring_data = {
            "session_start": datetime.now().isoformat(),
            "container_status": {},
            "process_timings": {},
            "resource_usage": [],
            "pipeline_progress": {},
        }

        # Container mapping
        self.containers = [
            "horse_racing_auto_downloader_clean",
            "horse_racing_data_pipeline_clean",
            "horse_racing_ml_trainer_clean",
            "horse_racing_postgres_clean",
            "horse_racing_redis_clean",
            "horse_racing_web_app_clean",
        ]

        self.process_stages = {
            "data_download": "auto_downloader",
            "preprocessing": "data_pipeline",
            "ml_training": "ml_trainer",
            "database": "postgres",
            "web_app": "web_app",
        }

    def start_monitoring(self):
        """Start the monitoring loop"""
        logger.info("⏱️ Starting Simple Pipeline Process Monitor")
        logger.info("=" * 60)

        try:
            asyncio.run(self.monitor_loop())
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
            self.save_monitoring_data()

    async def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("🔄 Starting monitoring loop...")

        while True:
            try:
                # Check every 20 seconds
                await self.check_container_status()
                await self.monitor_process_activity()
                await self.track_system_resources()
                await self.analyze_pipeline_progress()

                # Log summary every 2 minutes
                if datetime.now().minute % 2 == 0:
                    self.log_monitoring_summary()

                await asyncio.sleep(20)

            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(30)

    async def check_container_status(self):
        """Check status of all containers"""
        current_time = datetime.now().isoformat()
        container_status = {}

        for container in self.containers:
            try:
                # Get container status
                result = subprocess.run(
                    [
                        "docker",
                        "inspect",
                        "--format",
                        "{{.State.Status}}:{{.State.Health.Status}}:{{.State.StartedAt}}",
                        container,
                    ],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )

                if result.returncode == 0:
                    status_parts = result.stdout.strip().split(":")
                    container_status[container] = {
                        "status": (
                            status_parts[0] if len(status_parts) > 0 else "unknown"
                        ),
                        "health": (
                            status_parts[1]
                            if len(status_parts) > 1
                            else "no-health-check"
                        ),
                        "started_at": (
                            status_parts[2] if len(status_parts) > 2 else "unknown"
                        ),
                        "timestamp": current_time,
                    }
                else:
                    container_status[container] = {
                        "status": "not_found",
                        "error": result.stderr.strip(),
                        "timestamp": current_time,
                    }

            except Exception as e:
                container_status[container] = {
                    "status": "error",
                    "error": str(e),
                    "timestamp": current_time,
                }

        self.monitoring_data["container_status"] = container_status

    async def monitor_process_activity(self):
        """Monitor process activity within containers"""
        current_time = datetime.now().isoformat()

        for stage, container_type in self.process_stages.items():
            container_name = f"horse_racing_{container_type}_clean"

            try:
                # Get recent logs to detect activity
                result = subprocess.run(
                    ["docker", "logs", "--tail", "50", "--since", "2m", container_name],
                    capture_output=True,
                    text=True,
                    timeout=15,
                )

                if result.returncode == 0:
                    logs = result.stdout
                    activity_data = self.analyze_log_activity(stage, logs)

                    if stage not in self.monitoring_data["process_timings"]:
                        self.monitoring_data["process_timings"][stage] = []

                    self.monitoring_data["process_timings"][stage].append(
                        {"timestamp": current_time, **activity_data}
                    )

            except Exception as e:
                logger.error(f"❌ Error monitoring {stage}: {e}")

    def analyze_log_activity(self, stage: str, logs: str) -> dict:
        """Analyze log content for activity patterns"""
        activity_indicators = {
            "data_download": ["Download", "CSV", "Scraping", "Processing", "⏰", "📅"],
            "preprocessing": ["Preprocessing", "Processing CSV", "Enhanced", "✅"],
            "ml_training": [
                "Training",
                "Session",
                "Accuracy",
                "Model",
                "Power",
                "Monte",
            ],
            "database": ["INSERT", "UPDATE", "Connection", "Query"],
            "web_app": ["GET", "POST", "Request", "Response"],
        }

        completion_indicators = {
            "data_download": ["Download completed", "✅", "successfully downloaded"],
            "preprocessing": ["Processing complete", "preprocessed successfully"],
            "ml_training": ["Training complete", "Session completed"],
            "database": ["Connection established", "Ready"],
            "web_app": ["Server running", "Application started"],
        }

        error_indicators = ["Error", "Failed", "❌", "Exception", "Traceback"]

        # Count activity
        indicators = activity_indicators.get(stage, [])
        activity_count = sum(1 for indicator in indicators if indicator in logs)

        # Check completion
        completion = completion_indicators.get(stage, [])
        is_completed = any(comp in logs for comp in completion)

        # Check errors
        has_errors = any(error in logs for error in error_indicators)

        # Estimate processing time from timestamps
        lines = logs.strip().split("\n")
        log_timestamps = []
        for line in lines:
            if " - " in line:
                try:
                    timestamp_part = line.split(" - ")[0]
                    # Simple timestamp extraction
                    if ":" in timestamp_part:
                        log_timestamps.append(timestamp_part)
                except:
                    continue

        processing_duration = None
        if len(log_timestamps) >= 2:
            try:
                # Estimate duration based on first and last log entries
                processing_duration = f"{log_timestamps[0]} to {log_timestamps[-1]}"
            except:
                pass

        return {
            "activity_count": activity_count,
            "is_active": activity_count > 0,
            "is_completed": is_completed,
            "has_errors": has_errors,
            "processing_duration": processing_duration,
            "log_lines": len(lines),
            "recent_activity": logs[-200:] if logs else "",  # Last 200 chars
        }

    async def track_system_resources(self):
        """Track system resource usage"""
        current_time = datetime.now().isoformat()

        try:
            # Get CPU usage
            cpu_result = subprocess.run(
                ["top", "-bn1"], capture_output=True, text=True, timeout=10
            )
            cpu_line = next(
                (line for line in cpu_result.stdout.split("\n") if "Cpu(s)" in line), ""
            )

            # Get memory usage
            mem_result = subprocess.run(
                ["free", "-m"], capture_output=True, text=True, timeout=10
            )

            # Get disk usage
            disk_result = subprocess.run(
                ["df", "-h", "/"], capture_output=True, text=True, timeout=10
            )

            # Get Docker resource usage
            docker_stats_result = subprocess.run(
                [
                    "docker",
                    "stats",
                    "--no-stream",
                    "--format",
                    "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}",
                ]
                + self.containers,
                capture_output=True,
                text=True,
                timeout=15,
            )

            resource_data = {
                "timestamp": current_time,
                "cpu_info": cpu_line.strip(),
                "memory_info": mem_result.stdout,
                "disk_info": disk_result.stdout,
                "docker_stats": (
                    docker_stats_result.stdout
                    if docker_stats_result.returncode == 0
                    else "Error getting stats"
                ),
            }

            self.monitoring_data["resource_usage"].append(resource_data)

            # Keep only last 50 entries to prevent memory bloat
            if len(self.monitoring_data["resource_usage"]) > 50:
                self.monitoring_data["resource_usage"] = self.monitoring_data[
                    "resource_usage"
                ][-50:]

        except Exception as e:
            logger.error(f"❌ Error tracking resources: {e}")

    async def analyze_pipeline_progress(self):
        """Analyze overall pipeline progress"""
        current_time = datetime.now().isoformat()

        progress = {
            "timestamp": current_time,
            "stage_status": {},
            "overall_health": "unknown",
            "bottlenecks": [],
            "recommendations": [],
        }

        # Analyze each stage
        active_stages = 0
        completed_stages = 0
        error_stages = 0

        for stage in self.process_stages.keys():
            if stage in self.monitoring_data["process_timings"]:
                timings = self.monitoring_data["process_timings"][stage]
                if timings:
                    latest = timings[-1]

                    if latest.get("has_errors", False):
                        progress["stage_status"][stage] = "error"
                        error_stages += 1
                    elif latest.get("is_completed", False):
                        progress["stage_status"][stage] = "completed"
                        completed_stages += 1
                    elif latest.get("is_active", False):
                        progress["stage_status"][stage] = "active"
                        active_stages += 1
                    else:
                        progress["stage_status"][stage] = "idle"

        # Determine overall health
        total_stages = len(self.process_stages)
        if error_stages > 0:
            progress["overall_health"] = "degraded"
            progress["recommendations"].append(f"⚠️  {error_stages} stages have errors")
        elif active_stages > 0:
            progress["overall_health"] = "active"
        elif completed_stages == total_stages:
            progress["overall_health"] = "completed"
        else:
            progress["overall_health"] = "idle"

        # Check for bottlenecks
        if active_stages > 2:
            progress["bottlenecks"].append("Multiple stages running simultaneously")

        # Check container health
        unhealthy_containers = [
            name
            for name, status in self.monitoring_data["container_status"].items()
            if status.get("status") != "running"
        ]

        if unhealthy_containers:
            progress["bottlenecks"].append(
                f"Unhealthy containers: {', '.join(unhealthy_containers)}"
            )

        self.monitoring_data["pipeline_progress"] = progress

    def log_monitoring_summary(self):
        """Log comprehensive monitoring summary"""
        logger.info("📊 PIPELINE MONITORING SUMMARY")
        logger.info("=" * 50)

        # Container status
        logger.info("🐳 Container Status:")
        for container, status in self.monitoring_data["container_status"].items():
            container_short = container.replace("horse_racing_", "").replace(
                "_clean", ""
            )
            status_icon = "🟢" if status.get("status") == "running" else "🔴"
            health = status.get("health", "unknown")
            logger.info(
                f"  {status_icon} {container_short}: {status.get('status')} ({health})"
            )

        # Process activity
        logger.info("\n⚙️  Process Activity:")
        for stage in self.process_stages.keys():
            if stage in self.monitoring_data["process_timings"]:
                timings = self.monitoring_data["process_timings"][stage]
                if timings:
                    latest = timings[-1]
                    is_active = latest.get("is_active", False)
                    has_errors = latest.get("has_errors", False)

                    if has_errors:
                        status_icon = "❌"
                        status_text = "error"
                    elif is_active:
                        status_icon = "🔄"
                        status_text = "active"
                    else:
                        status_icon = "⏸️"
                        status_text = "idle"

                    activity_count = latest.get("activity_count", 0)
                    logger.info(
                        f"  {status_icon} {stage}: {status_text} (activity: {activity_count})"
                    )

        # Pipeline progress
        if "pipeline_progress" in self.monitoring_data:
            progress = self.monitoring_data["pipeline_progress"]
            health_icon = {
                "active": "🟢",
                "completed": "✅",
                "degraded": "🟡",
                "idle": "⏸️",
            }.get(progress.get("overall_health"), "❓")

            logger.info(
                f"\n🏁 Overall Health: {health_icon} {progress.get('overall_health', 'unknown')}"
            )

            if progress.get("bottlenecks"):
                logger.warning("⚠️  Bottlenecks:")
                for bottleneck in progress["bottlenecks"]:
                    logger.warning(f"  • {bottleneck}")

        # System resources
        if self.monitoring_data["resource_usage"]:
            latest_resources = self.monitoring_data["resource_usage"][-1]
            logger.info(f"\n🖥️  System Resources:")
            logger.info(f"  CPU: {latest_resources.get('cpu_info', 'unknown')}")

            # Parse memory info
            mem_info = latest_resources.get("memory_info", "")
            if mem_info:
                for line in mem_info.split("\n"):
                    if "Mem:" in line:
                        logger.info(f"  Memory: {line.strip()}")
                        break

    def save_monitoring_data(self):
        """Save monitoring data to JSON file"""
        filename = (
            f"pipeline_monitoring_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

        try:
            with open(filename, "w") as f:
                json.dump(self.monitoring_data, f, indent=2)
            logger.info(f"💾 Monitoring data saved to {filename}")
        except Exception as e:
            logger.error(f"❌ Error saving data: {e}")


def main():
    """Main function"""
    monitor = SimplePipelineMonitor()
    monitor.start_monitoring()


if __name__ == "__main__":
    print("⏱️ Simple Pipeline Process Monitor")
    print("=" * 50)
    print("Monitoring:")
    print("• Container Health & Status")
    print("• Process Activity & Timing")
    print("• System Resource Usage")
    print("• Pipeline Progress & Bottlenecks")
    print("")
    print("Press Ctrl+C to stop and save data")
    print("=" * 50)

    main()
