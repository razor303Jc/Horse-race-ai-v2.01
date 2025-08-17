#!/usr/bin/env python3
"""
🚀 Quick CSV Import - Post Download Trigger
===========================================

Import downloaded CSV data to database with correct credentials
"""

import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2


def main():
    print("🚀 Quick CSV Import - Post 15:15 Download")
    print("=" * 50)

    # Database connection with correct credentials
    try:
        conn = psycopg2.connect(
            host="horse_racing_postgres_clean",
            port=5432,
            database="horse_racing_db",
            user="horse_racing",
            password="secure_password_123",
        )
        print("✅ Database connection successful!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return

    # Find downloaded CSV files
    data_dirs = [
        "/app/data/daily_downloads/results_data",
        "/app/data/daily_downloads/cards_data",
    ]

    imported_files = 0
    total_records = 0

    for data_dir in data_dirs:
        data_path = Path(data_dir)
        if not data_path.exists():
            print(f"⚠️ Directory not found: {data_dir}")
            continue

        print(f"\n📁 Processing: {data_dir}")

        # Find all CSV files recursively
        csv_files = list(data_path.rglob("*.csv"))
        print(f"📊 Found {len(csv_files)} CSV files")

        for csv_file in csv_files:
            try:
                # Read CSV
                df = pd.read_csv(csv_file)
                if len(df) == 0:
                    print(f"   ⚠️ Empty file: {csv_file.name}")
                    continue

                # Determine table name from file structure
                table_name = get_table_name(csv_file)
                if not table_name:
                    print(f"   ⚠️ Cannot determine table for: {csv_file.name}")
                    continue

                # Import to database (simple INSERT)
                records_imported = import_csv_to_table(
                    conn, df, table_name, csv_file.name
                )
                if records_imported > 0:
                    imported_files += 1
                    total_records += records_imported
                    print(
                        f"   ✅ {csv_file.name}: {records_imported} records → {table_name}"
                    )
                else:
                    print(f"   ⚠️ {csv_file.name}: Import failed")

            except Exception as e:
                print(f"   ❌ Error processing {csv_file.name}: {e}")

    conn.close()

    print(f"\n🎯 IMPORT SUMMARY:")
    print(f"   📊 Files imported: {imported_files}")
    print(f"   📊 Total records: {total_records}")
    print(f"   ✅ CSV import completed!")


def get_table_name(csv_file):
    """Determine database table name from CSV file path"""
    file_name = csv_file.name.lower()

    if "races" in file_name:
        return "races"
    elif "horses" in file_name:
        return "horses"
    elif "records" in file_name:
        return "records"
    elif "jockeys" in file_name:
        return "jockeys"
    elif "trainers" in file_name:
        return "trainers"
    elif "racecard" in file_name:
        return "racecard_details"

    return None


def import_csv_to_table(conn, df, table_name, file_name):
    """Import DataFrame to database table"""
    try:
        cursor = conn.cursor()

        # Get existing table columns
        cursor.execute(
            f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = '{table_name}' 
            ORDER BY ordinal_position
        """
        )

        db_columns = [row[0] for row in cursor.fetchall()]
        if not db_columns:
            print(f"   ⚠️ Table '{table_name}' not found in database")
            return 0

        # Map CSV columns to database columns (case insensitive)
        csv_columns = df.columns.tolist()
        column_mapping = {}

        for csv_col in csv_columns:
            for db_col in db_columns:
                if csv_col.lower() == db_col.lower():
                    column_mapping[csv_col] = db_col
                    break

        if not column_mapping:
            print(f"   ⚠️ No matching columns found for {table_name}")
            return 0

        # Prepare data for insertion
        mapped_df = df[list(column_mapping.keys())].rename(columns=column_mapping)

        # Convert DataFrame to list of tuples
        records = [tuple(row) for row in mapped_df.values]

        # Create INSERT statement
        columns = list(column_mapping.values())
        placeholders = ",".join(["%s"] * len(columns))
        insert_sql = (
            f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        )

        # Execute batch insert
        cursor.executemany(insert_sql, records)
        conn.commit()

        return len(records)

    except Exception as e:
        conn.rollback()
        print(f"   ❌ Database error for {table_name}: {e}")
        return 0


if __name__ == "__main__":
    main()
