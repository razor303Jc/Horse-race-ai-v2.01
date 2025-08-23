#!/usr/bin/env python3
"""
Upload Results Data - Upload race results to results database
Direct version - for running from host using docker exec
"""

import pandas as pd
import subprocess
import json
from pathlib import Path
import sys
import os


def upload_csv_to_database(csv_file, table_name):
    """Upload a CSV file to the database using docker exec and COPY command"""
    print(f"\n📄 Uploading {csv_file} to {table_name}")

    try:
        # Load CSV to check data
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if len(df) == 0:
            print("⚠️ No data to upload")
            return False

        print(f"📋 Using columns: {list(df.columns)}")

        # Create temporary CSV with exact column mapping
        temp_csv = f"/tmp/{table_name}_upload.csv"
        df.to_csv(temp_csv, index=False, header=True)

        # Copy file into container
        copy_cmd = [
            "docker",
            "cp",
            temp_csv,
            f"horse_racing_postgres_clean:/tmp/{table_name}_upload.csv",
        ]
        subprocess.run(copy_cmd, check=True, capture_output=True)

        # Use COPY command to upload data
        copy_sql = f"""
        COPY {table_name} FROM '/tmp/{table_name}_upload.csv' 
        WITH (FORMAT csv, HEADER true);
        """

        # Execute the COPY command
        psql_cmd = [
            "docker",
            "exec",
            "-i",
            "horse_racing_postgres_clean",
            "psql",
            "-U",
            "horse_racing",
            "-d",
            "results_horse_racing_db",
            "-c",
            copy_sql,
        ]

        result = subprocess.run(psql_cmd, capture_output=True, text=True)

        if result.returncode == 0:
            # Get row count
            count_cmd = [
                "docker",
                "exec",
                "-i",
                "horse_racing_postgres_clean",
                "psql",
                "-U",
                "horse_racing",
                "-d",
                "results_horse_racing_db",
                "-t",
                "-c",
                f"SELECT COUNT(*) FROM {table_name};",
            ]
            count_result = subprocess.run(count_cmd, capture_output=True, text=True)
            total_rows = count_result.stdout.strip()

            print(f"✅ Upload completed! Total rows in {table_name}: {total_rows}")

            # Clean up temp file
            os.remove(temp_csv)
            return True
        else:
            print(f"❌ Upload failed: {result.stderr}")
            # Clean up temp file
            if os.path.exists(temp_csv):
                os.remove(temp_csv)
            return False

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def main():
    print("🏇 Results Data Uploader (Direct Version)")
    print("=" * 50)

    # Define RESULTS files to upload (after races finish)
    # IMPORTANT: Upload order matters due to foreign key constraints!
    data_dir = Path("data/daily_downloads/results_data")
    uploads = [
        # 1. Upload races first (parent table for results)
        (data_dir / "races" / "races.csv", "races"),
        # 2. Upload independent tables
        (data_dir / "horses" / "horses.csv", "horses"),
        (data_dir / "jockeys_stats" / "jockeys_stats.csv", "jockeys_stats"),
        (data_dir / "trainers_stats" / "trainers_stats.csv", "trainers_stats"),
        # 3. Upload records last (has foreign key to races)
        (data_dir / "records" / "records.csv", "records"),
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
        print("🎉 All results data uploaded successfully!")
    else:
        print("⚠️ Some uploads failed")


if __name__ == "__main__":
    main()
