#!/usr/bin/env python3
"""
Test Enhanced Dash Cleaning with Real Data
🧪 TEST: Apply enhanced dash cleaning to actual CSV files
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.clean_data import clean_dash_symbols


def test_real_data_cleaning():
    """Test dash cleaning on actual CSV files"""
    print("🧪 Testing Enhanced Dash Cleaning on Real Data")
    print("=" * 50)

    # Test files that exist
    test_files = [
        ("data/daily_downloads/mapped_races.csv", "races"),
        ("data/daily_downloads/mapped_records.csv", "records"),
        ("data/daily_downloads/mapped_horses.csv", "horses"),
    ]

    for file_path, table_name in test_files:
        file_path_obj = Path(file_path)
        if file_path_obj.exists():
            print(f"\n🔍 Testing {file_path} ({table_name})")

            # Load and analyze the data
            df = pd.read_csv(file_path)
            print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

            # Count dash symbols before cleaning
            dash_count_before = 0
            for col in df.columns:
                dash_count_before += (df[col].astype(str) == "-").sum()

            print(f"🔍 Found {dash_count_before} dash symbols before cleaning")

            if dash_count_before > 0:
                # Apply dash cleaning
                print("🧹 Applying enhanced dash cleaning...")
                cleaned_df = clean_dash_symbols(df.copy(), table_name)

                # Count dash symbols after cleaning
                dash_count_after = 0
                for col in cleaned_df.columns:
                    dash_count_after += (cleaned_df[col].astype(str) == "-").sum()

                print(f"✅ Dash symbols after cleaning: {dash_count_after}")
                print(
                    f"🎯 Successfully cleaned {dash_count_before - dash_count_after} dash symbols"
                )

                # Show a few examples of changes
                print("\n📋 Sample changes:")
                for col in df.columns[:5]:  # Check first 5 columns
                    dash_mask = df[col].astype(str) == "-"
                    if dash_mask.any():
                        idx = dash_mask.idxmax()  # Get first dash occurrence
                        original = df.loc[idx, col]
                        cleaned = cleaned_df.loc[idx, col]
                        print(f"  - {col}: '{original}' → '{cleaned}'")

            else:
                print("✅ No dash symbols found in this file")
        else:
            print(f"⚠️ File not found: {file_path}")

    print("\n🎉 Real data cleaning test completed!")


def main():
    """Run the real data test"""
    try:
        test_real_data_cleaning()
        return 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
