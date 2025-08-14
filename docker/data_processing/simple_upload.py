#!/usr/bin/env python3
"""
Simple Database Uploader for Mapped CSV Files
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

        # Load manifest
        manifest_path = "data/daily_downloads/upload_manifest.json"
        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        logger.info(f"Loaded manifest with {len(manifest['files'])} files")

        # Upload each file
        for file_path, config in manifest["files"].items():
            table_name = config["table"]

            logger.info(f"Processing {file_path} -> {table_name}")

            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"File not found: {file_path}")
                continue

            # Read CSV
            df = pd.read_csv(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path}")

            # Upload to database
            try:
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
