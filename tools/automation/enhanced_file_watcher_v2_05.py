#!/usr/bin/env python3
"""
Enhanced File Watcher & Auto-Processing System
Horse Racing AI v2.05 - Advanced Pipeline Integration
Latest Version: v2.05

Comprehensive file watcher system that monitors for racing data files and
integrates with the Node-RED C2 Command Center via the Pipeline API Handler.
Combines best features from all previous watcher implementations.

Features:
- Real-time monitoring of multiple data sources
- Integration with Pipeline API Handler for C2 control
- Advanced validation and data quality checks
- Event-driven pipeline triggering
- Redis integration for status tracking
- Database connectivity for immediate upload
- Support for Cards, Results, and Form data
- Automatic daily progression and completion tracking
- Clean error handling and recovery
- Comprehensive logging and monitoring

Author: Horse Racing AI System
Created: August 30, 2025
Version: v2.05 - Latest
"""

import asyncio
import zipfile
import shutil
import logging
import pandas as pd
import json
import os
import sys
import subprocess
import threading
import time
from pathlib import Path
from datetime import datetime, timedelta, time as time_obj
from typing import Optional, Dict, Any, List, Tuple, Set, Callable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import redis
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(
            "/home/jc/Documents/Horse-race-ai-v2.05/logs/enhanced_file_watcher_v2_05.log"
        ),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class EnhancedFileWatcherV205(FileSystemEventHandler):
    """
    Enhanced File Watcher v2.05 - Latest Version
    Integrates with Node-RED C2 Command Center and Pipeline API Handler
    """

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.05"):
        """Initialize the enhanced file watcher system"""
        self.base_path = Path(base_path)
        self.version = "v2.05"

        # Directory structure
        self.watch_dirs = {
            "manual_download": self.base_path / "data/daily_downloads/manual_download",
            "auto_download": self.base_path / "data/daily_downloads/auto_download",
            "external_feed": self.base_path / "data/external_feeds",
        }

        self.data_dirs = {
            "cards": self.base_path / "data/daily_downloads/cards_data",
            "results": self.base_path / "data/daily_downloads/results_data",
            "form": self.base_path / "data/daily_downloads/form_data",
            "processed": self.base_path / "data/processed",
            "backup": self.base_path / "data/backup",
        }

        # State and status files
        self.state_file = self.base_path / "data/watcher_state_v2_05.json"
        self.status_file = self.base_path / "data/watcher_status_v2_05.json"
        self.config_file = self.base_path / "config/enhanced_watcher_config_v2_05.json"

        # Create directories
        self.create_directory_structure()

        # Initialize connections
        self.redis_client = self._init_redis()
        self.db_config = self._get_db_config()

        # Load configuration and state
        self.config = self.load_configuration()
        self.state = self.load_watcher_state()

        # Processing status
        self.processing_status = {
            "cards_ready": False,
            "results_ready": False,
            "form_ready": False,
            "pipeline_active": False,
            "last_processed": None,
            "current_target_date": self.get_current_target_date(),
            "completed_days": set(self.state.get("completed_days", [])),
            "processing_queue": [],
            "error_count": 0,
            "success_count": 0,
        }

        # File patterns for different data types
        self.file_patterns = {
            "cards": ["racecard", "card", "race-card"],
            "results": ["result", "outcome"],
            "form": ["form", "past-performance", "history"],
        }

        # Pipeline API Handler integration
        self.pipeline_api_path = "/app/tools/pipeline_api_handler.py"

        logger.info(f"🚀 Enhanced File Watcher v{self.version} initialized")
        logger.info(f"📅 Target date: {self.processing_status['current_target_date']}")
        logger.info(
            f"✅ Completed days: {len(self.processing_status['completed_days'])}"
        )

    def create_directory_structure(self):
        """Create comprehensive directory structure"""
        all_dirs = list(self.watch_dirs.values()) + list(self.data_dirs.values())
        additional_dirs = [
            self.base_path / "logs",
            self.base_path / "config",
            self.base_path / "data/validation_reports",
            self.base_path / "data/processing_logs",
        ]

        for directory in all_dirs + additional_dirs:
            directory.mkdir(parents=True, exist_ok=True)

        logger.info(
            f"📁 Directory structure created - {len(all_dirs + additional_dirs)} directories"
        )

    def _init_redis(self) -> Optional[redis.Redis]:
        """Initialize Redis connection for status tracking"""
        try:
            client = redis.Redis(
                host="redis",
                port=6379,
                password="redis_password_123",
                decode_responses=True,
            )
            client.ping()
            logger.info("✅ Redis connection established")
            return client
        except Exception as e:
            logger.warning(f"⚠️ Redis connection failed: {e}")
            return None

    def _get_db_config(self) -> Dict[str, str]:
        """Get database configuration"""
        return {
            "host": "postgres",
            "port": "5432",
            "dbname": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def load_configuration(self) -> Dict[str, Any]:
        """Load watcher configuration"""
        default_config = {
            "watcher_settings": {
                "auto_process": True,
                "validation_required": True,
                "pipeline_integration": True,
                "auto_backup": True,
                "max_file_age_hours": 24,
                "retry_attempts": 3,
                "retry_delay_seconds": 30,
            },
            "data_validation": {
                "required_columns": {
                    "races": ["race_id", "race_time", "course"],
                    "horses": ["horse_id", "horse_name", "race_id"],
                    "results": ["race_id", "position", "horse_id"],
                },
                "min_race_count": 5,
                "max_missing_data_percent": 10,
            },
            "pipeline_triggers": {
                "immediate_stages": ["data_validation", "quality_check"],
                "delayed_stages": ["database_upload", "relationship_analysis"],
                "final_stages": ["ml_model_update", "ai_selections_generation"],
            },
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    config = json.load(f)
                logger.info("📋 Configuration loaded from file")
                return config
            except Exception as e:
                logger.warning(f"⚠️ Failed to load config: {e}")

        # Save default config
        self.save_configuration(default_config)
        return default_config

    def save_configuration(self, config: Dict[str, Any]):
        """Save configuration to file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(config, f, indent=2)
            logger.info("💾 Configuration saved")
        except Exception as e:
            logger.error(f"❌ Failed to save config: {e}")

    def load_watcher_state(self) -> Dict[str, Any]:
        """Load persistent watcher state"""
        default_state = {
            "version": self.version,
            "last_startup": datetime.now().isoformat(),
            "completed_days": [],
            "processing_history": [],
            "error_history": [],
            "statistics": {
                "total_files_processed": 0,
                "total_races_processed": 0,
                "total_errors": 0,
                "uptime_hours": 0,
            },
        }

        if self.state_file.exists():
            try:
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                logger.info("📁 Watcher state loaded")
                return state
            except Exception as e:
                logger.warning(f"⚠️ Failed to load state: {e}")

        return default_state

    def save_watcher_state(self):
        """Save current watcher state"""
        try:
            self.state["last_update"] = datetime.now().isoformat()
            self.state["completed_days"] = list(
                self.processing_status["completed_days"]
            )

            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2, default=str)

            # Also update Redis if available
            if self.redis_client:
                self.redis_client.set(
                    "watcher:state", json.dumps(self.state, default=str)
                )

            logger.debug("💾 Watcher state saved")
        except Exception as e:
            logger.error(f"❌ Failed to save state: {e}")

    def get_current_target_date(self) -> str:
        """Get the current target date for processing"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Check if today is already completed
        if today in self.processing_status.get("completed_days", set()):
            # Move to next available day
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            return tomorrow

        return today

    def update_redis_status(self, status_type: str, data: Any):
        """Update status in Redis for C2 dashboard"""
        if not self.redis_client:
            return

        try:
            key = f"watcher:{status_type}"
            if isinstance(data, dict):
                self.redis_client.set(key, json.dumps(data, default=str))
            else:
                self.redis_client.set(key, str(data))
        except Exception as e:
            logger.warning(f"⚠️ Failed to update Redis status: {e}")

    def on_created(self, event):
        """Handle new file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.info(f"🔍 New file detected: {file_path.name}")

        # Check if it's a file we care about
        if self.should_process_file(file_path):
            # Run async processing
            asyncio.create_task(self.process_file(file_path))

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed"""
        # Check file extension
        if file_path.suffix.lower() not in [".zip", ".csv", ".json"]:
            return False

        # Check if file matches any pattern
        filename_lower = file_path.name.lower()
        for data_type, patterns in self.file_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return True

        return False

    async def process_file(self, file_path: Path):
        """Process a detected file"""
        try:
            logger.info(f"🔄 Processing file: {file_path.name}")

            # Update status
            self.update_redis_status("current_processing", file_path.name)

            # Determine file type and processing method
            if file_path.suffix.lower() == ".zip":
                await self.process_zip_file(file_path)
            elif file_path.suffix.lower() == ".csv":
                await self.process_csv_file(file_path)

            # Update success count
            self.processing_status["success_count"] += 1
            self.save_watcher_state()

        except Exception as e:
            logger.error(f"❌ Error processing {file_path}: {e}")
            self.processing_status["error_count"] += 1
            await self.handle_processing_error(file_path, e)

    async def process_zip_file(self, zip_path: Path):
        """Process ZIP file based on content type"""
        try:
            # Determine data type from filename
            data_type = self.determine_data_type(zip_path.name)

            if data_type == "cards":
                await self.extract_race_cards(zip_path)
            elif data_type == "results":
                await self.extract_results(zip_path)
            elif data_type == "form":
                await self.extract_form_data(zip_path)
            else:
                logger.warning(f"⚠️ Unknown ZIP type: {zip_path.name}")
                return

            # Trigger pipeline if both cards and results are ready
            await self.check_pipeline_readiness()

        except Exception as e:
            logger.error(f"❌ Error processing ZIP file {zip_path}: {e}")
            raise

    def determine_data_type(self, filename: str) -> str:
        """Determine data type from filename"""
        filename_lower = filename.lower()

        for data_type, patterns in self.file_patterns.items():
            if any(pattern in filename_lower for pattern in patterns):
                return data_type

        return "unknown"

    async def extract_race_cards(self, zip_path: Path):
        """Extract race cards data"""
        try:
            logger.info(f"📋 Extracting race cards: {zip_path.name}")

            # Clear previous data
            target_dir = self.data_dirs["cards"]
            if target_dir.exists() and any(target_dir.iterdir()):
                shutil.rmtree(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)

            # Validate extracted data
            if await self.validate_cards_data():
                self.processing_status["cards_ready"] = True
                await self.backup_processed_file(zip_path, "cards")
                logger.info(f"✅ Race cards processed successfully")
            else:
                raise Exception("Cards data validation failed")

        except Exception as e:
            logger.error(f"❌ Error extracting race cards: {e}")
            raise

    async def extract_results(self, zip_path: Path):
        """Extract results data"""
        try:
            logger.info(f"🏁 Extracting results: {zip_path.name}")

            # Clear previous data
            target_dir = self.data_dirs["results"]
            if target_dir.exists() and any(target_dir.iterdir()):
                shutil.rmtree(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)

            # Validate extracted data
            if await self.validate_results_data():
                self.processing_status["results_ready"] = True
                await self.backup_processed_file(zip_path, "results")
                logger.info(f"✅ Results processed successfully")
            else:
                raise Exception("Results data validation failed")

        except Exception as e:
            logger.error(f"❌ Error extracting results: {e}")
            raise

    async def extract_form_data(self, zip_path: Path):
        """Extract form/historical data"""
        try:
            logger.info(f"📊 Extracting form data: {zip_path.name}")

            # Clear previous data
            target_dir = self.data_dirs["form"]
            if target_dir.exists() and any(target_dir.iterdir()):
                shutil.rmtree(target_dir)
                target_dir.mkdir(parents=True, exist_ok=True)

            # Extract ZIP
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_dir)

            # Validate extracted data
            if await self.validate_form_data():
                self.processing_status["form_ready"] = True
                await self.backup_processed_file(zip_path, "form")
                logger.info(f"✅ Form data processed successfully")
            else:
                raise Exception("Form data validation failed")

        except Exception as e:
            logger.error(f"❌ Error extracting form data: {e}")
            raise

    async def validate_cards_data(self) -> bool:
        """Validate race cards data structure"""
        try:
            cards_dir = self.data_dirs["cards"]

            # Check for required CSV files
            races_csv = list(cards_dir.glob("**/races.csv"))
            horses_csv = list(cards_dir.glob("**/horses.csv"))

            if not races_csv or not horses_csv:
                logger.error("❌ Missing required CSV files (races.csv, horses.csv)")
                return False

            # Validate races data
            races_df = pd.read_csv(races_csv[0])
            required_columns = self.config["data_validation"]["required_columns"][
                "races"
            ]

            missing_columns = [
                col for col in required_columns if col not in races_df.columns
            ]
            if missing_columns:
                logger.error(
                    f"❌ Missing required columns in races.csv: {missing_columns}"
                )
                return False

            # Check minimum race count
            min_races = self.config["data_validation"]["min_race_count"]
            if len(races_df) < min_races:
                logger.error(f"❌ Insufficient races: {len(races_df)} < {min_races}")
                return False

            logger.info(f"✅ Cards data validated: {len(races_df)} races")
            return True

        except Exception as e:
            logger.error(f"❌ Cards validation error: {e}")
            return False

    async def validate_results_data(self) -> bool:
        """Validate results data structure"""
        try:
            results_dir = self.data_dirs["results"]

            # Check for results CSV files
            results_csv = list(results_dir.glob("**/results_*.csv"))

            if not results_csv:
                logger.error("❌ No results CSV files found")
                return False

            # Validate at least one results file
            results_df = pd.read_csv(results_csv[0])
            required_columns = self.config["data_validation"]["required_columns"][
                "results"
            ]

            missing_columns = [
                col for col in required_columns if col not in results_df.columns
            ]
            if missing_columns:
                logger.error(
                    f"❌ Missing required columns in results: {missing_columns}"
                )
                return False

            logger.info(f"✅ Results data validated: {len(results_df)} results")
            return True

        except Exception as e:
            logger.error(f"❌ Results validation error: {e}")
            return False

    async def validate_form_data(self) -> bool:
        """Validate form data structure"""
        try:
            form_dir = self.data_dirs["form"]

            # Check for form-related CSV files
            form_files = list(form_dir.glob("**/*.csv"))

            if not form_files:
                logger.warning("⚠️ No form CSV files found")
                return True  # Form data is optional

            logger.info(f"✅ Form data validated: {len(form_files)} files")
            return True

        except Exception as e:
            logger.error(f"❌ Form validation error: {e}")
            return False

    async def backup_processed_file(self, file_path: Path, data_type: str):
        """Backup processed file with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{data_type}_{timestamp}_{file_path.name}"
            backup_path = self.data_dirs["backup"] / backup_name

            shutil.copy2(file_path, backup_path)

            # Remove original from manual download
            if file_path.parent.name == "manual_download":
                file_path.unlink()
                logger.info(f"🗑️ Cleaned up: {file_path.name}")

        except Exception as e:
            logger.warning(f"⚠️ Backup failed: {e}")

    async def check_pipeline_readiness(self):
        """Check if pipeline should be triggered"""
        if not self.config["watcher_settings"]["pipeline_integration"]:
            return

        cards_ready = self.processing_status["cards_ready"]
        results_ready = self.processing_status["results_ready"]

        if cards_ready and results_ready:
            logger.info("🚀 Both datasets ready - triggering pipeline")
            await self.trigger_pipeline_stages()

    async def trigger_pipeline_stages(self):
        """Trigger pipeline stages via API handler"""
        try:
            # Update Redis status
            self.update_redis_status("pipeline_active", True)

            # Get pipeline trigger configuration
            immediate_stages = self.config["pipeline_triggers"]["immediate_stages"]
            delayed_stages = self.config["pipeline_triggers"]["delayed_stages"]
            final_stages = self.config["pipeline_triggers"]["final_stages"]

            # Execute immediate stages
            for stage in immediate_stages:
                await self.execute_pipeline_stage(stage)
                await asyncio.sleep(5)  # Brief delay between stages

            # Execute delayed stages
            await asyncio.sleep(30)  # Wait for immediate stages to complete
            for stage in delayed_stages:
                await self.execute_pipeline_stage(stage)
                await asyncio.sleep(10)

            # Execute final stages
            await asyncio.sleep(60)  # Wait for processing stages
            for stage in final_stages:
                await self.execute_pipeline_stage(stage)
                await asyncio.sleep(15)

            # Mark day as completed
            current_date = self.processing_status["current_target_date"]
            self.processing_status["completed_days"].add(current_date)

            # Reset status for next day
            self.processing_status["cards_ready"] = False
            self.processing_status["results_ready"] = False
            self.processing_status["current_target_date"] = (
                self.get_current_target_date()
            )

            self.save_watcher_state()
            logger.info(f"🎉 Pipeline completed for {current_date}")

        except Exception as e:
            logger.error(f"❌ Pipeline trigger failed: {e}")
            self.update_redis_status("pipeline_active", False)

    async def execute_pipeline_stage(self, stage: str):
        """Execute a specific pipeline stage via API handler"""
        try:
            # Map stage names to API commands
            stage_commands = {
                "data_validation": "validate",
                "quality_check": "validate",
                "database_upload": "upload",
                "relationship_analysis": "process",
                "ml_model_update": "train",
                "ai_selections_generation": "ratings",
            }

            api_command = stage_commands.get(stage, "status")

            # Execute via Docker
            command = [
                "docker",
                "exec",
                "horse_racing_data_pipeline_clean",
                "python",
                self.pipeline_api_path,
                api_command,
            ]

            logger.info(f"🔧 Executing pipeline stage: {stage}")

            result = subprocess.run(
                command, capture_output=True, text=True, timeout=300  # 5 minute timeout
            )

            if result.returncode == 0:
                logger.info(f"✅ Pipeline stage completed: {stage}")

                # Try to parse API response
                try:
                    api_response = json.loads(result.stdout)
                    self.update_redis_status(f"stage_{stage}", api_response)
                except:
                    pass
            else:
                logger.error(f"❌ Pipeline stage failed: {stage} - {result.stderr}")

        except Exception as e:
            logger.error(f"❌ Stage execution error: {stage} - {e}")

    async def handle_processing_error(self, file_path: Path, error: Exception):
        """Handle processing errors with retry logic"""
        try:
            error_info = {
                "file": str(file_path),
                "error": str(error),
                "timestamp": datetime.now().isoformat(),
                "retry_count": 0,
            }

            # Add to error history
            if "error_history" not in self.state:
                self.state["error_history"] = []

            self.state["error_history"].append(error_info)

            # Update Redis
            self.update_redis_status("last_error", error_info)

            # Attempt retry if configured
            max_retries = self.config["watcher_settings"]["retry_attempts"]
            if error_info["retry_count"] < max_retries:
                retry_delay = self.config["watcher_settings"]["retry_delay_seconds"]
                logger.info(f"🔄 Retrying in {retry_delay} seconds...")

                await asyncio.sleep(retry_delay)
                await self.process_file(file_path)

        except Exception as e:
            logger.error(f"❌ Error handling failed: {e}")

    def get_status_summary(self) -> Dict[str, Any]:
        """Get comprehensive status summary for C2 dashboard"""
        return {
            "version": self.version,
            "timestamp": datetime.now().isoformat(),
            "target_date": self.processing_status["current_target_date"],
            "cards_ready": self.processing_status["cards_ready"],
            "results_ready": self.processing_status["results_ready"],
            "form_ready": self.processing_status["form_ready"],
            "pipeline_active": self.processing_status["pipeline_active"],
            "completed_days": len(self.processing_status["completed_days"]),
            "success_count": self.processing_status["success_count"],
            "error_count": self.processing_status["error_count"],
            "uptime": (
                datetime.now() - datetime.fromisoformat(self.state["last_startup"])
            ).total_seconds()
            / 3600,
            "redis_connected": self.redis_client is not None,
            "directories_monitored": len(self.watch_dirs),
            "last_processed": self.processing_status["last_processed"],
        }

    async def process_existing_files(self):
        """Process any existing files in watch directories"""
        logger.info("🔍 Checking for existing files...")

        for watch_name, watch_dir in self.watch_dirs.items():
            if not watch_dir.exists():
                continue

            for file_path in watch_dir.iterdir():
                if file_path.is_file() and self.should_process_file(file_path):
                    logger.info(f"🔄 Processing existing file: {file_path.name}")
                    await self.process_file(file_path)

    def start_monitoring(self):
        """Start file system monitoring"""
        observer = Observer()

        for watch_name, watch_dir in self.watch_dirs.items():
            if watch_dir.exists():
                observer.schedule(self, str(watch_dir), recursive=True)
                logger.info(f"👁️ Monitoring: {watch_dir}")

        observer.start()
        logger.info("🚀 File monitoring started")

        try:
            while True:
                # Update status periodically
                status = self.get_status_summary()
                self.update_redis_status("summary", status)

                # Save state periodically
                self.save_watcher_state()

                time.sleep(30)  # Update every 30 seconds

        except KeyboardInterrupt:
            logger.info("🛑 Shutting down file watcher...")
            observer.stop()

        observer.join()


class FileWatcherManagerV205:
    """Manager class for the Enhanced File Watcher v2.05"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.05"):
        self.base_path = base_path
        self.watcher = EnhancedFileWatcherV205(base_path)

    async def start_service(self):
        """Start the file watcher service"""
        logger.info("🚀 Starting Enhanced File Watcher Service v2.05")

        # Process existing files first
        await self.watcher.process_existing_files()

        # Start monitoring
        self.watcher.start_monitoring()

    def get_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return self.watcher.get_status_summary()


def main():
    """Main entry point for the Enhanced File Watcher v2.05"""
    import signal

    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)

    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    logger.info("🚀 Enhanced File Watcher v2.05 - Latest Version")
    logger.info("📁 Monitoring multiple data sources")
    logger.info("🔗 Integrated with Node-RED C2 Command Center")
    logger.info("🛑 Press Ctrl+C to stop")

    try:
        manager = FileWatcherManagerV205()
        asyncio.run(manager.start_service())

    except KeyboardInterrupt:
        logger.info("🛑 Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Service failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
