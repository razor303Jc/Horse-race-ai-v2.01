#!/usr/bin/env python3
"""
Production Pipeline Integration Script
====================================

Integrates the data upload system into the production pipeline.
This script handles scheduling, monitoring, and error handling.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("production_pipeline.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class ProductionPipeline:
    """
    Production-ready data upload pipeline
    """

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")
        self.config_file = self.project_root / "config" / "pipeline_config.json"
        self.status_file = self.project_root / "logs" / "pipeline_status.json"

        # Create directories if they don't exist
        self.config_file.parent.mkdir(exist_ok=True)
        self.status_file.parent.mkdir(exist_ok=True)

        # Load configuration
        self.config = self.load_config()

        # Import uploader
        try:
            from daily_data_uploader import DailyDataUploader

            self.uploader = DailyDataUploader()
            logger.info("✅ Production pipeline initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to initialize pipeline: {e}")
            raise

    def load_config(self):
        """Load pipeline configuration"""
        default_config = {
            "upload_schedule": {"enabled": True, "frequency": "daily", "time": "09:00"},
            "monitoring": {"enabled": True, "alert_on_failure": True, "max_retries": 3},
            "data_retention": {"keep_logs_days": 30, "keep_status_days": 7},
            "notifications": {"enabled": False, "webhook_url": "", "email": ""},
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                logger.info("✅ Configuration loaded from file")
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config, using defaults: {e}")

        # Save default configuration
        with open(self.config_file, "w") as f:
            json.dump(default_config, f, indent=2)
        logger.info("✅ Default configuration created")

        return default_config

    def save_status(self, status):
        """Save pipeline status"""
        try:
            with open(self.status_file, "w") as f:
                json.dump(status, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Failed to save status: {e}")

    def load_status(self):
        """Load pipeline status"""
        if self.status_file.exists():
            try:
                with open(self.status_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️ Failed to load status: {e}")
        return {}

    def check_system_health(self):
        """Check system health before upload"""
        health_checks = {
            "database_connection": False,
            "downloads_directory": False,
            "csv_files_available": False,
            "disk_space": False,
        }

        try:
            # Check database connection
            conn = self.uploader.get_connection()
            if conn:
                conn.close()
                health_checks["database_connection"] = True

            # Check downloads directory
            if self.uploader.daily_data_dir.exists():
                health_checks["downloads_directory"] = True

            # Check for CSV files
            available_files, _ = self.uploader.check_daily_files()
            if len(available_files) > 0:
                health_checks["csv_files_available"] = True

            # Check disk space (require at least 1GB free)
            statvfs = os.statvfs(self.project_root)
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            free_gb = free_bytes / (1024**3)
            if free_gb >= 1.0:
                health_checks["disk_space"] = True

        except Exception as e:
            logger.error(f"❌ Health check error: {e}")

        return health_checks

    def execute_upload_with_retry(self, max_retries=3):
        """Execute upload with retry logic"""
        last_error = None

        for attempt in range(1, max_retries + 1):
            try:
                logger.info(f"Upload attempt {attempt}/{max_retries}")

                success, summary = self.uploader.upload_daily_data(mode="append")

                if success:
                    logger.info(f"✅ Upload successful on attempt {attempt}")
                    return {
                        "success": True,
                        "attempt": attempt,
                        "summary": summary,
                        "timestamp": datetime.now(),
                    }
                else:
                    logger.warning(f"⚠️ Upload failed on attempt {attempt}")
                    last_error = "Upload returned failure status"

            except Exception as e:
                logger.error(f"❌ Upload attempt {attempt} failed: {e}")
                last_error = str(e)

            if attempt < max_retries:
                wait_time = 60 * attempt  # Exponential backoff
                logger.info(f"Waiting {wait_time} seconds before retry...")
                import time

                time.sleep(wait_time)

        return {
            "success": False,
            "attempts": max_retries,
            "error": last_error,
            "timestamp": datetime.now(),
        }

    def run_scheduled_upload(self):
        """Run scheduled upload with full monitoring"""
        logger.info("🚀 Starting scheduled data upload")

        start_time = datetime.now()

        # Check system health
        health_checks = self.check_system_health()
        failed_checks = [check for check, passed in health_checks.items() if not passed]

        if failed_checks:
            error_msg = f"Health checks failed: {failed_checks}"
            logger.error(f"❌ {error_msg}")

            status = {
                "timestamp": start_time,
                "status": "failed",
                "error": error_msg,
                "health_checks": health_checks,
                "duration": 0,
            }
            self.save_status(status)
            return status

        logger.info("✅ All health checks passed")

        # Execute upload with retry
        max_retries = self.config.get("monitoring", {}).get("max_retries", 3)
        result = self.execute_upload_with_retry(max_retries)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        # Create status report
        status = {
            "timestamp": start_time,
            "duration": duration,
            "health_checks": health_checks,
            "upload_result": result,
        }

        if result["success"]:
            status["status"] = "success"
            logger.info(
                f"✅ Scheduled upload completed successfully in {duration:.2f}s"
            )
        else:
            status["status"] = "failed"
            status["error"] = result.get("error", "Unknown error")
            logger.error(f"❌ Scheduled upload failed after {duration:.2f}s")

        self.save_status(status)

        # Send notifications if configured
        if self.config.get("notifications", {}).get("enabled", False):
            self.send_notification(status)

        return status

    def send_notification(self, status):
        """Send notification about upload status"""
        try:
            if status["status"] == "success":
                message = f"✅ Data upload successful at {status['timestamp']}"
            else:
                message = (
                    f"❌ Data upload failed: {status.get('error', 'Unknown error')}"
                )

            # Here you would integrate with your notification system
            # For example: webhook, email, Slack, etc.
            logger.info(f"📧 Notification: {message}")

        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")

    def cleanup_old_files(self):
        """Clean up old log files and status reports"""
        try:
            retention_days = self.config.get("data_retention", {}).get(
                "keep_logs_days", 30
            )
            cutoff_date = datetime.now() - timedelta(days=retention_days)

            # Clean up log files
            logs_dir = self.project_root / "logs"
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log*"):
                    if log_file.stat().st_mtime < cutoff_date.timestamp():
                        log_file.unlink()
                        logger.info(f"🗑️ Cleaned up old log: {log_file.name}")

            logger.info("✅ Cleanup completed")

        except Exception as e:
            logger.error(f"❌ Cleanup failed: {e}")

    def generate_status_report(self):
        """Generate detailed status report"""
        logger.info("📊 Generating status report...")

        # Get current status
        current_status = self.load_status()
        health_checks = self.check_system_health()

        # Get database summary
        try:
            available_files, missing_files = self.uploader.check_daily_files()
        except Exception as e:
            logger.error(f"Error checking files: {e}")
            available_files, missing_files = {}, []

        report = {
            "generated_at": datetime.now(),
            "system_health": health_checks,
            "last_upload": current_status,
            "available_files": {
                k: v.get("size", 0) for k, v in available_files.items()
            },
            "missing_files": missing_files,
            "configuration": self.config,
        }

        # Save report
        report_file = (
            self.project_root
            / "reports"
            / f"pipeline_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(exist_ok=True)

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)

        logger.info(f"✅ Status report saved: {report_file}")
        return report

    def validate_production_readiness(self):
        """Validate that the system is ready for production"""
        logger.info("🔍 Validating production readiness...")

        checks = {
            "health_checks": self.check_system_health(),
            "configuration": self.config is not None,
            "test_upload": False,
            "database_schema": False,
        }

        # Test upload (dry run)
        try:
            available_files, _ = self.uploader.check_daily_files()
            if available_files:
                # Just validate connection and files, don't actually upload
                conn = self.uploader.get_connection()
                if conn:
                    conn.close()
                    checks["test_upload"] = True
        except Exception as e:
            logger.error(f"Test upload failed: {e}")

        # Check database schema
        try:
            conn = self.uploader.get_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
                )
                tables = [row[0] for row in cursor.fetchall()]
                expected_tables = [
                    "race_results",
                    "horses",
                    "races_cards",
                    "jockey_stats",
                    "trainer_stats",
                    "racecard_details",
                ]
                if all(table in tables for table in expected_tables):
                    checks["database_schema"] = True
                conn.close()
        except Exception as e:
            logger.error(f"Database schema check failed: {e}")

        # Calculate readiness score
        health_score = (
            sum(checks["health_checks"].values()) / len(checks["health_checks"]) * 100
        )
        other_checks = [
            checks["configuration"],
            checks["test_upload"],
            checks["database_schema"],
        ]
        other_score = sum(other_checks) / len(other_checks) * 100

        overall_score = (health_score + other_score) / 2

        logger.info(f"Production readiness: {overall_score:.1f}%")

        if overall_score >= 90:
            logger.info("🎉 System is PRODUCTION READY!")
        elif overall_score >= 75:
            logger.info("✅ System is mostly ready with minor issues")
        else:
            logger.warning("⚠️ System needs attention before production deployment")

        return {
            "overall_score": overall_score,
            "health_checks": checks["health_checks"],
            "other_checks": {
                "configuration": checks["configuration"],
                "test_upload": checks["test_upload"],
                "database_schema": checks["database_schema"],
            },
        }


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Production Data Upload Pipeline")
    parser.add_argument(
        "action",
        choices=["upload", "status", "health", "validate", "cleanup", "report"],
        help="Action to perform",
    )

    args = parser.parse_args()

    try:
        pipeline = ProductionPipeline()

        if args.action == "upload":
            result = pipeline.run_scheduled_upload()
            if result["status"] == "success":
                print("✅ Upload completed successfully")
                sys.exit(0)
            else:
                print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        elif args.action == "status":
            report = pipeline.generate_status_report()
            print(f"Status report generated: {datetime.now()}")
            print(f"Health: {report['system_health']}")
            print(
                f"Last upload: {report.get('last_upload', {}).get('status', 'Unknown')}"
            )

        elif args.action == "health":
            health = pipeline.check_system_health()
            print("System Health Checks:")
            for check, passed in health.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {check}: {status}")

        elif args.action == "validate":
            readiness = pipeline.validate_production_readiness()
            print(f"Production Readiness: {readiness['overall_score']:.1f}%")

        elif args.action == "cleanup":
            pipeline.cleanup_old_files()
            print("✅ Cleanup completed")

        elif args.action == "report":
            report = pipeline.generate_status_report()
            print(f"✅ Report generated at {report['generated_at']}")

    except Exception as e:
        logger.error(f"❌ Pipeline error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
