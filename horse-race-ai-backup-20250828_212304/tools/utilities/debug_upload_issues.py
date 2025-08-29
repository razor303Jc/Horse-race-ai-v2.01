#!/usr/bin/env python3
"""
Debug Database Upload Issues
============================

Test specific data type conversion and upload issues.
"""

import asyncio
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

load_dotenv()


async def debug_upload_issues():
    """Debug specific upload issues with detailed error reporting"""
    print("🔧 Debugging Database Upload Issues")
    print("=" * 50)

    # Import the database manager
    from src.database.database_manager import DatabaseManager

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL not found")
        return

    db_manager = DatabaseManager(database_url)

    # Find a sample CSV file
    csv_files = list(Path("project_root / 'data' / daily_downloads").rglob("records.csv"))
    if not csv_files:
        print("❌ No records.csv files found")
        return

    csv_file = csv_files[0]
    print(f"📄 Testing with: {csv_file}")

    # Load CSV
    df = pd.read_csv(csv_file)
    print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")
    print("Columns:", df.columns.tolist()[:10], "...")

    # Check specific problematic rows
    print("\n🔍 Checking data types and ranges:")

    # Check ID column
    if "ID" in df.columns:
        id_values = df["ID"].dropna()
        print(f"ID range: {id_values.min()} to {id_values.max()}")
        print(f"ID type: {id_values.dtype}")

        # Check if any values are too large for different integer types
        large_ids = id_values[id_values > 2147483647]  # Max int32
        if len(large_ids) > 0:
            print(f"⚠️ Found {len(large_ids)} IDs requiring bigint: {large_ids.head()}")

    # Check other integer columns that might be problematic
    int_columns = ["Horse_ID", "jockey_ID", "trainer_ID", "Race_ID"]
    for col in int_columns:
        if col in df.columns:
            values = df[col].dropna()
            if len(values) > 0:
                print(f"{col} range: {values.min()} to {values.max()}")
                large_vals = values[values > 2147483647]
                if len(large_vals) > 0:
                    print(f"⚠️ {col} has {len(large_vals)} values requiring bigint")

    # Test data cleaning for a sample row
    print("\n🧪 Testing data conversion on sample row:")
    sample_row = df.iloc[0]
    print("Sample row data:")
    for col, val in sample_row.items()[:15]:  # First 15 columns
        print(f"  {col}: {val} ({type(val)})")

    # Test database connection
    print("\n🗄️ Testing database connection:")
    try:
        with db_manager.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                print(f"✅ Connected to: {version}")

                # Check race_results table structure
                cursor.execute(
                    """
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = 'race_results' 
                    AND column_name IN ('id', 'race_result_id', 'horse_id', 'jockey_id', 'trainer_id')
                    ORDER BY ordinal_position;
                """
                )

                print("race_results ID columns:")
                for row in cursor.fetchall():
                    print(f"  {row[0]}: {row[1]}")

    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return

    print("\n✅ Debug analysis complete")


if __name__ == "__main__":
    asyncio.run(debug_upload_issues())
