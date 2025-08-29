#!/usr/bin/env python3
"""
Test script to verify the updated date validation logic
"""

import csv
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.data_validator import HorseRacingDataValidator


def create_test_csv_file(csv_path: Path, dates: list):
    """Create a test CSV file with race data for specified dates"""
    csv_path.parent.mkdir(parents=True, exist_ok=True)

    with open(csv_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        # Write header
        writer.writerow(["race_id", "Date", "venue", "race_time", "distance"])

        # Write test data for each date
        for i, date in enumerate(dates):
            race_id = f"RACE_{date.strftime('%Y%m%d')}_{i+1:03d}"
            writer.writerow(
                [race_id, date.strftime("%Y-%m-%d"), "TEST_VENUE", "14:30", "1200"]
            )


def test_relaxed_date_validation():
    """Test that the updated validation logic accepts yesterday's results"""

    print("🧪 Testing updated date validation logic...")

    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directory structure
        results_path = temp_path / "results"
        cards_path = temp_path / "cards"

        # Create results CSV with yesterday's data (should be accepted)
        create_test_csv_file(results_path / "races" / "races.csv", [yesterday])

        # Create cards CSV with both today and yesterday (should be optimal)
        create_test_csv_file(cards_path / "races" / "races.csv", [today, yesterday])

        # Initialize validator
        validator = HorseRacingDataValidator(temp_path)

        # Run validation
        print(f"📅 Testing with dates: Results={yesterday}, Cards={today}, {yesterday}")

        try:
            # Test the private method directly
            validator._validate_date_consistency(results_path, cards_path)

            # Check validation results
            warnings = validator.validation_results.get("warnings", [])
            errors = validator.validation_results.get("errors", [])

            print(f"✅ Validation completed")
            print(f"📊 Warnings: {len(warnings)}")
            print(f"❌ Errors: {len(errors)}")

            # Check for specific warning patterns
            date_warnings = [w for w in warnings if "unexpected date" in w.lower()]

            if date_warnings:
                print(f"❌ Still rejecting dates: {date_warnings}")
                return False
            else:
                print(f"✅ No date rejection warnings - validation is now flexible!")

                # Show any remaining warnings (should be non-date related)
                if warnings:
                    print(f"ℹ️ Other warnings (OK): {warnings}")

                return True

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False


def test_stale_data_detection():
    """Test that truly stale data (>2 days old) is still caught"""

    print("\n🧪 Testing stale data detection...")

    today = datetime.now().date()
    old_date = today - timedelta(days=5)  # 5 days ago

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create test directory structure
        results_path = temp_path / "results"
        cards_path = temp_path / "cards"

        # Create results CSV with old data (should trigger warning)
        create_test_csv_file(results_path / "races" / "races.csv", [old_date])

        # Create cards CSV with old data
        create_test_csv_file(cards_path / "races" / "races.csv", [old_date])

        # Initialize validator
        validator = HorseRacingDataValidator(temp_path)

        try:
            # Test the private method directly
            validator._validate_date_consistency(results_path, cards_path)

            # Check validation results
            warnings = validator.validation_results.get("warnings", [])

            # Check for stale data warnings
            stale_warnings = [w for w in warnings if "stale" in w.lower()]

            if stale_warnings:
                print(f"✅ Correctly detected stale data: {stale_warnings}")
                return True
            else:
                print(f"❌ Failed to detect stale data")
                return False

        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            return False


def main():
    """Run all validation tests"""
    print("🚀 Testing updated Horse Racing Data Validator")
    print("=" * 60)

    test1_passed = test_relaxed_date_validation()
    test2_passed = test_stale_data_detection()

    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"✅ Relaxed date validation: {'PASSED' if test1_passed else 'FAILED'}")
    print(f"✅ Stale data detection: {'PASSED' if test2_passed else 'FAILED'}")

    if test1_passed and test2_passed:
        print(f"\n🎉 All tests PASSED! Validation logic is working correctly.")
        print(f"💡 The system will now accept yesterday's results as valid data.")
        return True
    else:
        print(f"\n❌ Some tests FAILED. Check the validation logic.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
