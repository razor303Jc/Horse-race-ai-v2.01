#!/usr/bin/env python3
"""
Upload Results Data - Direct upload to results_horse_racing_db
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

# Use DATABASE_URL for results database
RESULTS_DATABASE_URL = os.getenv(
    "RESULTS_DATABASE_URL",
    "postgresql://horse_racing:secure_password_123@172.18.0.3:5432/"
    "results_horse_racing_db",
)

# Replace 'postgres' hostname with container IP when running outside Docker
if "postgres:5432" in RESULTS_DATABASE_URL:
    RESULTS_DATABASE_URL = RESULTS_DATABASE_URL.replace(
        "postgres:5432", "172.18.0.3:5432"
    )

# Parse RESULTS_DATABASE_URL
parsed_url = urlparse(RESULTS_DATABASE_URL)
DATABASE_CONFIG = {
    "host": parsed_url.hostname or "172.18.0.3",
    "port": parsed_url.port or 5432,
    "database": (
        parsed_url.path.lstrip("/") if parsed_url.path else "results_horse_racing_db"
    ),
    "user": parsed_url.username or "horse_racing",
    "password": parsed_url.password or "secure_password_123",
}


def upload_csv_to_results_database(csv_file, table_name):
    """Upload a CSV file to the results database with column mapping"""
    print(f"\n📄 Uploading {csv_file} to {table_name} (results_horse_racing_db)")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if df.empty:
            print("⚠️ CSV file is empty, skipping upload")
            return True

        # Load and clean CSV data with proper type handling
        df = pd.read_csv(csv_file)
        print(f"📊 Loaded {len(df)} rows, {len(df.columns)} columns")

        if df.empty:
            print("⚠️ CSV file is empty, skipping upload")
            return True

        # Apply smart data type conversions
        for col in df.columns:
            if col.lower() in [
                "id",
                "race_id",
                "horse_id",
                "horse_number",
                "place",
                "draw",
                "age",
                "jockey_id",
                "trainer_id",
                "horse_rate",
            ]:
                # Convert to integers, handling NaN and float strings
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            elif (
                col.lower() in ["weight", "sp", "finish_time"]
                or "distance" in col.lower()
                or "time" in col.lower()
                or "speed" in col.lower()
            ):
                # Convert to floats, handling NaN
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            else:
                # Keep as strings, handle NaN
                df[col] = df[col].astype(str).replace("nan", None).replace("None", None)

        # Convert DataFrame to list of tuples for insertion
        data_tuples = [tuple(row) for row in df.values]
        columns = list(df.columns)

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        try:
            # Clear existing data from table
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"🗑️ Cleared existing data from {table_name}")

            # Prepare bulk insert query
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            # Execute bulk insert
            cursor.executemany(query, data_tuples)

            # Commit transaction
            conn.commit()

            print(f"✅ Successfully uploaded {len(data_tuples)} rows to {table_name}")
            return True

        except Exception as e:
            conn.rollback()
            print(f"❌ Upload failed: {e}")
            return False

        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False


def test_connection():
    """Test connection to results database"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Connected to results database: {version[0]}")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False


if __name__ == "__main__":
    # Test database connection
    print("🔍 Testing results database connection...")
    test_connection()
