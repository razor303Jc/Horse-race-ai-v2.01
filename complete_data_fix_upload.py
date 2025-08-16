#!/usr/bin/env python3
"""
Complete Data Fix Upload - Handles all data type issues found in git history
Based on previous working solutions for NULLs, blanks, and "-" characters
"""

import json
import re
from typing import Any, Dict, List, Union

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
    - Handle special conversions for UK weights and favorites
    """

    # Check if value is NULL, blank, or "-"
    if pd.isna(value) or value == "" or value == "-" or value is None:
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"

    # Special handling for specific columns based on git history
    if "weight" in column_name.lower() and "uk" in column_name.lower():
        return convert_uk_weight(value)

    if "fav" in column_name.lower():
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
        # Fallback to defaults from git history
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"


def upload_records_with_complete_fix():
    """Upload records with complete data handling based on git history"""

    # Database connection
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

        # Column mapping (from git history pattern)
        column_mapping = {
            "racingpostid": "racingpost_id",
            "race_number": "race_number",
            "date": "date",
            "time": "time",
            "course": "course",
            "Horse": "horse_name",
            "Horse_number": "horse_number",
            "finish position": "position",
            "age": "age",
            "Jockey": "jockey",
            "trainer": "trainer",
            "form": "form",
            "favorite": "fav",
            "OR rating": "or_rating",
            "horse_rate": "horse_rate",
            "sp": "sp",
            "distance behind": "distance_btn",
            "distance beaten total": "distance_btn_total",
            "weight (UK)": "weight_uk",
            "weight (kg)": "weight",
            "sectional_time_1f": "sectional_time_1f",
            "sectional_time_2f": "sectional_time_2f",
            "sectional_time_3f": "sectional_time_3f",
            "sectional_time_4f": "sectional_time_4f",
            "sectional_time_5f": "sectional_time_5f",
            "sectional_time_6f": "sectional_time_6f",
            "going": "going",
            "distance_sec_1f": "distance_sec_1f",
            "distance_sec_2f": "distance_sec_2f",
            "distance_sec_3f": "distance_sec_3f",
            "distance_sec_4f": "distance_sec_4f",
            "distance_sec_5f": "distance_sec_5f",
            "distance_sec_6f": "distance_sec_6f",
            "speed_achieved_1f": "speed_achieved_1f",
            "speed_achieved_2f": "speed_achieved_2f",
            "speed_achieved_3f": "speed_achieved_3f",
            "speed_achieved_4f": "speed_achieved_4f",
            "speed_achieved_5f": "speed_achieved_5f",
            "speed_achieved_6f": "speed_achieved_6f",
            "distance_speed_1f": "distance_speed_1f",
            "distance_speed_2f": "distance_speed_2f",
            "distance_speed_3f": "distance_speed_3f",
            "distance_speed_4f": "distance_speed_4f",
            "distance_speed_5f": "distance_speed_5f",
            "distance_speed_6f": "distance_speed_6f",
            "finish_time_1f": "finish_time_1f",
            "finish_time_2f": "finish_time_2f",
            "finish_time_3f": "finish_time_3f",
            "finish_time_4f": "finish_time_4f",
            "finish_time_5f": "finish_time_5f",
            "finish_time_6f": "finish_time_6f",
            "class": "class",
        }

        # Data type mapping based on git history patterns
        integer_columns = [
            "race_number",
            "horse_number",
            "position",
            "age",
            "fav",
            "or_rating",
            "horse_rate",
        ]

        float_columns = [
            "sp",
            "distance_btn",
            "distance_btn_total",
            "weight_uk",
            "weight",
            "sectional_time_1f",
            "sectional_time_2f",
            "sectional_time_3f",
            "sectional_time_4f",
            "sectional_time_5f",
            "sectional_time_6f",
            "distance_sec_1f",
            "distance_sec_2f",
            "distance_sec_3f",
            "distance_sec_4f",
            "distance_sec_5f",
            "distance_sec_6f",
            "speed_achieved_1f",
            "speed_achieved_2f",
            "speed_achieved_3f",
            "speed_achieved_4f",
            "speed_achieved_5f",
            "speed_achieved_6f",
            "distance_speed_1f",
            "distance_speed_2f",
            "distance_speed_3f",
            "distance_speed_4f",
            "distance_speed_5f",
            "distance_speed_6f",
            "finish_time_1f",
            "finish_time_2f",
            "finish_time_3f",
            "finish_time_4f",
            "finish_time_5f",
            "finish_time_6f",
        ]

        print(f"\n🔧 Applying complete data fixes (NULL/blank/'-' handling)...")

        # Process each row with complete data cleaning
        processed_data = []
        error_count = 0

        for index, row in df.iterrows():
            try:
                record_data = {}

                for csv_col, db_col in column_mapping.items():
                    if csv_col in df.columns:
                        raw_value = row[csv_col]

                        # Determine data type
                        if db_col in integer_columns:
                            data_type = "integer"
                        elif db_col in float_columns:
                            data_type = "float"
                        else:
                            data_type = "string"

                        # Clean the value using git history patterns
                        cleaned_value = clean_data_value(raw_value, db_col, data_type)
                        record_data[db_col] = cleaned_value
                    else:
                        # Missing column - use defaults from git history
                        if db_col in integer_columns:
                            record_data[db_col] = 0
                        elif db_col in float_columns:
                            record_data[db_col] = 0.0
                        else:
                            record_data[db_col] = "none"

                processed_data.append(record_data)

            except Exception as e:
                error_count += 1
                print(f"⚠️ Row {index + 1} error: {e}")
                continue

        print(f"✅ Processed {len(processed_data)} records ({error_count} errors)")

        # Upload to database using git history pattern
        cursor = conn.cursor()

        # Get columns for insert
        if processed_data:
            columns = list(processed_data[0].keys())
            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = (
                f"INSERT INTO records ({', '.join(columns)}) VALUES ({placeholders})"
            )

            success_count = 0
            for record in processed_data:
                try:
                    values = [record[col] for col in columns]
                    cursor.execute(insert_sql, values)
                    success_count += 1
                except Exception as e:
                    print(f"❌ Insert error: {e}")
                    print(f"   Problematic values: {record}")
                    break

            conn.commit()
            print(
                f"\n🎉 SUCCESS! Uploaded {success_count} records with complete data fixes!"
            )

            # Show some sample data
            cursor.execute("SELECT COUNT(*) FROM records")
            total_count = cursor.fetchone()[0]
            print(f"📊 Total records in database: {total_count}")

            cursor.execute(
                "SELECT horse_name, fav, weight_uk, horse_rate FROM records LIMIT 5"
            )
            samples = cursor.fetchall()
            print(f"\n📋 Sample data:")
            for sample in samples:
                print(f"   {sample}")

    except Exception as e:
        print(f"💥 Upload failed: {e}")
        conn.rollback()

    finally:
        if cursor:
            cursor.close()
        conn.close()


if __name__ == "__main__":
    upload_records_with_complete_fix()
