#!/usr/bin/env python3
"""
Data Cleaner - Fix data type issues before database upload
Enhanced with comprehensive dash/hyphen symbol handling
"""

import pandas as pd
import re
import json
from pathlib import Path


def load_column_type_mapping():
    """Load data type configuration from mapping file"""
    config_file = (
        Path(__file__).parent.parent.parent
        / "config"
        / "complete_csv_column_mapping.json"
    )
    try:
        with open(config_file, "r") as f:
            config = json.load(f)
        return config["table_mappings"]
    except Exception as e:
        print(f"⚠️ Could not load column mapping: {e}")
        return {}


def clean_dash_symbols(df, table_name):
    """
    🔧 ENHANCED: Clean dash/hyphen symbols based on data type
    - Numeric fields (int/decimal): "-" → 0
    - String fields: "-" → "None"
    - Weight fields: "10-2" → "10.2" (stones-pounds format)
    """
    print(f"🧹 Cleaning dash symbols for {table_name}...")

    # Load data type configuration
    type_mapping = load_column_type_mapping()
    table_config = type_mapping.get(table_name, {}).get("null_handling", {})

    integer_fields = table_config.get("integers", [])
    decimal_fields = table_config.get("decimals", [])
    string_fields = table_config.get("strings", [])

    cleaned_count = 0

    for column in df.columns:
        if column in df.columns:
            # Handle weight_uk specially (UK format like "10-2")
            if column == "weight_uk":
                # Convert UK weight format "10-2" to "10.2"
                mask = df[column].astype(str).str.match(r"^\d+-\d+$")
                df.loc[mask, column] = (
                    df.loc[mask, column].astype(str).str.replace("-", ".")
                )
                cleaned_count += mask.sum()

                # Convert standalone "-" to 0 for weight
                standalone_dash = df[column].astype(str) == "-"
                df.loc[standalone_dash, column] = 0
                cleaned_count += standalone_dash.sum()

            elif column in integer_fields:
                # Integer fields: "-" → 0
                dash_mask = df[column].astype(str) == "-"
                df.loc[dash_mask, column] = 0
                cleaned_count += dash_mask.sum()

            elif column in decimal_fields:
                # Decimal fields: "-" → 0
                dash_mask = df[column].astype(str) == "-"
                df.loc[dash_mask, column] = 0
                cleaned_count += dash_mask.sum()

            elif column in string_fields:
                # String fields: "-" → "None"
                dash_mask = df[column].astype(str) == "-"
                df.loc[dash_mask, column] = "None"
                cleaned_count += dash_mask.sum()

    if cleaned_count > 0:
        print(f"  ✅ Cleaned {cleaned_count} dash symbols across all columns")

    return df


def clean_percentage_fields(df, percentage_columns):
    """Convert percentage strings like '16.67%' to decimal numbers"""
    for col in percentage_columns:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace("%", "").replace("nan", "0")
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0) / 100
    return df


def clean_races_data():
    """Clean races data - fix draw field with 'Low' values and dash symbols"""
    print("🧹 Cleaning races data...")

    file_path = Path("data/daily_downloads/complete_mapped_races.csv")
    df = pd.read_csv(file_path)

    print(f"Original: {len(df)} rows")

    # Step 1: Clean dash symbols based on data types
    df = clean_dash_symbols(df, "races")

    # Fix draw field - convert 'Low' to 0 or NULL
    if "draw" in df.columns:
        # Replace 'Low' with 0, convert to numeric
        df["draw"] = df["draw"].replace("Low", 0)
        df["draw"] = pd.to_numeric(df["draw"], errors="coerce").fillna(0).astype(int)
        print("✅ Fixed draw field (converted 'Low' to 0)")

    # Clean any other integer fields
    integer_fields = [
        "race_number",
        "course_id",
        "runners_racecard",
        "runners",
        "ew_racecard",
        "ew",
        "places_ew_racecard",
        "places_ew",
    ]

    for field in integer_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0).astype(int)

    # Save cleaned data
    df.to_csv(file_path, index=False)
    print(f"✅ Cleaned races data saved: {len(df)} rows")


