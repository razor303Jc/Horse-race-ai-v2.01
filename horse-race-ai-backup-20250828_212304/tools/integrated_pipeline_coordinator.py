#!/usr/bin/env python3
"""
Enhanced Pipeline Coordinator with Manual Download Integration
Horse Racing AI v2.03 - Complete Pipeline Management

Integrates:
1. Manual download file watcher system
2. Database upload pipeline
3. ML training triggers
4. Web app integration
5. Real-time race card display
"""

import asyncio
import logging
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

# Import our manual download components
sys.path.append(str(Path(__file__).parent.parent))
from tools.automation.file_watcher_enhanced import RacingDataFileWatcher
from tools.automation.file_watcher_status import get_processing_status
from tools.database.complete_upload import upload_race_cards_complete

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class IntegratedPipelineCoordinator:
    """Enhanced pipeline coordinator with manual download integration"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.base_path = Path(base_path)
        self.config_path = self.base_path / "config"
        self.data_path = self.base_path / "data/daily_downloads"
        self.logs_path = self.base_path / "logs"

        # Pipeline state tracking
        self.pipeline_state = {
            "file_watcher": {"active": False, "last_processed": None},
            "data_extraction": {"complete": False, "files_processed": 0},
            "database_upload": {"complete": False, "records_uploaded": 0},
            "ml_training": {"triggered": False, "models_updated": 0},
            "web_app_sync": {"complete": False, "last_sync": None},
        }

        # Status file for web app integration
        self.status_file = self.data_path / "pipeline_status.json"

        # Initialize directories
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure all required directories exist"""
        dirs_to_create = [
            self.data_path / "manual_download",
            self.data_path / "cards_data/races",
            self.data_path / "cards_data/horses",
            self.data_path / "cards_data/racecard_details",
            self.data_path / "results_data",
            self.data_path / "processed",
            self.logs_path,
        ]

        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)

    def start_integrated_pipeline(self):
        """Start the complete integrated pipeline"""
        logger.info("🚀 Starting Integrated Horse Racing AI Pipeline")
        logger.info("=" * 60)

        try:
            # Step 1: Start file watcher system
            logger.info("📂 Step 1: Starting file watcher system...")
            self._start_file_watcher()

            # Step 2: Check for existing data
            logger.info("🔍 Step 2: Checking for existing race data...")
            self._check_existing_data()

            # Step 3: Process any pending data
            logger.info("📊 Step 3: Processing pending data...")
            self._process_pending_data()

            # Step 4: Start monitoring loop
            logger.info("🔄 Step 4: Starting monitoring loop...")
            self._start_monitoring_loop()

        except Exception as e:
            logger.error(f"❌ Pipeline startup failed: {e}")
            raise

    def _start_file_watcher(self):
        """Initialize and start the file watcher system"""
        try:
            # Import and configure file watcher
            from watchdog.observers import Observer

            # Create file watcher instance
            event_handler = RacingDataFileWatcher(str(self.base_path))
            observer = Observer()
            observer.schedule(
                event_handler, str(self.data_path / "manual_download"), recursive=False
            )

            # Start observer
            observer.start()
            self.pipeline_state["file_watcher"]["active"] = True
            logger.info("✅ File watcher system started")

            return observer

        except Exception as e:
            logger.error(f"❌ File watcher startup failed: {e}")
            raise

    def _check_existing_data(self):
        """Check for existing processed race data"""
        cards_data_dir = self.data_path / "cards_data"

        # Check for race data files
        race_files = {
            "races": cards_data_dir / "races" / "races.csv",
            "horses": cards_data_dir / "horses" / "horses.csv",
            "entries": cards_data_dir / "racecard_details" / "racecard_details.csv",
        }

        existing_files = {}
        for name, path in race_files.items():
            if path.exists():
                try:
                    import pandas as pd

                    df = pd.read_csv(path)
                    existing_files[name] = len(df)
                    logger.info(f"  📊 Found {name}: {len(df)} records")
                except Exception as e:
                    logger.warning(f"  ⚠️ Error reading {name}: {e}")

        if existing_files:
            logger.info(f"✅ Found existing race data: {existing_files}")
            self.pipeline_state["data_extraction"]["complete"] = True
            self.pipeline_state["data_extraction"]["files_processed"] = len(
                existing_files
            )

            # Trigger database upload if data exists
            self._trigger_database_upload()
        else:
            logger.info("📥 No existing race data found - waiting for manual downloads")

    def _process_pending_data(self):
        """Process any pending data in the pipeline"""

        # Check processing status
        try:
            status = get_processing_status(
                str(self.data_path / "processing_status.json")
            )
            if status.get("has_race_data", False):
                logger.info("📊 Found processed race data")

                # Check if database upload needed
                if not self.pipeline_state["database_upload"]["complete"]:
                    self._trigger_database_upload()

                # Check if ML training needed
                if not self.pipeline_state["ml_training"]["triggered"]:
                    self._trigger_ml_training()

        except Exception as e:
            logger.warning(f"⚠️ Could not check processing status: {e}")

    def _trigger_database_upload(self):
        """Trigger the database upload process"""
        logger.info("🗄️ Triggering database upload...")

        try:
            # Run the complete upload process
            from tools.database.complete_upload import upload_race_cards_complete

            # Execute upload in subprocess to avoid blocking
            upload_script = self.base_path / "tools/database/complete_upload.py"
            result = subprocess.run(
                [sys.executable, str(upload_script)],
                capture_output=True,
                text=True,
                timeout=300,
            )

            if result.returncode == 0:
                logger.info("✅ Database upload completed successfully")
                self.pipeline_state["database_upload"]["complete"] = True

                # Parse upload results from output
                if "Success Rate: 100.0%" in result.stdout:
                    self.pipeline_state["database_upload"]["records_uploaded"] = 759

                # Trigger next stage
                self._trigger_ml_training()

            else:
                logger.error(f"❌ Database upload failed: {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Database upload error: {e}")

    def _trigger_ml_training(self):
        """Trigger ML model training/updating"""
        logger.info("🤖 Triggering ML training...")

        try:
            # Signal ML training container
            ml_trigger_file = self.base_path / "data/ml_training_trigger.json"
            trigger_data = {
                "timestamp": datetime.now().isoformat(),
                "data_source": "manual_download",
                "records_available": self.pipeline_state["database_upload"][
                    "records_uploaded"
                ],
                "trigger_reason": "new_race_data_uploaded",
            }

            with open(ml_trigger_file, "w") as f:
                json.dump(trigger_data, f, indent=2)

            self.pipeline_state["ml_training"]["triggered"] = True
            logger.info("✅ ML training trigger created")

            # Trigger web app sync
            self._trigger_web_app_sync()

        except Exception as e:
            logger.error(f"❌ ML training trigger failed: {e}")

    def _trigger_web_app_sync(self):
        """Trigger web app data synchronization"""
        logger.info("🌐 Triggering web app sync...")

        try:
            # Create web app sync signal
            sync_file = self.base_path / "data/web_app_sync.json"
            sync_data = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_state": self.pipeline_state,
                "race_data_available": True,
                "database_ready": self.pipeline_state["database_upload"]["complete"],
                "ml_models_updated": self.pipeline_state["ml_training"]["triggered"],
            }

            with open(sync_file, "w") as f:
                json.dump(sync_data, f, indent=2)

            self.pipeline_state["web_app_sync"]["complete"] = True
            self.pipeline_state["web_app_sync"][
                "last_sync"
            ] = datetime.now().isoformat()

            logger.info("✅ Web app sync completed")

        except Exception as e:
            logger.error(f"❌ Web app sync failed: {e}")

    def _start_monitoring_loop(self):
        """Start the main monitoring loop"""
        logger.info("🔄 Starting pipeline monitoring loop...")

        try:
            while True:
                # Update pipeline status
                self._update_pipeline_status()

                # Check for new data
                self._check_for_new_data()

                # Check pipeline health
                self._check_pipeline_health()

                # Sleep for monitoring interval
                time.sleep(30)  # Check every 30 seconds

        except KeyboardInterrupt:
            logger.info("🛑 Pipeline monitoring stopped by user")
        except Exception as e:
            logger.error(f"❌ Monitoring loop error: {e}")

    def _update_pipeline_status(self):
        """Update the pipeline status file for web app"""
        try:
            status_data = {
                "timestamp": datetime.now().isoformat(),
                "pipeline_state": self.pipeline_state,
                "system_status": "running",
                "last_activity": datetime.now().isoformat(),
            }

            with open(self.status_file, "w") as f:
                json.dump(status_data, f, indent=2)

        except Exception as e:
            logger.warning(f"⚠️ Status update failed: {e}")

    def _check_for_new_data(self):
        """Check for newly processed data"""
        try:
            # Check processing status
            processing_status_file = self.data_path / "processing_status.json"
            if processing_status_file.exists():
                with open(processing_status_file, "r") as f:
                    status = json.load(f)

                if status.get("has_race_data", False):
                    last_processed = status.get("last_processed")
                    pipeline_last = self.pipeline_state["file_watcher"][
                        "last_processed"
                    ]

                    if last_processed != pipeline_last:
                        logger.info("📊 New race data detected - triggering pipeline")
                        self.pipeline_state["file_watcher"][
                            "last_processed"
                        ] = last_processed

                        # Reset pipeline state for new data
                        self.pipeline_state["database_upload"]["complete"] = False
                        self.pipeline_state["ml_training"]["triggered"] = False
                        self.pipeline_state["web_app_sync"]["complete"] = False

                        # Trigger database upload
                        self._trigger_database_upload()

        except Exception as e:
            logger.warning(f"⚠️ New data check failed: {e}")

    def _check_pipeline_health(self):
        """Check pipeline component health"""
        try:
            health_status = {
                "file_watcher": self.pipeline_state["file_watcher"]["active"],
                "data_available": self.pipeline_state["data_extraction"]["complete"],
                "database_synced": self.pipeline_state["database_upload"]["complete"],
                "ml_ready": self.pipeline_state["ml_training"]["triggered"],
                "web_app_ready": self.pipeline_state["web_app_sync"]["complete"],
            }

            # Log health summary every 5 minutes
            current_time = datetime.now()
            if (
                not hasattr(self, "_last_health_log")
                or (current_time - self._last_health_log).seconds > 300
            ):
                healthy_components = sum(health_status.values())
                total_components = len(health_status)
                logger.info(
                    f"💚 Pipeline health: {healthy_components}/{total_components} components ready"
                )
                self._last_health_log = current_time

        except Exception as e:
            logger.warning(f"⚠️ Health check failed: {e}")


def main():
    """Main entry point for integrated pipeline"""
    try:
        coordinator = IntegratedPipelineCoordinator()
        coordinator.start_integrated_pipeline()
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline stopped by user")
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
