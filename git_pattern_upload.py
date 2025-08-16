#!/usr/bin/env python3
"""
Complete Data Fix Upload - Correct Column Mapping
Based on actual database schema and CSV headers from git history
"""

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
    """
    Clean data value based on git history patterns
    - If NULL/blank/'-' and int: return 0
    - If NULL/blank/'-' and string: return 'none'
    """

    # Check if value is NULL, blank, or "-"
    if pd.isna(value) or value == "" or value == "-" or value is None:
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"

    # Special handling for specific columns
    if "weight" in column_name.lower() and "uk" in column_name.lower():
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


def upload_records_with_git_pattern():
    """Upload records using the correct column mapping from git history"""

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = None

    try:
        # Load CSV file
        df = pd.read_csv("./data/daily_downloads/cards_data/records/records.csv")
        print(f"📊 Loaded {len(df)} records from CSV")

        # Correct column mapping based on actual schema
        column_mapping = {
            "ID": "record_id",
            "Race_ID": "race_id",
            "Horse_number": "horse_number",
            "Place": "position",
            "Draw": "draw",
            "Horse_ID": "horse_id",
            "Country": "country",
            "Name": "horse",
            "Age": "age",
            "weight_uk": "weight_uk",  # Special conversion
            "weight": "weight",
            "gears": "gears",
            "Horse_rate": "or_rating",
            "jockey_ID": "jockey_id",
            "jockey": "jockey",
            "trainer_ID": "trainer_id",
            "trainer": "trainer",
            "fav": "fav",  # Special conversion
            "SP": "sp",
            "Distance_btn": "distance_btn",
            "Distance_btn_total": "distance_btn_total",
            "distance_sec_1": "distance_sec_1",
            "sectional_time_1": "sectional_time_1",
            "distance_sec_2": "distance_sec_2",
            "sectional_time_2": "sectional_time_2",
            "distance_sec_3": "distance_sec_3",
            "sectional_time_3": "sectional_time_3",
            "distance_sec_4": "distance_sec_4",
            "sectional_time_4": "sectional_time_4",
            "distance_sec_5": "distance_sec_5",
            "sectional_time_5": "sectional_time_5",
            "distance_sec_6": "distance_sec_6",
            "sectional_time_6": "sectional_time_6",
            "distance_sec_7": "distance_sec_7",
            "sectional_time_7": "sectional_time_7",
            "distance_sec_8": "distance_sec_8",
            "sectional_time_8": "sectional_time_8",
            "distance_sec_9": "distance_sec_9",
            "sectional_time_9": "sectional_time_9",
            "distance_sec_10": "distance_sec_10",
            "sectional_time_10": "sectional_time_10",
            "distance_sec_11": "distance_sec_11",
            "sectional_time_11": "sectional_time_11",
            "distance_sec_12": "distance_sec_12",
            "sectional_time_12": "sectional_time_12",
            "distance_sec_13": "distance_sec_13",
            "sectional_time_13": "sectional_time_13",
            "distance_sec_14": "distance_sec_14",
            "sectional_time_14": "sectional_time_14",
            "distance_sec_15": "distance_sec_15",
            "sectional_time_15": "sectional_time_15",
            "distance_sec_16": "distance_sec_16",
            "sectional_time_16": "sectional_time_16",
            "distance_sec_17": "distance_sec_17",
            "sectional_time_17": "sectional_time_17",
            "distance_sec_18": "distance_sec_18",
            "sectional_time_18": "sectional_time_18",
            "finish_time": "finish_time",
            "distance_speed_early_race": "distance_speed_early_race",
            "speed_achieved_early_race": "speed_achieved_early_race",
            "distance_speed_mid_race": "distance_speed_mid_race",
            "speed_achieved_mid_race": "speed_achieved_mid_race",
            "distance_speed_finish_race": "distance_speed_finish_race",
            "speed_achieved_finish_race": "speed_achieved_finish_race",
        }

        # Integer columns based on database schema
        integer_columns = [
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

        # Float columns
        float_columns = [
            "weight_uk",
            "weight",
            "sp",
            "distance_btn",
            "distance_btn_total",
            "distance_sec_1",
            "sectional_time_1",
            "distance_sec_2",
            "sectional_time_2",
            "distance_sec_3",
            "sectional_time_3",
            "distance_sec_4",
            "sectional_time_4",
            "distance_sec_5",
            "sectional_time_5",
            "distance_sec_6",
            "sectional_time_6",
            "distance_sec_7",
            "sectional_time_7",
            "distance_sec_8",
            "sectional_time_8",
            "distance_sec_9",
            "sectional_time_9",
            "distance_sec_10",
            "sectional_time_10",
            "distance_sec_11",
            "sectional_time_11",
            "distance_sec_12",
            "sectional_time_12",
            "distance_sec_13",
            "sectional_time_13",
            "distance_sec_14",
            "sectional_time_14",
            "distance_sec_15",
            "sectional_time_15",
            "distance_sec_16",
            "sectional_time_16",
            "distance_sec_17",
            "sectional_time_17",
            "distance_sec_18",
            "sectional_time_18",
            "finish_time",
            "distance_speed_early_race",
            "speed_achieved_early_race",
            "distance_speed_mid_race",
            "speed_achieved_mid_race",
            "distance_speed_finish_race",
            "speed_achieved_finish_race",
        ]

        cursor = conn.cursor()

        # Clear table like in git history pattern
        cursor.execute("DELETE FROM records")
        print("🧹 Cleared records table")

        uploaded = 0
        errors = 0

        print(f"🚀 Uploading {len(df)} records with complete data fixes...")

        for i, row in df.iterrows():
            try:
                values = []
                columns = []

                for csv_col, db_col in column_mapping.items():
                    if csv_col not in df.columns:
                        continue

                    val = row[csv_col]

                    # Determine data type
                    if db_col in integer_columns:
                        data_type = "integer"
                    elif db_col in float_columns:
                        data_type = "float"
                    else:
                        data_type = "string"

                    # Clean the value using git history patterns
                    cleaned_val = clean_data_value(val, db_col, data_type)

                    columns.append(db_col)
                    values.append(cleaned_val)

                # Insert row
                placeholders = ", ".join(["%s"] * len(values))
                sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, values)

                uploaded += 1

                if uploaded % 50 == 0:
                    print(f"   ✅ Uploaded {uploaded} records...")

            except Exception as e:
                errors += 1
                print(f"❌ Row {i+1} error: {e}")
                if errors > 10:  # Stop if too many errors
                    break
                continue

        conn.commit()
        print(f"\n🎉 SUCCESS! Uploaded {uploaded} records (Errors: {errors})")

        # Verify the upload
        cursor.execute("SELECT COUNT(*) FROM records")
        total_count = cursor.fetchone()[0]
        print(f"📊 Total records in database: {total_count}")

        # Show sample of the data
        cursor.execute("SELECT horse, fav, weight_uk, or_rating FROM records LIMIT 5")
        samples = cursor.fetchall()
        print("📋 Sample data:")
        for sample in samples:
            print(f"   {sample}")

    except Exception as e:
        print(f"💥 Upload failed: {e}")
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    upload_records_with_git_pattern()
