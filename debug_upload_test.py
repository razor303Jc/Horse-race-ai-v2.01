#!/usr/bin/env python3
"""
Debug CSV Upload - Test the patterns that worked
"""

import os

import pandas as pd
import psycopg2


# Database connection
def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def test_records_upload():
    """Test uploading records data like in the successful patterns"""
    print("🧪 Testing Records Upload Based on Git History Patterns")
    print("=" * 60)

    # Use the larger racecard_details.csv file (537 rows vs 209)
    csv_file = "data/daily_downloads/results_data/racecard_details/racecard_details.csv"

    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return False

    # Read CSV
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} rows from {csv_file}")
    print(f"📝 Columns: {list(df.columns)}")

    # Show sample data
    print(f"\n📋 Sample data:")
    print(df.head(2))

    # Simple column mapping based on what exists in both CSV and database
    column_mapping = {
        "id": "record_id",
        "race_id": "race_id",
        "horse_number": "horse_number",
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
    }

    # Check which columns exist
    available_columns = {}
    missing_columns = []
    for csv_col, db_col in column_mapping.items():
        if csv_col in df.columns:
            available_columns[csv_col] = db_col
        else:
            missing_columns.append(csv_col)

    print(f"\n✅ Available columns: {len(available_columns)}")
    for csv_col, db_col in available_columns.items():
        print(f"   {csv_col} → {db_col}")

    if missing_columns:
        print(f"\n⚠️ Missing columns: {missing_columns}")

    # Upload to database
    conn = connect_db()
    cursor = conn.cursor()

    try:
        print(f"\n🗄️ Uploading to database...")

        # Clear existing records
        cursor.execute("DELETE FROM records")
        print("   🧹 Cleared existing records")

        # Upload data row by row (like the successful patterns)
        uploaded = 0
        for _, row in df.iterrows():
            try:
                values = []
                columns = []

                for csv_col, db_col in available_columns.items():
                    val = row[csv_col]

                    # Handle NaN values
                    if pd.isna(val):
                        if db_col in [
                            "horse_number",
                            "draw",
                            "horse_id",
                            "age",
                            "or_rating",
                            "jockey_id",
                            "trainer_id",
                            "fav",
                        ]:
                            val = 0
                        elif db_col in ["weight_uk", "weight"]:
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

            except Exception as e:
                print(f"   ⚠️ Skipped row {uploaded}: {e}")
                continue

        conn.commit()
        print(f"   ✅ Successfully uploaded {uploaded} records")

        # Verify
        cursor.execute("SELECT COUNT(*) FROM records")
        count = cursor.fetchone()[0]
        print(f"   📊 Database now has {count} records")

        return uploaded > 0

    except Exception as e:
        print(f"   ❌ Upload failed: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    success = test_records_upload()
    if success:
        print("\n🎉 SUCCESS! Records uploaded successfully")
        print("Now the ML training should be able to access the data")
    else:
        print("\n❌ FAILED! Need to debug further")
