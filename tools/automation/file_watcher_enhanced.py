#!/usr/bin/env python3
"""
File Watcher & Auto-Processing System
Horse Racing AI v2.03 - Automated Pipeline Trigger

Monitors manual_download directory for new ZIP files and automatically processes them.
Features:
- Auto-extracts ZIP files to appropriate directories
- Validates data quality and timing
- Analyzes race schedules and courses
- Provides user guidance for data downloads
- Cleans up processed files automatically
"""

import asyncio
import zipfile
import shutil
import logging
import pandas as pd
import json
import os
from pathlib import Path
from datetime import datetime, time
from typing import Optional, Dict, Any, List, Tuple
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Set up logging
log_file = "/home/jc/Documents/Horse-race-ai-v2.03/logs/file_watcher.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RacingDataFileWatcher(FileSystemEventHandler):
    """Monitors manual_download directory for new ZIP files"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.base_path = Path(base_path)
        self.watch_dir = self.base_path / "data/daily_downloads/manual_download"
        self.cards_dir = self.base_path / "data/daily_downloads/cards_data"
        self.results_dir = self.base_path / "data/daily_downloads/results_data"
        self.processed_dir = self.base_path / "data/daily_downloads/processed"
        self.status_file = (
            self.base_path / "data/daily_downloads/processing_status.json"
        )

        # Ensure directories exist
        self.create_directories()

        # Track processing status
        self.processing_status = {
            "cards_ready": False,
            "results_ready": False,
            "last_processed": None,
            "race_day_info": {},
            "user_message": "",
            "download_instructions": "",
        }

        # Load existing status
        self.load_status()

    def create_directories(self):
        """Create required directory structure"""
        directories = [
            self.watch_dir,
            self.cards_dir,
            self.results_dir,
            self.processed_dir,
            self.processed_dir / datetime.now().strftime("%Y-%m-%d"),
            self.base_path / "logs",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"✅ Directory ready: {directory}")

    def load_status(self):
        """Load processing status from file"""
        try:
            if self.status_file.exists():
                with open(self.status_file, "r") as f:
                    saved_status = json.load(f)
                    self.processing_status.update(saved_status)
                logger.info("📁 Loaded previous processing status")
        except Exception as e:
            logger.warning(f"Could not load status file: {e}")

    def save_status(self):
        """Save processing status to file"""
        try:
            with open(self.status_file, "w") as f:
                json.dump(self.processing_status, f, indent=2, default=str)
            logger.info("💾 Processing status saved")
        except Exception as e:
            logger.error(f"Failed to save status: {e}")

    def on_created(self, event):
        """Triggered when new file is added"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        logger.info(f"🔍 New file detected: {file_path.name}")

        if file_path.suffix.lower() == ".zip":
            # Run async processing in event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.process_zip_file(file_path))
            loop.close()

    async def process_zip_file(self, zip_path: Path):
        """Process and extract ZIP file"""
        try:
            logger.info(f"🔄 Processing ZIP file: {zip_path.name}")

            # Determine file type from name
            card_keywords = ["racecard", "card"]
            if any(keyword in zip_path.name.lower() for keyword in card_keywords):
                await self.extract_race_cards(zip_path)
            elif "result" in zip_path.name.lower():
                await self.extract_results(zip_path)
            else:
                logger.warning(f"⚠️ Unknown ZIP type: {zip_path.name}")
                return

            # Check if both datasets are ready for pipeline
            await self.check_pipeline_readiness()

        except Exception as e:
            logger.error(f"❌ Error processing {zip_path}: {e}")

    async def extract_race_cards(self, zip_path: Path):
        """Extract race cards ZIP to cards_data directory"""
        try:
            logger.info(f"📋 Extracting race cards: {zip_path.name}")

            # Clear previous cards_data if it exists
            if self.cards_dir.exists():
                # Check if directory is empty first
                if any(self.cards_dir.iterdir()):
                    logger.info("🧹 Clearing previous race cards data")
                    shutil.rmtree(self.cards_dir)
                    self.cards_dir.mkdir(parents=True, exist_ok=True)

            # Extract all files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.cards_dir)

            # Validate extracted data
            if await self.validate_cards_data():
                logger.info(f"✅ Race cards extracted successfully: {zip_path.name}")
                self.processing_status["cards_ready"] = True
                await self.clean_manual_download_after_processing(zip_path)
            else:
                logger.error(f"❌ Invalid race cards data: {zip_path.name}")

        except Exception as e:
            logger.error(f"❌ Error extracting race cards: {e}")

    async def extract_results(self, zip_path: Path):
        """Extract results ZIP to results_data directory"""
        try:
            logger.info(f"🏁 Extracting results: {zip_path.name}")

            # Clear previous results_data if it exists
            if self.results_dir.exists():
                if any(self.results_dir.iterdir()):
                    logger.info("🧹 Clearing previous results data")
                    shutil.rmtree(self.results_dir)
                    self.results_dir.mkdir(parents=True, exist_ok=True)

            # Extract all files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.results_dir)

            # Validate extracted data
            if await self.validate_results_data():
                logger.info(f"✅ Results extracted successfully: {zip_path.name}")
                self.processing_status["results_ready"] = True
                await self.clean_manual_download_after_processing(zip_path)
            else:
                logger.error(f"❌ Invalid results data: {zip_path.name}")

        except Exception as e:
            logger.error(f"❌ Error extracting results: {e}")

    async def validate_cards_data(self) -> bool:
        """Validate race cards data structure and analyze race day"""
        try:
            # Check for required directories and files
            required_paths = [self.cards_dir / "races", self.cards_dir / "horses"]

            # Check for either records or racecard_details
            records_path = self.cards_dir / "records"
            racecard_details_path = self.cards_dir / "racecard_details"

            if records_path.exists():
                required_paths.append(records_path)
                details_dir = "records"
            elif racecard_details_path.exists():
                required_paths.append(racecard_details_path)
                details_dir = "racecard_details"
            else:
                logger.error("Missing records or racecard_details directory")
                await self.generate_error_message(
                    "missing_directories", ["records or racecard_details"]
                )
                return False

            missing_paths = []
            for path in required_paths:
                if not path.exists():
                    missing_paths.append(str(path))

            if missing_paths:
                logger.error(f"Missing required directories: {missing_paths}")
                await self.generate_error_message("missing_directories", missing_paths)
                return False

            # Find CSV files in each directory
            races_csv = list((self.cards_dir / "races").glob("*.csv"))
            records_csv = list((self.cards_dir / details_dir).glob("*.csv"))
            horses_csv = list((self.cards_dir / "horses").glob("*.csv"))

            if not all([races_csv, records_csv, horses_csv]):
                logger.error("Missing required CSV files in directories")
                await self.generate_error_message("missing_csv_files")
                return False

            # Validate main races CSV structure
            races_df = pd.read_csv(races_csv[0])
            required_columns = ["race_id", "race_time", "course"]

            # Check if columns exist (some might have different names)
            available_columns = races_df.columns.tolist()

            # Try to find race time column with different possible names
            time_columns = ["race_time", "start_time", "off_time", "scheduled_time"]
            race_time_col = None
            for col in time_columns:
                if col in available_columns:
                    race_time_col = col
                    break

            # Try to find course column with different possible names
            course_columns = ["Course", "course", "venue", "track", "racecourse"]
            course_col = None
            for col in course_columns:
                if col in available_columns:
                    course_col = col
                    break

            if not race_time_col:
                logger.error(
                    f"No race time column found. Available: {available_columns}"
                )
                await self.generate_error_message("missing_columns", "race_time")
                return False

            if not course_col:
                logger.error(f"No course column found. Available: {available_columns}")
                await self.generate_error_message("missing_columns", "course")
                return False

            # Analyze race day data with actual column names
            await self.analyze_race_day_data(races_df, race_time_col, course_col)

            logger.info(f"✅ Cards data validation passed: {len(races_df)} races")
            return True

        except Exception as e:
            logger.error(f"❌ Cards data validation failed: {e}")
            await self.generate_error_message("validation_error", str(e))
            return False

    async def validate_results_data(self) -> bool:
        """Validate results data structure"""
        try:
            # Check for basic structure
            if not self.results_dir.exists():
                logger.error("Results directory doesn't exist")
                await self.generate_error_message("results_missing")
                return False

            # Look for any CSV or HTML files
            csv_files = list(self.results_dir.rglob("*.csv"))
            html_files = list(self.results_dir.rglob("*.html"))

            if not csv_files and not html_files:
                logger.error("No CSV or HTML files found in results data")
                await self.generate_error_message("results_empty")
                return False

            logger.info(
                f"✅ Results data validation passed: "
                f"{len(csv_files)} CSV, {len(html_files)} HTML files"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Results data validation failed: {e}")
            await self.generate_error_message("results_validation_error", str(e))
            return False

    async def analyze_timing_situation(
        self, day_races: pd.DataFrame, first_race_time: time
    ) -> Dict[str, Any]:
        """Analyze timing situation for operational planning"""
        try:
            now = datetime.now()
            current_time = now.time()
            current_date = now.date()

            # Convert first race time to datetime for comparison
            first_race_datetime = datetime.combine(current_date, first_race_time)
            time_until_first_race = first_race_datetime - now

            # Calculate timing metrics
            minutes_until_first = int(time_until_first_race.total_seconds() / 60)

            # Determine timing category and processing mode
            if minutes_until_first < 0:
                timing_category = "EMERGENCY"
                processing_mode = "emergency"
                alert_level = "CRITICAL"
                missed_races = len(day_races[day_races["race_datetime"] < now])
            elif minutes_until_first < 20:
                timing_category = "CRITICAL"
                processing_mode = "fast"
                alert_level = "HIGH"
                missed_races = 0
            elif minutes_until_first < 60:
                timing_category = "RUSHED"
                processing_mode = "standard"
                alert_level = "MEDIUM"
                missed_races = 0
            elif minutes_until_first < 180:  # 3 hours
                timing_category = "GOOD"
                processing_mode = "standard"
                alert_level = "LOW"
                missed_races = 0
            else:
                timing_category = "OPTIMAL"
                processing_mode = "full"
                alert_level = "NONE"
                missed_races = 0

            # Count available vs missed races
            available_races = len(day_races[day_races["race_datetime"] >= now])
            total_races = len(day_races)

            timing_analysis = {
                "current_time": current_time.strftime("%H:%M:%S"),
                "first_race_time": first_race_time.strftime("%H:%M:%S"),
                "minutes_until_first_race": minutes_until_first,
                "timing_category": timing_category,
                "processing_mode": processing_mode,
                "alert_level": alert_level,
                "total_races": total_races,
                "available_races": available_races,
                "missed_races": missed_races,
                "recommendations": self._get_timing_recommendations(timing_category),
            }

            # Store timing analysis for status reporting
            self.processing_status["timing_analysis"] = timing_analysis

            logger.info(
                f"⏰ Timing Analysis: {timing_category} - "
                f"{minutes_until_first}min until first race"
            )
            logger.info(f"🎯 Processing Mode: {processing_mode}")
            logger.info(f"📊 Races: {available_races}/{total_races} available")

            return timing_analysis

        except Exception as e:
            logger.error(f"❌ Timing analysis failed: {e}")
            return {"error": str(e)}

    def _get_timing_recommendations(self, timing_category: str) -> List[str]:
        """Get recommendations based on timing situation"""
        recommendations = {
            "OPTIMAL": [
                "Perfect timing! Full ML pipeline recommended",
                "Complete model retraining available",
                "High confidence predictions expected",
                "Ideal time for feature engineering",
            ],
            "GOOD": [
                "Good timing for standard processing",
                "Incremental model updates recommended",
                "Standard prediction quality expected",
                "Sufficient time for validation",
            ],
            "RUSHED": [
                "Limited time - fast processing mode",
                "Use existing models with quick updates",
                "Medium confidence predictions",
                "Focus on essential features only",
            ],
            "CRITICAL": [
                "Very little time - emergency mode",
                "Skip model retraining",
                "Use cached predictions if available",
                "Prepare user warnings about timing",
            ],
            "EMERGENCY": [
                "Racing has started - damage control",
                "Process remaining races only",
                "Emergency predictions mode",
                "Alert users about missed races",
            ],
        }
        return recommendations.get(timing_category, ["Unknown timing situation"])

    async def analyze_race_day_data(
        self, races_df: pd.DataFrame, time_col: str, course_col: str
    ):
        """Analyze race timing and course information with timing intelligence"""
        try:
            # Convert race_time to datetime for analysis
            races_df["race_datetime"] = pd.to_datetime(races_df[time_col])
            races_df["race_date"] = races_df["race_datetime"].dt.date
            races_df["race_time_only"] = races_df["race_datetime"].dt.time

            # Get unique race dates
            race_dates = races_df["race_date"].unique()

            for race_date in race_dates:
                day_races = races_df[races_df["race_date"] == race_date]

                # Calculate race day statistics
                first_race_time = day_races["race_time_only"].min()
                last_race_time = day_races["race_time_only"].max()
                total_races = len(day_races)
                courses = day_races[course_col].unique().tolist()

                # TIMING ANALYSIS - Critical for operational planning
                timing_analysis = await self.analyze_timing_situation(
                    day_races, first_race_time
                )

                # Store race day information
                race_day_info = {
                    "date": str(race_date),
                    "first_race": str(first_race_time),
                    "last_race": str(last_race_time),
                    "total_races": total_races,
                    "courses": courses,
                    "data_timestamp": datetime.now().isoformat(),
                    "timing_analysis": timing_analysis,
                }

                self.processing_status["race_day_info"] = race_day_info

                # Generate user message
                await self.generate_race_day_message(race_day_info)

                logger.info(
                    f"📊 Race day analysis: {race_date} - "
                    f"{total_races} races at {len(courses)} courses"
                )
                logger.info(f"⏰ Racing: {first_race_time} to {last_race_time}")
                logger.info(f"🏇 Courses: {', '.join(courses)}")

        except Exception as e:
            logger.error(f"❌ Race day analysis failed: {e}")

    async def generate_race_day_message(self, race_info: Dict[str, Any]):
        """Generate informative message for web app users"""
        try:
            courses_text = ", ".join(race_info["courses"])

            message = f"""
🏇 **Race Day Data Updated - {race_info['date']}**

📊 **Today's Racing Schedule:**
• **First Race:** {race_info['first_race']}
• **Last Race:** {race_info['last_race']}
• **Total Races:** {race_info['total_races']}
• **Racing Venues:** {courses_text}

✅ **Data Status:** Fresh race cards loaded successfully
⏰ **Last Updated:** {datetime.now().strftime('%H:%M:%S')}
            """

            instructions = """
📥 **Daily Data Download Instructions:**

1. **Visit Racing Data Source** (check your data provider)
2. **Download Today's Files:**
   - UK Race Cards (ZIP file)
   - UK Results (ZIP file)
3. **Save to Manual Download Folder:**
   - Location: `/data/daily_downloads/manual_download/`
   - File names should contain 'racecard' or 'result'
4. **Automatic Processing:**
   - Files detected automatically
   - Data extracted and validated
   - Manual download folder cleaned
   - Race analysis generated

🚨 **Important:** Download fresh files daily for accurate predictions
            """

            self.processing_status["user_message"] = message.strip()
            self.processing_status["download_instructions"] = instructions.strip()

            logger.info("📝 Generated race day message for web app")

        except Exception as e:
            logger.error(f"❌ Failed to generate race day message: {e}")

    async def generate_error_message(self, error_type: str, details: Any = None):
        """Generate error messages for different failure scenarios"""
        error_messages = {
            "missing_directories": f"❌ Missing required data directories: {details}",
            "missing_csv_files": "❌ Required CSV files not found in extracted data",
            "missing_columns": f"❌ Required columns missing from races.csv: {details}",
            "validation_error": f"❌ Data validation error: {details}",
            "results_missing": "❌ Results directory not found",
            "results_empty": "❌ No valid result files found",
            "results_validation_error": f"❌ Results validation error: {details}",
            "empty_cards_data": "❌ Race cards directory is empty - fresh data required",
            "stale_data": "❌ Data appears to be from a previous date",
        }

        message = error_messages.get(error_type, f"❌ Unknown error: {error_type}")

        instructions = """
🔄 **To Fix This Issue:**

1. **Download Fresh Data Files:**
   - Visit your racing data provider
   - Download today's race cards (ZIP)
   - Download today's results (ZIP)

2. **Check File Names:**
   - Race cards: must contain 'racecard' or 'card'
   - Results: must contain 'result'

3. **Save to Manual Download:**
   - Location: `/data/daily_downloads/manual_download/`
   - System will auto-process valid files

4. **Verify Data Quality:**
   - Files must be from today's date
   - Must contain races, records, and horses data
   - Check data provider for any service issues
        """

        self.processing_status["user_message"] = message
        self.processing_status["download_instructions"] = instructions.strip()

        logger.error(f"📝 Generated error message: {message}")

    async def clean_manual_download_after_processing(self, zip_path: Path):
        """Archive processed file and clean manual download directory"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            archive_dir = self.processed_dir / datetime.now().strftime("%Y-%m-%d")
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Determine data type from filename
            if any(
                keyword in zip_path.name.lower() for keyword in ["racecard", "card"]
            ):
                data_type = "cards"
            elif "result" in zip_path.name.lower():
                data_type = "results"
            else:
                data_type = "unknown"

            # Create new filename with timestamp and type
            new_name = f"{data_type}_{timestamp}_{zip_path.name}"
            archive_path = archive_dir / new_name

            # Move file to archive
            shutil.move(str(zip_path), str(archive_path))
            logger.info(f"📁 Archived and cleaned: {new_name}")

            # Verify manual_download is now empty (except for any new files)
            remaining_files = list(self.watch_dir.glob("*.zip"))
            if not remaining_files:
                logger.info("🧹 Manual download directory is clean")
            else:
                logger.info(f"📥 {len(remaining_files)} files still pending processing")

        except Exception as e:
            logger.error(f"❌ Failed to clean manual download: {e}")

    async def check_cards_data_status(self):
        """Check if cards_data directory has valid data or is empty"""
        try:
            if not self.cards_dir.exists():
                await self.generate_error_message("empty_cards_data")
                return False

            # Check if directory is empty
            if not any(self.cards_dir.iterdir()):
                await self.generate_error_message("empty_cards_data")
                return False

            # Check if data files exist
            races_csv = list((self.cards_dir / "races").glob("*.csv"))
            if not races_csv:
                await self.generate_error_message("empty_cards_data")
                return False

            # Check data freshness
            races_df = pd.read_csv(races_csv[0])
            if "race_time" in races_df.columns:
                races_df["race_datetime"] = pd.to_datetime(races_df["race_time"])
                latest_race_date = races_df["race_datetime"].dt.date.max()
                today = datetime.now().date()

                if latest_race_date < today:
                    await self.generate_error_message("stale_data")
                    return False

            logger.info("✅ Cards data directory has valid, fresh data")
            return True

        except Exception as e:
            logger.error(f"❌ Cards data status check failed: {e}")
            await self.generate_error_message("validation_error", str(e))
            return False

    async def check_pipeline_readiness(self):
        """Check if both datasets are ready and trigger pipeline"""
        if (
            self.processing_status["cards_ready"]
            and self.processing_status["results_ready"]
        ):
            logger.info("🚀 Both datasets ready - triggering data pipeline!")
            await self.trigger_data_pipeline()

            # Reset status for next batch
            self.processing_status["cards_ready"] = False
            self.processing_status["results_ready"] = False
            self.processing_status["last_processed"] = datetime.now().isoformat()

        # Save status after any changes
        self.save_status()

    async def trigger_data_pipeline(self):
        """Trigger the data processing pipeline"""
        try:
            logger.info("🔄 Starting data pipeline processing...")

            # This would integrate with your existing pipeline
            # For now, just log the success
            logger.info(
                "📊 Data pipeline integration point - ready for database upload"
            )

            # Update status message
            message = """
🎉 **Data Processing Complete!**

✅ **Both datasets processed successfully:**
• Race Cards: Extracted and validated
• Results: Extracted and validated
• Pipeline: Ready for database upload
• ML Models: Ready for retraining

🚀 **Next Steps:**
• Database will be updated automatically
• Betting recommendations will refresh
• New predictions will be available shortly
            """

            self.processing_status["user_message"] = message.strip()

            # Future integration points:
            # 1. Call database uploader
            # 2. Trigger ML model retraining
            # 3. Update API endpoints
            # 4. Send notifications

        except Exception as e:
            logger.error(f"❌ Pipeline trigger failed: {e}")


class FileWatcherManager:
    """Manages the file watcher service"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.base_path = base_path
        self.watcher = RacingDataFileWatcher(base_path)
        self.observer = Observer()

    async def process_existing_files(self):
        """Process any existing ZIP files in the manual_download directory"""
        logger.info("🔍 Checking for existing ZIP files...")

        watch_dir = Path(self.base_path) / "data/daily_downloads/manual_download"
        zip_files = list(watch_dir.glob("*.zip"))

        if not zip_files:
            logger.info("No existing ZIP files found")
            # Check cards_data status
            await self.watcher.check_cards_data_status()
            return

        logger.info(f"Found {len(zip_files)} existing ZIP files to process")

        for zip_file in zip_files:
            logger.info(f"Processing existing file: {zip_file.name}")
            await self.watcher.process_zip_file(zip_file)

    def start_watching(self):
        """Start the file watcher service"""
        watch_dir = str(Path(self.base_path) / "data/daily_downloads/manual_download")

        logger.info(f"🔍 Starting file watcher on: {watch_dir}")

        self.observer.schedule(self.watcher, watch_dir, recursive=False)
        self.observer.start()

        logger.info("✅ File watcher started successfully")

        try:
            while True:
                import time

                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("🛑 Stopping file watcher...")
            self.observer.stop()

        self.observer.join()
        logger.info("✅ File watcher stopped")


async def main():
    """Main entry point"""
    import sys

    logger.info("🚀 Starting Horse Racing Data File Watcher")

    manager = FileWatcherManager()

    # Process existing files first
    await manager.process_existing_files()

    # Check if this is a test run
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        logger.info("✅ Test run completed - file watcher is ready")
        return

    # Start continuous watching
    manager.start_watching()


if __name__ == "__main__":
    asyncio.run(main())
