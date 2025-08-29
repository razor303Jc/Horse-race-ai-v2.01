#!/usr/bin/env python3
"""
Append-Only Historical Data Uploader
Add missing historical data without clearing existing data
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


def append_only_upload(csv_file, table_name, key_column="race_id"):
    """Upload CSV data by appending only new records"""
    logger.info(f"📤 Append-only upload: {csv_file} to {table_name}")

    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        logger.info(f"📊 Loaded {len(df)} rows from CSV")

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
            elif col_lower == "race_time":
                # Convert race_time to proper time format, handle 0.0 as NULL
                df[col] = df[col].astype(str)
                df[col] = df[col].replace("0.0", None)
                df[col] = df[col].replace("nan", None)
            elif (
                col_lower in ["weight", "sp", "finish_time"]
                or "distance" in col_lower
                or ("time" in col_lower and col_lower != "race_time")
                or "speed" in col_lower
            ):
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            else:
                df[col] = df[col].astype(str).replace("nan", None).replace("None", None)

        # Connect to database
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        try:
            # Get existing keys
            cursor.execute(f"SELECT {key_column} FROM {table_name}")
            existing_keys = set(row[0] for row in cursor.fetchall())
            logger.info(
                f"📊 Found {len(existing_keys)} existing records in {table_name}"
            )

            # Filter to only new records
            if key_column in df.columns:
                new_df = df[~df[key_column].isin(existing_keys)]
                logger.info(f"🆕 New records to insert: {len(new_df)}")
            else:
                new_df = df  # If no key column, insert all
                logger.info(f"🆕 Inserting all records (no key column): {len(new_df)}")

            if len(new_df) == 0:
                logger.info("✅ No new records to insert")
                return True

            # Prepare bulk insert for new records only
            columns = list(new_df.columns)
            data_tuples = [tuple(row) for row in new_df.values]

            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"

            # Execute bulk insert
            cursor.executemany(query, data_tuples)
            conn.commit()

            logger.info(
                f"✅ Successfully inserted {len(data_tuples)} new rows into {table_name}"
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


def upload_all_historical_data():
    """Upload all missing historical data"""
    logger.info("🚀 Append-Only Historical Data Upload")
    logger.info("=" * 50)

    # Step 1: Add missing races
    logger.info("\n📋 STEP 1: Add missing races")
    races_success = append_only_upload(
        "data/daily_downloads/complete_races_no_source_date.csv", "races", "Race_ID"
    )

    if not races_success:
        logger.error("❌ Failed to upload races")
        return False

    # Step 2: Add missing records
    logger.info("\n📋 STEP 2: Add missing records")

    # For records, we need to be more careful about duplicates
    # Let's use a combination of race_id and horse_number as uniqueness check
    records_success = append_only_upload_records()

    if not records_success:
        logger.error("❌ Failed to upload records")
        return False

    # Step 3: Check final counts
    logger.info("\n📋 STEP 3: Verify final database state")
    try:
        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM races")
        total_races = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*) FROM records")
        total_records = cursor.fetchone()[0]

        cursor.execute("SELECT MIN(race_id), MAX(race_id) FROM races")
        min_race, max_race = cursor.fetchone()

        cursor.execute(
            """
        SELECT DATE(created_at) as race_date, COUNT(*) as count 
        FROM races 
        GROUP BY DATE(created_at) 
        ORDER BY race_date
        """
        )
        date_counts = cursor.fetchall()

        logger.info(f"🏁 Total races: {total_races} (IDs: {min_race} to {max_race})")
        logger.info(f"📋 Total records: {total_records}")
        logger.info("📅 Races by date:")
        for date, count in date_counts:
            logger.info(f"   {date}: {count} races")

        cursor.close()
        conn.close()

        return True

    except Exception as e:
        logger.error(f"❌ Error checking final state: {e}")
        return False


def append_only_upload_records():
    """Special handling for records to avoid duplicates"""
    logger.info("📤 Append-only upload for records with duplicate checking")

    try:
        # Load records CSV
        df = pd.read_csv("data/daily_downloads/complete_records_no_source_date.csv")
        logger.info(f"📊 Loaded {len(df)} records from CSV")

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
            # Get existing race_id, horse_number combinations
            cursor.execute("SELECT race_id, horse_number FROM records")
            existing_combinations = set(cursor.fetchall())
            logger.info(f"📊 Found {len(existing_combinations)} existing records")

            # Filter out existing combinations
            new_records = []
            for _, row in df.iterrows():
                race_id = int(row["Race_ID"])
                horse_number = int(row["Horse_number"])
                if (race_id, horse_number) not in existing_combinations:
                    new_records.append(tuple(row))

            logger.info(f"🆕 New records to insert: {len(new_records)}")

            if len(new_records) == 0:
                logger.info("✅ No new records to insert")
                return True

            # Prepare bulk insert
            columns = list(df.columns)
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            query = f"INSERT INTO records ({columns_str}) VALUES ({placeholders})"

            # Execute bulk insert
            cursor.executemany(query, new_records)
            conn.commit()

            logger.info(f"✅ Successfully inserted {len(new_records)} new records")
            return True

        except Exception as e:
            conn.rollback()
            logger.error(f"❌ Records upload failed: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    except Exception as e:
        logger.error(f"❌ Failed to process records: {e}")
        return False


def main():
    """Main function"""
    try:
        logger.info("🏇 Append-Only Historical Data Uploader")
        logger.info("Adding complete historical results data (Aug 19-23)")

        success = upload_all_historical_data()

        if success:
            print("\n🎉 Complete historical data upload successful!")
            print("✅ All missing races from Aug 19-23 added to database")
            print("✅ All missing race records from Aug 19-23 added to database")
            return 0
        else:
            print("\n❌ Historical data upload failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Upload failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
