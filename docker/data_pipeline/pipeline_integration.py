#!/usr/bin/env python3
"""
Data Upload Pipeline Integration
===============================

Integrates the data upload functionality into the main system pipeline.
This script provides the interface between the auto downloader and the data upload system.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("pipeline_integration.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class PipelineIntegration:
    """
    Integrates data upload into the main system pipeline
    """

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")

        # Import after path setup
        try:
            from csv_column_mapper import ColumnMapper
            from daily_data_uploader import DailyDataUploader

            self.uploader = DailyDataUploader()
            self.mapper = ColumnMapper()
            logger.info("✅ Pipeline integration initialized successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import required modules: {e}")
            raise

    def check_system_readiness(self):
        """Check if the system is ready for data upload"""
        logger.info("Checking system readiness...")

        checks = {
            "database_connection": False,
            "downloads_directory": False,
            "column_mappings": False,
            "csv_files_available": False,
        }

        # Check database connection
        try:
            conn = self.uploader.get_database_connection()
            if conn:
                conn.close()
                checks["database_connection"] = True
                logger.info("✅ Database connection: OK")
            else:
                logger.error("❌ Database connection: FAILED")
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")

        # Check downloads directory
        if self.uploader.downloads_dir.exists():
            checks["downloads_directory"] = True
            logger.info("✅ Downloads directory: OK")
        else:
            logger.error(
                f"❌ Downloads directory not found: {self.uploader.downloads_dir}"
            )

        # Check column mappings
        if hasattr(self.mapper, "column_mappings") and self.mapper.column_mappings:
            checks["column_mappings"] = True
            logger.info("✅ Column mappings: OK")
        else:
            logger.error("❌ Column mappings: FAILED")

        # Check for available CSV files
        total_files = 0
        for table in self.mapper.column_mappings.keys():
            files = self.uploader.find_csv_files(table)
            total_files += len(files)

        if total_files > 0:
            checks["csv_files_available"] = True
            logger.info(f"✅ CSV files available: {total_files} files found")
        else:
            logger.warning("⚠️ No CSV files found for upload")

        # Summary
        passed_checks = sum(checks.values())
        total_checks = len(checks)
        readiness_score = (passed_checks / total_checks) * 100

        logger.info(
            f"System readiness: {passed_checks}/{total_checks} ({readiness_score:.1f}%)"
        )

        return checks, readiness_score

    def execute_daily_upload(self):
        """Execute the daily data upload process"""
        logger.info("🚀 Starting daily data upload process...")

        start_time = datetime.now()

        try:
            # Upload all available data
            results = self.uploader.upload_all_data()

            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()

            if results.get("success", False):
                summary = results.get("summary", {})
                logger.info("✅ Daily upload completed successfully!")
                logger.info(f"Files processed: {summary.get('files_processed', 0)}")
                logger.info(f"Total rows uploaded: {summary.get('total_rows', 0)}")
                logger.info(f"Duration: {duration:.2f} seconds")

                return {
                    "success": True,
                    "duration": duration,
                    "summary": summary,
                    "timestamp": end_time,
                }
            else:
                logger.error(
                    f"❌ Daily upload failed: {results.get('error', 'Unknown error')}"
                )
                return {
                    "success": False,
                    "error": results.get("error", "Unknown error"),
                    "duration": duration,
                    "timestamp": end_time,
                }

        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            logger.error(f"❌ Daily upload exception: {e}")
            return {
                "success": False,
                "error": str(e),
                "duration": duration,
                "timestamp": end_time,
            }

    def upload_specific_table(self, table_name):
        """Upload data for a specific table"""
        logger.info(f"Uploading data for table: {table_name}")

        if table_name not in self.mapper.column_mappings:
            error_msg = f"Unknown table: {table_name}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

        try:
            result = self.uploader.upload_csv_file(table_name)

            if result.get("success", False):
                logger.info(
                    f"✅ Upload successful for {table_name}: {result.get('rows_processed', 0)} rows"
                )
            else:
                logger.error(
                    f"❌ Upload failed for {table_name}: {result.get('error', 'Unknown error')}"
                )

            return result

        except Exception as e:
            error_msg = f"Upload exception for {table_name}: {e}"
            logger.error(f"❌ {error_msg}")
            return {"success": False, "error": error_msg}

    def get_upload_status(self):
        """Get current upload status and statistics"""
        logger.info("Getting upload status...")

        status = {
            "available_tables": list(self.mapper.column_mappings.keys()),
            "files_found": {},
            "last_upload": None,
            "database_status": "unknown",
        }

        # Check for available files
        for table in self.mapper.column_mappings.keys():
            files = self.uploader.find_csv_files(table)
            status["files_found"][table] = len(files)

        # Check database status
        try:
            conn = self.uploader.get_database_connection()
            if conn:
                conn.close()
                status["database_status"] = "connected"
            else:
                status["database_status"] = "connection_failed"
        except Exception:
            status["database_status"] = "error"

        # Check for upload log
        log_file = Path("daily_upload.log")
        if log_file.exists():
            try:
                stat = log_file.stat()
                status["last_upload"] = datetime.fromtimestamp(stat.st_mtime)
            except Exception:
                pass

        return status

    def create_upload_schedule(self):
        """Create a scheduled task for daily uploads"""
        logger.info("Creating upload schedule...")

        # Create a cron-style scheduler script
        scheduler_script = self.project_root / "scripts" / "daily_upload_scheduler.py"
        scheduler_script.parent.mkdir(exist_ok=True)

        script_content = '''#!/usr/bin/env python3
"""
Daily Upload Scheduler
=====================

