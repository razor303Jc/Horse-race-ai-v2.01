#!/usr/bin/env python3
"""
Upload Fresh Data to Recovered Database Schema
Compatible with the actual recovered database column structure
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
        clean_str = re.sub(r"(st|nd|rd|th)$", "", str(fav_str))
        return int(clean_str)
    except (ValueError, TypeError, AttributeError):
        return 0


def clean_data_value(value: Any, data_type: str) -> Any:
    """Clean data value using git history patterns"""

    if pd.isna(value) or value == "" or value == "-" or value is None:
        if data_type == "integer":
            return 0
        elif data_type == "float":
            return 0.0
        else:
            return "none"

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


def upload_fresh_records():
    """Upload fresh records data to recovered database schema"""

    print("🚀 Uploading Fresh Records to Recovered Database...")

    # Load CSV
    df = pd.read_csv("./data/daily_downloads/cards_data/records/records.csv")
    print(f"📊 Loaded {len(df)} fresh records from CSV")

    # Column mapping for recovered database schema
    # CSV columns -> Database columns
    column_mapping = {
        "ID": "record_id",  # integer
        "Race_ID": "race_id",  # integer
        "Place": "position",  # integer
        "Name": "horse",  # text
        "Age": "age",  # integer
        "weight": "weight",  # float (use kg weight, not UK format)
        "jockey": "jockey",  # text
        "trainer": "trainer",  # text
        "Horse_rate": "or_rating",  # integer
        "fav": "fav",  # integer (convert from 1st, 2nd format)
        "SP": "sp",  # float
    }

    # Data type definitions
    integer_columns = ["record_id", "race_id", "position", "age", "or_rating", "fav"]
    float_columns = ["weight", "sp"]

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    try:
        # Get current count
        cursor.execute("SELECT COUNT(*) FROM records")
        before_count = cursor.fetchone()[0]
        print(f"📋 Current records in database: {before_count}")

        uploaded = 0
        errors = 0

        for i, row in df.iterrows():
            try:
                values = []
                columns = []

                for csv_col, db_col in column_mapping.items():
                    if csv_col not in df.columns:
                        continue

                    val = row[csv_col]

                    # Special handling for specific columns
                    if db_col == "fav":
                        val = convert_fav_position(val)
                    elif db_col in integer_columns:
                        val = clean_data_value(val, "integer")
                    elif db_col in float_columns:
                        val = clean_data_value(val, "float")
                    else:
                        val = clean_data_value(val, "string")

                    columns.append(db_col)
                    values.append(val)

                # Add default values for missing columns in recovered schema
                if "ts" not in columns:
                    columns.append("ts")
                    values.append(0)
                if "rpr" not in columns:
                    columns.append("rpr")
                    values.append(0)
                if "odds" not in columns:
                    columns.append("odds")
                    values.append(0.0)
                if "extra" not in columns:
                    columns.append("extra")
                    values.append("none")

                # Insert row (ignore conflicts for duplicates)
                placeholders = ", ".join(["%s"] * len(values))
                sql = f"""
                INSERT INTO records ({', '.join(columns)}) 
                VALUES ({placeholders}) 
                ON CONFLICT (record_id) DO NOTHING
                """

                cursor.execute(sql, values)
                uploaded += 1

                if uploaded % 50 == 0:
                    print(f"   ✅ Uploaded {uploaded} records...")

            except Exception as e:
                errors += 1
                if errors <= 3:  # Show first few errors
                    print(f"❌ Row {i+1} error: {e}")
                if errors > 20:  # Stop if too many errors
                    break
                continue

        conn.commit()

        # Get final count
        cursor.execute("SELECT COUNT(*) FROM records")
        after_count = cursor.fetchone()[0]
        new_records = after_count - before_count

        print(f"\n🎉 UPLOAD COMPLETE!")
        print(f"📊 Records before: {before_count:,}")
        print(f"📊 Records after:  {after_count:,}")
        print(f"📈 New records:    {new_records:,}")
        print(f"❌ Errors:        {errors}")

        # Show sample of new data
        cursor.execute(
            "SELECT horse, fav, weight, or_rating FROM records ORDER BY record_id DESC LIMIT 3"
        )
        samples = cursor.fetchall()
        print(f"\n📋 Sample new records:")
        for sample in samples:
            print(
                f"   Horse: {sample[0]}, Fav: {sample[1]}, Weight: {sample[2]}, Rating: {sample[3]}"
            )

    except Exception as e:
        print(f"💥 Upload failed: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()


def check_ml_training_readiness():
    """Check if database is ready for ML training"""

    print("\n🤖 ML TRAINING READINESS CHECK:")
    print("=" * 40)

    conn = psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )

    cursor = conn.cursor()

    try:
        # Check all tables
        tables = ["records", "races", "horses", "jockeys_stats", "trainers_stats"]
        total_records = 0

        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                total_records += count
                status = "✅" if count > 0 else "⚠️"
                print(f"{status} {table:15}: {count:>7,} records")
            except Exception as e:
                print(f"❌ {table:15}: Error - {e}")

        print("=" * 40)
        print(f"🏆 TOTAL DATABASE: {total_records:>7,} records")

        if total_records > 10000:
            print("✅ Database ready for ML training!")
            return True
        else:
            print("⚠️ Consider adding more data for better ML training")
            return False

    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    upload_fresh_records()
    ml_ready = check_ml_training_readiness()

    if ml_ready:
        print("\n🚀 Ready to start ML training!")
        print("💡 Next step: Run ML training pipeline")
