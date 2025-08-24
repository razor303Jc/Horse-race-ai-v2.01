#!/usr/bin/env python3
"""
🎯 Fixed Data Uploader
===================

Upload the column-fixed CSV files to the database with proper schema matching.
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import os
from urllib.parse import urlparse

# Set database URL for cards database (container environment)
CARDS_DATABASE_URL = (
    "postgresql://horse_racing:secure_password_123@postgres:5432/"
    "cards_horse_racing_db"
)

# Parse CARDS_DATABASE_URL
parsed_url = urlparse(CARDS_DATABASE_URL)
DATABASE_CONFIG = {
    "host": parsed_url.hostname or "postgres",
    "port": parsed_url.port or 5432,
    "database": (
        parsed_url.path.lstrip("/") if parsed_url.path else "cards_horse_racing_db"
    ),
    "user": parsed_url.username or "horse_racing",
    "password": parsed_url.password or "secure_password_123",
}


def upload_csv_to_database(csv_file, table_name):
    """Upload a CSV file to the database with proper column mapping"""
    print(f"\n📄 Uploading {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"📋 Columns: {list(df.columns)}")

        if len(df) == 0:
            print("⚠️ No data to upload")
            return False

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)

        # Convert DataFrame to records for bulk insert
        insert_data = []
        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val) or val == "" or val == "None":
                    row_data.append(None)
                else:
                    row_data.append(val)
            insert_data.append(tuple(row_data))

        # Build INSERT statement with conflict handling
        columns = df.columns.tolist()
        cols_str = ", ".join(columns)

        # Use INSERT with ON CONFLICT to handle duplicates
        with conn.cursor() as cur:
            # For tables with auto-incrementing IDs, handle them specially
            if table_name in ["horses", "jockeys_stats", "trainers_stats"]:
                # Skip the ID column in insert, let database handle it
                if table_name == "horses" and "horse_id" in columns:
                    # Skip horse_id, it's auto-generated
                    cols_without_id = [col for col in columns if col != "horse_id"]
                    cols_str = ", ".join(cols_without_id)
                    insert_data = [
                        tuple(
                            row[i] for i, col in enumerate(columns) if col != "horse_id"
                        )
                        for row in insert_data
                    ]

                elif table_name == "jockeys_stats" and "jockey_id" in columns:
                    # Skip jockey_id, it's auto-generated
                    cols_without_id = [col for col in columns if col != "jockey_id"]
                    cols_str = ", ".join(cols_without_id)
                    insert_data = [
                        tuple(
                            row[i]
                            for i, col in enumerate(columns)
                            if col != "jockey_id"
                        )
                        for row in insert_data
                    ]

                elif table_name == "trainers_stats" and "trainer_id" in columns:
                    # Skip trainer_id, it's auto-generated
                    cols_without_id = [col for col in columns if col != "trainer_id"]
                    cols_str = ", ".join(cols_without_id)
                    insert_data = [
                        tuple(
                            row[i]
                            for i, col in enumerate(columns)
                            if col != "trainer_id"
                        )
                        for row in insert_data
                    ]

            query = f"""
                INSERT INTO {table_name} ({cols_str})
                VALUES %s
                ON CONFLICT DO NOTHING
            """

            print(f"🔄 Executing: INSERT INTO {table_name} ({cols_str}) VALUES ...")
            execute_values(cur, query, insert_data, page_size=1000)
            conn.commit()

            # Get number of inserted rows
            cur.execute(f"SELECT COUNT(*) FROM {table_name}")
            total_rows = cur.fetchone()[0]

        conn.close()
        print(f"✅ Upload completed! Total rows in {table_name}: {total_rows}")
        return True

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def main():
    print("🎯 Fixed Data Uploader")
    print("=" * 50)

    # Define fixed files to upload in dependency order
    data_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads/fixed")
    uploads = [
        # 1. Upload races first (parent table)
        (data_dir / "fixed_mapped_races.csv", "races"),
        # 2. Upload independent tables
        (data_dir / "fixed_mapped_horses.csv", "horses"),
        (data_dir / "fixed_mapped_jockeys_stats.csv", "jockeys_stats"),
        (data_dir / "fixed_mapped_trainers_stats.csv", "trainers_stats"),
        # 3. Upload racecard_details last (has foreign key to races)
        (data_dir / "fixed_mapped_racecard_details.csv", "racecard_details"),
    ]

    successful = 0
    total = len(uploads)

    for csv_file, table_name in uploads:
        if csv_file.exists():
            if upload_csv_to_database(csv_file, table_name):
                successful += 1
        else:
            print(f"⚠️ File not found: {csv_file}")

    print(f"\n📊 SUMMARY: {successful}/{total} uploads successful")

    if successful == total:
        print("🎉 All data uploaded successfully!")
    else:
        print("⚠️ Some uploads failed")


if __name__ == "__main__":
    main()
