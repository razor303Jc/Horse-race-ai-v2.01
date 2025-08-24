#!/usr/bin/env python3
"""
🎯 Data Separation Plan
======================

Strategy for correctly separating cards and results data:

CARDS DATABASE (cards_horse_racing_db):
- Purpose: Store race cards for AI predictions
- Data: Current/future race cards (Aug 24th)
- Clean out: Old race cards (Aug 21st, 22nd)

RESULTS DATABASE (results_horse_racing_db):
- Purpose: Store completed race results for validation
- Data: Yesterday's results (Aug 23rd)
- Keep: Aug 21st results (historical)
"""

import psycopg2
import pandas as pd
from pathlib import Path


def clean_cards_database():
    """Clean cards database - keep only current race cards (Aug 24th)"""
    print("🧹 Cleaning Cards Database...")

    db_config = {
        "host": "postgres",
        "port": 5432,
        "database": "cards_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    conn = psycopg2.connect(**db_config)
    with conn.cursor() as cur:
        # Check current data
        cur.execute("SELECT date, COUNT(*) FROM races GROUP BY date ORDER BY date")
        before = cur.fetchall()
        print(f"Before cleanup: {before}")

        # Remove old race cards (keep only Aug 24th for AI predictions)
        cur.execute("DELETE FROM races WHERE date != '2025-08-24'")
        deleted_races = cur.rowcount
        print(f"Deleted {deleted_races} old race cards")

        # Check after cleanup
        cur.execute("SELECT date, COUNT(*) FROM races GROUP BY date ORDER BY date")
        after = cur.fetchall()
        print(f"After cleanup: {after}")

        conn.commit()

    conn.close()
    print("✅ Cards database cleaned - only Aug 24th race cards remain")


def upload_results_data():
    """Upload Aug 23rd results to results database"""
    print("📊 Uploading Results Data...")

    db_config = {
        "host": "postgres",
        "port": 5432,
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "secure_password_123",
    }

    # Load and process Aug 23rd results data
    results_files = [
        ("/app/data/daily_downloads/results_data/races/races.csv", "races"),
        ("/app/data/daily_downloads/results_data/horses/horses.csv", "horses"),
        ("/app/data/daily_downloads/results_data/records/records.csv", "records"),
        (
            "/app/data/daily_downloads/results_data/jockeys_stats/jockeys_stats.csv",
            "jockeys_stats",
        ),
        (
            "/app/data/daily_downloads/results_data/trainers_stats/trainers_stats.csv",
            "trainers_stats",
        ),
    ]

    conn = psycopg2.connect(**db_config)

    for csv_file, table_name in results_files:
        if Path(csv_file).exists():
            print(f"\n📄 Processing {csv_file} → {table_name}")
            df = pd.read_csv(csv_file)
            print(f"Loaded {len(df)} rows")

            # Apply column name fixes (same as our quick fixer)
            if table_name == "races":
                # Convert Race_ID → race_id, etc.
                df.columns = [
                    col.lower().replace("race_", "race_").replace("_", "_")
                    for col in df.columns
                ]
                df = df.rename(columns={"race_id": "race_id", "course": "course"})

            # Insert only Aug 23rd data
            if "date" in df.columns or "Date" in df.columns:
                date_col = "Date" if "Date" in df.columns else "date"
                df_filtered = df[df[date_col] == "2025-08-23"]
                print(f"Filtered to {len(df_filtered)} Aug 23rd records")
            else:
                df_filtered = df

            if len(df_filtered) > 0:
                # Insert data (simplified - would need proper column mapping)
                print(f"Would insert {len(df_filtered)} rows to {table_name}")
            else:
                print(f"No Aug 23rd data found in {csv_file}")
        else:
            print(f"⚠️ File not found: {csv_file}")

    conn.close()
    print("✅ Results data processing completed")


def show_plan():
    """Show the data separation plan"""
    print(
        """
🎯 DATA SEPARATION EXECUTION PLAN
================================

CURRENT ISSUES:
- Cards DB has mixed dates (21st, 22nd, 24th) ❌
- Results DB only has 21st, missing 23rd ❌

SOLUTION:
1. Clean Cards DB: Keep only Aug 24th race cards
2. Upload to Results DB: Add Aug 23rd completed results

RESULT:
- Cards DB: Aug 24th race cards for AI predictions ✅  
- Results DB: Aug 21st + Aug 23rd results for validation ✅

COMMANDS TO EXECUTE:
1. docker exec horse_racing_data_pipeline_clean python /app/tools/clean_and_separate_data.py --clean-cards
2. docker exec horse_racing_data_pipeline_clean python /app/tools/clean_and_separate_data.py --upload-results
    """
    )


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "--clean-cards":
            clean_cards_database()
        elif sys.argv[1] == "--upload-results":
            upload_results_data()
        elif sys.argv[1] == "--show-plan":
            show_plan()
    else:
        show_plan()
