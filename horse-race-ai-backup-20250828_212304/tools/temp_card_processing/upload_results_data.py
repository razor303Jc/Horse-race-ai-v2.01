#!/usr/bin/env python3
"""
Comprehensive Results Data Upload Script
Processes all results ZIP files and uploads to results_horse_racing_db
"""

import os
import pandas as pd
import psycopg2
import zipfile
import logging
from psycopg2.extras import execute_values

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
logger = logging.getLogger(__name__)


def get_database_connection():
    """Get connection to results database"""
    return psycopg2.connect(
        host="postgres",
        database="results_horse_racing_db",
        user="horse_racing",
        password=os.getenv("POSTGRES_PASSWORD", "secure_password_123"),
    )


def extract_and_process_results_zip(zip_path, temp_dir="/tmp/results_extract"):
    """Extract results ZIP file and return processed data"""
    logger.info(f"🔧 Processing ZIP: {zip_path}")

    # Create temp directory
    os.makedirs(temp_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(temp_dir)

        # Process different data types
        data_files = {}

        # Process records (main results data)
        records_file = os.path.join(temp_dir, "records/records.csv")
        if os.path.exists(records_file):
            records_df = pd.read_csv(records_file)
            logger.info(f"📊 Found {len(records_df)} records")
            data_files["records"] = records_df

        # Process races
        races_file = os.path.join(temp_dir, "races/races.csv")
        if os.path.exists(races_file):
            races_df = pd.read_csv(races_file)
            logger.info(f"🏁 Found {len(races_df)} races")
            data_files["races"] = races_df

        # Process horses
        horses_file = os.path.join(temp_dir, "horses/horses.csv")
        if os.path.exists(horses_file):
            horses_df = pd.read_csv(horses_file)
            logger.info(f"🐎 Found {len(horses_df)} horses")
            data_files["horses"] = horses_df

        return data_files

    except Exception as e:
        logger.error(f"❌ Error processing ZIP {zip_path}: {e}")
        return {}
    finally:
        # Cleanup temp directory
        import shutil

        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


def upload_records_data(records_df, race_date=None):
    """Upload records data to results database"""
    logger.info(f"📤 Uploading {len(records_df)} records...")

    conn = get_database_connection()
    try:
        cursor = conn.cursor()

        # Get current max record_id
        cursor.execute("SELECT COALESCE(MAX(record_id), 0) FROM records")
        max_id = cursor.fetchone()[0]
        logger.info(f"📊 Current max record_id: {max_id}")

        # Prepare data for insertion with proper mapping
        records_data = []
        for i, (_, row) in enumerate(records_df.iterrows()):
            new_record_id = max_id + i + 1

            # Handle position field - convert racing codes to numbers or None
            position_val = row.get("Place")
            clean_position = None
            if pd.notna(position_val):
                try:
                    clean_position = int(position_val)
                except (ValueError, TypeError):
                    # Handle racing codes like "PU", "F", "UR", etc.
                    if str(position_val).isdigit():
                        clean_position = int(position_val)
                    # Leave as None for non-numeric positions

            # Handle starting price - extract numeric value
            sp_val = row.get("SP")
            clean_sp = None
            if pd.notna(sp_val):
                try:
                    clean_sp = float(sp_val)
                except (ValueError, TypeError):
                    # Try to extract number from strings like "7/2", "5/1"
                    sp_str = str(sp_val)
                    if "/" in sp_str and len(sp_str.split("/")) == 2:
                        try:
                            num, den = sp_str.split("/")
                            clean_sp = float(num) / float(den)
                        except:
                            pass

            # Map CSV columns to database schema
            record_data = (
                new_record_id,  # record_id
                row.get("Race_ID"),  # race_id
                row.get("Name", ""),  # horse_name
                row.get("jockey", ""),  # jockey
                row.get("trainer", ""),  # trainer
                clean_position,  # position (cleaned)
                clean_sp,  # starting_price (cleaned)
                row.get("weight", ""),  # weight (as string)
                row.get("Age") if pd.notna(row.get("Age")) else None,  # age
                None,  # form (not in CSV)
                (
                    row.get("jockey_ID") if pd.notna(row.get("jockey_ID")) else None
                ),  # jockey_id
                (
                    row.get("trainer_ID") if pd.notna(row.get("trainer_ID")) else None
                ),  # trainer_id
                (
                    row.get("Horse_ID") if pd.notna(row.get("Horse_ID")) else None
                ),  # horse_id
            )
            records_data.append(record_data)

        # Insert records with correct column mapping
        insert_query = """
            INSERT INTO records 
            (record_id, race_id, horse_name, jockey, trainer, position, starting_price, 
             weight, age, form, jockey_id, trainer_id, horse_id)
            VALUES %s
            ON CONFLICT (record_id) DO NOTHING
        """

        execute_values(cursor, insert_query, records_data)
        conn.commit()

        uploaded_count = cursor.rowcount
        logger.info(f"✅ Successfully uploaded {uploaded_count} new records")

    except Exception as e:
        logger.error(f"❌ Error uploading records: {e}")
        conn.rollback()
    finally:
        conn.close()


def process_all_results_data():
    """Process all available results ZIP files"""
    logger.info("🚀 COMPREHENSIVE RESULTS DATA UPLOAD")
    logger.info("=" * 60)

    processed_dir = "/app/data/daily_downloads/processed"
    results_files = []

    # Find all results ZIP files (excluding non_target for now)
    for root, dirs, files in os.walk(processed_dir):
        if "non_target" in root:
            continue  # Skip non_target files to avoid duplicates

        for file in files:
            if "results" in file and file.endswith(".zip"):
                zip_path = os.path.join(root, file)
                folder = os.path.basename(root)
                results_files.append((folder, zip_path))

    logger.info(f"📁 Found {len(results_files)} results files to process")

    total_records_uploaded = 0

    for folder, zip_path in sorted(results_files):
        logger.info(f"\\n📦 Processing {folder}: {os.path.basename(zip_path)}")

        # Extract and process data
        data_files = extract_and_process_results_zip(zip_path)

        if "records" in data_files and "races" in data_files:
            records_df = data_files["records"]
            races_df = data_files["races"]

            # Get race date from races data
            race_date = None
            if "Date" in races_df.columns and len(races_df) > 0:
                race_date = races_df["Date"].iloc[0]
                logger.info(f"📅 Race date: {race_date}")

            # Upload records
            initial_count = len(records_df)
            upload_records_data(records_df, race_date)
            total_records_uploaded += initial_count

        else:
            logger.warning(f"⚠️ Missing required data files in {zip_path}")

    logger.info(f"\\n🎉 UPLOAD COMPLETE!")
    logger.info(f"📊 Total records processed: {total_records_uploaded:,}")

    # Final database summary
    conn = get_database_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM records")
        final_count = cursor.fetchone()[0]
        logger.info(f"📋 Final database count: {final_count:,}")
    except Exception as e:
        logger.error(f"❌ Error getting final count: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    process_all_results_data()
