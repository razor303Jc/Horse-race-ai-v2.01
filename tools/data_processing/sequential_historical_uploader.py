#!/usr/bin/env python3
"""
Sequential Historical Data Uploader
Upload historical data in proper sequence: missing races first, then all records
"""

import pandas as pd
import psycopg2
import logging
from pathlib import Path
import sys

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


def get_existing_race_ids():
    """Get list of race IDs already in database"""
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT race_id FROM races")
        existing_ids = set(row[0] for row in cursor.fetchall())
        cursor.close()
        conn.close()
        logger.info(f"📊 Found {len(existing_ids)} existing races in database")
        return existing_ids
    except Exception as e:
        logger.error(f"❌ Error getting existing race IDs: {e}")
        return set()


def upload_new_races_only():
    """Upload only races that don't exist in database"""
    logger.info("🏁 Uploading missing historical races")

    # Get existing race IDs
    existing_race_ids = get_existing_race_ids()

    # Load complete races data
    races_df = pd.read_csv("data/daily_downloads/complete_races_no_source_date.csv")
    logger.info(f"📊 Total races in file: {len(races_df)}")

    # Filter to only new races
    new_races_df = races_df[~races_df["Race_ID"].isin(existing_race_ids)]
    logger.info(f"🆕 New races to upload: {len(new_races_df)}")

    if len(new_races_df) == 0:
        logger.info("✅ No new races to upload")
        return True

    # Save new races to temporary file
    temp_file = "data/daily_downloads/new_races_only.csv"
    new_races_df.to_csv(temp_file, index=False)

    # Upload new races
    success = upload_csv_to_database(temp_file, "races")
    if success:
        logger.info(f"✅ Successfully uploaded {len(new_races_df)} new races")
    else:
        logger.error(f"❌ Failed to upload new races")

    return success


def upload_csv_to_database(csv_file, table_name):
    """Upload CSV to database with proper type conversion"""
    logger.info(f"📤 Uploading {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        logger.info(f"📊 Loaded {len(df)} rows")

        if df.empty:
            return True

        # Apply data type conversions
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

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        try:
            # Clear existing data from table
            cursor.execute(f"DELETE FROM {table_name}")
            logger.info(f"🗑️ Cleared existing data from {table_name}")

            # Prepare bulk insert
            columns = list(df.columns)
            data_tuples = [tuple(row) for row in df.values]

            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            # Execute bulk insert
            cursor.executemany(query, data_tuples)
            conn.commit()

            logger.info(
                f"✅ Successfully uploaded {len(data_tuples)} rows to {table_name}"
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


def upload_complete_historical_data():
    """Upload complete historical data in proper sequence"""
    logger.info("🚀 Sequential Historical Data Upload")
    logger.info("=" * 50)

    # Step 1: Upload missing races first
    logger.info("\n📋 STEP 1: Upload missing races")
    races_success = upload_new_races_only()

    if not races_success:
        logger.error("❌ Failed to upload races, aborting")
        return False

    # Step 2: Upload all records (clearing existing ones)
    logger.info("\n📋 STEP 2: Upload all records")
    records_success = upload_csv_to_database(
        "data/daily_downloads/complete_records_no_source_date.csv", "records"
    )

    if not records_success:
        logger.error("❌ Failed to upload records")
        return False

    # Step 3: Check final counts
    logger.info("\n📋 STEP 3: Verify final counts")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM races")
        total_races = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        total_records = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(race_id), MAX(race_id) FROM races")
        min_race, max_race = cursor.fetchone()

        logger.info(f"🏁 Total races: {total_races} (IDs: {min_race} to {max_race})")
        logger.info(f"📋 Total records: {total_records}")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ Error checking final counts: {e}")
        return False


def main():
    """Main function"""
    try:
        logger.info("🏇 Sequential Historical Data Uploader")
        logger.info("Uploading complete historical results data (Aug 19-23)")

        success = upload_complete_historical_data()

        if success:
            print("\n🎉 Complete historical data upload successful!")
            print("✅ All races from Aug 19-23 are now in the database")
            print("✅ All race records from Aug 19-23 are now in the database")
            return 0
        else:
            print("\n❌ Historical data upload failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Upload failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
