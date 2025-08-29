#!/usr/bin/env python3
"""
Upload Mapped Data - Direct upload of our processed CSV files to database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
import os
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Use DATABASE_URL from environment like Docker containers do
# For race card data (before races), use cards database
CARDS_DATABASE_URL = os.getenv(
    "CARDS_DATABASE_URL",
    "postgresql://horse_racing:secure_password_123@localhost:5432/"
    "cards_horse_racing_db",
)

# Replace 'postgres' hostname with 'localhost' when running outside Docker
if "postgres:5432" in CARDS_DATABASE_URL:
    CARDS_DATABASE_URL = CARDS_DATABASE_URL.replace("postgres:5432", "localhost:5432")

# Parse CARDS_DATABASE_URL
parsed_url = urlparse(CARDS_DATABASE_URL)
DATABASE_CONFIG = {
    "host": parsed_url.hostname or "localhost",
    "port": parsed_url.port or 5432,
    "database": (
        parsed_url.path.lstrip("/") if parsed_url.path else "cards_horse_racing_db"
    ),
    "user": parsed_url.username or "horse_racing",
    "password": parsed_url.password or "secure_password_123",
}


def upload_csv_to_database(csv_file, table_name):
    """Upload a CSV file to the database with column mapping"""
    print(f"\n📄 Uploading {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if len(df) == 0:
            print("⚠️ No data to upload")
            return False

        # Since table names now match CSV files exactly, no complex mapping needed
        # Just handle special cases where column names might differ slightly

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)

        # Convert DataFrame to records for bulk insert
        # Handle NULL values properly
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
            query = f"""
                INSERT INTO {table_name} ({cols_str})
                VALUES %s
                ON CONFLICT DO NOTHING
            """
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
    print("🏇 Mapped Data Uploader")
    print("=" * 50)

    # Define RACE CARD files to upload (before race happens)
    # Results data is handled separately after races finish
    # IMPORTANT: Upload order matters due to foreign key constraints!
    data_dir = Path("data/daily_downloads")
    uploads = [
        # 1. Upload races first (parent table)
        (data_dir / "mapped_races.csv", "races"),
        # 2. Upload independent tables
        (data_dir / "mapped_horses.csv", "horses"),
        (data_dir / "mapped_jockeys_stats.csv", "jockeys_stats"),
        (data_dir / "mapped_trainers_stats.csv", "trainers_stats"),
        # 3. Upload racecard_details last (has foreign key to races)
        (data_dir / "mapped_racecard_details.csv", "racecard_details"),
        # mapped_records.csv is RESULTS data - handled by separate process
        # after races finish
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
