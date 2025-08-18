#!/usr/bin/env python3
"""
🔍 Comprehensive Pipeline Monitor & Logger
==========================================

Real-time monitoring and logging of the entire pipeline process
- Tracks all container states and logs
- Monitors database changes
- Records performance metrics
- Debugs pipeline issues

Author: AI Assistant
Date: August 17, 2025
"""

import json
import logging
import subprocess
import time
from datetime import datetime
from pathlib import Path

# Setup comprehensive logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "pipeline_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("PipelineMonitor")


class PipelineMonitor:
    """Comprehensive pipeline monitoring and debugging system"""

    def __init__(self):
        self.containers = [
            "horse_racing_auto_downloader_clean",
            "horse_racing_data_pipeline_clean",
            "horse_racing_postgres_clean",
            "horse_racing_redis_clean",
            "horse_racing_web_app_clean",
            "horse_racing_ml_trainer_clean",
        ]
        self.start_time = datetime.now()
        self.metrics = {
            "container_health": {},
            "database_records": {},
            "file_counts": {},
            "performance_timings": {},
            "errors": [],
        }

    def log_separator(self, title):
        """Create a visual separator in logs"""
        separator = "=" * 60
        logger.info(f"\n{separator}")
        logger.info(f"🔍 {title}")
        logger.info(separator)

    def check_container_health(self):
        """Monitor all container health states"""
        self.log_separator("Container Health Check")

        try:
            # Get container status
            result = subprocess.run(
                ["docker-compose", "-f", "docker-compose.clean.yml", "ps"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                logger.info("✅ Docker containers status:")
                for line in result.stdout.split("\n"):
                    if "horse_racing" in line:
                        logger.info(f"  📦 {line.strip()}")
            else:
                logger.error(f"❌ Failed to get container status: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Container health check failed: {e}")

    def monitor_auto_downloader_logs(self):
        """Monitor auto-downloader logs in real-time"""
        self.log_separator("Auto-Downloader Logs")

        try:
            result = subprocess.run(
                [
                    "docker",
                    "logs",
                    "--tail",
                    "20",
                    "horse_racing_auto_downloader_clean",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                logger.info("📋 Auto-Downloader recent logs:")
                for line in result.stdout.strip().split("\n"):
                    if line.strip():
                        logger.info(f"  🔸 {line}")
            else:
                logger.error(f"❌ Failed to get auto-downloader logs: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Auto-downloader log monitoring failed: {e}")

    def check_database_status(self):
        """Monitor database table record counts"""
        self.log_separator("Database Status")

        try:
            # Check database record counts
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
                    """
                SELECT 
                    'races' as table_name, COUNT(*) as records FROM races
                UNION ALL
                SELECT 'records', COUNT(*) FROM records  
                UNION ALL
                SELECT 'horses', COUNT(*) FROM horses
                UNION ALL
                SELECT 'jockeys_stats', COUNT(*) FROM jockeys_stats
                UNION ALL
                SELECT 'trainers_stats', COUNT(*) FROM trainers_stats;
                """,
                ],
                capture_output=True,
                text=True,
                timeout=20,
            )

            if result.returncode == 0:
                logger.info("🗃️ Database table record counts:")
                for line in result.stdout.split("\n"):
                    if "|" in line and "table_name" not in line and line.strip():
                        logger.info(f"  📊 {line.strip()}")
            else:
                logger.error(f"❌ Database status check failed: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Database monitoring failed: {e}")

    def check_data_files(self):
        """Monitor data file status"""
        self.log_separator("Data Files Status")

        try:
            # Check downloaded files
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_auto_downloader_clean",
                    "find",
                    "/app/data/daily_downloads",
                    "-name",
                    "*.csv",
                    "-type",
                    "f",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                csv_files = [f for f in result.stdout.strip().split("\n") if f.strip()]
                logger.info(f"📁 Found {len(csv_files)} CSV files:")
                for file in csv_files[:10]:  # Show first 10
                    logger.info(f"  📄 {file.split('/')[-1]}")
                if len(csv_files) > 10:
                    logger.info(f"  ... and {len(csv_files) - 10} more files")
            else:
                logger.info("📁 No CSV files found or container not accessible")

            # Check preprocessed files
            result2 = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_data_pipeline_clean",
                    "find",
                    "/app/data/preprocessed",
                    "-name",
                    "*.csv",
                    "-type",
                    "f",
                ],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result2.returncode == 0:
                preprocessed_files = [
                    f for f in result2.stdout.strip().split("\n") if f.strip()
                ]
                logger.info(f"🧹 Found {len(preprocessed_files)} preprocessed files")
            else:
                logger.info("🧹 No preprocessed files found")

        except Exception as e:
            logger.error(f"❌ Data file monitoring failed: {e}")

    def monitor_pipeline_coordinator(self):
        """Check pipeline coordinator status"""
        self.log_separator("Pipeline Coordinator Status")

        try:
            # Check if pipeline coordinator is running
            result = subprocess.run(
                ["docker", "exec", "horse_racing_data_pipeline_clean", "ps", "aux"],
                capture_output=True,
                text=True,
                timeout=15,
            )

            if result.returncode == 0:
                pipeline_processes = []
                for line in result.stdout.split("\n"):
                    if (
                        "pipeline_coordinator" in line
                        or "enhanced_preprocessing" in line
                    ):
                        pipeline_processes.append(line.strip())

                if pipeline_processes:
                    logger.info("🔄 Pipeline processes running:")
                    for process in pipeline_processes:
                        logger.info(f"  ⚙️ {process}")
                else:
                    logger.info("⏸️ No active pipeline processes detected")
            else:
                logger.error(f"❌ Failed to check pipeline processes: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Pipeline coordinator monitoring failed: {e}")

    def get_system_metrics(self):
        """Get system performance metrics"""
        self.log_separator("System Performance Metrics")

        try:
            # Get Docker stats
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
                timeout=20,
            )

            if result.returncode == 0:
                logger.info("💻 Container resource usage:")
                for line in result.stdout.split("\n")[1:]:  # Skip header
                    if line.strip():
                        logger.info(f"  📈 {line}")
            else:
                logger.error(f"❌ Failed to get system metrics: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ System metrics monitoring failed: {e}")

    def trigger_manual_pipeline_test(self):
        """Trigger a manual pipeline test run"""
        self.log_separator("Manual Pipeline Test")

        try:
            logger.info("🧪 Triggering manual enhanced preprocessing...")

            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_data_pipeline_clean",
                    "python",
                    "/app/enhanced_preprocessing_pipeline.py",
                ],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Manual preprocessing completed successfully")
                # Log key output lines
                for line in result.stdout.split("\n"):
                    if any(
                        keyword in line
                        for keyword in ["INFO:", "Processing", "complete", "rows"]
                    ):
                        logger.info(f"  📝 {line.strip()}")
            else:
                logger.error(f"❌ Manual preprocessing failed: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Manual pipeline test failed: {e}")

    def save_metrics_summary(self):
        """Save monitoring metrics to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        metrics_file = log_dir / f"pipeline_metrics_{timestamp}.json"

        self.metrics["monitoring_duration"] = (
            datetime.now() - self.start_time
        ).total_seconds()
        self.metrics["timestamp"] = timestamp

        try:
            with open(metrics_file, "w") as f:
                json.dump(self.metrics, f, indent=2, default=str)
            logger.info(f"💾 Metrics saved to {metrics_file}")
        except Exception as e:
            logger.error(f"❌ Failed to save metrics: {e}")

    def run_comprehensive_monitoring(self, duration_minutes=30):
        """Run comprehensive monitoring for specified duration"""
        logger.info(
            f"🚀 Starting comprehensive pipeline monitoring for {duration_minutes} minutes..."
        )
        logger.info(f"⏰ Current time: {datetime.now().strftime('%H:%M:%S')}")
        logger.info("📊 Monitoring the 20:00 scheduled pipeline execution...")

        end_time = datetime.now().timestamp() + (duration_minutes * 60)
        cycle = 0

        while datetime.now().timestamp() < end_time:
            cycle += 1
            logger.info(f"\n🔍 === MONITORING CYCLE {cycle} ===")
            logger.info(f"⏰ Time: {datetime.now().strftime('%H:%M:%S')}")

            # Run all monitoring checks
            self.check_container_health()
            self.monitor_auto_downloader_logs()
            self.check_database_status()
            self.check_data_files()
            self.monitor_pipeline_coordinator()

            if cycle % 3 == 0:  # Every 3rd cycle
                self.get_system_metrics()

            # Check if it's close to 20:00
            current_hour = datetime.now().hour
            current_minute = datetime.now().minute

            if current_hour == 20 and current_minute <= 5:
                logger.info(
                    "🎯 20:00 execution window detected! Monitoring more closely..."
                )
                time.sleep(30)  # Monitor every 30 seconds during execution
            else:
                time.sleep(120)  # Monitor every 2 minutes otherwise

        self.save_metrics_summary()
        logger.info("🏁 Monitoring completed!")


def main():
    """Main monitoring function"""
    try:
        monitor = PipelineMonitor()

        # Check current time
        now = datetime.now()
        logger.info(f"🕐 Current time: {now.strftime('%H:%M:%S')}")

        if now.hour >= 20:
            logger.info("⚠️ 20:00 has passed, checking for recent activity...")

        # Run comprehensive monitoring
        monitor.run_comprehensive_monitoring(duration_minutes=35)

    except KeyboardInterrupt:
        logger.info("⏹️ Monitoring stopped by user")
    except Exception as e:
        logger.error(f"❌ Monitoring failed: {e}")


if __name__ == "__main__":
    main()