def clean_records_data():
    """Clean records data - handle missing columns, data types, and dash symbols"""
    print("🧹 Cleaning records data...")

    file_path = Path("data/daily_downloads/complete_mapped_records.csv")
    df = pd.read_csv(file_path)

    print(f"Original: {len(df)} rows, {len(df.columns)} columns")

    # Step 1: Clean dash symbols based on data types
    df = clean_dash_symbols(df, "records")

    # Remove columns that don't exist in database
    columns_to_remove = []
    for col in df.columns:
        if "odds" in col.lower() and col not in ["sp"]:  # Remove odds columns
            columns_to_remove.append(col)
        elif col in [
            "result_race_id",
            "result_horse_number",
            "result_id",
            "timeform_comments",
        ]:
            columns_to_remove.append(col)  # Remove columns not in database schema

    if columns_to_remove:
        df = df.drop(columns=columns_to_remove)
        print(f"✅ Removed non-existent columns: {columns_to_remove}")

    # Fix numeric fields
    numeric_fields = [
        "record_id",
        "race_id",
        "horse_number",
        "position",
        "draw",
        "horse_id",
        "age",
        "or_rating",
        "jockey_id",
        "trainer_id",
        "fav",
    ]

    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    # Note: weight_uk dash handling is done in clean_dash_symbols function
    if "weight_uk" in df.columns:
        df["weight_uk"] = pd.to_numeric(df["weight_uk"], errors="coerce").fillna(0)

    # Fix distance fields - convert fractions to decimals
    distance_fields = ["distance_btn", "distance_btn_total"]
    for field in distance_fields:
        if field in df.columns:
            df[field] = df[field].astype(str)
            df[field] = df[field].str.replace("½", "0.5")
            df[field] = df[field].str.replace("¼", "0.25")
            df[field] = df[field].str.replace("¾", "0.75")
            df[field] = df[field].str.replace("nk", "0.1")  # neck
            df[field] = df[field].str.replace("hd", "0.05")  # head
            df[field] = df[field].str.replace("sh", "0.01")  # short head
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    # Handle SP (starting price) field
    if "sp" in df.columns:
        df["sp"] = pd.to_numeric(df["sp"], errors="coerce").fillna(0)

    # Save cleaned data
    df.to_csv(file_path, index=False)
    print(f"✅ Cleaned records data saved: {len(df)} rows, {len(df.columns)} columns")


def clean_horses_data():
    """Clean horses data - fix percentage fields and dash symbols"""
    print("🧹 Cleaning horses data...")

    file_path = Path("data/daily_downloads/complete_mapped_horses.csv")
    df = pd.read_csv(file_path)

    print(f"Original: {len(df)} rows")

    # Step 1: Clean dash symbols based on data types
    df = clean_dash_symbols(df, "horses")

    # Fix percentage fields
    percentage_cols = [
        "percentage_wins",
        "percentage_placed",
        "flat_aw_rate",
        "flat_aw_placed_rate",
        "flat_turf_rate",
        "flat_turf_placed_rate",
        "chase_rate",
        "chase_placed_rate",
        "hurdle_rate",
        "hurdle_placed_rate",
    ]

    df = clean_percentage_fields(df, percentage_cols)
    print("✅ Fixed percentage fields")

    # Fix numeric fields
    numeric_fields = [
        "horse_id",
        "race_id_last_race",
        "age",
        "total_races",
        "wins",
        "placed",
        "flat_aw_races",
        "flat_aw_wins",
        "flat_aw_placed",
        "flat_turf_races",
        "flat_turf_wins",
        "flat_turf_placed",
        "chase_races",
        "chase_wins",
        "chase_placed",
        "hurdle_races",
        "hurdle_wins",
        "hurdle_placed",
    ]

    for field in numeric_fields:
        if field in df.columns:
            df[field] = pd.to_numeric(df[field], errors="coerce").fillna(0)

    # Save cleaned data
    df.to_csv(file_path, index=False)
    print(f"✅ Cleaned horses data saved: {len(df)} rows")


def clean_jockeys_stats():
    """Clean jockeys stats data - fix percentage fields and dash symbols"""
    print("🧹 Cleaning jockeys stats data...")

    file_path = Path("data/daily_downloads/complete_mapped_jockeys_stats.csv")
    df = pd.read_csv(file_path)

    print(f"Original: {len(df)} rows")

    # Step 1: Clean dash symbols based on data types
    df = clean_dash_symbols(df, "jockeys_stats")

    # Fix percentage fields
    percentage_cols = [
        "percentage_wins",
        "percentage_placed",
        "flat_aw_rate",
        "flat_aw_placed_rate",
        "flat_turf_rate",
        "flat_turf_placed_rate",
        "chase_rate",
        "chase_placed_rate",
        "hurdle_rate",
        "hurdle_placed_rate",
    ]

    df = clean_percentage_fields(df, percentage_cols)
    print("✅ Fixed percentage fields")

    # Save cleaned data
    df.to_csv(file_path, index=False)
    print(f"✅ Cleaned jockeys stats saved: {len(df)} rows")


def clean_trainers_stats():
    """Clean trainers stats data - fix percentage fields and dash symbols"""
    print("🧹 Cleaning trainers stats data...")

    file_path = Path("data/daily_downloads/complete_mapped_trainers_stats.csv")
    df = pd.read_csv(file_path)

    print(f"Original: {len(df)} rows")

    # Step 1: Clean dash symbols based on data types
    df = clean_dash_symbols(df, "trainers_stats")

    # Fix percentage fields
    percentage_cols = [
        "percentage_wins",
        "percentage_placed",
        "flat_aw_rate",
        "flat_aw_placed_rate",
        "flat_turf_rate",
        "flat_turf_placed_rate",
        "chase_rate",
        "chase_placed_rate",
        "hurdle_rate",
        "hurdle_placed_rate",
    ]

    df = clean_percentage_fields(df, percentage_cols)
    print("✅ Fixed percentage fields")

    # Save cleaned data
    df.to_csv(file_path, index=False)
    print(f"✅ Cleaned trainers stats saved: {len(df)} rows")


def main():
    print("🧹 Data Cleaner - Fixing Data Type Issues")
    print("=" * 50)

    clean_races_data()
    clean_records_data()
    clean_horses_data()
    clean_jockeys_stats()
    clean_trainers_stats()

    print("\n🎉 All data cleaned and ready for upload!")


if __name__ == "__main__":
    main()
