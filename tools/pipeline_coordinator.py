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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/pipeline_orchestrator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


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

    def run_pipeline_sequence(self):
        """Run the complete pipeline sequence"""
        logger.info("🚀 Starting pipeline sequence...")

        # Stage 1: Data Validation (already done in auto-downloader)
        self.mark_stage_complete("data_download", "Auto-downloader completed")

        # Stage 2: CSV Import
        if self.run_csv_import():
            self.mark_stage_complete("csv_import", "Database import successful")

            # Stage 2.5: Enhanced Data Preprocessing (NEW)
            if self.run_enhanced_preprocessing():
                self.mark_stage_complete(
                    "enhanced_preprocessing", "Data cleaning and formatting completed"
                )

                # Stage 3: Data Preprocessing
                if self.run_data_preprocessing():
                    self.mark_stage_complete(
                        "data_preprocessing", "Data relationships processed"
                    )

                    # Stage 4: Trigger ML Pipeline
                    self.trigger_ml_pipeline()
                else:
                    logger.error("❌ Data preprocessing failed")
            else:
                logger.error("❌ Enhanced preprocessing failed")
        else:
            logger.error("❌ CSV import failed")

    def run_csv_import(self) -> bool:
        """Run CSV import using existing tools"""
        logger.info("📊 Stage 2: Starting CSV Import...")

        try:
            # Use the complete upload solution
            result = subprocess.run(
                ["python", "/app/tools/data_processing/corrected_uploader.py"],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ CSV import completed successfully")
                logger.info(f"Import output: {result.stdout[-200:]}")  # Last 200 chars
                return True
            else:
                logger.error(f"❌ CSV import failed: {result.stderr}")

                # Try alternative uploader
                logger.info("🔄 Trying alternative CSV uploader...")
                result = subprocess.run(
                    ["python", "/app/tools/data_processing/database_uploader.py"],
                    capture_output=True,
                    text=True,
                    timeout=300,
                )

                if result.returncode == 0:
                    logger.info("✅ Alternative CSV import successful")
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

    def run_enhanced_preprocessing(self) -> bool:
        """Run enhanced CSV data preprocessing and cleaning"""
        logger.info("🧹 Stage 2.5: Starting Enhanced Data Preprocessing...")

        try:
            # Import and run enhanced preprocessing pipeline
            result = subprocess.run(
                [
                    "python",
                    "/app/enhanced_preprocessing_pipeline.py",
                ],
                capture_output=True,
                text=True,
                timeout=900,  # 15 minutes for preprocessing
            )

            if result.returncode == 0:
                logger.info("✅ Enhanced data preprocessing completed")
                logger.info(f"Preprocessing output: {result.stdout}")
                return True
            else:
                logger.error(f"❌ Enhanced preprocessing failed: {result.stderr}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Enhanced preprocessing timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Enhanced preprocessing exception: {e}")
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
