#!/usr/bin/env python3
"""
🚀 Proper Pipeline Orchestrator
==============================

Real pipeline coordinator that:
1. Monitors for downloaded data files
2. Triggers CSV import automatically
3. Orchestrates pipeline stages in sequence
4. Handles dependencies and error recovery
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


def setup_logging():
    """Setup logging with fallback if file writing fails"""
    # Configure basic logging first
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    logger = logging.getLogger(__name__)

    try:
        # Ensure logs directory exists and is writable
        logs_dir = Path("/app/logs")
        if not logs_dir.exists():
            logs_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Created logs directory: {logs_dir}")

        # Try to create a test file to check permissions
        test_file = logs_dir / "test_permissions.tmp"
        test_file.write_text("test")
        test_file.unlink()  # Remove test file

        # Create actual log file
        log_file = logs_dir / "pipeline_orchestrator.log"
        file_handler = logging.FileHandler(str(log_file))
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(file_handler)
        print(f"✅ Logging to file: {log_file}")

    except (PermissionError, OSError) as e:
        print(f"⚠️  Cannot write to log file: {e}")
        print("📝 Using console logging only - this is safe for Docker containers")
        # For Docker containers, console logging is often preferred anyway
        # as logs can be accessed via `docker logs <container>`

    return logger


logger = setup_logging()


class PipelineOrchestrator:
    """Production pipeline orchestrator with file monitoring and stage management"""

    def __init__(self):
        self.data_dir = Path("/app/data/daily_downloads")
        self.logs_dir = Path("/app/logs")
        self.stage_status = {}
        self.last_file_check = {}

        # Database connection for pipeline stages
        self.db_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }  # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        logger.info("🚀 Pipeline Orchestrator initialized")

    def start_orchestration(self):
        """Start the main orchestration loop"""
        logger.info("🎯 Starting pipeline orchestration...")

        while True:
            try:
                # Check for new downloads
                if self.check_for_new_downloads():
                    logger.info("📁 New download detected! Starting pipeline...")
                    self.run_pipeline_sequence()

                # Check stage status periodically
                self.monitor_pipeline_health()

                # Wait before next check
                time.sleep(30)

            except KeyboardInterrupt:
                logger.info("🛑 Pipeline orchestrator stopped")
                break
            except Exception as e:
                logger.error(f"❌ Orchestrator error: {e}")
                time.sleep(60)  # Wait longer on errors

    def check_for_new_downloads(self) -> bool:
        """Check if new data files have been downloaded"""
        try:
            results_dir = self.data_dir / "results_data"
            cards_dir = self.data_dir / "cards_data"

            # Check if both directories exist with CSV files
            if not (results_dir.exists() and cards_dir.exists()):
                return False

            # Look for races.csv files as indicators
            results_races = results_dir / "races" / "races.csv"
            cards_races = cards_dir / "races" / "races.csv"

            if not (results_races.exists() and cards_races.exists()):
                return False

            # Check if files are newer than last check
            current_files = {
                "results_races": results_races.stat().st_mtime,
                "cards_races": cards_races.stat().st_mtime,
            }

            # Compare with last check
            if hasattr(self, "last_download_check"):
                if current_files == self.last_download_check:
                    return False  # No changes

            self.last_download_check = current_files

            # Validate file sizes (basic check)
            if results_races.stat().st_size < 1000 or cards_races.stat().st_size < 1000:
                logger.warning("⚠️ Downloaded files seem too small")
                return False

            logger.info(f"✅ Valid download detected:")
            logger.info(f"   📊 Results: {results_races.stat().st_size} bytes")
            logger.info(f"   📊 Cards: {cards_races.stat().st_size} bytes")

            return True

        except Exception as e:
            logger.error(f"❌ Error checking downloads: {e}")
            return False

    def check_manual_downloads(self):
        """Check for manual download ZIP files"""
        logger.info("🔍 Checking for manual downloads...")

        try:
            manual_dir = Path("/app/data/daily_downloads/manual_download")
            if not manual_dir.exists():
                logger.info("📂 No manual download directory found")
                return False

            # Check for ZIP files
            zip_files = list(manual_dir.glob("*.zip"))
            if not zip_files:
                logger.info("📁 No ZIP files found in manual download directory")
                return False

            logger.info(f"✅ Found {len(zip_files)} ZIP files for processing")
            for zip_file in zip_files:
                logger.info(f"   📦 {zip_file.name}")

            return True

        except Exception as e:
            logger.error(f"❌ Error checking manual downloads: {e}")
            return False

    def process_manual_downloads(self):
        """Process manual downloads using file watcher"""
        logger.info("⚙️ Processing manual downloads...")

        try:
            # Import and run file watcher
            import sys

            sys.path.append("/app/tools/automation")

            from file_watcher_enhanced import FileWatcherEnhanced

            watcher = FileWatcherEnhanced()
            result = watcher.process_existing_files()

            if result.get("success", False):
                logger.info("✅ Manual downloads processed successfully")
                processed_files = result.get("processed_files", [])
                for file_info in processed_files:
                    logger.info(f"   📦 Processed: {file_info}")
                return True
            else:
                logger.error(
                    f"❌ Manual download processing failed: {result.get('error', 'Unknown error')}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Error processing manual downloads: {e}")
            import traceback

            traceback.print_exc()
            return False

    def run_pipeline_sequence(self):
        """Run the complete pipeline sequence"""
        logger.info("🚀 Starting pipeline sequence...")

        # Stage 1: Check for Manual Download Data
        if self.check_manual_downloads():
            self.mark_stage_complete("data_download", "Manual download data available")

            # Stage 2: Process Manual Downloads
            if self.process_manual_downloads():
                self.mark_stage_complete(
                    "manual_processing", "Manual downloads processed"
                )

                # Stage 3: CSV Import
                if self.run_csv_import():
                    self.mark_stage_complete("csv_import", "Database import successful")

                    # Stage 4: Data Preprocessing
                    if self.run_data_preprocessing():
                        self.mark_stage_complete(
                            "data_preprocessing", "Data relationships processed"
                        )

                        # Stage 5: Trigger ML Pipeline
                        self.trigger_ml_pipeline()
                    else:
                        logger.error("❌ Data preprocessing failed")
                else:
                    logger.error("❌ CSV import failed")
            else:
                logger.error("❌ Manual download processing failed")
        else:
            logger.error("❌ CSV import failed")

    def run_csv_import(self) -> bool:
        """Run CSV import using existing tools"""
        logger.info("📊 Stage 2: Starting CSV Import...")

        try:
            # Use the working race card upload solution
            result = subprocess.run(
                ["python", "/app/tools/data_processing/upload_mapped_data.py"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Race card database upload completed successfully")
                logger.info(f"Upload output: {result.stdout[-200:]}")  # Last 200 chars
                return True
            else:
                logger.error(f"❌ Race card upload failed: {result.stderr}")

                # Try fallback uploader if needed
                logger.info("🔄 Trying fallback CSV uploader...")
                result = subprocess.run(
                    ["python", "/app/tools/data_processing/upload_mapped_data.py"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    logger.info("✅ Fallback CSV import successful")
                    return True
                else:
                    logger.error(f"❌ Both CSV importers failed")
                    return False

        except subprocess.TimeoutExpired:
            logger.error("❌ CSV import timed out")
            return False
        except Exception as e:
            logger.error(f"❌ CSV import exception: {e}")
            return False

    def run_data_preprocessing(self) -> bool:
        """Run data preprocessing and relationship building"""
        logger.info("🔄 Stage 3: Starting Data Preprocessing...")

        try:
            # Run automated relationships pipeline
            result = subprocess.run(
                [
                    "python",
                    "/app/tools/data_processing/automated_relationships_pipeline.py",
                ],
                capture_output=True,
                text=True,
                timeout=600,
            )

            if result.returncode == 0:
                logger.info("✅ Data preprocessing completed")
                return True
            else:
                logger.error(f"❌ Data preprocessing failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Data preprocessing timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Data preprocessing exception: {e}")
            return False

    def trigger_ml_pipeline(self):
        """Trigger ML training and analysis pipeline"""
        logger.info("🤖 Stage 4: Triggering ML Pipeline...")

        try:
            # Run ML training orchestrator in background
            subprocess.Popen(
                ["python", "/app/tools/ml_training/ml_training_orchestrator.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

            logger.info("✅ ML pipeline triggered (running in background)")
            self.mark_stage_complete("ml_pipeline", "ML training started")

        except Exception as e:
            logger.error(f"❌ ML pipeline trigger failed: {e}")

    def mark_stage_complete(self, stage_name: str, message: str):
        """Mark a pipeline stage as complete"""
        timestamp = datetime.now().isoformat()
        self.stage_status[stage_name] = {
            "completed_at": timestamp,
            "message": message,
            "status": "completed",
        }

        logger.info(f"✅ Stage completed: {stage_name} - {message}")

        # Save status to file
        status_file = self.logs_dir / "pipeline_status.json"
        with open(status_file, "w") as f:
            json.dump(self.stage_status, f, indent=2)

    def monitor_pipeline_health(self):
        """Monitor overall pipeline health"""
        try:
            # Check database connectivity
            import psycopg2

            conn = psycopg2.connect(**self.db_config)
            conn.close()

            # Log status every 10 minutes
            if not hasattr(self, "_last_health_log"):
                self._last_health_log = 0

            current_time = time.time()
            if current_time - self._last_health_log > 600:  # 10 minutes
                completed_stages = len(
                    [
                        s
                        for s in self.stage_status.values()
                        if s["status"] == "completed"
                    ]
                )
                logger.info(
                    f"💚 Pipeline Health: {completed_stages} stages completed, Database connected"
                )
                self._last_health_log = current_time

        except Exception as e:
            logger.warning(f"⚠️ Health check issue: {e}")

    def get_status_summary(self) -> dict:
        """Get current pipeline status summary"""
        return {
            "orchestrator_uptime": datetime.now().isoformat(),
            "completed_stages": len(
                [s for s in self.stage_status.values() if s["status"] == "completed"]
            ),
            "stage_details": self.stage_status,
            "data_directory_exists": self.data_dir.exists(),
            "last_download_check": getattr(self, "last_download_check", None),
        }


def main():
    """Main orchestrator function"""
    logger.info("🚀 Starting Proper Pipeline Orchestrator")

    # Create and start orchestrator
    orchestrator = PipelineOrchestrator()

    try:
        orchestrator.start_orchestration()
    except Exception as e:
        logger.error(f"❌ Fatal orchestrator error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
