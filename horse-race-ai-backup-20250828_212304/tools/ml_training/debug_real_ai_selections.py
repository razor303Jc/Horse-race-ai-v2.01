#!/usr/bin/env python3
"""
Debug version of Real AI Selections Generator
"""

import logging
import sys
import os
import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime, date, timedelta

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

print("Starting debug AI selections...")


def connect_results_database():
    """Connect to results database for training"""
    print("Connecting to results database...")
    return psycopg2.connect(
        host="postgres",
        database="results_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )


def connect_cards_database():
    """Connect to cards database for race card data"""
    print("Connecting to cards database...")
    return psycopg2.connect(
        host="postgres",
        database="cards_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )


def check_data_availability():
    """Check what data is available"""
    print("Checking data availability...")

    # Check results database
    with connect_results_database() as conn:
        cursor = conn.cursor()

        # Check races table
        cursor.execute("SELECT COUNT(*) FROM races WHERE result IS NOT NULL")
        results_count = cursor.fetchone()[0]
        print(f"Results database: {results_count} races with results")

        # Get date range
        cursor.execute(
            "SELECT MIN(date), MAX(date) FROM races WHERE result IS NOT NULL"
        )
        min_date, max_date = cursor.fetchone()
        print(f"Results date range: {min_date} to {max_date}")

    # Check cards database
    with connect_cards_database() as conn:
        cursor = conn.cursor()

        # Check races table
        cursor.execute("SELECT COUNT(*) FROM races")
        races_count = cursor.fetchone()[0]
        print(f"Cards database: {races_count} races")

        # Check racecard_details
        cursor.execute("SELECT COUNT(*) FROM racecard_details")
        cards_count = cursor.fetchone()[0]
        print(f"Cards database: {cards_count} racecard entries")

        # Get today's races
        today = date.today()
        cursor.execute("SELECT COUNT(*) FROM races WHERE date = %s", (today,))
        today_races = cursor.fetchone()[0]
        print(f"Today's races: {today_races}")

        # Get sample race data
        cursor.execute(
            """
            SELECT r.race_id, r.course, r.race_time, COUNT(rd.horse_name) as horses
            FROM races r
            LEFT JOIN racecard_details rd ON r.race_id = rd.race_id
            WHERE r.date >= %s
            GROUP BY r.race_id, r.course, r.race_time
            ORDER BY r.date, r.race_time
            LIMIT 5
        """,
            (today,),
        )

        sample_races = cursor.fetchall()
        print("Sample upcoming races:")
        for race in sample_races:
            print(f"  Race {race[0]}: {race[1]} at {race[2]} ({race[3]} horses)")


if __name__ == "__main__":
    try:
        check_data_availability()
        print("Debug check completed successfully!")
    except Exception as e:
        print(f"Error during debug check: {e}")
        import traceback

        traceback.print_exc()
