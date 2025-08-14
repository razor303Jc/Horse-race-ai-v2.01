#!/usr/bin/env python3
"""
Clean Database Uploader for Fixed CSV Files
"""

import json
import logging
import os

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    # Database connection
    database_url = (
        "postgresql://horse_racing:secure_password_123@localhost:5433/horse_racing_db"
    )

    try:
        # Create engine
        engine = create_engine(database_url)
        logger.info("Connected to PostgreSQL database")

        # Upload cleaned files
        files_to_upload = [
            {
                "file": "data/daily_downloads/cleaned_races.csv",
                "table": "races",
                "strategy": "replace",  # Replace existing data
            },
            {
                "file": "data/daily_downloads/cleaned_records.csv",
                "table": "records",
                "strategy": "append",  # Append new data
            },
        ]

        for upload_config in files_to_upload:
            file_path = upload_config["file"]
            table_name = upload_config["table"]
            strategy = upload_config["strategy"]

            logger.info(
                f"Processing {file_path} -> {table_name} (strategy: {strategy})"
            )

            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                continue

            # Read CSV
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path}")

            # Upload to database
            try:
                if strategy == "replace":
                    # Clear existing data first
                    with engine.connect() as conn:
                        conn.execute(f"DELETE FROM {table_name}")
                        conn.commit()
                    logger.info(f"Cleared existing data from {table_name}")

                df.to_sql(table_name, engine, if_exists="append", index=False)
                logger.info(f"Successfully uploaded {len(df)} rows to {table_name}")

            except Exception as e:
                logger.error(f"Error uploading to {table_name}: {e}")
                continue

        logger.info("Upload process completed")

    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return False

    return True


if __name__ == "__main__":
    main()