Automated daily data upload scheduler for the horse racing system.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

from pipeline_integration import PipelineIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("scheduled_upload.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def main():
    """Main scheduler function"""
    logger.info(f"🕐 Scheduled upload started at {datetime.now()}")
    
    try:
        pipeline = PipelineIntegration()
        
        # Check system readiness
        checks, readiness_score = pipeline.check_system_readiness()
        
        if readiness_score < 75:  # Require 75% readiness
            logger.warning(f"⚠️ System not ready for upload (readiness: {readiness_score:.1f}%)")
            sys.exit(1)
        
        # Execute daily upload
        result = pipeline.execute_daily_upload()
        
        if result["success"]:
            logger.info("✅ Scheduled upload completed successfully")
            sys.exit(0)
        else:
            logger.error(f"❌ Scheduled upload failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Scheduler exception: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
'''

        with open(scheduler_script, "w") as f:
            f.write(script_content)

        # Make it executable
        scheduler_script.chmod(0o755)

        logger.info(f"✅ Scheduler script created: {scheduler_script}")

        # Create systemd service file (optional)
        service_content = f"""[Unit]
Description=Horse Racing Data Upload Service
After=network.target postgresql.service

[Service]
Type=oneshot
User={os.getenv("USER", "jc")}
WorkingDirectory={self.project_root}
ExecStart=/usr/bin/python3 {scheduler_script}
Environment=PYTHONPATH={self.project_root}

[Install]
WantedBy=multi-user.target
"""

        service_file = self.project_root / "config" / "horse-racing-upload.service"
        service_file.parent.mkdir(exist_ok=True)

        with open(service_file, "w") as f:
            f.write(service_content)

        logger.info(f"✅ Systemd service file created: {service_file}")

        # Create timer file
        timer_content = """[Unit]
Description=Run Horse Racing Data Upload Daily
Requires=horse-racing-upload.service

[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
"""

        timer_file = self.project_root / "config" / "horse-racing-upload.timer"

        with open(timer_file, "w") as f:
            f.write(timer_content)

        logger.info(f"✅ Systemd timer file created: {timer_file}")

        return {
            "scheduler_script": scheduler_script,
            "service_file": service_file,
            "timer_file": timer_file,
        }

    def integrate_with_docker(self):
        """Integrate upload functionality with Docker containers"""
        logger.info("Integrating with Docker containers...")

        # Update docker-compose.yml to include upload service
        docker_compose_file = self.project_root / "docker-compose.yml"

        if docker_compose_file.exists():
            logger.info("✅ Docker compose file found - integration possible")

            # Create upload service configuration
            upload_service_config = """
  upload-service:
    build: .
    container_name: racing-upload-service
    depends_on:
      - db
    environment:
      - DATABASE_URL=postgresql://racing_user:racing_password@db:5432/racing_data
      - PYTHONPATH=/app
    volumes:
      - ./downloads:/app/downloads
      - ./logs:/app/logs
    command: python3 scripts/daily_upload_scheduler.py
    networks:
      - racing-network
"""

            logger.info("✅ Upload service configuration ready for Docker integration")
            return {"docker_config": upload_service_config}
        else:
            logger.warning("⚠️ Docker compose file not found")
            return {"docker_config": None}

    def generate_integration_report(self):
        """Generate integration status report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = (
            self.project_root / "reports" / f"pipeline_integration_{timestamp}.md"
        )
        report_file.parent.mkdir(exist_ok=True)

        # Get current status
        checks, readiness_score = self.check_system_readiness()
        status = self.get_upload_status()

        with open(report_file, "w") as f:
            f.write(f"# Data Upload Pipeline Integration Report\n\n")
            f.write(f"**Generated:** {datetime.now()}\n")
            f.write(f"**System Readiness:** {readiness_score:.1f}%\n\n")

            f.write("## System Checks\n\n")
            for check_name, passed in checks.items():
                status_icon = "✅" if passed else "❌"
                f.write(
                    f"- **{check_name.replace('_', ' ').title()}:** {status_icon}\n"
                )

            f.write("\n## Available Data\n\n")
            total_files = sum(status["files_found"].values())
            f.write(f"**Total CSV files found:** {total_files}\n\n")

            for table, count in status["files_found"].items():
                f.write(f"- {table}: {count} files\n")

            f.write(f"\n## Database Status\n\n")
            f.write(f"**Connection Status:** {status['database_status']}\n")

            if status.get("last_upload"):
                f.write(f"**Last Upload:** {status['last_upload']}\n")

            f.write("\n## Integration Status\n\n")
            if readiness_score >= 90:
                f.write(
                    "🎉 **EXCELLENT:** System is fully integrated and ready for production.\n"
                )
            elif readiness_score >= 75:
                f.write("✅ **GOOD:** System is operational with minor issues.\n")
            elif readiness_score >= 50:
                f.write("⚠️ **NEEDS ATTENTION:** Some components require fixes.\n")
            else:
                f.write("🔥 **CRITICAL:** Major integration issues detected.\n")

            f.write("\n## Next Steps\n\n")
            if readiness_score >= 75:
                f.write("- Set up automated scheduling\n")
                f.write("- Configure monitoring alerts\n")
                f.write("- Deploy to production environment\n")
            else:
                f.write("- Fix failing system checks\n")
                f.write("- Verify database configuration\n")
                f.write("- Test upload functionality\n")

        logger.info(f"Integration report saved: {report_file}")
        return report_file


def main():
    """Main function for command line usage"""
    import argparse

    parser = argparse.ArgumentParser(description="Data Upload Pipeline Integration")
    parser.add_argument(
        "action",
        choices=["check", "upload", "status", "schedule", "docker", "report"],
        help="Action to perform",
    )
    parser.add_argument("--table", help="Specific table to upload (for upload action)")

    args = parser.parse_args()

    try:
        pipeline = PipelineIntegration()

        if args.action == "check":
            checks, score = pipeline.check_system_readiness()
            print(f"System readiness: {score:.1f}%")

        elif args.action == "upload":
            if args.table:
                result = pipeline.upload_specific_table(args.table)
            else:
                result = pipeline.execute_daily_upload()

            if result["success"]:
                print("✅ Upload completed successfully")
            else:
                print(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
                sys.exit(1)

        elif args.action == "status":
            status = pipeline.get_upload_status()
            print(f"Database: {status['database_status']}")
            print(f"Available files: {sum(status['files_found'].values())}")

        elif args.action == "schedule":
            result = pipeline.create_upload_schedule()
            print(f"✅ Scheduler created: {result['scheduler_script']}")

        elif args.action == "docker":
            result = pipeline.integrate_with_docker()
            if result["docker_config"]:
                print("✅ Docker integration configuration ready")
            else:
                print("⚠️ Docker compose file not found")

        elif args.action == "report":
            report = pipeline.generate_integration_report()
            print(f"✅ Integration report saved: {report}")

    except Exception as e:
        logger.error(f"❌ Pipeline integration error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
