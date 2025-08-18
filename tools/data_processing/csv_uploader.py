#!/usr/bin/env python3
"""
Daily CSV Uploader - Process today's downloaded CSV files
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


# Find the latest CSV files from daily downloads
def find_latest_csv_files():
    """Find the most recent CSV files from daily downloads"""
    downloads_dir = Path("project_root / 'data' / daily_downloads")
    csv_files = {}

    # Look for records.csv (race results)
    records_files = list(downloads_dir.rglob("records/records.csv"))
    if records_files:
        csv_files["race_results"] = str(
            max(records_files, key=lambda f: f.stat().st_mtime)
        )

    # Look for races.csv (race cards) in cards_data
    races_files = list(downloads_dir.glob("cards_project_root / 'data' / races/races.csv"))
    if races_files:
        csv_files["races_cards"] = str(
            max(races_files, key=lambda f: f.stat().st_mtime)
        )

    # Look for racecard_details.csv
    racecard_files = list(
        downloads_dir.glob("cards_project_root / 'data' / racecard_details/racecard_details.csv")
    )
    if racecard_files:
        csv_files["racecard_details"] = str(
            max(racecard_files, key=lambda f: f.stat().st_mtime)
        )

    return csv_files


def upload_csv_to_table(file_path, table_name, conn):
    """Upload CSV to database table"""
    try:
        print(f"📊 Processing {file_path} -> {table_name}")

        # Read CSV
        df = pd.read_csv(file_path)
        print(f"   Rows: {len(df)}, Columns: {len(df.columns)}")

        if len(df) == 0:
            print(f"   ⚠️ Empty file, skipping")
            return False

        # Get table columns (excluding auto-increment columns)
        with conn.cursor() as cur:
            cur.execute(
                f"""
                SELECT column_name, data_type, column_default
                FROM information_schema.columns 
                WHERE table_name = '{table_name}' 
                ORDER BY ordinal_position
            """
            )
            all_table_cols = cur.fetchall()

        if not all_table_cols:
            print(f"   ❌ Table {table_name} not found")
            return False

        # Filter out auto-increment and timestamp columns
        table_cols = []
        for col_name, data_type, col_default in all_table_cols:
            # Skip auto-increment columns (id)
            if col_default and "nextval" in str(col_default):
                print(f"   ⏭️ Skipping auto-increment column: {col_name}")
                continue
            # Skip auto-updated timestamp columns
            if col_name in ["created_at", "updated_at"]:
                print(f"   ⏭️ Skipping timestamp column: {col_name}")
                continue
            table_cols.append((col_name, data_type))

        # Match CSV columns to table columns
        csv_cols = [col.lower() for col in df.columns]
        table_col_names = [col[0] for col in table_cols]

        print(f"   CSV columns: {csv_cols[:5]}...")
        print(f"   Table columns: {table_col_names[:5]}...")

        # Simple column mapping - match by name
        matched_cols = []
        for table_col in table_col_names:
            if table_col in csv_cols:
                matched_cols.append(table_col)

        if not matched_cols:
            print(f"   ❌ No matching columns found")
            return False

        print(f"   ✅ Matched {len(matched_cols)} columns")

        # Prepare data for insert
        insert_data = []
        for _, row in df.iterrows():
            row_data = []
            for col in matched_cols:
                val = row.get(col)
                if pd.isna(val):
                    row_data.append(None)
                else:
                    row_data.append(str(val))
            insert_data.append(tuple(row_data))

        # Insert data
        if insert_data:
            with conn.cursor() as cur:
                cols_str = ", ".join(matched_cols)
                placeholders = ", ".join(["%s"] * len(matched_cols))

                execute_values(
                    cur,
                    f"INSERT INTO {table_name} ({cols_str}) VALUES %s",
                    insert_data,
                    page_size=1000,
                )
                conn.commit()
                print(f"   ✅ Inserted {len(insert_data)} rows")
                return True
        else:
            print(f"   ⚠️ No valid data to insert")
            return False

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False


def main():
    print("🚀 Daily CSV Uploader - Processing Downloaded Files")
    print("=" * 60)

    # Find CSV files
    csv_files = find_latest_csv_files()
    print(f"📁 Found {len(csv_files)} CSV files:")
    for table, file_path in csv_files.items():
        print(f"   {table}: {file_path}")
    print()

    if not csv_files:
        print("❌ No CSV files found in project_root / 'data' / daily_downloads")
        return

    # Connect to database
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        print("✅ Database connected")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Process each file
    successful = 0
    total = len(csv_files)

    for table_name, file_path in csv_files.items():
        print(f"\n🔄 Processing {table_name}...")
        if upload_csv_to_table(file_path, table_name, conn):
            successful += 1

    conn.close()

    print(f"\n📊 SUMMARY: {successful}/{total} files uploaded successfully")

    if successful == total:
        print("�� All files uploaded successfully!")
    else:
        print("⚠️ Some files failed - check errors above")


if __name__ == "__main__":
    main()
