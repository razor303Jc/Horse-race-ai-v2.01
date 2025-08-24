#!/usr/bin/env python3
"""
Daily Racing Data File Watcher
Horse Racing AI v2.04 - Daily Monitoring System

Continuously monitors for each day's racing files until they arrive,
then automatically advances to the next day. Provides persistence
and automatic daily progression.
"""

import asyncio
import zipfile
import shutil
import logging
import json
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta, time
from typing import Optional, Dict, Any, Set
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import CSV backup integration
try:
    from tools.pipeline.csv_backup_integration import CSVBackupIntegrator
except ImportError as e:
    logging.warning(f"CSV backup integration not available: {e}")
    CSVBackupIntegrator = None

# Set up logging
log_file = "/home/jc/Documents/Horse-race-ai-v2.04/logs/daily_file_watcher.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DailyRacingFileWatcher(FileSystemEventHandler):
    """Daily monitoring system for racing data files"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.watch_dir = self.base_path / "data/daily_downloads/manual_download"
        self.cards_dir = self.base_path / "data/daily_downloads/cards_data"
        self.results_dir = self.base_path / "data/daily_downloads/results_data"
        self.processed_dir = self.base_path / "data/daily_downloads/processed"
        self.state_file = self.base_path / "data/daily_watcher_state.json"

        # Create directories
        self.create_directories()

        # Initialize CSV backup integration
        self.backup_integrator = None
        if CSVBackupIntegrator:
            try:
                self.backup_integrator = CSVBackupIntegrator(str(self.base_path))
                logger.info("✅ CSV backup integration initialized")
            except Exception as e:
                logger.warning(f"⚠️ CSV backup integration failed: {e}")

        # Daily tracking state - load first
        self.state = self.load_watcher_state()

        # Daily completion tracking - initialize before get_current_target_date
        self.completed_days: Set[str] = set(self.state.get("completed_days", []))

        # Now get target date (which needs completed_days)
        self.current_target_date = self.get_current_target_date()

        # Files needed per day
        self.required_files_per_day = {"cards": False, "results": False}

        logger.info(f"🗓️ Daily File Watcher initialized")
        logger.info(f"📅 Target date: {self.current_target_date}")
        logger.info(f"✅ Completed days: {len(self.completed_days)}")

    def create_directories(self):
        """Create required directory structure"""
        directories = [
            self.watch_dir,
            self.cards_dir,
            self.results_dir,
            self.processed_dir,
            self.base_path / "logs",
            self.base_path / "data",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    def load_watcher_state(self) -> Dict[str, Any]:
        """Load persistent watcher state from file"""
        try:
            if self.state_file.exists():
                with open(self.state_file, "r") as f:
                    state = json.load(f)
                logger.info(
                    f"📄 Loaded watcher state: {len(state.get('completed_days', []))} completed days"
                )
                return state
            else:
                logger.info("📄 No existing state file - starting fresh")
                return {
                    "completed_days": [],
                    "last_target_date": None,
                    "total_processed": 0,
                    "created_at": datetime.now().isoformat(),
                }
        except Exception as e:
            logger.error(f"❌ Error loading watcher state: {e}")
            return {"completed_days": [], "total_processed": 0}

    def save_watcher_state(self):
        """Save persistent watcher state to file"""
        try:
            self.state["completed_days"] = list(self.completed_days)
            self.state["last_target_date"] = self.current_target_date
            self.state["last_updated"] = datetime.now().isoformat()

            with open(self.state_file, "w") as f:
                json.dump(self.state, f, indent=2)

            logger.info(
                f"💾 Watcher state saved: {len(self.completed_days)} completed days"
            )
        except Exception as e:
            logger.error(f"❌ Error saving watcher state: {e}")

    def get_current_target_date(self) -> str:
        """Get the current target date for file watching"""
        today = datetime.now().date()

        # If we've already completed today, move to tomorrow
        today_str = today.strftime("%Y-%m-%d")
        if today_str in self.completed_days:
            tomorrow = today + timedelta(days=1)
            target_date = tomorrow.strftime("%Y-%m-%d")
            logger.info(f"📅 Today already completed, targeting: {target_date}")
            return target_date

        # Otherwise target today
        logger.info(f"📅 Targeting today: {today_str}")
        return today_str

    def advance_to_next_day(self):
        """Advance target date to next day after completion"""
        current_date = datetime.strptime(self.current_target_date, "%Y-%m-%d").date()
        next_date = current_date + timedelta(days=1)
        self.current_target_date = next_date.strftime("%Y-%m-%d")

        # Reset daily file tracking
        self.required_files_per_day = {"cards": False, "results": False}

        logger.info(f"📅 Advanced to next day: {self.current_target_date}")
        self.save_watcher_state()
        self.update_status_display()

    def mark_day_completed(self, date_str: str):
        """Mark a specific day as completed"""
        self.completed_days.add(date_str)
        self.state["total_processed"] = self.state.get("total_processed", 0) + 1

        logger.info(f"✅ Day completed: {date_str}")
        logger.info(f"📊 Total days processed: {self.state['total_processed']}")

        self.save_watcher_state()
        self.advance_to_next_day()

    def on_created(self, event):
        """Triggered when new file is added"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.info(f"🔍 New file detected: {file_path.name}")

        if file_path.suffix.lower() == ".zip":
            # Run processing in a separate thread to avoid asyncio issues
            import threading

            thread = threading.Thread(
                target=self._run_async_processing, args=(file_path,)
            )
            thread.daemon = True
            thread.start()

    def _run_async_processing(self, zip_path: Path):
        """Run async processing in a new event loop"""
        try:
            import asyncio

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_daily_zip_file(zip_path))
            loop.close()
        except Exception as e:
            logger.error(f"❌ Error in async processing: {e}")

    async def process_daily_zip_file(self, zip_path: Path):
        """Process ZIP file for current target date"""
        try:
            logger.info(
                f"🔄 Processing ZIP for {self.current_target_date}: {zip_path.name}"
            )

            # Check if file matches current target date
            if not self.is_file_for_target_date(zip_path):
                logger.warning(
                    f"⚠️ File doesn't match target date {self.current_target_date}: {zip_path.name}"
                )

                # Enhanced user warning with specific instructions
                file_type = self.determine_file_type(zip_path)
                expected_name = self.get_expected_filename(file_type)

                print("\n" + "=" * 80)
                print("🚨 FILE NAME MISMATCH WARNING")
                print("=" * 80)
                print(f"📁 Received file: {zip_path.name}")
                print(f"📅 Target date: {self.current_target_date}")
                print(f"🎯 Expected name: {expected_name}")
                print(f"📝 File type detected: {file_type}")
                print()
                print("💡 TO FIX THIS:")
                print(f"   1. Rename your file to: {expected_name}")
                print(f"   2. Place it in: {self.watch_dir}")
                print("   3. The system will automatically detect and process it")
                print()
                print(
                    "📂 This file has been moved to: data/daily_downloads/processed/non_target/"
                )
                print("=" * 80)

                # Archive the file but don't process it
                await self.archive_non_target_file(zip_path)
                return

            # Determine file type and process
            file_type = self.determine_file_type(zip_path)
            if file_type == "cards":
                success = await self.extract_daily_race_cards(zip_path)
                if success:
                    self.required_files_per_day["cards"] = True
                    logger.info(f"✅ Cards received for {self.current_target_date}")

            elif file_type == "results":
                success = await self.extract_daily_results(zip_path)
                if success:
                    self.required_files_per_day["results"] = True
                    logger.info(f"✅ Results received for {self.current_target_date}")

            else:
                logger.warning(f"⚠️ Unknown file type: {zip_path.name}")
                return

            # Check if day is complete
            await self.check_daily_completion()

        except Exception as e:
            logger.error(f"❌ Error processing daily ZIP file {zip_path}: {e}")

    def is_file_for_target_date(self, zip_path: Path) -> bool:
        """Check if file matches the current target date"""
        filename = zip_path.name.lower()
        target_date = self.current_target_date

        # Check for date patterns in filename
        date_patterns = [
            target_date,  # 2025-08-23
            target_date.replace("-", ""),  # 20250823
            target_date.replace("-", "_"),  # 2025_08_23
            target_date.replace("-", "/"),  # 2025/08/23
        ]

        # Also check for "today" if target is today
        if target_date == datetime.now().strftime("%Y-%m-%d"):
            date_patterns.extend(["today", "current"])

        return any(pattern in filename for pattern in date_patterns)

    def determine_file_type(self, zip_path: Path) -> str:
        """Determine if file is cards or results"""
        filename = zip_path.name.lower()

        card_keywords = ["racecard", "card", "meeting"]
        result_keywords = ["result", "outcome", "winner"]

        if any(keyword in filename for keyword in card_keywords):
            return "cards"
        elif any(keyword in filename for keyword in result_keywords):
            return "results"
        else:
            return "unknown"

    def get_expected_filename(self, file_type: str) -> str:
        """Get the expected filename for a given file type and current target date"""
        if file_type == "cards":
            return f"racecards_{self.current_target_date}.zip"
        elif file_type == "results":
            return f"results_{self.current_target_date}.zip"
        else:
            return f"unknown_{self.current_target_date}.zip"

    async def extract_daily_race_cards(self, zip_path: Path) -> bool:
        """Extract race cards for current target date"""
        try:
            logger.info(
                f"📋 Extracting cards for {self.current_target_date}: {zip_path.name}"
            )

            # Create CSV backup first (if backup integration is available)
            if self.backup_integrator:
                try:
                    backup_result = self.backup_integrator.process_download_with_backup(
                        zip_path, "cards", self.current_target_date, automated=True
                    )
                    if backup_result.get("success", False):
                        logger.info(
                            f"✅ CSV backup created: {backup_result.get('backup_result', {}).get('archive_name', 'Unknown')}"
                        )
                    else:
                        logger.warning(
                            f"⚠️ CSV backup failed: {backup_result.get('errors', [])}"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ CSV backup integration error: {e}")

            # Create date-specific directory
            target_cards_dir = self.cards_dir / self.current_target_date
            if target_cards_dir.exists():
                shutil.rmtree(target_cards_dir)
            target_cards_dir.mkdir(parents=True, exist_ok=True)

            # Extract files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_cards_dir)

            # Validate data
            if await self.validate_cards_data(target_cards_dir):
                logger.info(f"✅ Cards validated for {self.current_target_date}")
                await self.archive_processed_file(zip_path, "cards")
                return True
            else:
                logger.error(f"❌ Invalid cards data for {self.current_target_date}")
                return False

        except Exception as e:
            logger.error(f"❌ Error extracting cards: {e}")
            return False

    async def extract_daily_results(self, zip_path: Path) -> bool:
        """Extract results for current target date"""
        try:
            logger.info(
                f"🏁 Extracting results for {self.current_target_date}: {zip_path.name}"
            )

            # Create CSV backup first (if backup integration is available)
            if self.backup_integrator:
                try:
                    backup_result = self.backup_integrator.process_download_with_backup(
                        zip_path, "results", self.current_target_date, automated=True
                    )
                    if backup_result.get("success", False):
                        archive_name = backup_result.get("backup_result", {}).get(
                            "archive_name", "Unknown"
                        )
                        logger.info(f"✅ CSV backup created: {archive_name}")
                    else:
                        logger.warning(
                            f"⚠️ CSV backup failed: {backup_result.get('errors', [])}"
                        )
                except Exception as e:
                    logger.warning(f"⚠️ CSV backup integration error: {e}")

            # Create date-specific directory
            target_results_dir = self.results_dir / self.current_target_date
            if target_results_dir.exists():
                shutil.rmtree(target_results_dir)
            target_results_dir.mkdir(parents=True, exist_ok=True)

            # Extract files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(target_results_dir)

            # Validate data
            if await self.validate_results_data(target_results_dir):
                logger.info(f"✅ Results validated for {self.current_target_date}")
                await self.archive_processed_file(zip_path, "results")
                return True
            else:
                logger.error(f"❌ Invalid results data for {self.current_target_date}")
                return False

        except Exception as e:
            logger.error(f"❌ Error extracting results: {e}")
            return False

    async def validate_cards_data(self, cards_dir: Path) -> bool:
        """Validate race cards data structure"""
        try:
            # Check for expected structure
            races_files = list((cards_dir / "races").glob("*.csv"))
            horses_files = list((cards_dir / "horses").glob("*.csv"))
            racecard_files = list((cards_dir / "racecard_details").glob("*.csv"))

            if not races_files:
                logger.error("No races.csv found in races/ directory")
                return False
            if not horses_files:
                logger.error("No horses.csv found in horses/ directory")
                return False
            if not racecard_files:
                logger.error(
                    "No racecard_details.csv found in racecard_details/ directory"
                )
                return False

            # Validate races.csv structure
            races_df = pd.read_csv(races_files[0])
            required_race_columns = ["race_id", "race_time", "course"]
            df_columns_lower = [col.lower() for col in races_df.columns]
            missing = []
            for required_col in required_race_columns:
                if required_col.lower() not in df_columns_lower:
                    missing.append(required_col)

            if missing:
                logger.error(f"Missing columns in races.csv: {missing}")
                logger.info(f"Available columns: {list(races_df.columns)}")
                return False

            # Validate horses.csv structure
            horses_df = pd.read_csv(horses_files[0])
            required_horse_columns = ["id", "name"]
            df_columns_lower = [col.lower() for col in horses_df.columns]
            missing = []
            for required_col in required_horse_columns:
                if required_col.lower() not in df_columns_lower:
                    missing.append(required_col)

            if missing:
                logger.error(f"Missing columns in horses.csv: {missing}")
                logger.info(f"Available columns: {list(horses_df.columns)}")
                return False

            # Validate racecard_details.csv structure
            racecard_df = pd.read_csv(racecard_files[0])
            required_racecard_columns = ["race_id", "horse_id"]
            df_columns_lower = [col.lower() for col in racecard_df.columns]
            missing = []
            for required_col in required_racecard_columns:
                if required_col.lower() not in df_columns_lower:
                    missing.append(required_col)

            if missing:
                logger.error(f"Missing columns in racecard_details.csv: {missing}")
                logger.info(f"Available columns: {list(racecard_df.columns)}")
                return False

            logger.info(
                f"✅ Cards validation passed: {len(races_df)} races, {len(horses_df)} horses, {len(racecard_df)} entries"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Cards validation failed: {e}")
            return False

    async def validate_results_data(self, results_dir: Path) -> bool:
        """Validate results data structure"""
        try:
            # Look for CSV or HTML files
            csv_files = list(results_dir.rglob("*.csv"))
            html_files = list(results_dir.rglob("*.html"))

            if not csv_files and not html_files:
                logger.error("No CSV or HTML files found in results data")
                return False

            logger.info(
                f"✅ Results validation passed: {len(csv_files)} CSV, {len(html_files)} HTML files"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Results validation failed: {e}")
            return False

    async def check_daily_completion(self):
        """Check if current day is complete and advance if needed"""
        cards_ready = self.required_files_per_day["cards"]
        results_ready = self.required_files_per_day["results"]

        logger.info(f"📊 Daily status for {self.current_target_date}:")
        logger.info(f"   📋 Cards: {'✅' if cards_ready else '⏳'}")
        logger.info(f"   🏁 Results: {'✅' if results_ready else '⏳'}")

        if cards_ready and results_ready:
            logger.info(f"🎉 All files received for {self.current_target_date}!")

            # Trigger pipeline processing
            await self.trigger_daily_pipeline()

            # Mark day as completed
            self.mark_day_completed(self.current_target_date)
        else:
            missing = []
            if not cards_ready:
                missing.append("race cards")
            if not results_ready:
                missing.append("results")

            logger.info(f"⏳ Still waiting for: {', '.join(missing)}")
            self.update_status_display()

    async def trigger_daily_pipeline(self):
        """Trigger processing pipeline for completed day"""
        try:
            logger.info(f"🚀 Triggering pipeline for {self.current_target_date}")

            # Future integration points:
            # - Database upload
            # - ML model retraining
            # - API endpoint updates
            # - Notification sending

            logger.info(f"📊 Pipeline triggered for {self.current_target_date}")

        except Exception as e:
            logger.error(f"❌ Pipeline trigger failed: {e}")

    async def archive_processed_file(self, zip_path: Path, file_type: str):
        """Archive processed file with date and type"""
        try:
            archive_dir = self.processed_dir / self.current_target_date
            archive_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%H%M%S")
            new_name = (
                f"{file_type}_{self.current_target_date}_{timestamp}_{zip_path.name}"
            )
            archive_path = archive_dir / new_name

            shutil.move(str(zip_path), str(archive_path))
            logger.info(f"📁 Archived: {new_name}")

        except Exception as e:
            logger.error(f"❌ Failed to archive {zip_path}: {e}")

    async def archive_non_target_file(self, zip_path: Path):
        """Archive file that doesn't match target date"""
        try:
            archive_dir = self.processed_dir / "non_target"
            archive_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_name = f"non_target_{timestamp}_{zip_path.name}"
            archive_path = archive_dir / new_name

            shutil.move(str(zip_path), str(archive_path))
            logger.info(f"📁 Archived non-target file: {new_name}")

        except Exception as e:
            logger.error(f"❌ Failed to archive non-target file {zip_path}: {e}")

    def update_status_display(self):
        """Update status display and web app"""
        try:
            status = {
                "watcher_status": "active",
                "target_date": self.current_target_date,
                "files_needed": {
                    "cards": not self.required_files_per_day["cards"],
                    "results": not self.required_files_per_day["results"],
                },
                "completed_days": list(self.completed_days),
                "total_processed": len(self.completed_days),
                "last_updated": datetime.now().isoformat(),
                "instructions": self.get_daily_instructions(),
            }

            status_file = self.base_path / "data/daily_watcher_status.json"
            with open(status_file, "w") as f:
                json.dump(status, f, indent=2)

            logger.info(f"📊 Status updated for {self.current_target_date}")

        except Exception as e:
            logger.error(f"❌ Error updating status: {e}")

    def get_daily_instructions(self) -> Dict[str, Any]:
        """Get instructions for current target date"""
        cards_needed = not self.required_files_per_day["cards"]
        results_needed = not self.required_files_per_day["results"]

        instructions = {
            "target_date": self.current_target_date,
            "files_needed": [],
            "watch_directory": str(self.watch_dir),
            "file_naming": {
                "cards": f"racecards_{self.current_target_date}.zip",
                "results": f"results_{self.current_target_date}.zip",
            },
        }

        if cards_needed:
            instructions["files_needed"].append(
                {
                    "type": "race_cards",
                    "description": f"Race cards for {self.current_target_date}",
                    "keywords": ["racecard", "card", "meeting"],
                }
            )

        if results_needed:
            instructions["files_needed"].append(
                {
                    "type": "results",
                    "description": f"Race results for {self.current_target_date}",
                    "keywords": ["result", "outcome", "winner"],
                }
            )

        return instructions


class DailyFileWatcherManager:
    """Manages the daily file watcher service"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = base_path
        self.watcher = DailyRacingFileWatcher(base_path)
        self.observer = Observer()
        self.running = False

    async def process_existing_files(self):
        """Process any existing ZIP files on startup"""
        logger.info("🔍 Checking for existing ZIP files...")

        watch_dir = Path(self.base_path) / "data/daily_downloads/manual_download"
        zip_files = list(watch_dir.glob("*.zip"))

        if not zip_files:
            logger.info("No existing ZIP files found")
            return

        logger.info(f"Found {len(zip_files)} existing ZIP files")

        for zip_file in zip_files:
            await self.watcher.process_daily_zip_file(zip_file)

    def start_watching(self):
        """Start the daily file watcher service"""
        watch_dir = str(Path(self.base_path) / "data/daily_downloads/manual_download")

        logger.info(f"🔍 Starting daily file watcher")
        logger.info(f"📂 Watching: {watch_dir}")
        logger.info(f"📅 Target date: {self.watcher.current_target_date}")

        self.observer.schedule(self.watcher, watch_dir, recursive=False)
        self.observer.start()
        self.running = True

        # Update initial status
        self.watcher.update_status_display()

        logger.info("✅ Daily file watcher started successfully")

    def stop_watching(self):
        """Stop the file watcher"""
        if self.running:
            logger.info("🛑 Stopping daily file watcher...")
            self.observer.stop()
            self.observer.join()
            self.running = False
            logger.info("✅ Daily file watcher stopped")

    async def run_continuous(self):
        """Run continuous monitoring"""
        try:
            while True:
                # Check if it's a new day and advance if needed
                current_date = datetime.now().strftime("%Y-%m-%d")
                if (
                    current_date != self.watcher.current_target_date
                    and current_date not in self.watcher.completed_days
                ):
                    logger.info(f"📅 New day detected: {current_date}")
                    self.watcher.current_target_date = current_date
                    self.watcher.required_files_per_day = {
                        "cards": False,
                        "results": False,
                    }
                    self.watcher.update_status_display()

                await asyncio.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("🛑 Keyboard interrupt received")
        except Exception as e:
            logger.error(f"❌ Error in continuous monitoring: {e}")
        finally:
            self.stop_watching()


async def main():
    """Main entry point for daily file watcher"""
    logger.info("🚀 Starting Daily Racing File Watcher v2.04")

    manager = DailyFileWatcherManager()

    try:
        # Process any existing files
        await manager.process_existing_files()

        # Start watching
        manager.start_watching()

        # Run continuous monitoring
        await manager.run_continuous()

    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
    finally:
        manager.stop_watching()


if __name__ == "__main__":
    asyncio.run(main())
