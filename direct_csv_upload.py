#!/usr/bin/env python3
"""
Direct CSV Upload - Matches actual database schema exactly
"""

import logging
import os

import pandas as pd
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def connect_db():
    return psycopg2.connect(
        host="localhost",
        port=5434,
        database="horse_racing_db",
        user="horse_racing",
        password="secure_password_123",
    )


def upload_races():
    """Upload races data from CSV to database"""
    logger.info("Uploading races data...")

    # Try both potential race CSV files
    csv_files = [
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/cards_data/races/races.csv",
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/results_data/races/races.csv",
    ]

    df = None
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {csv_file} with {len(df)} rows")
            break

    if df is None:
        logger.error("No races CSV file found")
        return False

    # Map CSV columns to database columns (exact match to actual schema)
    column_mapping = {
        "Race_ID": "race_id",  # text
        "race_number": "race_number",  # integer
        "race_time": "race_time",  # text
        "course_id": "course_id",  # integer -> bigint
        "Course": "course",  # text
        "Race_type": "race_type",  # text
        "Date": "date",  # text
        "Race_name": "race_name",  # text
        "Class": "class",  # text
        "Years": "years",  # text
        "Distance": "distance",  # text
        "Surface": "surface",  # text
        "Prize": "prize",  # text
        "Runners_racecard": "runners_racecard",  # integer
        "Runners": "runners",  # integer
        "Draw": "draw",  # integer -> but CSV has "High" values!
        "EW_racecard": "ew_racecard",  # integer
        "EW": "ew",  # integer
        "Places_EW_racecard": "places_ew_racecard",  # integer
        "Places_EW": "places_ew",  # integer
    }

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear existing data
        cursor.execute("DELETE FROM races")
        logger.info("Cleared existing races data")

        # Process each row
        for _, row in df.iterrows():
            values = {}

            for csv_col, db_col in column_mapping.items():
                if csv_col in df.columns:
                    val = row[csv_col]

                    # Handle special cases for integer columns with text values
                    if db_col == "draw" and isinstance(val, str):
                        # Convert "High" to a high number, "Low" to low number
                        if val.lower() == "high":
                            val = 999
                        elif val.lower() == "low":
                            val = 1
                        else:
                            try:
                                val = int(val)
                            except:
                                val = 0

                    # Handle NaN/null values
                    if pd.isna(val):
                        if db_col in [
                            "race_number",
                            "course_id",
                            "runners_racecard",
                            "runners",
                            "draw",
                            "ew_racecard",
                            "ew",
                            "places_ew_racecard",
                            "places_ew",
                        ]:
                            val = 0
                        else:
                            val = "none"

                    values[db_col] = val
                else:
                    # Set default for missing columns
                    if db_col in [
                        "race_number",
                        "course_id",
                        "runners_racecard",
                        "runners",
                        "draw",
                        "ew_racecard",
                        "ew",
                        "places_ew_racecard",
                        "places_ew",
                    ]:
                        values[db_col] = 0
                    else:
                        values[db_col] = "none"

            # Insert row
            columns = list(values.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            sql = f"INSERT INTO races ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(sql, list(values.values()))

        conn.commit()
        logger.info(f"Successfully uploaded {len(df)} races")
        return True

    except Exception as e:
        logger.error(f"Failed to upload races: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def upload_records():
    """Upload records data from CSV to database"""
    logger.info("Uploading records data...")

    # Try both potential record CSV files
    csv_files = [
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/cards_data/records/records.csv",
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/results_data/racecard_details/racecard_details.csv",
    ]

    df = None
    for csv_file in csv_files:
        if os.path.exists(csv_file):
            df = pd.read_csv(csv_file)
            logger.info(f"Loaded {csv_file} with {len(df)} rows")
            # Use the larger file (results usually have more data)
            if df is not None and len(df) > 100:
                break

    if df is None:
        logger.error("No records CSV file found")
        return False

    # Map CSV columns to database columns (based on actual schema)
    # Only map columns that exist in BOTH CSV and database
    if "ID" in df.columns:
        # This is the results records.csv
        column_mapping = {
            "ID": "record_id",  # text
            "Race_ID": "race_id",  # text
            "Horse_number": "horse_number",  # integer
            "Place": "position",  # integer
            "Draw": "draw",  # integer
            "Horse_ID": "horse_id",  # bigint
            "Country": "country",  # text
            "Name": "horse",  # text
            "Age": "age",  # integer
            "weight_uk": "weight_uk",  # numeric
            "weight": "weight",  # numeric
            "gears": "gears",  # text
            "Horse_rate": "or_rating",  # integer
            "jockey_ID": "jockey_id",  # bigint
            "jockey": "jockey",  # text
            "trainer_ID": "trainer_id",  # bigint
            "trainer": "trainer",  # text
            "fav": "fav",  # integer
            "SP": "sp",  # numeric
        }
    else:
        # This is the racecard_details.csv
        column_mapping = {
            "id": "record_id",  # text
            "race_id": "race_id",  # text
            "horse_number": "horse_number",  # integer
            "Draw": "draw",  # integer
            "Horse_ID": "horse_id",  # bigint
            "Country": "country",  # text
            "Name": "horse",  # text
            "Age": "age",  # integer
            "weight_uk": "weight_uk",  # numeric
            "weight": "weight",  # numeric
            "gears": "gears",  # text
            "Horse_rate": "or_rating",  # integer
            "jockey_ID": "jockey_id",  # bigint
            "jockey": "jockey",  # text
            "trainer_ID": "trainer_id",  # bigint
            "trainer": "trainer",  # text
            "fav": "fav",  # integer
        }

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear existing data
        cursor.execute("DELETE FROM records")
        logger.info("Cleared existing records data")

        # Process each row
        for _, row in df.iterrows():
            values = {}

            for csv_col, db_col in column_mapping.items():
                if csv_col in df.columns:
                    val = row[csv_col]

                    # Handle NaN/null values
                    if pd.isna(val):
                        if db_col in [
                            "horse_number",
                            "position",
                            "draw",
                            "horse_id",
                            "age",
                            "or_rating",
                            "jockey_id",
                            "trainer_id",
                            "fav",
                        ]:
                            val = 0
                        elif db_col in ["weight_uk", "weight", "sp"]:
                            val = 0.0
                        else:
                            val = "none"

                    values[db_col] = val
                else:
                    # Set default for missing columns
                    if db_col in [
                        "horse_number",
                        "position",
                        "draw",
                        "horse_id",
                        "age",
                        "or_rating",
                        "jockey_id",
                        "trainer_id",
                        "fav",
                    ]:
                        values[db_col] = 0
                    elif db_col in ["weight_uk", "weight", "sp"]:
                        values[db_col] = 0.0
                    else:
                        values[db_col] = "none"

            # Insert row
            columns = list(values.keys())
            placeholders = ", ".join(["%s"] * len(columns))
            sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({placeholders})"
            cursor.execute(sql, list(values.values()))

        conn.commit()
        logger.info(f"Successfully uploaded {len(df)} records")
        return True

    except Exception as e:
        logger.error(f"Failed to upload records: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def main():
    logger.info("Starting direct CSV upload with correct schema mapping...")

    # Upload both tables
    races_success = upload_races()
    records_success = upload_records()

    if races_success and records_success:
        logger.info("✅ Both tables uploaded successfully!")

        # Show final counts
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM races")
        races_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM records")
        records_count = cursor.fetchone()[0]

        logger.info(f"Database now contains:")
        logger.info(f"  - {races_count} races")
        logger.info(f"  - {records_count} records")

        cursor.close()
        conn.close()
    else:
        logger.error("❌ Upload failed")


if __name__ == "__main__":
    main()
