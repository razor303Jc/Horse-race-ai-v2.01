#!/usr/bin/env python3
"""
Robust Data Validation Script for Auto-Downloader
=================================================

Validates downloaded horse racing data for:
- Date consistency (results = previous day, cards = current day)
- Race ID overlap detection
- Record count validation
- Data integrity checks
"""

import csv
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataValidationError(Exception):
    """Custom exception for data validation failures"""

    pass


class HorseRacingDataValidator:
    """Validates horse racing data downloads for quality and integrity"""

    def __init__(self, data_dir: Path = Path("data/daily_downloads")):
        self.data_dir = Path(data_dir)
        self.validation_results = {
            "validation_timestamp": datetime.now().isoformat(),
            "data_directory": str(self.data_dir),
            "checks_performed": [],
            "warnings": [],
            "errors": [],
            "summary": {},
        }

    def validate_download(
        self, results_dir: str = "results_data", cards_dir: str = "cards_data"
    ) -> Dict:
        """
        Perform comprehensive validation of downloaded data

        Args:
            results_dir: Directory name containing results data
            cards_dir: Directory name containing cards data

        Returns:
            Dict containing validation results
        """
        logger.info("🔍 Starting comprehensive data validation...")

        results_path = self.data_dir / results_dir
        cards_path = self.data_dir / cards_dir

        try:
            # Check if data directories exist
            self._check_directory_existence(results_path, cards_path)

            # Validate date consistency
            self._validate_date_consistency(results_path, cards_path)

            # Check for Race ID overlaps
            self._validate_race_id_integrity(results_path, cards_path)

            # Validate record counts
            self._validate_record_counts(results_path, cards_path)

            # Check data file integrity
            self._validate_file_integrity(results_path, cards_path)

            # Generate summary
            self._generate_validation_summary()

            logger.info("✅ Data validation completed successfully")

        except Exception as e:
            self.validation_results["errors"].append(f"Validation failed: {str(e)}")
            logger.error(f"❌ Data validation failed: {e}")

        return self.validation_results

    def _check_directory_existence(self, results_path: Path, cards_path: Path) -> None:
        """Check if required data directories exist"""
        self.validation_results["checks_performed"].append("directory_existence")

        if not results_path.exists():
            raise DataValidationError(f"Results directory not found: {results_path}")

        if not cards_path.exists():
            raise DataValidationError(f"Cards directory not found: {cards_path}")

        logger.info(
            f"✅ Data directories found: {results_path.name}, {cards_path.name}"
        )

    def _validate_date_consistency(self, results_path: Path, cards_path: Path) -> None:
        """Validate that dates are consistent with expectations"""
        self.validation_results["checks_performed"].append("date_consistency")

        today = datetime.now().date()
        yesterday = today - timedelta(days=1)

        # Check results data (should be yesterday)
        results_dates = self._extract_dates_from_csv(
            results_path / "races" / "races.csv"
        )
        if results_dates:
            for date in results_dates:
                if date != yesterday:
                    self.validation_results["warnings"].append(
                        f"Results data contains unexpected date: {date} (expected: {yesterday})"
                    )

        # Check cards data (should be today)
        cards_dates = self._extract_dates_from_csv(cards_path / "races" / "races.csv")
        if cards_dates:
            for date in cards_dates:
                if date != today:
                    self.validation_results["warnings"].append(
                        f"Cards data contains unexpected date: {date} (expected: {today})"
                    )

        self.validation_results["summary"]["results_dates"] = [
            str(d) for d in results_dates
        ]
        self.validation_results["summary"]["cards_dates"] = [
            str(d) for d in cards_dates
        ]

        logger.info(f"✅ Date validation: Results={results_dates}, Cards={cards_dates}")

    def _extract_dates_from_csv(self, csv_path: Path) -> Set[datetime.date]:
        """Extract unique dates from races CSV file"""
        dates = set()

        if not csv_path.exists():
            return dates

        try:
            with open(csv_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if "Date" in row and row["Date"]:
                        try:
                            race_date = datetime.strptime(
                                row["Date"], "%Y-%m-%d"
                            ).date()
                            dates.add(race_date)
                        except ValueError:
                            self.validation_results["warnings"].append(
                                f"Invalid date format in {csv_path}: {row['Date']}"
                            )
        except Exception as e:
            self.validation_results["warnings"].append(f"Error reading {csv_path}: {e}")

        return dates

    def _validate_race_id_integrity(self, results_path: Path, cards_path: Path) -> None:
        """Check for Race ID overlaps and validate sequencing"""
        self.validation_results["checks_performed"].append("race_id_integrity")

        # Extract Race IDs from both datasets
        results_race_ids = self._extract_race_ids(results_path / "races" / "races.csv")
        cards_race_ids = self._extract_race_ids(cards_path / "races" / "races.csv")

        # Check for overlaps
        overlapping_ids = results_race_ids.intersection(cards_race_ids)
        if overlapping_ids:
            self.validation_results["errors"].append(
                f"Race ID overlap detected: {sorted(overlapping_ids)}"
            )

        # Check ID ranges
        if results_race_ids:
            results_min, results_max = min(results_race_ids), max(results_race_ids)
            self.validation_results["summary"][
                "results_race_id_range"
            ] = f"{results_min}-{results_max}"

        if cards_race_ids:
            cards_min, cards_max = min(cards_race_ids), max(cards_race_ids)
            self.validation_results["summary"][
                "cards_race_id_range"
            ] = f"{cards_min}-{cards_max}"

        # Validate sequential progression
        if results_race_ids and cards_race_ids:
            if max(results_race_ids) >= min(cards_race_ids):
                self.validation_results["warnings"].append(
                    "Race IDs are not properly sequential between results and cards"
                )

        self.validation_results["summary"]["race_id_overlap_count"] = len(
            overlapping_ids
        )

        logger.info(
            f"✅ Race ID validation: Results={len(results_race_ids)}, Cards={len(cards_race_ids)}, Overlaps={len(overlapping_ids)}"
        )

    def _extract_race_ids(self, csv_path: Path) -> Set[int]:
        """Extract Race IDs from CSV file"""
        race_ids = set()

        if not csv_path.exists():
            return race_ids

        try:
            with open(csv_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if "Race_ID" in row and row["Race_ID"]:
                        try:
                            race_ids.add(int(row["Race_ID"]))
                        except ValueError:
                            self.validation_results["warnings"].append(
                                f"Invalid Race_ID in {csv_path}: {row['Race_ID']}"
                            )
        except Exception as e:
            self.validation_results["warnings"].append(f"Error reading {csv_path}: {e}")

        return race_ids

    def _validate_record_counts(self, results_path: Path, cards_path: Path) -> None:
        """Validate record counts are within expected ranges"""
        self.validation_results["checks_performed"].append("record_counts")

        # Expected ranges for UK/Irish racing
        expected_ranges = {
            "daily_races_min": 20,
            "daily_races_max": 100,
            "daily_records_min": 100,
            "daily_records_max": 1000,
            "cards_races_min": 10,
            "cards_races_max": 80,
        }

        # Count results data
        results_races = self._count_csv_records(results_path / "races" / "races.csv")
        results_records = self._count_csv_records(
            results_path / "records" / "records.csv"
        )

        # Count cards data
        cards_races = self._count_csv_records(cards_path / "races" / "races.csv")

        # Validate ranges
        if (
            results_races < expected_ranges["daily_races_min"]
            or results_races > expected_ranges["daily_races_max"]
        ):
            self.validation_results["warnings"].append(
                f"Results races count outside expected range: {results_races} (expected: {expected_ranges['daily_races_min']}-{expected_ranges['daily_races_max']})"
            )

        if (
            results_records < expected_ranges["daily_records_min"]
            or results_records > expected_ranges["daily_records_max"]
        ):
            self.validation_results["warnings"].append(
                f"Results records count outside expected range: {results_records} (expected: {expected_ranges['daily_records_min']}-{expected_ranges['daily_records_max']})"
            )

        if (
            cards_races < expected_ranges["cards_races_min"]
            or cards_races > expected_ranges["cards_races_max"]
        ):
            self.validation_results["warnings"].append(
                f"Cards races count outside expected range: {cards_races} (expected: {expected_ranges['cards_races_min']}-{expected_ranges['cards_races_max']})"
            )

        # Store counts
        self.validation_results["summary"]["record_counts"] = {
            "results_races": results_races,
            "results_records": results_records,
            "cards_races": cards_races,
        }

        logger.info(
            f"✅ Record count validation: Results races={results_races}, Records={results_records}, Cards races={cards_races}"
        )

    def _count_csv_records(self, csv_path: Path) -> int:
        """Count records in CSV file (excluding header)"""
        if not csv_path.exists():
            return 0

        try:
            with open(csv_path, "r", encoding="utf-8") as file:
                return sum(1 for line in file) - 1  # Subtract header
        except Exception as e:
            self.validation_results["warnings"].append(
                f"Error counting records in {csv_path}: {e}"
            )
            return 0

    def _validate_file_integrity(self, results_path: Path, cards_path: Path) -> None:
        """Check that all expected files exist and have content"""
        self.validation_results["checks_performed"].append("file_integrity")

        expected_files = {
            "results": ["races/races.csv", "records/records.csv", "horses/horses.csv"],
            "cards": ["races/races.csv", "racecard_details/racecard_details.html"],
        }

        missing_files = []
        empty_files = []

        # Check results files
        for file_path in expected_files["results"]:
            full_path = results_path / file_path
            if not full_path.exists():
                missing_files.append(f"results/{file_path}")
            elif full_path.stat().st_size == 0:
                empty_files.append(f"results/{file_path}")

        # Check cards files
        for file_path in expected_files["cards"]:
            full_path = cards_path / file_path
            if not full_path.exists():
                missing_files.append(f"cards/{file_path}")
            elif full_path.stat().st_size == 0:
                empty_files.append(f"cards/{file_path}")

        if missing_files:
            self.validation_results["errors"].extend(
                [f"Missing file: {f}" for f in missing_files]
            )

        if empty_files:
            self.validation_results["warnings"].extend(
                [f"Empty file: {f}" for f in empty_files]
            )

        self.validation_results["summary"]["file_integrity"] = {
            "missing_files": len(missing_files),
            "empty_files": len(empty_files),
        }

        logger.info(
            f"✅ File integrity: Missing={len(missing_files)}, Empty={len(empty_files)}"
        )

    def _generate_validation_summary(self) -> None:
        """Generate overall validation summary"""
        error_count = len(self.validation_results["errors"])
        warning_count = len(self.validation_results["warnings"])

        self.validation_results["summary"]["validation_status"] = (
            "FAILED" if error_count > 0 else "PASSED"
        )
        self.validation_results["summary"]["error_count"] = error_count
        self.validation_results["summary"]["warning_count"] = warning_count
        self.validation_results["summary"]["checks_performed_count"] = len(
            self.validation_results["checks_performed"]
        )

    def save_validation_report(self, output_path: Optional[Path] = None) -> Path:
        """Save validation report to JSON file"""
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.data_dir / f"validation_report_{timestamp}.json"

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(self.validation_results, file, indent=2)

        logger.info(f"📄 Validation report saved: {output_path}")
        return output_path

    def print_validation_summary(self) -> None:
        """Print a human-readable validation summary"""
        summary = self.validation_results["summary"]

        print("\n" + "=" * 60)
        print("🔍 DATA VALIDATION SUMMARY")
        print("=" * 60)
        print(
            f"Status: {'✅ PASSED' if summary['validation_status'] == 'PASSED' else '❌ FAILED'}"
        )
        print(f"Errors: {summary['error_count']}")
        print(f"Warnings: {summary['warning_count']}")
        print(f"Checks Performed: {summary['checks_performed_count']}")

        if "record_counts" in summary:
            print(f"\nRecord Counts:")
            print(f"  Results Races: {summary['record_counts']['results_races']}")
            print(f"  Results Records: {summary['record_counts']['results_records']}")
            print(f"  Cards Races: {summary['record_counts']['cards_races']}")

        if "results_dates" in summary:
            print(f"\nDates:")
            print(f"  Results: {', '.join(summary['results_dates'])}")
            print(f"  Cards: {', '.join(summary['cards_dates'])}")

        if "race_id_overlap_count" in summary:
            print(f"\nRace ID Analysis:")
            print(f"  Overlaps: {summary['race_id_overlap_count']}")
            if "results_race_id_range" in summary:
                print(f"  Results Range: {summary['results_race_id_range']}")
            if "cards_race_id_range" in summary:
                print(f"  Cards Range: {summary['cards_race_id_range']}")

        if self.validation_results["errors"]:
            print(f"\n❌ Errors:")
            for error in self.validation_results["errors"]:
                print(f"  - {error}")

        if self.validation_results["warnings"]:
            print(f"\n⚠️ Warnings:")
            for warning in self.validation_results["warnings"]:
                print(f"  - {warning}")

        print("=" * 60)


def main():
    """Command line interface for data validation"""
    import argparse

    parser = argparse.ArgumentParser(description="Validate horse racing data downloads")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path("data/daily_downloads"),
        help="Data directory path (default: data/daily_downloads)",
    )
    parser.add_argument(
        "--results-dir",
        type=str,
        default="results_data",
        help="Results data directory name (default: results_data)",
    )
    parser.add_argument(
        "--cards-dir",
        type=str,
        default="cards_data",
        help="Cards data directory name (default: cards_data)",
    )
    parser.add_argument(
        "--save-report", action="store_true", help="Save validation report to JSON file"
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Only show errors and warnings"
    )

    args = parser.parse_args()

    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)

    # Run validation
    validator = HorseRacingDataValidator(args.data_dir)
    results = validator.validate_download(args.results_dir, args.cards_dir)

    # Print summary
    validator.print_validation_summary()

    # Save report if requested
    if args.save_report:
        validator.save_validation_report()

    # Exit with appropriate code
    exit_code = 1 if results["summary"]["validation_status"] == "FAILED" else 0
    exit(exit_code)


if __name__ == "__main__":
    main()
