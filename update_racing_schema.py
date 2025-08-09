#!/usr/bin/env python3
"""
Update Database Schema for Racing Text Fields
Converts numeric-only fields to support racing text like 'nk', '4/1' etc.
"""

import logging

import psycopg2

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def update_schema_for_racing_text():
    """
    Update database schema to handle racing-specific text values
    """
    try:
        connection = psycopg2.connect(**DATABASE_CONFIG)
        cursor = connection.cursor()

        logger.info("🔧 Updating database schema for racing text fields...")

        # Update race_results table
        updates = [
            "ALTER TABLE race_results ALTER COLUMN win_odds TYPE VARCHAR(20)",
            "ALTER TABLE race_results ALTER COLUMN place_odds TYPE VARCHAR(20)",
            "ALTER TABLE race_results ALTER COLUMN margin TYPE VARCHAR(20)",
            # Update racecard_details table
            "ALTER TABLE racecard_details ALTER COLUMN win_odds TYPE VARCHAR(20)",
            "ALTER TABLE racecard_details ALTER COLUMN place_odds TYPE VARCHAR(20)",
        ]

        for update_sql in updates:
            try:
                cursor.execute(update_sql)
                logger.info(f"✅ {update_sql}")
            except Exception as e:
                logger.warning(f"⚠️ {update_sql} - {e}")

        connection.commit()
        cursor.close()
        connection.close()

        logger.info("🎉 Schema updated successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to update schema: {e}")
        return False


if __name__ == "__main__":
    print("🐎 Updating Horse Racing Database Schema")
    print("=" * 50)
    print("Converting numeric fields to support racing text")
    print("(e.g., 'nk' for neck, '4/1' for odds)")
    print("=" * 50)

    success = update_schema_for_racing_text()

    if success:
        print("\n✅ SCHEMA UPDATE COMPLETE!")
        print("Database now supports racing text values")
    else:
        print("\n❌ SCHEMA UPDATE FAILED!")
        print("Check logs for details")
