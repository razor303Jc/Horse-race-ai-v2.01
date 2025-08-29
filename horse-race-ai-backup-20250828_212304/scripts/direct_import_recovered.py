#!/usr/bin/env python3
"""
Direct Import of Recovered Racing Data
Import the recovered CSV data directly using COPY command
"""

import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2


def setup_logging():
    """Setup comprehensive logging"""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/direct_recovered_import.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def connect_to_docker_database():
    """Connect to PostgreSQL database in Docker"""
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5434",  # Docker mapped port
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        print("✅ Connected to Docker database (port 5434)")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None


def analyze_csv_structure(csv_path):
    """Analyze CSV structure and show preview"""
    logger = logging.getLogger(__name__)

    df = pd.read_csv(csv_path, nrows=5)
    logger.info(f"📊 CSV Structure for {csv_path}:")
    logger.info(f"   Columns: {list(df.columns)}")
    logger.info(f"   Shape: {df.shape}")
    logger.info(f"   Sample data:\n{df.head(2)}")

    return df.columns.tolist()


def import_races_data(conn, csv_path):
    """Import races data"""
    logger = logging.getLogger(__name__)
    cursor = conn.cursor()

    try:
        # Analyze structure first
        columns = analyze_csv_structure(csv_path)

        # Read and process races data
        df = pd.read_csv(csv_path)
        logger.info(f"📊 Loading {len(df)} races from {csv_path}")

        # Insert races data
        inserted = 0
        for _, row in df.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO races (
                        race_id, race_number, race_time, course_id, course,
                        race_type, date, race_name, class, years, distance,
                        surface, prize, runners_racecard, runners, draw,
                        ew_racecard, ew, places_ew_racecard, places_ew
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (race_id) DO NOTHING
                """,
                    (
                        str(row["Race_ID"]),
                        row.get("race_number"),
                        row.get("race_time"),
                        row.get("course_id"),
                        row.get("Course"),
                        row.get("Race_type"),
                        row.get("Date"),
                        row.get("Race_name"),
                        row.get("Class"),
                        row.get("Years"),
                        row.get("Distance"),
                        row.get("Surface"),
                        row.get("Prize"),
                        row.get("Runners_racecard"),
                        row.get("Runners"),
                        row.get("Draw"),
                        row.get("EW_racecard"),
                        row.get("EW"),
                        row.get("Places_EW_racecard"),
                        row.get("Places_EW"),
                    ),
                )
                inserted += 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to insert race {row.get('Race_ID')}: {e}")

        conn.commit()
        logger.info(f"✅ Inserted {inserted} races")
        return inserted

    except Exception as e:
        logger.error(f"❌ Failed to import races: {e}")
        conn.rollback()
        return 0


def import_records_data(conn, csv_path):
    """Import records data"""
    logger = logging.getLogger(__name__)
    cursor = conn.cursor()

    try:
        # Analyze structure first
        columns = analyze_csv_structure(csv_path)

        # Read and process records data
        df = pd.read_csv(csv_path)
        logger.info(f"📊 Loading {len(df)} records from {csv_path}")

        # Insert records data
        inserted = 0
        for _, row in df.iterrows():
            try:
                cursor.execute(
                    """
                    INSERT INTO records (
                        record_id, race_id, horse_number, position, draw,
                        horse_id, country, horse, age, weight_uk, weight,
                        gears, horse_rate, jockey_id, jockey, trainer_id,
                        trainer, fav, sp, distance_btn, finish_time
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (record_id) DO NOTHING
                """,
                    (
                        row.get("ID"),
                        str(row.get("Race_ID")),
                        row.get("Horse_number"),
                        row.get("Place"),
                        row.get("Draw"),
                        row.get("Horse_ID"),
                        row.get("Country"),
                        row.get("Name"),
                        row.get("Age"),
                        row.get("weight_uk"),
                        row.get("weight"),
                        row.get("gears"),
                        row.get("Horse_rate"),
                        row.get("jockey_ID"),
                        row.get("jockey"),
                        row.get("trainer_ID"),
                        row.get("trainer"),
                        row.get("fav"),
                        row.get("SP"),
                        row.get("Distance_btn"),
                        row.get("finish_time"),
                    ),
                )
                inserted += 1
            except Exception as e:
                logger.warning(f"⚠️ Failed to insert record {row.get('ID')}: {e}")

        conn.commit()
        logger.info(f"✅ Inserted {inserted} records")
        return inserted

    except Exception as e:
        logger.error(f"❌ Failed to import records: {e}")
        conn.rollback()
        return 0


def main():
    """Main import process"""
    logger = setup_logging()
    logger.info("🔄 Starting direct import of recovered data...")

    # Connect to database
    conn = connect_to_docker_database()
    if not conn:
        logger.error("❌ Could not connect to database")
        return False

    try:
        # Define data files
        project_root = Path(__file__).parent.parent
        recovered_base = (
            project_root / "data" / "recovered_from_trash" / "extracted_results"
        )

        races_file = recovered_base / "races" / "races.csv"
        records_file = recovered_base / "records" / "records.csv"

        total_imported = 0

        # Import races
        if races_file.exists():
            races_imported = import_races_data(conn, races_file)
            total_imported += races_imported
        else:
            logger.warning(f"⚠️ Races file not found: {races_file}")

        # Import records
        if records_file.exists():
            records_imported = import_records_data(conn, records_file)
            total_imported += records_imported
        else:
            logger.warning(f"⚠️ Records file not found: {records_file}")

        logger.info(f"✅ Import completed: {total_imported} total records imported")
        return total_imported > 0

    except Exception as e:
        logger.error(f"❌ Import failed: {e}")
        return False

    finally:
        if conn:
            conn.close()
            logger.info("🔌 Database connection closed")


if __name__ == "__main__":
    success = main()
    if success:
        print("✅ Recovered data import completed successfully")
        sys.exit(0)
    else:
        print("❌ Recovered data import failed")
        sys.exit(1)
