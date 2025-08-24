#!/usr/bin/env python3
"""
🗓️ Enhanced Date & Race Validation Script
==========================================

Enhanced validation for horse racing data downloads with comprehensive date checking:
- Compare today's date vs downloaded file dates
- Extract first and last race times
- Validate data freshness and accuracy
- Warn user before pipeline processing if dates are wrong
- Handle zip file extraction and CSV parsing

Author: AI Assistant
Date: August 24, 2025
"""

import csv
import json
import logging
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import tempfile
import shutil

import pandas as pd

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DateValidationError(Exception):
    """Custom exception for date validation failures"""

    pass


class EnhancedDateValidator:
    """Enhanced validation for horse racing data with comprehensive date checking"""

    def __init__(self, data_dir: Path = Path("data/daily_downloads")):
        self.data_dir = Path(data_dir)
        self.today = datetime.now().date()
        self.validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "today_date": str(self.today),
            "data_directory": str(self.data_dir),
            "files_analyzed": [],
            "date_issues": [],
            "race_times": {},
            "warnings": [],
            "errors": [],
            "summary": {},
            "pipeline_recommendation": "proceed",  # proceed, warning, stop
        }

    def validate_all_downloads(self) -> Dict:
        """
        Comprehensive validation of all downloaded data files

        Returns:
            Dict containing detailed validation results and recommendations
        """
        logger.info("🔍 Starting enhanced date validation...")

        try:
            # Check processed files
            self._validate_processed_files()

            # Check raw download files
            self._validate_raw_downloads()

            # Generate final recommendations
            self._generate_recommendations()

            # Display summary to user
            self._display_user_summary()

            logger.info("✅ Enhanced date validation completed")

        except Exception as e:
            self.validation_results["errors"].append(f"Validation failed: {str(e)}")
            logger.error(f"❌ Enhanced date validation failed: {e}")

        return self.validation_results

    def _validate_processed_files(self) -> None:
        """Validate files in the processed directory"""
        processed_dir = self.data_dir / "processed"

        if not processed_dir.exists():
            logger.warning("⚠️ No processed directory found")
            return

        # Look for today's and yesterday's processed files
        for date_dir in processed_dir.iterdir():
            if date_dir.is_dir() and date_dir.name.startswith("20"):
                try:
                    file_date = datetime.strptime(date_dir.name, "%Y-%m-%d").date()
                    self._validate_date_directory(date_dir, file_date)
                except ValueError:
                    logger.warning(f"⚠️ Invalid date directory format: {date_dir.name}")

    def _validate_raw_downloads(self) -> None:
        """Validate raw download files in results_data and cards_data"""
        # Check results data
        results_dir = self.data_dir / "results_data"
        if results_dir.exists():
            self._validate_data_directory(results_dir, "results")

        # Check cards data
        cards_dir = self.data_dir / "cards_data"
        if cards_dir.exists():
            self._validate_data_directory(cards_dir, "cards")

    def _validate_date_directory(self, date_dir: Path, file_date: date) -> None:
        """Validate a specific date directory and its files"""
        logger.info(f"📅 Analyzing date directory: {date_dir.name}")

        date_analysis = {
            "directory": str(date_dir),
            "file_date": str(file_date),
            "days_difference": (self.today - file_date).days,
            "is_today": file_date == self.today,
            "is_yesterday": file_date == (self.today - timedelta(days=1)),
            "files": [],
            "race_times": {},
            "issues": [],
        }

        # Check if date is appropriate
        if date_analysis["days_difference"] > 2:
            days_diff = date_analysis["days_difference"]
            date_analysis["issues"].append(f"Data is {days_diff} days old")
            self.validation_results["date_issues"].append(
                f"Stale data found: {file_date} is {days_diff} days old"
            )

        # Analyze zip files in this directory
        for zip_file in date_dir.glob("*.zip"):
            self._analyze_zip_file(zip_file, date_analysis)

        self.validation_results["files_analyzed"].append(date_analysis)

    def _validate_data_directory(self, data_dir: Path, data_type: str) -> None:
        """Validate a data directory (results_data or cards_data)"""
        logger.info(f"📁 Analyzing {data_type} directory: {data_dir}")

        # Check for CSV files directly
        races_csv = data_dir / "races" / "races.csv"
        if races_csv.exists():
            self._analyze_csv_file(races_csv, data_type, "direct")

        # Check for date subdirectories
        for item in data_dir.iterdir():
            if item.is_dir() and item.name.startswith("20"):
                try:
                    file_date = datetime.strptime(item.name, "%Y-%m-%d").date()
                    self._validate_date_directory(item, file_date)
                except ValueError:
                    continue

    def _analyze_zip_file(self, zip_path: Path, date_analysis: Dict) -> None:
        """Extract and analyze a zip file for date and race time information"""
        logger.info(f"📦 Analyzing zip file: {zip_path.name}")

        file_info = {
            "filename": zip_path.name,
            "size": zip_path.stat().st_size,
            "dates_found": [],
            "race_times": [],
            "issues": [],
        }

        # Create temporary directory for extraction
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(temp_dir)

                # Look for CSV files in extracted content
                temp_path = Path(temp_dir)
                for csv_file in temp_path.rglob("*.csv"):
                    if "races" in csv_file.name.lower():
                        self._analyze_csv_content(csv_file, file_info)

            except Exception as e:
                file_info["issues"].append(f"Failed to extract zip: {e}")
                logger.error(f"❌ Failed to analyze {zip_path.name}: {e}")

        date_analysis["files"].append(file_info)

    def _analyze_csv_file(self, csv_path: Path, data_type: str, source: str) -> None:
        """Analyze a CSV file directly"""
        logger.info(f"📄 Analyzing CSV file: {csv_path}")

        file_info = {
            "filename": csv_path.name,
            "data_type": data_type,
            "source": source,
            "size": csv_path.stat().st_size,
            "dates_found": [],
            "race_times": [],
            "issues": [],
        }

        self._analyze_csv_content(csv_path, file_info)

        # Add to validation results
        if "files_analyzed" not in self.validation_results:
            self.validation_results["files_analyzed"] = []

        # Create a simple analysis entry for direct CSV files
        csv_analysis = {
            "directory": str(csv_path.parent),
            "file_date": "unknown",
            "files": [file_info],
            "race_times": file_info["race_times"],
            "issues": file_info["issues"],
        }

        self.validation_results["files_analyzed"].append(csv_analysis)

    def _analyze_csv_content(self, csv_path: Path, file_info: Dict) -> None:
        """Analyze the content of a CSV file for dates and race times"""
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"📊 CSV contains {len(df)} records")

            # Extract dates
            dates_found = self._extract_dates_from_dataframe(df)
            file_info["dates_found"] = [str(d) for d in dates_found]

            if dates_found:
                # Check date freshness
                latest_date = max(dates_found)

                days_old = (self.today - latest_date).days

                if days_old > 1:
                    issue = (
                        f"Data dates are {days_old} days old "
                        f"(latest: {latest_date})"
                    )
                    file_info["issues"].append(issue)
                    self.validation_results["date_issues"].append(issue)

                # Extract race times for today's or recent dates
                recent_dates = [d for d in dates_found if (self.today - d).days <= 1]
                if recent_dates:
                    race_times = self._extract_race_times_from_dataframe(
                        df, recent_dates
                    )
                    file_info["race_times"] = race_times

                    # Store in main validation results
                    for race_date, times in race_times.items():
                        if race_date not in self.validation_results["race_times"]:
                            self.validation_results["race_times"][race_date] = times

            else:
                file_info["issues"].append("No valid dates found in data")

        except Exception as e:
            error_msg = f"Failed to analyze CSV content: {e}"
            file_info["issues"].append(error_msg)
            logger.error(f"❌ {error_msg}")

    def _extract_dates_from_dataframe(self, df: pd.DataFrame) -> Set[date]:
        """Extract unique dates from a DataFrame"""
        dates = set()

        # Common date column names
        date_columns = ["Date", "date", "race_date", "Date_time"]

        for col in date_columns:
            if col in df.columns:
                for date_str in df[col].dropna().unique():
                    try:
                        # Try different date formats
                        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y%m%d"]:
                            try:
                                date_obj = datetime.strptime(str(date_str), fmt).date()
                                dates.add(date_obj)
                                break
                            except ValueError:
                                continue
                    except Exception:
                        continue

        return dates

    def _extract_race_times_from_dataframe(
        self, df: pd.DataFrame, target_dates: List[date]
    ) -> Dict[str, Dict]:
        """Extract first and last race times for specific dates"""
        race_times = {}

        # Time column names
        time_columns = ["race_time", "time", "start_time", "off_time"]
        date_columns = ["Date", "date", "race_date"]

        # Find the date and time columns
        date_col = None
        time_col = None

        for col in date_columns:
            if col in df.columns:
                date_col = col
                break

        for col in time_columns:
            if col in df.columns:
                time_col = col
                break

        if not date_col or not time_col:
            return race_times

        for target_date in target_dates:
            target_date_str = target_date.strftime("%Y-%m-%d")

            # Filter for target date
            date_races = df[df[date_col] == target_date_str]

            if len(date_races) > 0:
                times = []
                for time_str in date_races[time_col].dropna():
                    try:
                        # Parse time (assuming HH:MM format)
                        time_obj = datetime.strptime(str(time_str), "%H:%M").time()
                        times.append(time_obj)
                    except ValueError:
                        continue

                if times:
                    times.sort()
                    race_times[target_date_str] = {
                        "first_race": str(times[0]),
                        "last_race": str(times[-1]),
                        "total_races": len(times),
                        "all_times": [str(t) for t in times],
                    }

        return race_times

    def _generate_recommendations(self) -> None:
        """Generate pipeline recommendations based on validation results"""
        if self.validation_results["errors"]:
            self.validation_results["pipeline_recommendation"] = "stop"
            self.validation_results["recommendation_reason"] = "Critical errors found"

        elif self.validation_results["date_issues"]:
            issues = self.validation_results["date_issues"]
            if any("days old" in issue and "2" in issue for issue in issues):
                self.validation_results["pipeline_recommendation"] = "stop"
                reason = "Data too old (2+ days)"
                self.validation_results["recommendation_reason"] = reason
            else:
                self.validation_results["pipeline_recommendation"] = "warning"
                reason = "Date issues detected"
                self.validation_results["recommendation_reason"] = reason

        else:
            self.validation_results["pipeline_recommendation"] = "proceed"
            self.validation_results["recommendation_reason"] = "All checks passed"

    def _display_user_summary(self) -> None:
        """Display a clear summary for the user"""
        print("\n" + "=" * 80)
        print("🗓️  ENHANCED DATE VALIDATION SUMMARY")
        print("=" * 80)

        print(f"📅 Today's Date: {self.today}")
        print(f"📁 Data Directory: {self.data_dir}")

        # Show date issues
        if self.validation_results["date_issues"]:
            print("\n⚠️  DATE ISSUES DETECTED:")
            for issue in self.validation_results["date_issues"]:
                print(f"   • {issue}")
        else:
            print("\n✅ No date issues detected")

        # Show race times
        if self.validation_results["race_times"]:
            print("\n🏁 RACE TIMES DETECTED:")
            for race_date, times in self.validation_results["race_times"].items():
                print(f"   📅 {race_date}:")
                print(f"      🌅 First Race: {times['first_race']}")
                print(f"      🌅 Last Race:  {times['last_race']}")
                print(f"      🏇 Total Races: {times['total_races']}")
        else:
            print("\n⚠️  No race times detected")

        # Show recommendation
        recommendation = self.validation_results["pipeline_recommendation"]
        reason = self.validation_results.get("recommendation_reason", "")

        print(f"\n🎯 PIPELINE RECOMMENDATION: {recommendation.upper()}")
        print(f"   Reason: {reason}")

        if recommendation == "stop":
            print("\n🛑 RECOMMENDATION: DO NOT PROCEED WITH PIPELINE")
            print("   The downloaded files have date issues that need to be resolved.")
            print("   Consider re-downloading today's data from the racing services.")

        elif recommendation == "warning":
            print("\n⚠️  RECOMMENDATION: PROCEED WITH CAUTION")
            print(
                "   Minor date issues detected. Pipeline can proceed but "
                "monitor results."
            )

        else:
            print("\n🚀 RECOMMENDATION: PROCEED WITH PIPELINE")
            print("   All date validations passed successfully.")

        print("\n" + "=" * 80)

    def save_validation_report(self, output_path: Optional[Path] = None) -> Path:
        """Save detailed validation report to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.data_dir / f"validation_report_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.validation_results, f, indent=2, default=str)

        logger.info("📄 Validation report saved: %s", output_path)
        return output_path


def main():
    """Main execution function"""
    validator = EnhancedDateValidator()
    results = validator.validate_all_downloads()

    # Save report
    validator.save_validation_report()

    # Return exit code based on recommendation
    if results["pipeline_recommendation"] == "stop":
        return 1
    elif results["pipeline_recommendation"] == "warning":
        return 2
    else:
        return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
