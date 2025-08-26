#!/usr/bin/env python3
"""
Process manually downloaded racing data with date validation and upload to database.
This script handles the date offset issue and validates data before upload.
"""

import os
import sys
import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from datetime import datetime, date
import json

# Database connection settings
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "horse_racing",
    "password": "horse_racing123",
    "dbname": "cards_horse_racing_db",
}


def connect_to_cards_db():
    """Connect to the cards database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Database connection failed: {e}")
        return None


def validate_date_consistency(races_file, expected_date):
    """Validate that the race dates in the file match what we expect"""
    try:
        df = pd.read_csv(races_file)
        unique_dates = df["Date"].unique()
        print(f"Found dates in data: {unique_dates}")

        if len(unique_dates) == 1 and unique_dates[0] == expected_date:
            print(f"✅ Date validation passed: All races are for {expected_date}")
            return True
        else:
            print(
                f"⚠️ Date validation warning: Expected {expected_date}, found {unique_dates}"
            )
            return False
    except Exception as e:
        print(f"Date validation failed: {e}")
        return False


def process_races_data(races_file, conn):
    """Process and upload races data"""
    try:
        df = pd.read_csv(races_file)
        print(f"Processing {len(df)} races...")

        cursor = conn.cursor()

        # Prepare data for insertion
        race_records = []
        for _, row in df.iterrows():
            race_records.append(
                (
                    row["Race_ID"],
                    row["race_number"],
                    row["race_time"],
                    row["course_id"],
                    row["Course"],
                    row["Race_type"],
                    row["Date"],
                    row["Race_name"],
                    row["Class"],
                    row["Years"],
                    row["Distance"],
                    row["Surface"],
                    row["Prize"],
                    row["Runners_racecard"],
                    row["Runners"],
                    row["Draw"],
                    row["EW_racecard"],
                    row["EW"],
                    row["Places_EW_racecard"],
                    row["Places_EW"],
                )
            )

        # Insert races (with ON CONFLICT DO NOTHING to avoid duplicates)
        insert_query = """
        INSERT INTO races (
            race_id, race_number, race_time, course_id, course, race_type,
            date, race_name, class, years, distance, surface, prize,
            runners_racecard, runners, draw, ew_racecard, ew,
            places_ew_racecard, places_ew
        ) VALUES %s
        ON CONFLICT (race_id) DO NOTHING
        """

        execute_values(cursor, insert_query, race_records)
        inserted = cursor.rowcount
        conn.commit()

        print(f"✅ Inserted {inserted} new races")
        return inserted

    except Exception as e:
        print(f"❌ Error processing races: {e}")
        conn.rollback()
        return 0


def process_horses_data(horses_file, conn):
    """Process and upload horses data"""
    try:
        df = pd.read_csv(horses_file)
        print(f"Processing {len(df)} horses...")

        cursor = conn.cursor()

        # Prepare data for insertion
        horse_records = []
        for _, row in df.iterrows():
            horse_records.append(
                (
                    row.get("ID"),
                    row.get("Race_ID"),
                    row.get("horse_number"),
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
                )
            )

        # Insert horses
        insert_query = """
        INSERT INTO horses (
            id, race_id, horse_number, draw, horse_id, country, name, age,
            weight_uk, weight, gears, horse_rate, jockey_id, jockey,
            trainer_id, trainer, fav, sp
        ) VALUES %s
        ON CONFLICT (id) DO NOTHING
        """

        execute_values(cursor, insert_query, horse_records)
        inserted = cursor.rowcount
        conn.commit()

        print(f"✅ Inserted {inserted} new horses")
        return inserted

    except Exception as e:
        print(f"❌ Error processing horses: {e}")
        conn.rollback()
        return 0


def main():
    """Main processing function"""
    manual_dir = (
        "/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/manual_download"
    )

    races_file = os.path.join(manual_dir, "races", "races.csv")
    horses_file = os.path.join(manual_dir, "horses", "horses.csv")

    print("🏇 Processing Manual Racing Data Upload")
    print("=====================================")

    # Validate files exist
    if not os.path.exists(races_file):
        print(f"❌ Races file not found: {races_file}")
        return

    if not os.path.exists(horses_file):
        print(f"❌ Horses file not found: {horses_file}")
        return

    # Validate date (expecting August 25th data in today's download)
    expected_date = "2025-08-25"
    if not validate_date_consistency(races_file, expected_date):
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            print("Aborted.")
            return

    # Connect to database
    conn = connect_to_cards_db()
    if not conn:
        print("❌ Cannot connect to database")
        return

    try:
        print(f"\n📅 Processing data for {expected_date}")

        # Process races
        races_inserted = process_races_data(races_file, conn)

        # Process horses
        horses_inserted = process_horses_data(horses_file, conn)

        print(f"\n✅ Processing Complete!")
        print(f"   • Races inserted: {races_inserted}")
        print(f"   • Horses inserted: {horses_inserted}")

        # Verify the data
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM races WHERE date = %s", (expected_date,))
        race_count = cursor.fetchone()[0]

        cursor.execute(
            """
            SELECT COUNT(*) FROM horses h 
            JOIN races r ON h.race_id = r.race_id 
            WHERE r.date = %s
        """,
            (expected_date,),
        )
        horse_count = cursor.fetchone()[0]

        print(f"\n📊 Database verification:")
        print(f"   • Total races for {expected_date}: {race_count}")
        print(f"   • Total horses for {expected_date}: {horse_count}")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
