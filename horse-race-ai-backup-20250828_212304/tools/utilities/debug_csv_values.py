#!/usr/bin/env python3
"""
Debug Database Insert Values
============================

Capture and analyze the exact values being inserted to find the BIGINT overflow source.
"""

import os

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


def debug_csv_conversion():
    """Debug the CSV data conversion process to find extreme values"""
    print("🔍 Debugging CSV Conversion Process")
    print("=" * 60)

    # Find the problematic CSV files
    import glob

    records_files = glob.glob("project_root / 'data' / **/records.csv", recursive=True)
    racecard_files = glob.glob("project_root / 'data' / **/racecard_details.csv", recursive=True)

    if not records_files:
        print("❌ No records.csv files found")
        return

    print(f"Found {len(records_files)} records.csv files")
    print(f"Found {len(racecard_files)} racecard_details.csv files")

    # Test the same conversion process our code uses
    for csv_file in records_files[:1]:  # Just test first file
        print(f"\n📄 Testing: {csv_file}")

        try:
            df = pd.read_csv(csv_file)
            print(f"   Original shape: {df.shape}")

            # Simulate our integer conversion process
            print("\n🔧 Testing integer conversion on all columns...")

            for col in df.columns:
                try:
                    # Try converting to numeric
                    numeric_series = pd.to_numeric(df[col], errors="coerce")
                    non_null = numeric_series.dropna()

                    if len(non_null) > 0:
                        min_val = non_null.min()
                        max_val = non_null.max()

                        # Check for BIGINT overflow
                        bigint_max = 9223372036854775807

                        if abs(max_val) > bigint_max or abs(min_val) > bigint_max:
                            print(f"🔴 {col}: BIGINT OVERFLOW!")
                            print(f"   Min: {min_val}")
                            print(f"   Max: {max_val}")
                            print(
                                f"   Extreme values: {non_null[abs(non_null) > bigint_max].tolist()[:5]}"
                            )
                        elif abs(max_val) > 1000000000:  # > 1 billion
                            print(f"⚠️ {col}: Large values (but OK)")
                            print(f"   Max: {max_val}")

                        # Check for infinity
                        if any(pd.isinf(non_null)):
                            print(f"🔴 {col}: Contains INFINITY values!")
                            inf_values = non_null[pd.isinf(non_null)]
                            print(f"   Infinity values: {inf_values.tolist()[:5]}")

                except Exception as e:
                    continue

            # Test specific columns that might be problematic
            test_columns = ["ID", "Race_ID", "Horse_ID", "jockey_ID", "trainer_ID"]
            existing_test_cols = [col for col in test_columns if col in df.columns]

            if existing_test_cols:
                print(f"\n🎯 Detailed analysis of ID columns: {existing_test_cols}")

                for col in existing_test_cols:
                    print(f"\n   {col}:")
                    print(f"     Data type: {df[col].dtype}")
                    print(
                        f"     Sample values: {df[col].dropna().unique()[:10].tolist()}"
                    )

                    # Convert to numeric and check
                    numeric_vals = pd.to_numeric(df[col], errors="coerce").dropna()
                    if len(numeric_vals) > 0:
                        print(f"     Min: {numeric_vals.min()}")
                        print(f"     Max: {numeric_vals.max()}")

                        # Check if any value would overflow when processed
                        for val in numeric_vals.unique():
                            if abs(val) > 9223372036854775807:
                                print(f"     🔴 OVERFLOW VALUE: {val}")

        except Exception as e:
            print(f"❌ Error processing {csv_file}: {e}")


if __name__ == "__main__":
    debug_csv_conversion()
