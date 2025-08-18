#!/usr/bin/env python3
"""
🔍 Horse Racing Pipeline & Training Performance Monitor
=======================================================

Real-time monitoring for:
- Pipeline execution stages
- ML training performance
- Power ratings system
- Monte Carlo simulations
- Data processing metrics
- System health

Author: AI Assistant
Date: August 17, 2025
"""

import json
import logging
import os
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

import psycopg2
import redis

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/tmp/pipeline_monitor.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class PipelinePerformanceMonitor:
    """Comprehensive monitoring for pipeline and ML training performance"""

    def __init__(self):
        self.base_path = Path("/home/jc/Documents/Horse-race-ai-v2.02")
        self.monitoring_interval = 30  # seconds

        # Database connection
        self.db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Redis connection for pipeline status
        self.redis_config = {
            "host": "localhost",
            "port": 6380,
            "password": "redis_password_123",
        }

        # Performance metrics
        self.metrics = {
            "pipeline_stages": {},
            "ml_training": {},
            "power_ratings": {},
            "monte_carlo": {},
            "data_quality": {},
            "system_health": {},
        }

    def get_docker_container_status(self) -> Dict[str, str]:
        """Get status of all Docker containers"""
        try:
            result = subprocess.run(
                [
                    "docker-compose",
                    "-f",
                    "docker-compose.clean.yml",
                    "ps",
                    "--format",
                    "json",
                ],
                capture_output=True,
                text=True,
                cwd=self.base_path,
            )

            if result.returncode == 0:
                containers = {}
                for line in result.stdout.strip().split("\n"):
                    if line:
                        try:
                            container = json.loads(line)
                            containers[container.get("Service", "unknown")] = (
                                container.get("State", "unknown")
                            )
                        except json.JSONDecodeError:
                            pass
                return containers
            else:
                logger.error(f"Failed to get container status: {result.stderr}")
                return {}
        except Exception as e:
            logger.error(f"Error getting container status: {e}")
            return {}

    def get_database_metrics(self) -> Dict[str, int]:
        """Get database record counts and health"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cur = conn.cursor()

            # Get table counts
            cur.execute(
                """
                SELECT 
                    'races' as table_name, COUNT(*) as count FROM races
                UNION ALL
                SELECT 'records', COUNT(*) FROM records
                UNION ALL
                SELECT 'horses', COUNT(*) FROM horses
                UNION ALL
                SELECT 'jockeys_stats', COUNT(*) FROM jockeys_stats
                UNION ALL
                SELECT 'trainers_stats', COUNT(*) FROM trainers_stats
            """
            )

            metrics = {}
            for table_name, count in cur.fetchall():
                metrics[f"{table_name}_count"] = count

            # Get database size
            cur.execute("SELECT pg_size_pretty(pg_database_size('horse_racing_db'))")
            metrics["database_size"] = cur.fetchone()[0]

            conn.close()
            return metrics

        except Exception as e:
            logger.error(f"Error getting database metrics: {e}")
            return {}

    def get_ml_training_status(self) -> Dict[str, any]:
        """Get ML training performance metrics"""
        try:
            # Check for ML training logs
            ml_logs = []
            log_patterns = [
                "horse_racing_ml_trainer_clean",
                "ml_training",
                "power_ratings",
                "monte_carlo",
            ]

            for pattern in log_patterns:
                try:
                    result = subprocess.run(
                        [
                            "docker",
                            "logs",
                            "--tail",
                            "20",
                            f"horse_racing_ml_trainer_clean",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        ml_logs.append(
                            {
                                "container": pattern,
                                "logs": result.stdout.strip().split("\n")[
                                    -5:
                                ],  # Last 5 lines
                            }
                        )
                except:
                    pass

            # Parse training metrics from logs
            training_metrics = {
                "active_sessions": 0,
                "accuracy_scores": [],
                "power_ratings_status": "unknown",
                "monte_carlo_status": "unknown",
                "last_training_time": None,
            }

            for log_entry in ml_logs:
                for line in log_entry["logs"]:
                    if "accuracy" in line.lower():
                        try:
                            # Extract accuracy percentage
                            import re

                            accuracy_match = re.search(r"(\d+\.?\d*)%", line)
                            if accuracy_match:
                                training_metrics["accuracy_scores"].append(
                                    float(accuracy_match.group(1))
                                )
                        except:
                            pass

                    if "power rating" in line.lower():
                        training_metrics["power_ratings_status"] = "active"

                    if "monte carlo" in line.lower():
                        training_metrics["monte_carlo_status"] = "active"

            return training_metrics

        except Exception as e:
            logger.error(f"Error getting ML training status: {e}")
            return {}

    def get_pipeline_stage_status(self) -> Dict[str, str]:
        """Get current pipeline stage execution status"""
        try:
            # Check pipeline coordinator logs
            result = subprocess.run(
                ["docker", "logs", "--tail", "50", "horse_racing_data_pipeline_clean"],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                logs = result.stdout.strip().split("\n")

                # Parse pipeline stages
                stages = {
                    "data_download": "waiting",
                    "enhanced_preprocessing": "waiting",
                    "data_preprocessing": "waiting",
                    "csv_import": "waiting",
                    "ml_training": "waiting",
                }

                for line in logs:
                    if "✅" in line:
                        if "download" in line.lower():
                            stages["data_download"] = "completed"
                        elif "enhanced preprocessing" in line.lower():
                            stages["enhanced_preprocessing"] = "completed"
                        elif "preprocessing" in line.lower():
                            stages["data_preprocessing"] = "completed"
                        elif "import" in line.lower():
                            stages["csv_import"] = "completed"
                        elif "ml" in line.lower() or "training" in line.lower():
                            stages["ml_training"] = "completed"

                    elif "🔄" in line or "Starting" in line:
                        if "download" in line.lower():
                            stages["data_download"] = "running"
                        elif "enhanced preprocessing" in line.lower():
                            stages["enhanced_preprocessing"] = "running"
                        elif "preprocessing" in line.lower():
                            stages["data_preprocessing"] = "running"
                        elif "import" in line.lower():
                            stages["csv_import"] = "running"
                        elif "ml" in line.lower() or "training" in line.lower():
                            stages["ml_training"] = "running"

                return stages

        except Exception as e:
            logger.error(f"Error getting pipeline status: {e}")

        return {}

    def get_data_quality_metrics(self) -> Dict[str, any]:
        """Get data quality metrics after preprocessing"""
        try:
            # Check for preprocessed data files
            preprocessed_path = self.base_path / "data" / "preprocessed"

            if not preprocessed_path.exists():
                return {"status": "no_preprocessed_data"}

            csv_files = list(preprocessed_path.rglob("*.csv"))

            metrics = {
                "preprocessed_files": len(csv_files),
                "total_size_mb": 0,
                "files_processed": [],
            }

            for csv_file in csv_files:
                file_size = csv_file.stat().st_size / (1024 * 1024)  # MB
                metrics["total_size_mb"] += file_size
                metrics["files_processed"].append(
                    {
                        "file": csv_file.name,
                        "size_mb": round(file_size, 2),
                        "modified": datetime.fromtimestamp(
                            csv_file.stat().st_mtime
                        ).isoformat(),
                    }
                )

            metrics["total_size_mb"] = round(metrics["total_size_mb"], 2)

            return metrics

        except Exception as e:
            logger.error(f"Error getting data quality metrics: {e}")
            return {}

    def display_monitoring_dashboard(self):
        """Display comprehensive monitoring dashboard"""

        print("\n" + "=" * 80)
        print("🔍 HORSE RACING PIPELINE & TRAINING PERFORMANCE MONITOR")
        print("=" * 80)
        print(f"📅 Monitoring Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()

        # System Health
        print("🖥️  SYSTEM HEALTH:")
        print("-" * 20)
        containers = self.get_docker_container_status()
        for service, status in containers.items():
            status_icon = "✅" if "up" in status.lower() else "❌"
            print(f"   {status_icon} {service}: {status}")
        print()

        # Database Metrics
        print("🗃️  DATABASE METRICS:")
        print("-" * 22)
        db_metrics = self.get_database_metrics()
        for metric, value in db_metrics.items():
            print(f"   📊 {metric}: {value}")
        print()

        # Pipeline Stages
        print("🔄 PIPELINE STAGES:")
        print("-" * 20)
        stages = self.get_pipeline_stage_status()
        for stage, status in stages.items():
            if status == "completed":
                icon = "✅"
            elif status == "running":
                icon = "🔄"
            elif status == "waiting":
                icon = "⏳"
            else:
                icon = "❓"
            print(f"   {icon} {stage.replace('_', ' ').title()}: {status}")
        print()

        # ML Training Performance
        print("🤖 ML TRAINING PERFORMANCE:")
        print("-" * 28)
        ml_metrics = self.get_ml_training_status()

        if ml_metrics.get("accuracy_scores"):
            avg_accuracy = sum(ml_metrics["accuracy_scores"]) / len(
                ml_metrics["accuracy_scores"]
            )
            print(f"   🎯 Average Accuracy: {avg_accuracy:.2f}%")
            print(f"   📈 Recent Scores: {ml_metrics['accuracy_scores']}")
        else:
            print("   ⏳ No training data available yet")

        print(
            f"   ⚡ Power Ratings: {ml_metrics.get('power_ratings_status', 'unknown')}"
        )
        print(f"   🎲 Monte Carlo: {ml_metrics.get('monte_carlo_status', 'unknown')}")
        print()

        # Data Quality
        print("📊 DATA QUALITY METRICS:")
        print("-" * 26)
        quality_metrics = self.get_data_quality_metrics()

        if quality_metrics.get("preprocessed_files", 0) > 0:
            print(f"   📄 Preprocessed Files: {quality_metrics['preprocessed_files']}")
            print(f"   💾 Total Size: {quality_metrics['total_size_mb']} MB")
            print(
                f"   🕒 Latest Processing: {quality_metrics.get('files_processed', [{}])[-1].get('modified', 'Unknown') if quality_metrics.get('files_processed') else 'None'}"
            )
        else:
            print("   ⏳ No preprocessed data available")
        print()

        # Next Schedule
        print("⏰ SCHEDULE STATUS:")
        print("-" * 18)
        now = datetime.now()
        next_run = now.replace(hour=19, minute=20, second=0, microsecond=0)
        if next_run <= now:
            next_run += timedelta(days=1)

        time_until = next_run - now
        hours, remainder = divmod(time_until.total_seconds(), 3600)
        minutes, _ = divmod(remainder, 60)

        print(f"   📅 Next Run: {next_run.strftime('%Y-%m-%d %H:%M')}")
        print(f"   ⏱️  Time Until: {int(hours)}h {int(minutes)}m")
        print()

    def run_continuous_monitoring(self):
        """Run continuous monitoring loop"""
        print("🚀 Starting continuous pipeline monitoring...")
        print(f"📊 Monitoring interval: {self.monitoring_interval} seconds")
        print("Press Ctrl+C to stop monitoring")
        print()

        try:
            while True:
                self.display_monitoring_dashboard()
                time.sleep(self.monitoring_interval)

        except KeyboardInterrupt:
            print("\n⏹️  Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Horse Racing Pipeline Performance Monitor"
    )
    parser.add_argument(
        "--mode",
        choices=["once", "continuous"],
        default="continuous",
        help="Run mode: 'once' for single check, 'continuous' for live monitoring",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=30,
        help="Monitoring interval in seconds (for continuous mode)",
    )

    args = parser.parse_args()

    monitor = PipelinePerformanceMonitor()
    monitor.monitoring_interval = args.interval

    if args.mode == "once":
        monitor.display_monitoring_dashboard()
    else:
        monitor.run_continuous_monitoring()


if __name__ == "__main__":
    main()
