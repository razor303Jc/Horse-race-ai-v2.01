#!/usr/bin/env python3
"""
Safe Upload - Handle Duplicates and Separate Transactions
Upload with INSERT ON CONFLICT and separate transactions per table
"""

import os
import re
from typing import Any

import pandas as pd
import psycopg2


def convert_uk_weight(weight_str: str) -> float:
    """Convert UK weight format like '9-9' to decimal"""
    if pd.isna(weight_str) or weight_str in ["", "-", "none", None]:
        return 0.0

    try:
        if "-" in str(weight_str) and str(weight_str) != "-":
            parts = str(weight_str).split("-")
            if len(parts) == 2:
                stones = float(parts[0])
                pounds = float(parts[1])
                return stones + (pounds / 14)
        return float(weight_str)
    except (ValueError, TypeError, AttributeError):
        return 0.0


def convert_fav_position(fav_str: str) -> int:
    """Convert favorite position like '1st', '2nd' to integer"""
    if pd.isna(fav_str) or fav_str in ["", "-", "none", None]:
        return 0

    try:
        # Remove 'st', 'nd', 'rd', 'th' suffixes
        clean_str = re.sub(r"(st|nd|rd|th)$", "", str(fav_str))
        return int(clean_str)
    except (ValueError, TypeError, AttributeError):
        return 0


def clean_data_value(value: Any, column_name: str, data_type: str) -> Any:
    """Clean data value using NULL/blank/'-' pattern"""

    # Check if value is NULL, blank, or "-"
    if pd.isna(value) or value == "" or value == "-" or value is None:
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"

    # Special handling for specific columns
    if "weight_uk" in column_name.lower():
        return convert_uk_weight(value)

    if column_name == "fav":
        return convert_fav_position(value)

    # Type conversion with fallbacks
    try:
        if data_type == "integer":
            return int(float(str(value)))
        elif data_type == "float":
            return float(str(value))
        else:
            return str(value)
    except (ValueError, TypeError):
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"


def get_column_types(table_name: str):
    """Get data types for each table's columns"""

    integer_columns = {
        "races": [
            "race_number",
            "course_id",
            "Runners_racecard",
            "Runners",
            "Draw",
            "EW_racecard",
            "EW",
            "Places_EW_racecard",
            "Places_EW",
        ],
        "records": ["Horse_number", "Place", "Draw", "Age", "Horse_rate", "fav"],
        "horses": [
            "age",
            "Total_races",
            "Wins",
            "placed",
            "Flat_AW_races",
            "Flat_AW_wins",
            "Flat_AW_placed",
            "Flat_Turf_races",
            "Flat_Turf_wins",
            "Flat_Turf_placed",
            "Chase_races",
            "Chase_wins",
            "Chase_placed",
            "Hurdle_races",
            "Hurdle_wins",
            "Hurdle_placed",
        ],
        "jockeys_stats": [
            "Total_races",
            "Wins",
            "Placed",
            "Flat_AW_races",
            "Flat_AW_wins",
            "Flat_AW_placed",
            "Flat_Turf_races",
            "Flat_Turf_wins",
            "Flat_Turf_placed",
            "Chase_races",
            "Chase_wins",
            "Chase_placed",
            "Hurdle_races",
            "Hurdle_wins",
            "Hurdle_placed",
        ],
        "trainers_stats": [
            "Total_races",
            "Wins",
            "Placed",
            "Flat_AW_races",
            "Flat_AW_wins",
            "Flat_AW_placed",
            "Flat_Turf_races",
            "Flat_Turf_wins",
            "Flat_Turf_placed",
            "Chase_races",
            "Chase_wins",
            "Chase_placed",
            "Hurdle_races",
            "Hurdle_wins",
            "Hurdle_placed",
        ],
        "racecard_details": ["horse_number", "Draw", "Age", "Horse_rate", "fav"],
    }

    float_columns = {
        "races": [],
        "records": ["weight_uk", "weight", "SP", "Distance_btn", "Distance_btn_total"]
        + [f"distance_sec_{i}" for i in range(1, 19)]
        + [f"sectional_time_{i}" for i in range(1, 19)]
        + [
            "finish_time",
            "distance_speed_early_race",
            "speed_achieved_early_race",
            "distance_speed_mid_race",
            "speed_achieved_mid_race",
            "distance_speed_finish_race",
            "speed_achieved_finish_race",
        ],
        "horses": [
            "Percentage_wins",
            "Percentage_placed",
            "Flat_AW_rate",
            "Flat_AW_placed_rate",
            "Flat_Turf_rate",
            "Flat_Turf_placed_rate",
            "Chase_rate",
            "Chase_placed_rate",
            "Hurdle_rate",
            "Hurdle_placed_rate",
        ],
        "jockeys_stats": [
            "Percentage_wins",
            "Percentage_placed",
            "Flat_AW_rate",
            "Flat_AW_placed_rate",
            "Flat_Turf_rate",
            "Flat_Turf_placed_rate",
            "Chase_rate",
            "Chase_placed_rate",
            "Hurdle_rate",
            "Hurdle_placed_rate",
        ],
        "trainers_stats": [
            "Percentage_wins",
            "Percentage_placed",
            "Flat_AW_rate",
            "Flat_AW_placed_rate",
            "Flat_Turf_rate",
            "Flat_Turf_placed_rate",
            "Chase_rate",
            "Chase_placed_rate",
            "Hurdle_rate",
            "Hurdle_placed_rate",
        ],
        "racecard_details": ["weight_uk", "weight", "odds_decimal"],
    }

    return integer_columns.get(table_name, []), float_columns.get(table_name, [])


