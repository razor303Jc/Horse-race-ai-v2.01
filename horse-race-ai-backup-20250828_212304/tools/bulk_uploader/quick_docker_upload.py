#!/usr/bin/env python3
"""
Quick Docker Bulk Upload Script
Runs directly inside the ML trainer container to upload processed data
"""

import pandas as pd
import psycopg2
import psycopg2.extras
from pathlib import Path
import logging
import sys

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database config for Docker network
DB_CONFIG = {
    "host": "postgres",
    "port": 5432,
    "database": "results_horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

# Column mappings
COLUMN_MAPPINGS = {
    "horses": {"id": "horse_id", "name": "horse_name", "UptoDate": "uptodate"},
    "jockeys_stats": {
        "UptoDate": "uptodate",
        "Jockey_ID": "jockey_id",
        "Name": "jockey_name",
    },
    "trainers_stats": {
        "UptoDate": "uptodate",
        "Trainer_ID": "trainer_id",
        "Name": "trainer_name",
    },
    "records": {"id": "record_id", "Race_ID": "race_id"},
    "races": {"Race_ID": "race_id"},
}

# Upload order (foreign key constraints)
UPLOAD_ORDER = ["races", "horses", "jockeys_stats", "trainers_stats", "records"]


def test_connection():
    """Test database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
        conn.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def classify_file(file_path: Path) -> str:
    """Classify file to determine target table"""
    name = file_path.name.lower()
    if "horse" in name:
        return "horses"
    elif "jockey" in name:
        return "jockeys_stats"
    elif "trainer" in name:
        return "trainers_stats"
    elif "race" in name and "record" not in name:
        return "races"
    elif "record" in name or "result" in name:
        return "records"
    return None


def process_csv(file_path: Path, table_name: str):
    """Process and upload CSV file"""
    try:
        logger.info(f"📄 Processing {file_path.name} → {table_name}")

        # Load CSV
        df = pd.read_csv(file_path)
        logger.info(f"   Loaded {len(df)} rows")

        # Apply column mappings
        mappings = COLUMN_MAPPINGS.get(table_name, {})
        if mappings:
            df = df.rename(columns=mappings)
            logger.info(f"   Applied mappings: {mappings}")

        # Clean data
        df = df.dropna(how="all")
        df = df.fillna("")  # Replace NaN with empty string

        # Upload to database
        conn = psycopg2.connect(**DB_CONFIG)
        with conn:
            columns = list(df.columns)
            data_tuples = [tuple(row) for row in df.values]

            # Build query with proper parameter handling
            placeholders = "(" + ",".join(["%s"] * len(columns)) + ")"
            columns_str = ",".join(columns)
            query = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES %s
                ON CONFLICT DO NOTHING
            """

            # Execute bulk insert
            with conn.cursor() as cur:
                psycopg2.extras.execute_values(
                    cur, query, data_tuples, template=None, page_size=1000
                )

            conn.commit()

        conn.close()
        logger.info(f"   ✅ Uploaded {len(df)} records to {table_name}")
        return len(df)

    except Exception as e:
        logger.error(f"   ❌ Failed to process {file_path.name}: {e}")
        return 0


def main():
    """Main upload process"""
    print("🚀 Quick Docker Bulk Upload")
    print("=" * 40)

    # Test connection
    if not test_connection():
        return 1

    # Find processed directory
    processed_dir = Path("/app/data/daily_downloads/processed")
    if not processed_dir.exists():
        logger.error(f"❌ Directory not found: {processed_dir}")
        return 1

    # Find CSV files (excluding non_target)
    csv_files = []
    for file_path in processed_dir.rglob("*.csv"):
        if "non_target" not in str(file_path):
            csv_files.append(file_path)

    if not csv_files:
        logger.info("ℹ️  No CSV files found to process")
        return 0

    logger.info(f"📋 Found {len(csv_files)} CSV files")

    # Group by table
    files_by_table = {}
    for file_path in csv_files:
        table_name = classify_file(file_path)
        if table_name:
            if table_name not in files_by_table:
                files_by_table[table_name] = []
            files_by_table[table_name].append(file_path)

    # Process in order
    total_uploaded = 0
    for table_name in UPLOAD_ORDER:
        if table_name in files_by_table:
            logger.info(f"\n🔄 Processing {table_name} table:")
            table_uploaded = 0
            for file_path in files_by_table[table_name]:
                uploaded = process_csv(file_path, table_name)
                table_uploaded += uploaded
            logger.info(f"   📊 Table {table_name}: {table_uploaded} total records")
            total_uploaded += table_uploaded

    logger.info(f"\n🎉 Upload complete! Total records: {total_uploaded}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
