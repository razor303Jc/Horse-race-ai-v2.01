#!/usr/bin/env python3
"""
Index Table Updater for Horse Racing Database
Automatically updates index tables when new race results are added.
Finds new horses, jockeys, and trainers and adds them to index tables.
"""

import psycopg2
import logging
from datetime import datetime

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "database": "results_horse_racing_db",
    "user": "horse_racing",
    "password": "horse_racing_password",
    "port": "5432",
}


def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("index_update.log"), logging.StreamHandler()],
    )


def get_db_connection():
    """Establish database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise


def update_horses_index(cursor):
    """Find new horses and add them to horses_index"""
    query = """
    INSERT INTO horses_index (horse_name, horse_id)
    SELECT DISTINCT horse_name, horse_id 
    FROM race_results 
    WHERE horse_name IS NOT NULL 
    AND horse_name != ''
    AND NOT EXISTS (
        SELECT 1 FROM horses_index 
        WHERE horses_index.horse_name = race_results.horse_name
        AND horses_index.horse_id = race_results.horse_id
    )
    """

    cursor.execute(query)
    new_horses = cursor.rowcount
    logging.info(f"Added {new_horses} new horses to index")
    return new_horses


def update_jockeys_index(cursor):
    """Find new jockeys and add them to jockeys_index"""
    query = """
    INSERT INTO jockeys_index (jockey_name, jockey_id)
    SELECT DISTINCT jockey_name, 
           ROW_NUMBER() OVER (ORDER BY jockey_name) + COALESCE(
               (SELECT MAX(jockey_id) FROM jockeys_index), 0
           ) as jockey_id
    FROM race_results 
    WHERE jockey_name IS NOT NULL 
    AND jockey_name != ''
    AND NOT EXISTS (
        SELECT 1 FROM jockeys_index 
        WHERE jockeys_index.jockey_name = race_results.jockey_name
    )
    """

    cursor.execute(query)
    new_jockeys = cursor.rowcount
    logging.info(f"Added {new_jockeys} new jockeys to index")
    return new_jockeys


def update_trainers_index(cursor):
    """Find new trainers and add them to trainers_index"""
    query = """
    INSERT INTO trainers_index (trainer_name, trainer_id)
    SELECT DISTINCT trainer_name,
           ROW_NUMBER() OVER (ORDER BY trainer_name) + COALESCE(
               (SELECT MAX(trainer_id) FROM trainers_index), 0
           ) as trainer_id
    FROM race_results 
    WHERE trainer_name IS NOT NULL 
    AND trainer_name != ''
    AND NOT EXISTS (
        SELECT 1 FROM trainers_index 
        WHERE trainers_index.trainer_name = race_results.trainer_name
    )
    """

    cursor.execute(query)
    new_trainers = cursor.rowcount
    logging.info(f"Added {new_trainers} new trainers to index")
    return new_trainers


def get_index_stats(cursor):
    """Get current statistics of index tables"""
    stats = {}

    # Horses count
    cursor.execute("SELECT COUNT(*) FROM horses_index")
    stats["horses"] = cursor.fetchone()[0]

    # Jockeys count
    cursor.execute("SELECT COUNT(*) FROM jockeys_index")
    stats["jockeys"] = cursor.fetchone()[0]

    # Trainers count
    cursor.execute("SELECT COUNT(*) FROM trainers_index")
    stats["trainers"] = cursor.fetchone()[0]

    # Race results count
    cursor.execute("SELECT COUNT(*) FROM race_results")
    stats["race_results"] = cursor.fetchone()[0]

    return stats


def main():
    """Main execution function"""
    setup_logging()
    logging.info("Starting index table update process")

    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Get stats before update
        stats_before = get_index_stats(cursor)
        logging.info(
            f"Before update - Horses: {stats_before['horses']}, "
            f"Jockeys: {stats_before['jockeys']}, "
            f"Trainers: {stats_before['trainers']}, "
            f"Race Results: {stats_before['race_results']}"
        )

        # Update each index table
        new_horses = update_horses_index(cursor)
        new_jockeys = update_jockeys_index(cursor)
        new_trainers = update_trainers_index(cursor)

        # Commit changes
        conn.commit()

        # Get stats after update
        stats_after = get_index_stats(cursor)
        logging.info(
            f"After update - Horses: {stats_after['horses']}, "
            f"Jockeys: {stats_after['jockeys']}, "
            f"Trainers: {stats_after['trainers']}"
        )

        # Summary
        total_new = new_horses + new_jockeys + new_trainers
        if total_new > 0:
            logging.info(
                f"Index update completed successfully! "
                f"Added {total_new} new entities."
            )
        else:
            logging.info("No new entities found - index tables are up to date.")

    except Exception as e:
        logging.error(f"Index update failed: {e}")
        if "conn" in locals():
            conn.rollback()
        raise
    finally:
        if "cursor" in locals():
            cursor.close()
        if "conn" in locals():
            conn.close()
        logging.info("Database connection closed")


if __name__ == "__main__":
    main()
