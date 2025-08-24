#!/usr/bin/env python3
"""
Investigate Dash Symbols in Real Data
🔍 ANALYSIS: Examine actual dash symbols in CSV files
"""

import pandas as pd
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def investigate_dash_symbols():
    """Investigate what dash symbols actually look like in the data"""
    print("🔍 Investigating Dash Symbols in Real Data")
    print("=" * 50)

    # Test the records file which had dash symbols
    file_path = "data/daily_downloads/mapped_records.csv"
    df = pd.read_csv(file_path)

    print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

    # Look for different types of dash/missing values
    dash_variations = ["-", "–", "—", "−", "—"]  # Different types of dashes

    for dash_char in dash_variations:
        count = 0
        columns_with_dash = []

        for col in df.columns:
            dash_count_in_col = (df[col].astype(str) == dash_char).sum()
            count += dash_count_in_col
            if dash_count_in_col > 0:
                columns_with_dash.append(f"{col}({dash_count_in_col})")

        if count > 0:
            print(
                f"🔍 Found {count} '{dash_char}' symbols in columns: {', '.join(columns_with_dash[:5])}"
            )

    # Look for NaN/null values
    null_count = df.isnull().sum().sum()
    print(f"🔍 Found {null_count} NaN/null values")

    # Look for empty strings
    empty_count = 0
    for col in df.columns:
        empty_count += (df[col].astype(str) == "").sum()
    print(f"🔍 Found {empty_count} empty string values")

    # Show sample data with potential issues
    print("\n📋 Sample data analysis:")
    for col in df.columns[:10]:  # Check first 10 columns
        unique_values = df[col].astype(str).unique()
        suspicious_values = [
            v
            for v in unique_values
            if v in ["-", "–", "—", "−", "—", "", "nan", "None"]
        ]
        if suspicious_values:
            print(f"  - {col}: {suspicious_values}")

    # Show actual unique values for a few columns
    print("\n🔍 Detailed analysis of first few columns:")
    for col in df.columns[:5]:
        unique_vals = (
            df[col].dropna().astype(str).unique()[:10]
        )  # First 10 unique values
        print(f"  - {col}: {list(unique_vals)}")

        # Check for dash-like values
        dash_like = [v for v in unique_vals if len(str(v)) == 1 and str(v) in "−–—-"]
        if dash_like:
            print(f"    🎯 Dash-like values: {dash_like}")


def main():
    """Run the investigation"""
    try:
        investigate_dash_symbols()
        return 0
    except Exception as e:
        print(f"❌ Investigation failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
