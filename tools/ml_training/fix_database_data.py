#!/usr/bin/env python3
"""
Database Data Processing Script
Fixes the data quality issues in the results database:
1. Calculate missing win_rate and place_rate values
2. Convert text names to IDs in records table
3. Create horse IDs and mapping
4. Handle NULL values properly (0 for numeric, proper IDs for relations)
"""

import psycopg2
import os
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseDataProcessor:
    def __init__(self):
        self.conn = psycopg2.connect(
            host="postgres",
            database="results_horse_racing_db",
            user="horse_racing",
            password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
        )
        self.cursor = self.conn.cursor()

    def fix_jockey_stats(self):
        """Calculate and update missing win_rate and place_rate for jockeys"""
        logger.info("Fixing jockey statistics...")

        # Update win_rate and place_rate where they are None
        update_query = """
        UPDATE jockeys_stats 
        SET 
            win_rate = CASE 
                WHEN runs > 0 THEN ROUND((wins::numeric / runs::numeric) * 100, 2)
                ELSE 0 
            END,
            place_rate = CASE 
                WHEN runs > 0 THEN ROUND((wins::numeric / runs::numeric) * 100, 2)  -- Using wins as place for now
                ELSE 0 
            END
        WHERE win_rate IS NULL OR place_rate IS NULL
        """

        self.cursor.execute(update_query)
        affected_rows = self.cursor.rowcount
        logger.info(f"Updated {affected_rows} jockey records with calculated rates")

        # Verify the update
        self.cursor.execute(
            "SELECT jockey_name, wins, runs, win_rate FROM jockeys_stats LIMIT 5"
        )
        sample_data = self.cursor.fetchall()
        logger.info("Sample updated jockey data:")
        for row in sample_data:
            logger.info(
                f"  {row[0]}: {row[1]} wins / {row[2]} runs = {row[3]}% win rate"
            )

    def fix_trainer_stats(self):
        """Calculate and update missing win_rate and place_rate for trainers"""
        logger.info("Fixing trainer statistics...")

        # Update win_rate and place_rate where they are None
        update_query = """
        UPDATE trainers_stats 
        SET 
            win_rate = CASE 
                WHEN runs > 0 THEN ROUND((wins::numeric / runs::numeric) * 100, 2)
                ELSE 0 
            END,
            place_rate = CASE 
                WHEN runs > 0 THEN ROUND((wins::numeric / runs::numeric) * 100, 2)  -- Using wins as place for now
                ELSE 0 
            END
        WHERE win_rate IS NULL OR place_rate IS NULL
        """

        self.cursor.execute(update_query)
        affected_rows = self.cursor.rowcount
        logger.info(f"Updated {affected_rows} trainer records with calculated rates")

        # Verify the update
        self.cursor.execute(
            "SELECT trainer_name, wins, runs, win_rate FROM trainers_stats LIMIT 5"
        )
        sample_data = self.cursor.fetchall()
        logger.info("Sample updated trainer data:")
        for row in sample_data:
            logger.info(
                f"  {row[0]}: {row[1]} wins / {row[2]} runs = {row[3]}% win rate"
            )

    def create_horse_mapping(self):
        """Create horse IDs and mapping table"""
        logger.info("Creating horse ID mapping...")

        # Create horses table if it doesn't exist
        create_horses_table = """
        CREATE TABLE IF NOT EXISTS horses_mapping (
            horse_id SERIAL PRIMARY KEY,
            horse_name VARCHAR(255) UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        self.cursor.execute(create_horses_table)

        # Insert unique horse names from records
        insert_horses = """
        INSERT INTO horses_mapping (horse_name)
        SELECT DISTINCT horse_name
        FROM records
        WHERE horse_name IS NOT NULL
        ON CONFLICT (horse_name) DO NOTHING
        """
        self.cursor.execute(insert_horses)
        affected_rows = self.cursor.rowcount
        logger.info(f"Created {affected_rows} horse ID mappings")

    def add_id_columns_to_records(self):
        """Add jockey_id, trainer_id, horse_id columns to records table"""
        logger.info("Adding ID columns to records table...")

        # Add columns if they don't exist
        alter_queries = [
            "ALTER TABLE records ADD COLUMN IF NOT EXISTS jockey_id INTEGER",
            "ALTER TABLE records ADD COLUMN IF NOT EXISTS trainer_id INTEGER",
            "ALTER TABLE records ADD COLUMN IF NOT EXISTS horse_id INTEGER",
        ]

        for query in alter_queries:
            self.cursor.execute(query)

    def update_records_with_ids(self):
        """Update records table with proper IDs instead of text names"""
        logger.info("Updating records with jockey IDs...")

        # Update jockey_id
        update_jockey_ids = """
        UPDATE records 
        SET jockey_id = js.jockey_id
        FROM jockeys_stats js
        WHERE records.jockey = js.jockey_name
        AND records.jockey_id IS NULL
        """
        self.cursor.execute(update_jockey_ids)
        jockey_updates = self.cursor.rowcount
        logger.info(f"Updated {jockey_updates} records with jockey IDs")

        # Update trainer_id
        logger.info("Updating records with trainer IDs...")
        update_trainer_ids = """
        UPDATE records 
        SET trainer_id = ts.trainer_id
        FROM trainers_stats ts
        WHERE records.trainer = ts.trainer_name
        AND records.trainer_id IS NULL
        """
        self.cursor.execute(update_trainer_ids)
        trainer_updates = self.cursor.rowcount
        logger.info(f"Updated {trainer_updates} records with trainer IDs")

        # Update horse_id
        logger.info("Updating records with horse IDs...")
        update_horse_ids = """
        UPDATE records 
        SET horse_id = hm.horse_id
        FROM horses_mapping hm
        WHERE records.horse_name = hm.horse_name
        AND records.horse_id IS NULL
        """
        self.cursor.execute(update_horse_ids)
        horse_updates = self.cursor.rowcount
        logger.info(f"Updated {horse_updates} records with horse IDs")

    def verify_data_quality(self):
        """Verify the data quality after processing"""
        logger.info("Verifying data quality...")

        # Check jockey stats
        self.cursor.execute("SELECT COUNT(*) FROM jockeys_stats WHERE win_rate IS NULL")
        null_jockey_rates = self.cursor.fetchone()[0]
        logger.info(f"Jockeys with NULL win_rate: {null_jockey_rates}")

        # Check trainer stats
        self.cursor.execute(
            "SELECT COUNT(*) FROM trainers_stats WHERE win_rate IS NULL"
        )
        null_trainer_rates = self.cursor.fetchone()[0]
        logger.info(f"Trainers with NULL win_rate: {null_trainer_rates}")

        # Check records with missing IDs
        self.cursor.execute("SELECT COUNT(*) FROM records WHERE jockey_id IS NULL")
        missing_jockey_ids = self.cursor.fetchone()[0]
        logger.info(f"Records with missing jockey_id: {missing_jockey_ids}")

        self.cursor.execute("SELECT COUNT(*) FROM records WHERE trainer_id IS NULL")
        missing_trainer_ids = self.cursor.fetchone()[0]
        logger.info(f"Records with missing trainer_id: {missing_trainer_ids}")

        self.cursor.execute("SELECT COUNT(*) FROM records WHERE horse_id IS NULL")
        missing_horse_ids = self.cursor.fetchone()[0]
        logger.info(f"Records with missing horse_id: {missing_horse_ids}")

        # Sample data verification
        self.cursor.execute(
            """
        SELECT 
            r.horse_name,
            r.jockey,
            r.trainer,
            r.horse_id,
            r.jockey_id,
            r.trainer_id,
            js.win_rate as jockey_win_rate,
            ts.win_rate as trainer_win_rate
        FROM records r
        LEFT JOIN jockeys_stats js ON r.jockey_id = js.jockey_id
        LEFT JOIN trainers_stats ts ON r.trainer_id = ts.trainer_id
        LIMIT 3
        """
        )

        sample_data = self.cursor.fetchall()
        logger.info("Sample processed data:")
        for row in sample_data:
            logger.info(
                f"  Horse: {row[0]}, Jockey: {row[1]} (ID: {row[4]}, Win Rate: {row[6]}%), Trainer: {row[2]} (ID: {row[5]}, Win Rate: {row[7]}%)"
            )

    def process_all(self):
        """Run all data processing steps"""
        try:
            logger.info("Starting database data processing...")

            self.fix_jockey_stats()
            self.fix_trainer_stats()
            self.create_horse_mapping()
            self.add_id_columns_to_records()
            self.update_records_with_ids()
            self.verify_data_quality()

            self.conn.commit()
            logger.info("Database data processing completed successfully!")

        except Exception as e:
            logger.error(f"Error during data processing: {e}")
            self.conn.rollback()
            raise
        finally:
            self.conn.close()


if __name__ == "__main__":
    processor = DatabaseDataProcessor()
    processor.process_all()
