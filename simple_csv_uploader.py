#!/usr/bin/env python3
"""
Simple CSV to Database Uploader
Uploads CSV files to the correct database schema with proper validation
"""

import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleCSVUploader:
    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5434,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Load column mapping
        self.mapping_file = "/home/jc/Documents/Horse-race-ai-v2.02/config/complete_csv_column_mapping.json"
        with open(self.mapping_file, "r") as f:
            self.column_mapping = json.load(f)

    def connect_db(self):
        """Connect to PostgreSQL database"""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            return None

    def upload_csv_to_table(self, csv_path, table_name):
        """Upload a single CSV file to specified table"""
        logger.info(f"Uploading {csv_path} to {table_name}")

        # Check if CSV file exists
        if not os.path.exists(csv_path):
            logger.warning(f"CSV file not found: {csv_path}")
            return False

        # Load CSV
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")
            logger.info(f"CSV columns: {list(df.columns)}")
        except Exception as e:
            logger.error(f"Failed to read CSV {csv_path}: {e}")
            return False

        if df.empty:
            logger.warning(f"CSV file is empty: {csv_path}")
            return False

        # Get column mapping for this table
        table_config = self.column_mapping["table_mappings"].get(table_name)
        if not table_config:
            logger.error(f"No mapping found for table: {table_name}")
            return False

        column_mapping = table_config["column_mapping"]

        # Map CSV columns to database columns
        mapped_data = {}
        for db_col, csv_col in column_mapping.items():
            if csv_col in df.columns:
                mapped_data[db_col] = df[csv_col]
            else:
                logger.warning(
                    f"CSV column '{csv_col}' not found for database column '{db_col}'"
                )
                # Set default values for missing columns
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
                    mapped_data[db_col] = 0
                elif db_col in [
                    "sp",
                    "distance_btn",
                    "distance_btn_total",
                    "weight_uk",
                    "weight",
                ]:
                    mapped_data[db_col] = 0.0
                else:
                    mapped_data[db_col] = "none"

        # Create DataFrame with mapped columns
        upload_df = pd.DataFrame(mapped_data)

        # Connect to database and upload
        conn = self.connect_db()
        if not conn:
            return False

        try:
            cursor = conn.cursor()

            # Clear existing data in table
            cursor.execute(f"DELETE FROM {table_name}")
            logger.info(f"Cleared existing data from {table_name}")

            # Prepare insert statement
            columns = list(upload_df.columns)
            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"

            # Insert data
            for index, row in upload_df.iterrows():
                values = []
                for col in columns:
                    value = row[col]
                    # Handle NaN values
                    if pd.isna(value):
                        if col in [
                            "race_number",
                            "course_id",
                            "runners_racecard",
                            "runners",
                            "draw",
                            "ew_racecard",
                            "ew",
                            "places_ew_racecard",
                            "places_ew",
                            "horse_number",
                            "position",
                            "horse_id",
                            "age",
                            "jockey_id",
                            "trainer_id",
                            "fav",
                            "or_rating",
                        ]:
                            values.append(0)
                        elif (
                            col
                            in [
                                "sp",
                                "distance_btn",
                                "distance_btn_total",
                                "weight_uk",
                                "weight",
                            ]
                            or "sectional_time" in col
                            or "distance_sec" in col
                            or "speed_achieved" in col
                            or "distance_speed" in col
                            or "finish_time" in col
                        ):
                            values.append(0.0)
                        else:
                            values.append("none")
                    else:
                        values.append(value)

                cursor.execute(insert_sql, values)

            conn.commit()
            logger.info(f"Successfully uploaded {len(upload_df)} rows to {table_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to upload to {table_name}: {e}")
            conn.rollback()
            return False
        finally:
            cursor.close()
            conn.close()

    def upload_all_csv_files(self):
        """Upload all CSV files from today's download"""
        base_path = "/home/jc/Documents/Horse-race-ai-v2.02/data/daily_downloads"

        # Upload races from both cards and results
        races_files = [
            f"{base_path}/cards_data/races/races.csv",
            f"{base_path}/results_data/races/races.csv",
        ]

        records_files = [
            f"{base_path}/cards_data/records/records.csv",
            f"{base_path}/results_data/racecard_details/racecard_details.csv",
        ]

        # Upload races
        races_uploaded = False
        for races_file in races_files:
            if os.path.exists(races_file):
                if self.upload_csv_to_table(races_file, "races"):
                    races_uploaded = True
                    break

        if not races_uploaded:
            logger.error("No races files could be uploaded")

        # Upload records
        records_uploaded = False
        for records_file in records_files:
            if os.path.exists(records_file):
                if self.upload_csv_to_table(records_file, "records"):
                    records_uploaded = True
                    break

        if not records_uploaded:
            logger.error("No records files could be uploaded")

        return races_uploaded and records_uploaded


def main():
    uploader = SimpleCSVUploader()

    logger.info("Starting CSV upload process...")
    success = uploader.upload_all_csv_files()

    if success:
        logger.info("✅ All CSV files uploaded successfully!")

        # Verify upload by checking record counts
        conn = uploader.connect_db()
        if conn:
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
        logger.error("❌ CSV upload failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
