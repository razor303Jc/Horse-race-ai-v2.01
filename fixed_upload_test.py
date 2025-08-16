#!/usr/bin/env python3
"""
Fixed CSV Upload - Based on test framework discoveries
Handles the specific data type issues found during testing
"""

import re

import pandas as pd
import psycopg2


def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def convert_uk_weight(weight_str):
    """Convert UK weight format like '9-9' to numeric"""
    if pd.isna(weight_str) or weight_str == "":
        return 0.0

    weight_str = str(weight_str).strip()

    # Handle formats like "9-9" (9 stones 9 pounds)
    if "-" in weight_str:
        try:
            parts = weight_str.split("-")
            stones = int(parts[0])
            pounds = int(parts[1]) if len(parts) > 1 else 0
            # Convert to total pounds (1 stone = 14 pounds)
            total_pounds = (stones * 14) + pounds
            return float(total_pounds)
        except:
            return 0.0

    # Handle direct numeric values
    try:
        return float(weight_str)
    except:
        return 0.0


def convert_fav_position(fav_str):
    """Convert favorite position like '1st', '2nd' to integer"""
    if pd.isna(fav_str) or fav_str == "":
        return 0

    fav_str = str(fav_str).strip().lower()

    # Extract number from position strings
    if "st" in fav_str or "nd" in fav_str or "rd" in fav_str or "th" in fav_str:
        # Extract number from '1st', '2nd', etc.
        match = re.match(r"(\d+)", fav_str)
        if match:
            return int(match.group(1))

    # Handle direct numbers
    try:
        return int(float(fav_str))
    except:
        return 0


def upload_records_fixed():
    """Upload records with proper data type handling"""
    print("🧪 Fixed CSV Upload - Based on Test Framework Discoveries")
    print("=" * 60)

    csv_file = "data/daily_downloads/results_data/racecard_details/racecard_details.csv"
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} rows")

    # Test the data conversion functions first
    print("\n🔧 Testing data conversions...")
    test_weights = ["9-9", "10-2", "8-11", "11-0", "NaN", ""]
    for w in test_weights:
        converted = convert_uk_weight(w)
        print(f"   Weight '{w}' → {converted}")

    test_favs = ["1st", "2nd", "3rd", "4th", "5", "NaN", ""]
    for f in test_favs:
        converted = convert_fav_position(f)
        print(f"   Fav '{f}' → {converted}")

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear table
        cursor.execute("DELETE FROM records")
        print("\n🧹 Cleared records table")

        # Column mapping with data type handling
        column_mapping = {
            "id": "record_id",
            "race_id": "race_id",
            "horse_number": "horse_number",
            "Draw": "draw",
            "Horse_ID": "horse_id",
            "Country": "country",
            "Name": "horse",
            "Age": "age",
            "weight_uk": "weight_uk",  # Will convert UK format
            "weight": "weight",
            "gears": "gears",
            "Horse_rate": "or_rating",
            "jockey_ID": "jockey_id",
            "jockey": "jockey",
            "trainer_ID": "trainer_id",
            "trainer": "trainer",
            "fav": "fav",  # Will convert position format
        }

        uploaded = 0
        errors = 0

        print(f"\n🚀 Uploading {len(df)} records with data type fixes...")

        for i, row in df.iterrows():
            try:
                values = []
                columns = []

                for csv_col, db_col in column_mapping.items():
                    if csv_col not in df.columns:
                        continue

                    val = row[csv_col]

                    # Apply specific data type conversions
                    if db_col == "weight_uk":
                        val = convert_uk_weight(val)
                    elif db_col == "fav":
                        val = convert_fav_position(val)
                    elif pd.isna(val):
                        # Handle NaN values by column type
                        if db_col in [
                            "horse_number",
                            "draw",
                            "horse_id",
                            "age",
                            "or_rating",
                            "jockey_id",
                            "trainer_id",
                        ]:
                            val = 0
                        elif db_col in ["weight", "weight_uk"]:
                            val = 0.0
                        else:
                            val = "none"

                    columns.append(db_col)
                    values.append(val)

                # Insert row
                placeholders = ", ".join(["%s"] * len(values))
                sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                uploaded += 1

                # Progress indicator
                if uploaded % 100 == 0:
                    print(f"   📊 Uploaded {uploaded}/{len(df)} rows...")

            except Exception as e:
                errors += 1
                if errors <= 5:  # Show first 5 errors
                    print(f"   ⚠️ Row {i} error: {e}")
                continue

        conn.commit()
        print(f"\n✅ Upload completed!")
        print(f"   📊 Successfully uploaded: {uploaded} records")
        print(f"   ⚠️ Errors: {errors} records")

        # Verify final count
        cursor.execute("SELECT COUNT(*) FROM records")
        final_count = cursor.fetchone()[0]
        print(f"   🗄️ Database verification: {final_count} records")

        # Show sample data
        cursor.execute(
            "SELECT record_id, race_id, horse, age, weight_uk, fav FROM records LIMIT 3"
        )
        samples = cursor.fetchall()
        print(f"\n📋 Sample data:")
        for sample in samples:
            print(f"   {sample}")

        return final_count > 0

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    success = upload_records_fixed()
    if success:
        print("\n🎉 SUCCESS! Data type issues fixed, records uploaded!")
        print("ML training should now have access to properly formatted data")
    else:
        print("\n❌ FAILED! Still need more debugging")
