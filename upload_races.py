#!/usr/bin/env python3
"""
Simple Races Uploader
"""

import logging

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    database_url = (
        "postgresql://horse_racing:secure_password_123@localhost:5433/horse_racing_db"
    )

    try:
        engine = create_engine(database_url)
        logger.info("Connected to PostgreSQL database")

        # Upload cleaned races
        df = pd.read_csv("data/daily_downloads/cleaned_races.csv")
        logger.info(f"Loaded {len(df)} rows from cleaned_races.csv")

        df.to_sql("races", engine, if_exists="append", index=False)
        logger.info(f"Successfully uploaded {len(df)} rows to races")

    except Exception as e:
        logger.error(f"Error: {e}")


if __name__ == "__main__":
    main()
