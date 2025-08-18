#!/usr/bin/env python3
"""
⏱️ Pipeline Process Performance Tracker
=======================================

Tracks timing and performance for all pipeline processes:
1. Data Download Stage
2. Enhanced Preprocessing Stage
3. Database Upload Stage
4. ML Training Stage (Power Ratings & Monte Carlo)
5. Pipeline Coordination
6. System Resource Usage

Measures execution time, throughput, and identifies bottlenecks.
"""

import asyncio
import json
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import psutil

import docker

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PipelineProcessTracker:
    """Tracks performance and timing for all pipeline processes"""

    def __init__(self):
        self.docker_client = docker.from_env()
        self.tracking_data = {
            "session_start": datetime.now().isoformat(),
            "process_timings": {},
            "performance_metrics": {},
            "stage_progress": {},
            "bottlenecks": [],
        }

        # Pipeline process mapping
        self.processes = {
            "data_download": {
                "container": "horse_racing_auto_downloader_clean",
                "log_indicators": ["Download", "CSV", "Scraping"],
                "performance_file": "/app/logs/auto_downloader.log",
            },
            "enhanced_preprocessing": {
                "container": "horse_racing_data_pipeline_clean",
                "log_indicators": ["Preprocessing", "Processing CSV", "Enhanced"],
                "performance_file": "/app/enhanced_preprocessing_pipeline.py",
            },
            "database_upload": {
                "container": "horse_racing_data_pipeline_clean",
                "log_indicators": ["Upload", "INSERT", "Database"],
                "performance_file": "/app/tools/csv_processing/",
            },
            "ml_training": {
                "container": "horse_racing_ml_trainer_clean",
                "log_indicators": ["Training", "Session", "Accuracy", "Model"],
                "performance_file": "/app/tools/ml_training/",
            },
            "power_ratings": {
                "container": "horse_racing_ml_trainer_clean",
                "log_indicators": ["Power", "Rating", "Score"],
                "performance_file": "/app/tools/ml_training/",
            },
            "monte_carlo": {
                "container": "horse_racing_ml_trainer_clean",
                "log_indicators": ["Monte", "Carlo", "Simulation"],
                "performance_file": "/app/tools/ml_training/",
            },
        }

    def start_tracking(self):
        """Start process performance tracking"""
        logger.info("⏱️ Starting Pipeline Process Performance Tracking")
        logger.info("=" * 70)

        # Initial system baseline
        self.capture_system_baseline()

        # Start tracking loop
        asyncio.run(self.tracking_loop())

    async def tracking_loop(self):
        """Main tracking loop"""
        logger.info("🔄 Starting process tracking loop...")

        while True:
            try:
                # Track every 15 seconds for detailed timing
                await self.track_all_processes()
                await self.measure_pipeline_flow()
                await self.identify_bottlenecks()
                await self.track_resource_usage()

                # Log progress every 2 minutes
                if datetime.now().minute % 2 == 0:
                    self.log_process_summary()

                await asyncio.sleep(15)

            except KeyboardInterrupt:
                logger.info("🛑 Tracking stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Tracking error: {e}")
                await asyncio.sleep(30)

    def capture_system_baseline(self):
        """Capture initial system performance baseline"""
        logger.info("📊 Capturing system baseline...")

        baseline = {
            "timestamp": datetime.now().isoformat(),
            "cpu_count": psutil.cpu_count(),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "disk_total_gb": round(psutil.disk_usage("/").total / (1024**3), 2),
            "initial_cpu_percent": psutil.cpu_percent(interval=1),
            "initial_memory_percent": psutil.virtual_memory().percent,
        }

        self.tracking_data["system_baseline"] = baseline
        logger.info(
            f"System: {baseline['cpu_count']} CPUs, {baseline['memory_total_gb']}GB RAM"
        )

    async def track_all_processes(self):
        """Track performance of all pipeline processes"""
        current_time = datetime.now().isoformat()

        for process_name, process_info in self.processes.items():
            try:
                # Get process timing and status
                timing_data = await self.measure_process_timing(
                    process_name, process_info
                )

                # Update tracking data
                if process_name not in self.tracking_data["process_timings"]:
                    self.tracking_data["process_timings"][process_name] = []

                self.tracking_data["process_timings"][process_name].append(
                    {"timestamp": current_time, **timing_data}
                )

            except Exception as e:
                logger.error(f"❌ Error tracking {process_name}: {e}")

    async def measure_process_timing(
        self, process_name: str, process_info: dict
    ) -> dict:
        """Measure timing for a specific process"""
        container_name = process_info["container"]
        log_indicators = process_info["log_indicators"]

        try:
            # Get container
            container = self.docker_client.containers.get(container_name)

            # Get recent logs
            logs = container.logs(tail=100, since=datetime.now() - timedelta(minutes=5))
            log_text = logs.decode("utf-8")

            # Analyze process activity
            activity_detected = any(
                indicator in log_text for indicator in log_indicators
            )

            # Get container stats
            stats = container.stats(stream=False)
            cpu_percent = self.calculate_cpu_percentage(stats)
            memory_mb = self.calculate_memory_usage(stats)

            # Check for completion indicators
            completion_status = self.check_completion_status(process_name, log_text)

            # Estimate execution time if active
            execution_time = self.estimate_execution_time(process_name, log_text)

            return {
                "status": "active" if activity_detected else "idle",
                "cpu_percent": cpu_percent,
                "memory_mb": memory_mb,
                "activity_detected": activity_detected,
                "completion_status": completion_status,
                "estimated_execution_time_seconds": execution_time,
                "container_healthy": container.status == "running",
            }

        except Exception as e:
            return {"status": "error", "error": str(e), "container_healthy": False}

    def check_completion_status(self, process_name: str, log_text: str) -> str:
        """Check if process has completed successfully"""
        completion_indicators = {
            "data_download": ["Download completed", "✅", "successfully"],
            "enhanced_preprocessing": ["Processing complete", "✅", "preprocessed"],
            "database_upload": ["Upload complete", "inserted", "✅"],
            "ml_training": ["Training complete", "Session completed", "Accuracy"],
            "power_ratings": ["Power ratings calculated", "Rating complete"],
            "monte_carlo": ["Simulation complete", "Monte Carlo finished"],
        }

        if process_name in completion_indicators:
            indicators = completion_indicators[process_name]
            if any(indicator in log_text for indicator in indicators):
                return "completed"

        error_indicators = ["Error", "Failed", "❌", "Exception"]
        if any(error in log_text for error in error_indicators):
            return "error"

        return "in_progress"

    def estimate_execution_time(
        self, process_name: str, log_text: str
    ) -> Optional[float]:
        """Estimate execution time based on log timestamps"""
        lines = log_text.strip().split("\n")
        if len(lines) < 2:
            return None

        try:
            # Look for timestamp patterns in logs
            timestamps = []
            for line in lines:
                # Common timestamp patterns
                if " - " in line and ":" in line:
                    timestamp_part = line.split(" - ")[0]
                    try:
                        # Try parsing common timestamp formats
                        dt = datetime.fromisoformat(timestamp_part)
                        timestamps.append(dt)
                    except:
                        continue

            if len(timestamps) >= 2:
                duration = (timestamps[-1] - timestamps[0]).total_seconds()
                return duration

        except Exception:
            pass

        return None

    async def measure_pipeline_flow(self):
        """Measure the flow between pipeline stages"""
        flow_data = {
            "timestamp": datetime.now().isoformat(),
            "stage_transitions": {},
            "data_flow_rate": {},
            "queue_sizes": {},
        }

        # Check data flow between stages
        flow_data["data_flow_rate"] = await self.measure_data_throughput()
        flow_data["queue_sizes"] = await self.check_processing_queues()

        self.tracking_data["pipeline_flow"] = flow_data

    async def measure_data_throughput(self) -> dict:
        """Measure data throughput at each stage"""
        throughput = {}

        try:
            # Data download throughput (CSV files per minute)
            download_container = self.docker_client.containers.get(
                "horse_racing_auto_downloader_clean"
            )
            csv_result = download_container.exec_run(
                "find /app/data -name '*.csv' -mmin -5 | wc -l"
            )
            recent_csvs = (
                int(csv_result.output.decode().strip()) if csv_result.output else 0
            )
            throughput["download_csvs_per_5min"] = recent_csvs

            # Preprocessing throughput (processed files)
            pipeline_container = self.docker_client.containers.get(
                "horse_racing_data_pipeline_clean"
            )
            processed_result = pipeline_container.exec_run(
                "find /app/data/preprocessed -name '*.csv' -mmin -5 | wc -l"
            )
            processed_files = (
                int(processed_result.output.decode().strip())
                if processed_result.output
                else 0
            )
            throughput["preprocessing_files_per_5min"] = processed_files

            # Database throughput (records inserted)
            db_throughput = await self.measure_database_throughput()
            throughput.update(db_throughput)

        except Exception as e:
            logger.error(f"❌ Error measuring throughput: {e}")
            throughput["error"] = str(e)

        return throughput

    async def measure_database_throughput(self) -> dict:
        """Measure database insertion throughput"""
        try:
            # Query recent database activity
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "horse_racing_db",
                    "-c",
                    "SELECT schemaname, tablename, n_tup_ins as inserts, n_tup_upd as updates, n_tup_del as deletes FROM pg_stat_user_tables;",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                return {"database_activity": result.stdout}
            else:
                return {"database_error": result.stderr}

        except Exception as e:
            return {"database_error": str(e)}

    async def check_processing_queues(self) -> dict:
        """Check for processing queues and backlogs"""
        queues = {}

        try:
            # Check pending CSV files
            download_container = self.docker_client.containers.get(
                "horse_racing_auto_downloader_clean"
            )
            pending_result = download_container.exec_run(
                "find /app/data/daily_downloads -name '*.csv' | wc -l"
            )
            pending_csvs = (
                int(pending_result.output.decode().strip())
                if pending_result.output
                else 0
            )
            queues["pending_csv_files"] = pending_csvs

            # Check unprocessed files
            pipeline_container = self.docker_client.containers.get(
                "horse_racing_data_pipeline_clean"
            )
            unprocessed_result = pipeline_container.exec_run(
                "find /app/data/daily_downloads -name '*.csv' ! -path '*/preprocessed/*' | wc -l"
            )
            unprocessed_files = (
                int(unprocessed_result.output.decode().strip())
                if unprocessed_result.output
                else 0
            )
            queues["unprocessed_files"] = unprocessed_files

        except Exception as e:
            queues["error"] = str(e)

        return queues

    async def identify_bottlenecks(self):
        """Identify performance bottlenecks in the pipeline"""
        bottlenecks = []
        current_time = datetime.now().isoformat()

        # Check for slow processes
        for process_name, timings in self.tracking_data["process_timings"].items():
            if not timings:
                continue

            latest = timings[-1]

            # Check for long execution times
            if latest.get("estimated_execution_time_seconds", 0) > 300:  # 5 minutes
                bottlenecks.append(
                    {
                        "type": "slow_execution",
                        "process": process_name,
                        "execution_time": latest["estimated_execution_time_seconds"],
                        "timestamp": current_time,
                    }
                )

            # Check for high resource usage
            if latest.get("cpu_percent", 0) > 80:
                bottlenecks.append(
                    {
                        "type": "high_cpu",
                        "process": process_name,
                        "cpu_percent": latest["cpu_percent"],
                        "timestamp": current_time,
                    }
                )

            if latest.get("memory_mb", 0) > 2000:  # 2GB
                bottlenecks.append(
                    {
                        "type": "high_memory",
                        "process": process_name,
                        "memory_mb": latest["memory_mb"],
                        "timestamp": current_time,
                    }
                )

        # Check for queue backlogs
        if "pipeline_flow" in self.tracking_data:
            flow = self.tracking_data["pipeline_flow"]
            if flow.get("queue_sizes", {}).get("pending_csv_files", 0) > 50:
                bottlenecks.append(
                    {
                        "type": "csv_backlog",
                        "pending_files": flow["queue_sizes"]["pending_csv_files"],
                        "timestamp": current_time,
                    }
                )

        self.tracking_data["bottlenecks"].extend(bottlenecks)

        # Log new bottlenecks
        for bottleneck in bottlenecks:
            logger.warning(
                f"🚨 BOTTLENECK: {bottleneck['type']} in {bottleneck.get('process', 'pipeline')}"
            )

    async def track_resource_usage(self):
        """Track system resource usage over time"""
        resource_data = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage("/").percent,
            "network_io": psutil.net_io_counters()._asdict(),
            "disk_io": psutil.disk_io_counters()._asdict(),
        }

        # Track Docker container resources
        container_resources = {}
        for process_name, process_info in self.processes.items():
            try:
                container = self.docker_client.containers.get(process_info["container"])
                stats = container.stats(stream=False)
                container_resources[process_name] = {
                    "cpu_percent": self.calculate_cpu_percentage(stats),
                    "memory_mb": self.calculate_memory_usage(stats),
                }
            except Exception:
                container_resources[process_name] = {"error": "unable_to_get_stats"}

        resource_data["container_resources"] = container_resources

        if "resource_usage" not in self.tracking_data:
            self.tracking_data["resource_usage"] = []

        self.tracking_data["resource_usage"].append(resource_data)

    def log_process_summary(self):
        """Log comprehensive process performance summary"""
        logger.info("📊 PIPELINE PROCESS SUMMARY")
        logger.info("=" * 60)

        # Process status overview
        for process_name in self.processes.keys():
            if process_name in self.tracking_data["process_timings"]:
                timings = self.tracking_data["process_timings"][process_name]
                if timings:
                    latest = timings[-1]
                    status = latest.get("status", "unknown")
                    cpu = latest.get("cpu_percent", 0)
                    memory = latest.get("memory_mb", 0)

                    status_icon = (
                        "🔄"
                        if status == "active"
                        else "⏸️" if status == "idle" else "❌"
                    )
                    logger.info(
                        f"{status_icon} {process_name}: {status} | CPU: {cpu}% | RAM: {memory}MB"
                    )

        # System resources
        if self.tracking_data.get("resource_usage"):
            latest_resources = self.tracking_data["resource_usage"][-1]
            logger.info(
                f"🖥️  System: CPU {latest_resources['cpu_percent']}% | "
                f"RAM {latest_resources['memory_percent']}% | "
                f"Disk {latest_resources['disk_percent']}%"
            )

        # Bottlenecks
        recent_bottlenecks = [
            b
            for b in self.tracking_data["bottlenecks"]
            if (datetime.now() - datetime.fromisoformat(b["timestamp"])).seconds < 300
        ]
        if recent_bottlenecks:
            logger.warning(f"⚠️  Recent bottlenecks: {len(recent_bottlenecks)}")

        # Pipeline flow
        if "pipeline_flow" in self.tracking_data:
            flow = self.tracking_data["pipeline_flow"]
            queues = flow.get("queue_sizes", {})
            logger.info(
                f"📋 Queue: {queues.get('pending_csv_files', 0)} CSV files, "
                f"{queues.get('unprocessed_files', 0)} unprocessed"
            )

    # Helper methods
    def calculate_cpu_percentage(self, stats):
        """Calculate CPU percentage from container stats"""
        try:
            cpu_delta = (
                stats["cpu_stats"]["cpu_usage"]["total_usage"]
                - stats["precpu_stats"]["cpu_usage"]["total_usage"]
            )
            system_delta = (
                stats["cpu_stats"]["system_cpu_usage"]
                - stats["precpu_stats"]["system_cpu_usage"]
            )

            if system_delta > 0 and cpu_delta > 0:
                cpu_percent = (
                    (cpu_delta / system_delta)
                    * len(stats["cpu_stats"]["cpu_usage"]["percpu_usage"])
                    * 100.0
                )
                return round(cpu_percent, 2)
        except (KeyError, ZeroDivisionError):
            pass
        return 0.0

    def calculate_memory_usage(self, stats):
        """Calculate memory usage in MB"""
        try:
            memory_usage = stats["memory_stats"]["usage"]
            return round(memory_usage / (1024 * 1024), 2)
        except KeyError:
            return 0.0

    def save_tracking_data(self, filename: str = None):
        """Save tracking data to JSON file"""
        if filename is None:
            filename = f"pipeline_process_tracking_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, "w") as f:
            json.dump(self.tracking_data, f, indent=2)

        logger.info(f"💾 Tracking data saved to {filename}")


async def main():
    """Main tracking function"""
    tracker = PipelineProcessTracker()

    try:
        tracker.start_tracking()
    except KeyboardInterrupt:
        logger.info("🛑 Process tracking stopped")
        tracker.save_tracking_data()
    except Exception as e:
        logger.error(f"❌ Tracking error: {e}")
        tracker.save_tracking_data()


if __name__ == "__main__":
    print("⏱️ Pipeline Process Performance Tracker")
    print("=" * 70)
    print("This will track timing and performance for:")
    print("• Data Download Process")
    print("• Enhanced Preprocessing")
    print("• Database Upload")
    print("• ML Training (Power Ratings & Monte Carlo)")
    print("• Resource Usage & Bottlenecks")
    print("• Pipeline Flow & Throughput")
    print("")
    print("Press Ctrl+C to stop tracking and save data")
    print("=" * 70)

    asyncio.run(main())
