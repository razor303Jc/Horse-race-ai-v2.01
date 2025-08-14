#!/usr/bin/env python3
"""
Data Cleaner for Database Upload
Fixes data type issues before uploading to PostgreSQL
"""

import numpy as np
import pandas as pd


def clean_records_data(input_file, output_file):
    """Clean the records CSV file for database upload"""
    print(f"🧹 Cleaning records data: {input_file}")

    # Read the CSV
    df = pd.read_csv(input_file)
    print(f"📊 Original data: {len(df)} rows, {len(df.columns)} columns")

    # Clean or_rating column - replace "-" with NULL
    if "or_rating" in df.columns:
        before_count = (df["or_rating"] == "-").sum()
        df["or_rating"] = df["or_rating"].replace("-", None)
        print(f"🔧 Fixed {before_count} '-' values in or_rating column")

    # Clean any other numeric columns that might have "-" values
    numeric_columns = ["position", "age", "weight", "ts", "rpr", "odds", "sp"]
    for col in numeric_columns:
        if col in df.columns:
            before_count = (df[col] == "-").sum()
            if before_count > 0:
                df[col] = df[col].replace("-", None)
                print(f"🔧 Fixed {before_count} '-' values in {col} column")

    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"✅ Cleaned data saved: {output_file}")
    print(f"📊 Final data: {len(df)} rows, {len(df.columns)} columns")
    return df


def clean_races_data(input_file, output_file):
    """Clean the races CSV file for database upload"""
    print(f"🧹 Cleaning races data: {input_file}")

    # Read the CSV
    df = pd.read_csv(input_file)
    print(f"📊 Original data: {len(df)} rows, {len(df.columns)} columns")

    # Remove any duplicates based on race_id
    before_count = len(df)
    df = df.drop_duplicates(subset=["race_id"], keep="first")
    after_count = len(df)
    if before_count != after_count:
        print(f"🔧 Removed {before_count - after_count} duplicate races")

    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"✅ Cleaned data saved: {output_file}")
    print(f"📊 Final data: {len(df)} rows, {len(df.columns)} columns")
    return df


def main():
    """Main cleaning function"""
    print("🚀 Starting data cleaning process...")

    # Clean records data
    records_df = clean_records_data(
        "data/daily_downloads/mapped_records.csv",
        "data/daily_downloads/cleaned_records.csv",
    )

    # Clean races data
    races_df = clean_races_data(
        "data/daily_downloads/mapped_races.csv",
        "data/daily_downloads/cleaned_races.csv",
    )

    print("\n📊 Data Cleaning Summary:")
    print(f"✅ Records: {len(records_df)} rows cleaned")
    print(f"✅ Races: {len(races_df)} rows cleaned")
    print("🎉 Data cleaning completed!")


if __name__ == "__main__":
    main()
