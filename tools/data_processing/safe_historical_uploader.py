#!/usr/bin/env python3
"""
Safe Historical Results Uploader
Upload historical data without clearing existing data, handling foreign keys properly
"""

import pandas as pd
import psycopg2
import logging
from pathlib import Path
import sys
import os

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Database configuration
DATABASE_CONFIG = {
    "host": "172.18.0.3",
    "port": 5432,
    "database": "results_horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}


def safe_upload_without_clearing(csv_file, table_name):
    """Upload CSV data without clearing existing table data"""
    logger.info(f"📤 Safe uploading {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        logger.info(f"📊 Loaded {len(df)} rows")

        if df.empty:
            logger.warning("⚠️ CSV file is empty")
            return True

        # Apply smart data type conversions
        for col in df.columns:
            col_lower = col.lower()

            if col_lower in [
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
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
            elif (
                col_lower in ["weight", "sp", "finish_time"]
                or "distance" in col_lower
                or "time" in col_lower
                or "speed" in col_lower
            ):
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            else:
                df[col] = df[col].astype(str).replace("nan", None).replace("None", None)

        # Convert to tuples for insertion
        data_tuples = [tuple(row) for row in df.values]
        columns = list(df.columns)

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        try:
            # Use INSERT ON CONFLICT DO NOTHING for safe insertion
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))

            if table_name == "races":
                # For races, use race_id as conflict resolution
                query = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT (race_id) DO NOTHING
                """
            elif table_name == "records":
                # For records, we need a composite unique constraint or use a different approach
                # First, let's insert only records for races that exist
                query = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                ON CONFLICT DO NOTHING
                """
            else:
                query = f"""
                INSERT INTO {table_name} ({columns_str}) 
                VALUES ({placeholders})
                """

            # Execute bulk insert with conflict resolution
            inserted_count = 0
            for row in data_tuples:
                try:
                    cursor.execute(query, row)
                    if cursor.rowcount > 0:
                        inserted_count += 1
                except psycopg2.IntegrityError as e:
                    # Skip rows that violate constraints
                    conn.rollback()
                    logger.debug(f"Skipped row due to constraint: {e}")
                    continue
                except Exception as e:
                    conn.rollback()
                    logger.debug(f"Skipped row due to error: {e}")
                    continue

            # Commit all successful insertions
            conn.commit()
            logger.info(
                f"✅ Successfully inserted {inserted_count} new rows into {table_name}"
            )
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Upload failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"❌ Failed to process CSV: {e}")
        return False


def upload_historical_data_safely():
    """Upload all historical data safely without clearing existing data"""
    logger.info("🔧 Safe Historical Results Data Upload")
    logger.info("=" * 50)

    # Files to upload (in dependency order)
    files_to_upload = [
        ("data/daily_downloads/complete_races.csv", "races"),
        ("data/daily_downloads/complete_records.csv", "records"),
    ]

    results = {}

    for csv_file, table_name in files_to_upload:
        if not os.path.exists(csv_file):
            logger.warning(f"⚠️ File not found: {csv_file}")
            continue

        logger.info(f"\n📋 Processing {table_name}")

        # Remove source_date column if present
        df = pd.read_csv(csv_file)
        if "source_date" in df.columns:
            df = df.drop("source_date", axis=1)
            fixed_file = csv_file.replace(".csv", "_no_source_date.csv")
            df.to_csv(fixed_file, index=False)
            csv_file = fixed_file
            logger.info("🗑️ Removed source_date column")

        # Upload safely
        success = safe_upload_without_clearing(csv_file, table_name)
        results[table_name] = success

    # Check final counts
    logger.info("\n" + "=" * 50)
    logger.info("📊 CHECKING FINAL DATABASE COUNTS")
    logger.info("=" * 50)

    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM races")
        races_count = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        records_count = cursor.fetchone()[0]

        logger.info(f"🏁 Total races in database: {races_count}")
        logger.info(f"📋 Total records in database: {records_count}")

        cursor.close()
        conn.close()

    except Exception as e:
        logger.error(f"❌ Error checking counts: {e}")

    successful_uploads = sum(results.values())
    logger.info(
        f"\n✅ Successfully uploaded {successful_uploads}/{len(results)} tables"
    )

    return successful_uploads > 0


def main():
    """Main function"""
    try:
        logger.info("🏇 Safe Historical Results Uploader")
        logger.info("Safely uploading complete historical results (Aug 19-23)")

        success = upload_historical_data_safely()

        if success:
            print("\n🎉 Historical results upload completed!")
            return 0
        else:
            print("\n❌ Historical results upload had issues!")
            return 1

    except Exception as e:
        logger.error(f"💥 Upload failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
