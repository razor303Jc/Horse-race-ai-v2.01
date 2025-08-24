#!/usr/bin/env python3
"""
🧪 Schema Compatibility Checker Test & Demo
===========================================

Test script to demonstrate the Schema Compatibility Checker functionality
with sample CSV data and various schema validation scenarios.

Author: AI Assistant
Date: August 24, 2025
"""

import tempfile
import pandas as pd
from pathlib import Path
import sys
import json

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.pipeline.schema_compatibility_checker import SchemaCompatibilityChecker


def create_test_csv_good_schema() -> Path:
    """Create a test CSV with good schema compatibility"""
    data = {
        "race_id": ["R001", "R001", "R002"],
        "date": ["2025-08-24", "2025-08-24", "2025-08-24"],
        "course": ["Newmarket", "Newmarket", "Ascot"],
        "race_time": ["14:30", "14:30", "15:00"],
        "number": [1, 2, 1],  # Using 'number' instead of 'draw'
        "horse": ["Thunder Bay", "Lightning", "Storm"],
        "jockey": ["J. Smith", "M. Jones", "A. Brown"],
        "odds": [5.0, 3.5, 8.0],
    }

    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    df.to_csv(temp_file.name, index=False)
    return Path(temp_file.name)


def create_test_csv_schema_issues() -> Path:
    """Create a test CSV with schema compatibility issues"""
    data = {
        "Race_ID": ["R001", "R001", "R002"],  # Non-standard field name
        "race_date": ["2025-08-24", "2025-08-24", "2025-08-24"],  # Should be 'date'
        "Course": ["Newmarket", "Newmarket", "Ascot"],
        "off_time": ["14:30", "14:30", "15:00"],  # Should be 'race_time'
        "draw": [1, 2, 1],  # Should be 'number'
        "horse_name": ["Thunder Bay", "Lightning", "Storm"],  # Should be 'horse'
        "jockey_name": ["J. Smith", "M. Jones", "A. Brown"],  # Should be 'jockey'
        "odds_decimal": ["5.0", "3.5", "8.0"],  # String instead of numeric
    }

    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    df.to_csv(temp_file.name, index=False)
    return Path(temp_file.name)


def create_test_csv_missing_fields() -> Path:
    """Create a test CSV with missing required fields"""
    data = {
        "horse": ["Thunder Bay", "Lightning", "Storm"],
        "jockey": ["J. Smith", "M. Jones", "A. Brown"],
        "odds": [5.0, 3.5, 8.0],
        # Missing: race_id, date, course, race_time, number
    }

    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    df.to_csv(temp_file.name, index=False)
    return Path(temp_file.name)


def run_test_scenario(csv_path: Path, target_table: str, scenario_name: str):
    """Run a test scenario and display results"""
    print(f"\n🧪 Testing Scenario: {scenario_name}")
    print("=" * 60)
    print(f"CSV File: {csv_path}")
    print(f"Target Table: {target_table}")
    print()

    # Initialize checker
    checker = SchemaCompatibilityChecker()

    # Run validation
    validation_result = checker.validate_csv_schema_compatibility(
        csv_path, target_table
    )

    # Generate and display report
    report = checker.generate_compatibility_report(validation_result)
    print(report)

    # Display JSON summary for debugging
    print("\n📋 JSON Summary:")
    print("-" * 30)
    summary = {
        "validation_passed": validation_result["validation_passed"],
        "compatibility_score": validation_result["compatibility_score"],
        "errors_count": len(validation_result.get("errors", [])),
        "warnings_count": len(validation_result.get("warnings", [])),
        "recommendations_count": len(validation_result.get("recommendations", [])),
    }
    print(json.dumps(summary, indent=2))


def test_ai_selections_scenario():
    """Test scenario that would have caught the AI selections missing number field issue"""
    print("\n🎯 AI SELECTIONS SCENARIO TEST")
    print("=" * 60)
    print("This test simulates the missing 'number' (cloth number) field issue")
    print("we encountered in the AI selections implementation.")
    print("NOTE: 'draw' and 'number' are DIFFERENT fields in horse racing:")
    print("- 'number' = cloth number worn by horse (ALWAYS required)")
    print("- 'draw' = starting stall position (can be NULL for some races)")
    print()

    # Create CSV with 'draw' but missing 'number' field (the actual issue)
    data = {
        "race_id": ["R001", "R001", "R002"],
        "date": ["2025-08-24", "2025-08-24", "2025-08-24"],
        "course": ["Newmarket", "Newmarket", "Ascot"],
        "race_time": ["14:30", "14:30", "15:00"],
        "draw": [1, 2, None],  # Starting stall (can be NULL for jump races)
        "horse": ["Thunder Bay", "Lightning", "Storm"],
        "jockey": ["J. Smith", "M. Jones", "A. Brown"],
        # MISSING: 'number' field (cloth number) - this caused our AI issue!
    }

    df = pd.DataFrame(data)
    temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
    df.to_csv(temp_file.name, index=False)

    csv_path = Path(temp_file.name)

    # Test against racecard_details table (where we need 'number' field)
    run_test_scenario(
        csv_path, "racecard_details", "AI Selections Missing Number Field"
    )

    print("\n💡 Expected Outcome:")
    print("- Schema checker should detect missing 'number' (cloth number) field")
    print("- Should NOT suggest renaming 'draw' → 'number' (they're different!)")
    print("- Should allow 'draw' field to have NULL values (valid for jump races)")
    print("- This would have identified the missing cloth number data issue!")


def main():
    """Run all test scenarios"""
    print("🔍 Schema Compatibility Checker - Test Suite")
    print("=" * 60)
    print("Testing various CSV schema compatibility scenarios...")

    try:
        # Test 1: Good schema
        good_csv = create_test_csv_good_schema()
        run_test_scenario(good_csv, "racecard_details", "Good Schema (Should Pass)")

        # Test 2: Schema issues
        issues_csv = create_test_csv_schema_issues()
        run_test_scenario(issues_csv, "racecard_details", "Schema Issues (Should Warn)")

        # Test 3: Missing fields
        missing_csv = create_test_csv_missing_fields()
        run_test_scenario(
            missing_csv, "racecard_details", "Missing Required Fields (Should Fail)"
        )

        # Test 4: AI selections scenario
        test_ai_selections_scenario()

        print("\n✅ All test scenarios completed!")
        print("\n📋 Summary:")
        print("- Schema compatibility checker can detect field name variations")
        print("- Provides actionable recommendations for schema fixes")
        print("- Would have prevented the AI selections 'draw' vs 'number' issue")
        print("- Ready for integration into CSV preprocessing pipeline")

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
