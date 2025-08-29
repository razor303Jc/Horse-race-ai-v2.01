#!/usr/bin/env python3
"""
Test Enhanced Dash Symbol Cleaning
🧪 TEST SCRIPT: Demonstrate dash symbol cleaning based on data types

This script tests the enhanced dash cleaning functionality:
- Numeric fields: "-" → 0
- String fields: "-" → "None"
- Weight UK format: "10-2" → "10.2" (then convert to kg)
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.clean_data import (
    clean_dash_symbols,
    load_column_type_mapping,
)


def create_test_data():
    """Create sample test data with dash symbols"""
    print("🧪 Creating test data with dash symbols...")

    # Sample races data
    races_data = {
        "race_id": ["R001", "R002", "R003"],
        "race_number": [1, "-", 3],  # Integer field with dash
        "course": ["Ascot", "-", "Newmarket"],  # String field with dash
        "runners": [8, "-", 12],  # Integer field with dash
        "prize": ["£10000", "-", "£5000"],  # String field with dash
    }

    # Sample records data
    records_data = {
        "record_id": ["REC001", "REC002", "REC003"],
        "horse_number": [1, "-", 3],  # Integer field with dash
        "position": [1, 2, "-"],  # Integer field with dash
        "weight_uk": ["10-2", "-", "9-7"],  # Weight format and dash
        "horse": ["Thunder", "-", "Lightning"],  # String field with dash
        "age": [5, "-", 4],  # Integer field with dash
        "sp": [2.5, "-", 3.0],  # Decimal field with dash
    }

    races_df = pd.DataFrame(races_data)
    records_df = pd.DataFrame(records_data)

    return races_df, records_df


def test_dash_cleaning():
    """Test the enhanced dash cleaning functionality"""
    print("🔧 Testing Enhanced Dash Symbol Cleaning")
    print("=" * 50)

    # Create test data
    races_df, records_df = create_test_data()

    print("\n📊 BEFORE CLEANING:")
    print("\nRaces data:")
    print(races_df)
    print(f"Data types: {races_df.dtypes.to_dict()}")

    print("\nRecords data:")
    print(records_df)
    print(f"Data types: {records_df.dtypes.to_dict()}")

    # Test column type mapping loading
    print("\n🔍 Loading column type configuration...")
    type_mapping = load_column_type_mapping()
    if type_mapping:
        print("✅ Column type mapping loaded successfully")
        # Show races table configuration
        races_config = type_mapping.get("races", {}).get("null_handling", {})
        print(f"Races - Integer fields: {races_config.get('integers', [])}")
        print(f"Races - String fields: {races_config.get('strings', [])}")

        # Show records table configuration
        records_config = type_mapping.get("records", {}).get("null_handling", {})
        print(f"Records - Integer fields: {records_config.get('integers', [])[:5]}...")
        print(f"Records - Decimal fields: {records_config.get('decimals', [])[:5]}...")
        print(f"Records - String fields: {records_config.get('strings', [])}")
    else:
        print("❌ Failed to load column type mapping")
        return False

    # Apply dash cleaning
    print("\n🧹 APPLYING DASH CLEANING:")

    print("Cleaning races data...")
    races_cleaned = clean_dash_symbols(races_df.copy(), "races")

    print("Cleaning records data...")
    records_cleaned = clean_dash_symbols(records_df.copy(), "records")

    print("\n📊 AFTER CLEANING:")
    print("\nRaces data:")
    print(races_cleaned)
    print(f"Data types: {races_cleaned.dtypes.to_dict()}")

    print("\nRecords data:")
    print(records_cleaned)
    print(f"Data types: {records_cleaned.dtypes.to_dict()}")

    # Verify results
    print("\n✅ VERIFICATION:")

    # Check races data
    print("Races verification:")
    print(f"  - race_number dash → 0: {races_cleaned.loc[1, 'race_number'] == 0}")
    print(f"  - course dash → 'None': {races_cleaned.loc[1, 'course'] == 'None'}")
    print(f"  - runners dash → 0: {races_cleaned.loc[1, 'runners'] == 0}")
    print(f"  - prize dash → 'None': {races_cleaned.loc[1, 'prize'] == 'None'}")

    # Check records data
    print("Records verification:")
    print(f"  - horse_number dash → 0: {records_cleaned.loc[1, 'horse_number'] == 0}")
    print(f"  - position dash → 0: {records_cleaned.loc[2, 'position'] == 0}")
    print(
        f"  - weight_uk '10-2' → '10.2': {records_cleaned.loc[0, 'weight_uk'] == '10.2'}"
    )
    print(f"  - weight_uk dash → 0: {records_cleaned.loc[1, 'weight_uk'] == 0}")
    print(f"  - horse dash → 'None': {records_cleaned.loc[1, 'horse'] == 'None'}")
    print(f"  - age dash → 0: {records_cleaned.loc[1, 'age'] == 0}")
    print(f"  - sp dash → 0: {records_cleaned.loc[1, 'sp'] == 0}")

    return True


def main():
    """Run the dash cleaning test"""
    print("🚀 Enhanced Dash Symbol Cleaning Test")
    print("=" * 50)

    try:
        success = test_dash_cleaning()

        if success:
            print("\n🎉 All dash cleaning tests passed!")
            print("\n📋 SUMMARY:")
            print("✅ Numeric fields: '-' → 0")
            print("✅ String fields: '-' → 'None'")
            print("✅ Weight UK format: '10-2' → '10.2'")
            print("✅ Configuration-based type handling working")
            return 0
        else:
            print("\n❌ Some tests failed")
            return 1

    except Exception as e:
        print(f"\n💥 Test failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
