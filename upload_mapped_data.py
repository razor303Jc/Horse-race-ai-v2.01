#!/usr/bin/env python3
"""
Upload Mapped Data - Direct upload of our processed CSV files to database
"""

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path

# Database configuration for Docker
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5434,  # Docker mapped port
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


def upload_csv_to_database(csv_file, table_name):
    """Upload a CSV file to the database"""
    print(f"\n📄 Uploading {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if len(df) == 0:
            print("⚠️ No data to upload")
            return False

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

        # Build INSERT statement
        columns = df.columns.tolist()
        cols_str = ", ".join(columns)
        placeholders = ", ".join(["%s"] * len(columns))

        # Simple insert without conflict resolution
        with conn.cursor() as cur:
            query = f"INSERT INTO {table_name} ({cols_str}) VALUES %s"
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

    # Define the files to upload
    data_dir = Path("data/daily_downloads")
    uploads = [
        (data_dir / "complete_mapped_races.csv", "races"),
        (data_dir / "complete_mapped_records.csv", "records"),
        (data_dir / "complete_mapped_horses.csv", "horses"),
        (data_dir / "complete_mapped_jockeys_stats.csv", "jockeys_stats"),
        (data_dir / "complete_mapped_trainers_stats.csv", "trainers_stats"),
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