def upload_csv_safe(csv_path: str, table_name: str):
    """Upload a single CSV file with safe duplicate handling"""

    if not os.path.exists(csv_path):
        print(f"   ⚠️ File not found: {csv_path}")
        return 0

    # Use separate connection for each table
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    try:
        df = pd.read_csv(csv_path)
        print(f"   📊 Loading {len(df)} records from {os.path.basename(csv_path)}")

        if len(df) == 0:
            print("   ⚠️ Empty file, skipping")
            return 0

        # Get column types for this table
        integer_cols, float_cols = get_column_types(table_name)

        uploaded = 0
        errors = 0

        for i, row in df.iterrows():
            try:
                values = []
                columns = []

                for col in df.columns:
                    val = row[col]

                    # Determine data type
                    if col in integer_cols:
                        data_type = "integer"
                    elif col in float_cols:
                        data_type = "float"
                    else:
                        data_type = "string"

                    # Clean the value
                    cleaned_val = clean_data_value(val, col, data_type)

                    columns.append(col)
                    values.append(cleaned_val)

                # Use INSERT ... ON CONFLICT DO NOTHING for duplicates
                placeholders = ", ".join(["%s"] * len(values))

                # Get primary key column name
                pk_col = (
                    "Race_ID"
                    if table_name == "races"
                    else (
                        "Jockey_ID"
                        if table_name == "jockeys_stats"
                        else ("Trainer_ID" if table_name == "trainers_stats" else "id")
                    )
                )

                sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT ({pk_col}) DO NOTHING"
                cursor.execute(sql, values)

                uploaded += 1

                if uploaded % 100 == 0:
                    print(f"     ✅ Processed {uploaded} records...")

            except Exception as e:
                errors += 1
                if errors <= 3:  # Show first 3 errors
                    print(f"     ❌ Row {i+1} error: {e}")
                if errors > 10:  # Stop if too many errors
                    break
                continue

        conn.commit()
        print(f"   ✅ Successfully processed {uploaded} records (errors: {errors})")
        return uploaded

    except Exception as e:
        print(f"   ❌ Table {table_name} failed: {e}")
        conn.rollback()
        return 0

    finally:
        cursor.close()
        conn.close()


def safe_upload_all():
    """Safe upload all CSV files with separate transactions"""

    print("🚀 Safe upload with duplicate handling...")

    # Define CSV files and their paths
    csv_files = [
        ("./data/daily_downloads/cards_data/races/races.csv", "races"),
        ("./data/daily_downloads/results_data/races/races.csv", "races"),
        ("./data/daily_downloads/cards_data/horses/horses.csv", "horses"),
        ("./data/daily_downloads/results_data/horses/horses.csv", "horses"),
        (
            "./data/daily_downloads/cards_data/jockeys_stats/jockeys_stats.csv",
            "jockeys_stats",
        ),
        (
            "./data/daily_downloads/cards_data/trainers_stats/trainers_stats.csv",
            "trainers_stats",
        ),
        ("./data/daily_downloads/cards_data/records/records.csv", "records"),
        (
            "./data/daily_downloads/results_data/racecard_details/racecard_details.csv",
            "racecard_details",
        ),
    ]

    total_uploaded = 0

    for csv_path, table_name in csv_files:
        print(f"\n📂 Processing {table_name}...")
        uploaded = upload_csv_safe(csv_path, table_name)
        total_uploaded += uploaded

    print(f"\n🎉 Safe upload complete! Total processed: {total_uploaded} records")

    # Show final counts
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )
    cursor = conn.cursor()

    print("\n📊 Final database summary:")
    tables = [
        "races",
        "records",
        "horses",
        "jockeys_stats",
        "trainers_stats",
        "racecard_details",
    ]
    total_records = 0
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        total_records += count
        print(f"   {table:15}: {count:>6,} records")

    print(f"\n🏆 TOTAL DATABASE: {total_records:>6,} records")

    cursor.close()
    conn.close()


if __name__ == "__main__":
    safe_upload_all()
