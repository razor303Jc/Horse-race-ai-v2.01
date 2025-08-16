#!/usr/bin/env python3
"""
Complete Fresh Data Upload - All CSV Files
Upload all fresh download data from August 15th to add to recovered database
"""

import re
from pathlib import Path
from typing import Any, Dict, List

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
    """Clean data value using git history patterns"""

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


def upload_records_data():
    """Upload records.csv data"""
    print("📊 Uploading Records Data...")

    csv_path = "./data/daily_downloads/cards_data/records/records.csv"
    df = pd.read_csv(csv_path)

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
        "weight_uk": "weight_uk",
        "weight": "weight",
        "gears": "gears",
        "Horse_rate": "or_rating",
        "jockey_ID": "jockey_id",
        "jockey": "jockey",
        "trainer_ID": "trainer_id",
        "trainer": "trainer",
        "fav": "fav",
        "SP": "sp",
        "Distance_btn": "distance_btn",
        "Distance_btn_total": "distance_btn_total",
    }

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

    float_columns = ["weight_uk", "weight", "sp", "distance_btn", "distance_btn_total"]

    return upload_csv_data(
        df, "records", column_mapping, integer_columns, float_columns
    )


def upload_races_data():
    """Upload both races CSV files"""
    print("📊 Uploading Races Data...")

    # Cards data races
    cards_path = "./data/daily_downloads/cards_data/races/races.csv"
    results_path = "./data/daily_downloads/results_data/races/races.csv"

    uploaded_total = 0

    for path, source in [(cards_path, "cards"), (results_path, "results")]:
        print(f"   Processing {source} races...")
        df = pd.read_csv(path)

        # Basic races column mapping
        column_mapping = {}
        for col in df.columns:
            # Map CSV columns to database columns (lowercase, replace spaces with _)
            db_col = col.lower().replace(" ", "_").replace("-", "_")
            column_mapping[col] = db_col

        # Auto-detect integer and float columns
        integer_columns = []
        float_columns = []

        for col in df.columns:
            sample_data = df[col].dropna().head(10)
            if len(sample_data) > 0:
                try:
                    # Try to convert to numeric
                    pd.to_numeric(sample_data)
                    if sample_data.dtype in ["int64", "int32"]:
                        integer_columns.append(column_mapping[col])
                    else:
                        float_columns.append(column_mapping[col])
                except:
                    pass  # String column

        count = upload_csv_data(
            df,
            "races",
            column_mapping,
            integer_columns,
            float_columns,
            ignore_conflicts=True,
        )
        uploaded_total += count

    return uploaded_total


def upload_horses_data():
    """Upload both horses CSV files"""
    print("📊 Uploading Horses Data...")

    cards_path = "./data/daily_downloads/cards_data/horses/horses.csv"
    results_path = "./data/daily_downloads/results_data/horses/horses.csv"

    uploaded_total = 0

    for path, source in [(cards_path, "cards"), (results_path, "results")]:
        print(f"   Processing {source} horses...")
        df = pd.read_csv(path)

        # Basic horses column mapping
        column_mapping = {}
        for col in df.columns:
            db_col = col.lower().replace(" ", "_").replace("-", "_")
            column_mapping[col] = db_col

        # Auto-detect data types
        integer_columns = []
        float_columns = []

        for col in df.columns:
            sample_data = df[col].dropna().head(10)
            if len(sample_data) > 0:
                try:
                    pd.to_numeric(sample_data)
                    if sample_data.dtype in ["int64", "int32"]:
                        integer_columns.append(column_mapping[col])
                    else:
                        float_columns.append(column_mapping[col])
                except:
                    pass

        count = upload_csv_data(
            df,
            "horses",
            column_mapping,
            integer_columns,
            float_columns,
            ignore_conflicts=True,
        )
        uploaded_total += count

    return uploaded_total


def upload_csv_data(
    df: pd.DataFrame,
    table_name: str,
    column_mapping: Dict,
    integer_columns: List,
    float_columns: List,
    ignore_conflicts: bool = False,
):
    """Generic CSV upload function with data cleaning"""

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()
    uploaded = 0

    try:
        # Check if table exists
        cursor.execute(f"SELECT to_regclass('public.{table_name}')")
        table_exists = cursor.fetchone()[0] is not None

        if not table_exists:
            print(f"   ⚠️ Table {table_name} doesn't exist, skipping...")
            return 0

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

                    # Clean the value
                    cleaned_val = clean_data_value(val, db_col, data_type)

                    columns.append(db_col)
                    values.append(cleaned_val)

                # Insert row
                placeholders = ", ".join(["%s"] * len(values))

                if ignore_conflicts:
                    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders}) ON CONFLICT DO NOTHING"
                else:
                    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

                cursor.execute(sql, values)
                uploaded += 1

                if uploaded % 100 == 0:
                    print(f"   ✅ Uploaded {uploaded} {table_name} records...")

            except Exception as e:
                if (
                    "duplicate key" in str(e).lower()
                    or "already exists" in str(e).lower()
                ):
                    continue  # Skip duplicates
                else:
                    print(f"❌ Row {i+1} error: {e}")
                    continue

        conn.commit()
        print(f"   🎉 Successfully uploaded {uploaded} {table_name} records!")

    except Exception as e:
        print(f"💥 {table_name} upload failed: {e}")
        conn.rollback()
        uploaded = 0

    finally:
        cursor.close()
        conn.close()

    return uploaded


def upload_all_fresh_data():
    """Upload all fresh CSV data from August 15th downloads"""

    print("🚀 UPLOADING ALL FRESH DATA FROM AUGUST 15th")
    print("=" * 50)

    total_uploaded = 0

    # Upload in order of dependencies
    total_uploaded += upload_races_data()
    total_uploaded += upload_horses_data()
    total_uploaded += upload_records_data()

    # Final database summary
    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    print("\n📊 FINAL DATABASE STATE:")
    print("=" * 30)

    tables = ["races", "horses", "records", "jockeys_stats", "trainers_stats"]
    grand_total = 0

    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            grand_total += count
            print(f"📋 {table:15}: {count:>7,} records")
        except:
            print(f"📋 {table:15}: Table not found")

    print("=" * 30)
    print(f"🏆 TOTAL DATABASE: {grand_total:>7,} records")
    print(f"📈 FRESH UPLOADS:  {total_uploaded:>7,} records")

    cursor.close()
    conn.close()

    print("\n✅ Ready for ML Training!")


if __name__ == "__main__":
    upload_all_fresh_data()
