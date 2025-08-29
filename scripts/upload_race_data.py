#!/usr/bin/env python3
"""
Script to validate, process, and upload race card data to the database
"""

import os
import sys
import csv
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db_connection():
    """Get database connection using environment variables"""
    try:
        connection = psycopg2.connect(
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
            database=os.getenv("DB_NAME", "cards_horse_racing_db"),
            user=os.getenv("DB_USER", "horse_racing"),
            password=os.getenv("DB_PASSWORD", "horse_racing_password"),
        )
        return connection
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None


def validate_csv_data(csv_file_path):
    """Validate CSV data format and content"""
    logger.info(f"Validating {csv_file_path}")

    if not os.path.exists(csv_file_path):
        logger.error(f"File not found: {csv_file_path}")
        return False

    try:
        with open(csv_file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            rows = list(reader)

        logger.info(f"Found {len(rows)} rows in {os.path.basename(csv_file_path)}")

        if len(rows) == 0:
            logger.warning(f"No data rows found in {csv_file_path}")
            return False

        # Check if we have expected columns for races
        if "Race_ID" in rows[0]:
            logger.info("Races CSV validation passed")
        elif "Horse_ID" in rows[0]:
            logger.info("Horses CSV validation passed")
        else:
            logger.warning(f"Unknown CSV format in {csv_file_path}")

        return True

    except Exception as e:
        logger.error(f"Validation failed for {csv_file_path}: {e}")
        return False


def upload_races_data(csv_file_path, conn):
    """Upload races data to database"""
    logger.info("Uploading races data...")

    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        cursor = conn.cursor()

        uploaded_count = 0
        skipped_count = 0

        for row in reader:
            try:
                # Check if race already exists
                cursor.execute(
                    "SELECT race_id FROM races WHERE race_id = %s", (row["Race_ID"],)
                )
                if cursor.fetchone():
                    logger.debug(f"Race {row['Race_ID']} already exists, skipping")
                    skipped_count += 1
                    continue

                # Insert race data
                insert_query = """
                INSERT INTO races (
                    race_id, race_number, race_time, course_id, course, race_type,
                    date, race_name, class, years, distance, surface, prize,
                    runners_racecard, runners, draw, ew_racecard, ew,
                    places_ew_racecard, places_ew
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                # Handle empty/None values
                course_id = (
                    row.get("course_id")
                    if row.get("course_id") and row.get("course_id").strip()
                    else None
                )

                cursor.execute(
                    insert_query,
                    (
                        row["Race_ID"],
                        row["race_number"],
                        row["race_time"] if row["race_time"] else None,
                        course_id,
                        row["Course"],
                        row["Race_type"],
                        row["Date"],
                        row["Race_name"],
                        row["Class"],
                        row["Years"],
                        row["Distance"],
                        row["Surface"],
                        row["Prize"],
                        (
                            int(row["Runners_racecard"])
                            if row["Runners_racecard"]
                            else None
                        ),
                        int(row["Runners"]) if row["Runners"] else None,
                        row["Draw"] if row["Draw"] and row["Draw"] != "None" else None,
                        int(row["EW_racecard"]) if row["EW_racecard"] else None,
                        int(row["EW"]) if row["EW"] else None,
                        (
                            int(row["Places_EW_racecard"])
                            if row["Places_EW_racecard"]
                            else None
                        ),
                        int(row["Places_EW"]) if row["Places_EW"] else None,
                    ),
                )
                uploaded_count += 1

            except Exception as e:
                logger.error(
                    f"Error inserting race {row.get('Race_ID', 'unknown')}: {e}"
                )
                continue

        conn.commit()
        cursor.close()

        logger.info(
            f"Races upload complete: {uploaded_count} uploaded, {skipped_count} skipped"
        )
        return uploaded_count > 0


def upload_horses_data(csv_file_path, conn):
    """Upload horses data to database"""
    logger.info("Uploading horses data...")

    with open(csv_file_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        cursor = conn.cursor()

        uploaded_count = 0
        skipped_count = 0

        for row in reader:
            try:
                # Check if horse entry already exists
                cursor.execute(
                    "SELECT horse_id FROM horses WHERE horse_id = %s AND race_id = %s",
                    (row["Horse_ID"], row["Race_ID"]),
                )
                if cursor.fetchone():
                    skipped_count += 1
                    continue

                # Insert horse data
                insert_query = """
                INSERT INTO horses (
                    horse_id, race_id, horse_name, age, weight, jockey, trainer,
                    owner, odds, position, lengths_beaten, comment, form
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
                """

                cursor.execute(
                    insert_query,
                    (
                        row["Horse_ID"],
                        row["Race_ID"],
                        row["Horse_name"],
                        (
                            int(row["Age"])
                            if row["Age"] and row["Age"].isdigit()
                            else None
                        ),
                        row["Weight"],
                        row["Jockey"],
                        row["Trainer"],
                        row["Owner"],
                        row["Odds"],
                        (
                            int(row["Position"])
                            if row["Position"] and row["Position"].isdigit()
                            else None
                        ),
                        row["Lengths_beaten"],
                        row["Comment"],
                        row["Form"],
                    ),
                )
                uploaded_count += 1

            except Exception as e:
                logger.error(
                    f"Error inserting horse {row.get('Horse_ID', 'unknown')}: {e}"
                )
                continue

        conn.commit()
        cursor.close()

        logger.info(
            f"Horses upload complete: {uploaded_count} uploaded, {skipped_count} skipped"
        )
        return uploaded_count > 0


def main():
    """Main function to validate, process, and upload data"""
    if len(sys.argv) != 2:
        print("Usage: python upload_race_data.py <data_directory>")
        sys.exit(1)

    data_dir = sys.argv[1]

    if not os.path.exists(data_dir):
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)

    # File paths
    races_csv = os.path.join(data_dir, "races", "races.csv")
    horses_csv = os.path.join(data_dir, "horses", "horses.csv")

    # Validate data
    logger.info("Starting data validation...")

    if not validate_csv_data(races_csv):
        logger.error("Races data validation failed")
        sys.exit(1)

    if not validate_csv_data(horses_csv):
        logger.error("Horses data validation failed")
        sys.exit(1)

    logger.info("Data validation completed successfully")

    # Connect to database
    logger.info("Connecting to database...")
    conn = get_db_connection()
    if not conn:
        logger.error("Database connection failed")
        sys.exit(1)

    try:
        # Upload data
        logger.info("Starting data upload...")

        races_success = upload_races_data(races_csv, conn)
        horses_success = upload_horses_data(horses_csv, conn)

        if races_success or horses_success:
            logger.info("✅ Data upload completed successfully!")
        else:
            logger.warning("⚠️ No new data was uploaded (may already exist)")

    except Exception as e:
        logger.error(f"Upload process failed: {e}")
        conn.rollback()
        sys.exit(1)

    finally:
        conn.close()
        logger.info("Database connection closed")


if __name__ == "__main__":
    main()
