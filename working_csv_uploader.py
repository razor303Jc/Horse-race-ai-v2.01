#!/usr/bin/env python3
"""
Working CSV Uploader - Based on successful upload patterns from git history
Uses the correct database schema and table names
"""

import logging
import os

import pandas as pd
import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database connection (corrected port)
DB_CONFIG = {
    "host": "localhost",
    "port": 5434,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


def connect_db():
    return psycopg2.connect(**DB_CONFIG)


def upload_races():
    """Upload races data - this worked before according to upload_report"""
    logger.info("Uploading races data...")

    # Try both race files (use the one that exists)
    race_files = [
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/results_data/races/races.csv",
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/cards_data/races/races.csv",
    ]

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear races table
        cursor.execute("DELETE FROM races")

        total_uploaded = 0
        for race_file in race_files:
            if os.path.exists(race_file):
                df = pd.read_csv(race_file)
                logger.info(f"Processing {race_file}: {len(df)} rows")

                # Use pandas to_sql equivalent with direct SQL
                for _, row in df.iterrows():
                    try:
                        # Insert each row with the CSV column names exactly as they are
                        values = []
                        columns = []

                        # Map only the columns that exist in both CSV and database
                        csv_to_db_mapping = {
                            "Race_ID": "race_id",
                            "race_number": "race_number",
                            "race_time": "race_time",
                            "course_id": "course_id",
                            "Course": "course",
                            "Race_type": "race_type",
                            "Date": "date",
                            "Race_name": "race_name",
                            "Class": "class",
                            "Years": "years",
                            "Distance": "distance",
                            "Surface": "surface",
                            "Prize": "prize",
                            "Runners_racecard": "runners_racecard",
                            "Runners": "runners",
                            "Draw": "draw",
                            "EW_racecard": "ew_racecard",
                            "EW": "ew",
                            "Places_EW_racecard": "places_ew_racecard",
                            "Places_EW": "places_ew",
                        }

                        for csv_col, db_col in csv_to_db_mapping.items():
                            if csv_col in df.columns:
                                val = row[csv_col]

                                # Handle Draw column which can be "High", "Low", or numbers
                                if db_col == "draw":
                                    if pd.isna(val) or val == "":
                                        val = 0
                                    elif isinstance(val, str):
                                        if val.lower() == "high":
                                            val = 999
                                        elif val.lower() == "low":
                                            val = 1
                                        else:
                                            try:
                                                val = int(val)
                                            except:
                                                val = 0

                                # Handle NaN values
                                elif pd.isna(val):
                                    if db_col in [
                                        "race_number",
                                        "course_id",
                                        "runners_racecard",
                                        "runners",
                                        "ew_racecard",
                                        "ew",
                                        "places_ew_racecard",
                                        "places_ew",
                                    ]:
                                        val = 0
                                    else:
                                        val = "none"

                                columns.append(db_col)
                                values.append(val)

                        # Insert the row
                        if columns and values:
                            placeholders = ", ".join(["%s"] * len(values))
                            sql = f"INSERT INTO races ({', '.join(columns)}) VALUES ({placeholders})"
                            cursor.execute(sql, values)
                            total_uploaded += 1

                    except Exception as e:
                        logger.warning(f"Skipped row due to error: {e}")
                        continue

        conn.commit()
        logger.info(f"✅ Successfully uploaded {total_uploaded} races")
        return total_uploaded

    except Exception as e:
        logger.error(f"Failed to upload races: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()


def upload_records():
    """Upload records data - combine both records.csv and racecard_details.csv into records table"""
    logger.info("Uploading records data...")

    # Both files should go into records table
    record_files = [
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/cards_data/records/records.csv",
        "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads/results_data/racecard_details/racecard_details.csv",
    ]

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Clear records table
        cursor.execute("DELETE FROM records")

        total_uploaded = 0
        for record_file in record_files:
            if os.path.exists(record_file):
                df = pd.read_csv(record_file)
                logger.info(f"Processing {record_file}: {len(df)} rows")

                # Different column mappings for different files
                if "records.csv" in record_file:
                    # This is the main records file
                    csv_to_db_mapping = {
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
                    }
                else:
                    # This is racecard_details.csv
                    csv_to_db_mapping = {
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

                # Process each row
                for _, row in df.iterrows():
                    try:
                        values = []
                        columns = []

                        for csv_col, db_col in csv_to_db_mapping.items():
                            if csv_col in df.columns:
                                val = row[csv_col]

                                # Handle NaN values based on column type
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

                                columns.append(db_col)
                                values.append(val)

                        # Insert the row
                        if columns and values:
                            placeholders = ", ".join(["%s"] * len(values))
                            sql = f"INSERT INTO records ({', '.join(columns)}) VALUES ({placeholders})"
                            cursor.execute(sql, values)
                            total_uploaded += 1

                    except Exception as e:
                        logger.warning(f"Skipped row due to error: {e}")
                        continue

        conn.commit()
        logger.info(f"✅ Successfully uploaded {total_uploaded} records")
        return total_uploaded

    except Exception as e:
        logger.error(f"Failed to upload records: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()


def main():
    logger.info("Starting working CSV upload based on git history patterns...")

    # Upload races (this worked before according to upload_report_20250816.json)
    races_count = upload_races()

    # Upload records (combining records.csv and racecard_details.csv)
    records_count = upload_records()

    # Show final status
    logger.info(f"✅ Upload completed!")
    logger.info(f"   - Races: {races_count}")
    logger.info(f"   - Records: {records_count}")

    # Verify database state
    try:
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM races")
        db_races_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM records")
        db_records_count = cursor.fetchone()[0]

        logger.info(f"Database verification:")
        logger.info(f"   - {db_races_count} races in database")
        logger.info(f"   - {db_records_count} records in database")

        cursor.close()
        conn.close()

        if db_races_count > 0 and db_records_count > 0:
            logger.info("🎉 SUCCESS! Database has data and ML training can now proceed")
            return True
        else:
            logger.error("❌ Database still empty after upload")
            return False

    except Exception as e:
        logger.error(f"Database verification failed: {e}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
