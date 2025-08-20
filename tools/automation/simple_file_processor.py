#!/usr/bin/env python3
"""
Simple File Processor - Process existing ZIP files
Horse Racing AI v2.03 - Manual File Processing

Processes existing ZIP files in manual_download directory without watchdog.
"""

import asyncio
import zipfile
import shutil
import logging
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any

# Set up logging
log_file = "/home/jc/Documents/Horse-race-ai-v2.03/logs/file_processor.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(log_file), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SimpleFileProcessor:
    """Simple file processor for existing ZIP files"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.03"):
        self.base_path = Path(base_path)
        self.watch_dir = self.base_path / "data/daily_downloads/manual_download"
        self.cards_dir = self.base_path / "data/daily_downloads/cards_data"
        self.results_dir = self.base_path / "data/daily_downloads/results_data"
        self.processed_dir = self.base_path / "data/daily_downloads/processed"

        # Ensure directories exist
        self.create_directories()

        # Track processing status
        self.processing_status = {
            "cards_ready": False,
            "results_ready": False,
            "race_summary": {},
        }

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

    async def process_existing_files(self):
        """Process any existing ZIP files in the manual_download directory"""
        logger.info("🔍 Checking for existing ZIP files...")

        zip_files = list(self.watch_dir.glob("*.zip"))

        if not zip_files:
            logger.info("📁 No ZIP files found in manual_download directory")
            logger.info(f"📂 Directory: {self.watch_dir}")
            self.generate_user_instructions()
            return

        logger.info(f"Found {len(zip_files)} ZIP files to process")

        for zip_file in zip_files:
            logger.info(f"🔄 Processing: {zip_file.name}")
            await self.process_zip_file(zip_file)

        # Check if we can analyze the data
        await self.check_and_analyze_data()

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

        except Exception as e:
            logger.error(f"❌ Error processing {zip_path}: {e}")

    async def extract_race_cards(self, zip_path: Path):
        """Extract race cards ZIP to cards_data directory"""
        try:
            logger.info(f"📋 Extracting race cards: {zip_path.name}")

            # Clear previous cards_data
            if self.cards_dir.exists():
                shutil.rmtree(self.cards_dir)
            self.cards_dir.mkdir(parents=True, exist_ok=True)

            # Extract all files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.cards_dir)

            # Validate extracted data
            if await self.validate_cards_data():
                logger.info(f"✅ Race cards extracted successfully: {zip_path.name}")
                self.processing_status["cards_ready"] = True
                await self.archive_processed_file(zip_path, "cards")
            else:
                logger.error(f"❌ Invalid race cards data: {zip_path.name}")

        except Exception as e:
            logger.error(f"❌ Error extracting race cards: {e}")

    async def extract_results(self, zip_path: Path):
        """Extract results ZIP to results_data directory"""
        try:
            logger.info(f"🏁 Extracting results: {zip_path.name}")

            # Clear previous results_data
            if self.results_dir.exists():
                shutil.rmtree(self.results_dir)
            self.results_dir.mkdir(parents=True, exist_ok=True)

            # Extract all files
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(self.results_dir)

            # Validate extracted data
            if await self.validate_results_data():
                logger.info(f"✅ Results extracted successfully: {zip_path.name}")
                self.processing_status["results_ready"] = True
                await self.archive_processed_file(zip_path, "results")
            else:
                logger.error(f"❌ Invalid results data: {zip_path.name}")

        except Exception as e:
            logger.error(f"❌ Error extracting results: {e}")

    async def validate_cards_data(self) -> bool:
        """Validate race cards data structure"""
        try:
            # Check for required directories and files
            required_paths = [
                self.cards_dir / "races",
                self.cards_dir / "records",
                self.cards_dir / "horses",
            ]

            missing_paths = []
            for path in required_paths:
                if not path.exists():
                    missing_paths.append(str(path))

            if missing_paths:
                logger.error(f"Missing required directories: {missing_paths}")
                return False

            # Find CSV files in each directory
            races_csv = list((self.cards_dir / "races").glob("*.csv"))
            records_csv = list((self.cards_dir / "records").glob("*.csv"))
            horses_csv = list((self.cards_dir / "horses").glob("*.csv"))

            if not all([races_csv, records_csv, horses_csv]):
                logger.error("Missing required CSV files in directories")
                return False

            # Validate main races CSV structure
            races_df = pd.read_csv(races_csv[0])
            required_columns = ["race_id", "race_time", "course"]

            missing_columns = [
                col for col in required_columns if col not in races_df.columns
            ]
            if missing_columns:
                logger.error(
                    f"Missing required columns in races.csv: " f"{missing_columns}"
                )
                return False

            # Analyze race day data
            await self.analyze_race_day_data(races_df)

            logger.info(f"✅ Cards data validation passed: {len(races_df)} races")
            return True

        except Exception as e:
            logger.error(f"❌ Cards data validation failed: {e}")
            return False

    async def validate_results_data(self) -> bool:
        """Validate results data structure"""
        try:
            # Check for basic structure
            if not self.results_dir.exists():
                logger.error("Results directory doesn't exist")
                return False

            # Look for any CSV or HTML files
            csv_files = list(self.results_dir.rglob("*.csv"))
            html_files = list(self.results_dir.rglob("*.html"))

            if not csv_files and not html_files:
                logger.error("No CSV or HTML files found in results data")
                return False

            logger.info(
                f"✅ Results data validation passed: "
                f"{len(csv_files)} CSV, {len(html_files)} HTML files"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Results data validation failed: {e}")
            return False

    async def analyze_race_day_data(self, races_df: pd.DataFrame):
        """Analyze race timing and course data for the day"""
        try:
            # Convert race_time to datetime
            races_df["race_datetime"] = pd.to_datetime(races_df["race_time"])

            # Get race day information
            race_date = races_df["race_datetime"].dt.date.iloc[0]
            first_race = races_df["race_datetime"].min()
            last_race = races_df["race_datetime"].max()
            total_races = len(races_df)

            # Get unique courses
            courses = races_df["course"].unique().tolist()

            # Store race summary
            self.processing_status["race_summary"] = {
                "date": str(race_date),
                "first_race_time": first_race.strftime("%H:%M"),
                "last_race_time": last_race.strftime("%H:%M"),
                "total_races": total_races,
                "courses": courses,
                "file_processed_at": datetime.now().isoformat(),
            }

            logger.info(f"📅 Race Day Analysis: {race_date}")
            logger.info(f"🏁 First Race: {first_race.strftime('%H:%M')}")
            logger.info(f"🏁 Last Race: {last_race.strftime('%H:%M')}")
            logger.info(f"🏇 Total Races: {total_races}")
            logger.info(f"🏟️ Courses: {', '.join(courses)}")

            # Generate web app status message
            await self.update_web_app_status()

        except Exception as e:
            logger.error(f"❌ Error analyzing race day data: {e}")

    async def update_web_app_status(self):
        """Update web app with current race day status and instructions"""
        try:
            summary = self.processing_status["race_summary"]

            # Create status message for web app
            status_message = {
                "status": "data_ready",
                "message": f"✅ Race data loaded for {summary['date']}",
                "details": {
                    "races_today": summary["total_races"],
                    "first_race": summary["first_race_time"],
                    "last_race": summary["last_race_time"],
                    "courses": summary["courses"],
                    "last_updated": summary["file_processed_at"],
                },
                "instructions": self.get_download_instructions(),
            }

            # Save status to file for web app to read
            status_file = self.base_path / "data/race_day_status.json"
            with open(status_file, "w") as f:
                json.dump(status_message, f, indent=2)

            logger.info(f"📊 Web app status updated: {status_file}")

        except Exception as e:
            logger.error(f"❌ Error updating web app status: {e}")

    def get_download_instructions(self) -> dict:
        """Generate download instructions for users"""
        return {
            "title": "Daily Race Data Download",
            "steps": [
                "1. Visit the Horse Racing data source",
                "2. Download today's race cards ZIP file",
                "3. Download today's results ZIP file",
                "4. Save both files to: data/daily_downloads/manual_download/",
                "5. Run: python tools/automation/simple_file_processor.py",
            ],
            "file_patterns": {
                "race_cards": "uk-racecards-*.zip",
                "results": "uk-results-*.zip",
            },
            "watch_directory": str(self.watch_dir),
            "notes": [
                "ZIP files are automatically deleted after processing",
                "Extracted data is validated before use",
                "System shows error if no race data available",
            ],
        }

    def generate_user_instructions(self):
        """Generate detailed user instructions when data is missing"""
        logger.info("📋 SYSTEM SETUP REQUIRED:")
        logger.info("=" * 60)
        logger.info("1. Download Race Cards:")
        logger.info("   - Visit horse racing data source")
        logger.info("   - Download today's race cards ZIP")
        logger.info(f"   - Save to: {self.watch_dir}")
        logger.info("")
        logger.info("2. Download Results:")
        logger.info("   - Download today's results ZIP")
        logger.info(f"   - Save to: {self.watch_dir}")
        logger.info("")
        logger.info("3. File Processing:")
        logger.info("   - Run: python tools/automation/simple_file_processor.py")
        logger.info("   - Files will be auto-extracted")
        logger.info("   - Original ZIP files moved to processed folder")
        logger.info("   - Race data analyzed and status updated")
        logger.info("")
        logger.info("4. System Status:")
        logger.info("   - Check data/race_day_status.json")
        logger.info("   - Web app shows current race information")
        logger.info("=" * 60)

    async def archive_processed_file(self, zip_path: Path, data_type: str):
        """Archive processed ZIP file with timestamp"""
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            archive_dir = self.processed_dir / timestamp
            archive_dir.mkdir(parents=True, exist_ok=True)

            # Create new filename with data type
            new_name = f"{data_type}_{timestamp}_{zip_path.name}"
            archive_path = archive_dir / new_name

            # Move file to archive
            shutil.move(str(zip_path), str(archive_path))
            logger.info(f"📁 Archived: {new_name}")

        except Exception as e:
            logger.error(f"❌ Failed to archive {zip_path}: {e}")

    async def check_and_analyze_data(self):
        """Check if we have data and analyze it"""
        # Check if cards_data has content
        if self.cards_dir.exists():
            csv_files = list(self.cards_dir.rglob("*.csv"))
            if csv_files:
                logger.info(f"📊 Found {len(csv_files)} CSV files in cards_data")

                # Try to analyze existing data
                races_csv = list((self.cards_dir / "races").glob("*.csv"))
                if races_csv:
                    try:
                        races_df = pd.read_csv(races_csv[0])
                        await self.analyze_race_day_data(races_df)
                    except Exception as e:
                        logger.error(f"❌ Error analyzing existing data: {e}")
            else:
                logger.warning("⚠️ cards_data directory exists but is empty")
        else:
            logger.warning("⚠️ No cards_data directory found")

        # Clean manual_download directory
        await self.clean_manual_download_dir()

    async def clean_manual_download_dir(self):
        """Clean manual_download directory back to empty default state"""
        try:
            remaining_files = list(self.watch_dir.glob("*"))
            if remaining_files:
                for file_path in remaining_files:
                    if file_path.is_file():
                        file_path.unlink()
                        logger.info(f"🗑️ Cleaned: {file_path.name}")

                logger.info("✅ Manual download directory reset to empty default")
            else:
                logger.info("✅ Manual download directory already empty")

        except Exception as e:
            logger.error(f"❌ Error cleaning manual download directory: {e}")


async def main():
    """Main entry point"""
    logger.info("🚀 Starting Horse Racing Data File Processor")

    processor = SimpleFileProcessor()

    # Process existing files
    await processor.process_existing_files()

    logger.info("✅ File processing completed")


if __name__ == "__main__":
    asyncio.run(main())
