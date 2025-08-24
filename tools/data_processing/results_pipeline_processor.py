#!/usr/bin/env python3
"""
Results Data Pipeline Processor
Processes results data from processed directory and uploads to results_horse_racing_db
"""

import os
import sys
import zipfile
import logging
import pandas as pd
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import after path setup
from tools.data_processing.clean_data import (
    clean_races_data,
    clean_records_data,
    clean_horses_data,
    clean_jockeys_stats,
    clean_trainers_stats,
)
from tools.data_processing.upload_results_data import upload_csv_to_results_database


def clean_csv_data(csv_type, input_file, output_file):
    """Clean CSV data based on type"""
    if csv_type == "races":
        return clean_races_data()
    elif csv_type == "records":
        return clean_records_data()
    elif csv_type == "horses":
        return clean_horses_data()
    elif csv_type == "jockeys_stats":
        return clean_jockeys_stats()
    elif csv_type == "trainers_stats":
        return clean_trainers_stats()
    else:
        logger.warning(f"Unknown CSV type: {csv_type}")
        return False


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data/logs/results_pipeline.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def extract_results_zip(zip_path, extract_dir):
    """Extract results zip file and return list of CSV files"""
    logger.info(f"📦 Extracting {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)

    # Find CSV files
    csv_files = []
    for root, dirs, files in os.walk(extract_dir):
        for file in files:
            if file.endswith(".csv"):
                csv_files.append(os.path.join(root, file))

    logger.info(f"📄 Found {len(csv_files)} CSV files")
    return csv_files


def identify_csv_type(csv_path):
    """Identify the type of CSV file based on filename patterns"""
    filename = os.path.basename(csv_path).lower()

    if "race" in filename and "card" not in filename:
        return "races"
    elif "record" in filename or "result" in filename:
        return "records"
    elif "horse" in filename:
        return "horses"
    elif "jockey" in filename:
        return "jockeys_stats"
    elif "trainer" in filename:
        return "trainers_stats"
    else:
        logger.warning(f"⚠️ Unknown CSV type for: {filename}")
        return "unknown"


def process_results_date(date_dir):
    """Process all results data for a specific date"""
    logger.info(f"🗓️ Processing results for date: {os.path.basename(date_dir)}")

    # Find results zip file
    results_files = [
        f
        for f in os.listdir(date_dir)
        if f.startswith("results_") and f.endswith(".zip")
    ]

    if not results_files:
        logger.warning(f"⚠️ No results zip file found in {date_dir}")
        return False

    results_zip = os.path.join(date_dir, results_files[0])
    logger.info(f"📦 Processing: {results_zip}")

    # Create temporary extraction directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Extract zip file
        csv_files = extract_results_zip(results_zip, temp_dir)

        if not csv_files:
            logger.error(f"❌ No CSV files found in {results_zip}")
            return False

        # Process each CSV file
        success_count = 0
        total_files = len(csv_files)

        for csv_file in csv_files:
            try:
                # Identify CSV type
                csv_type = identify_csv_type(csv_file)

                if csv_type == "unknown":
                    logger.warning(f"⚠️ Skipping unknown CSV type: {csv_file}")
                    continue

                logger.info(f"🧹 Processing {csv_type}: {os.path.basename(csv_file)}")

                # Copy to daily_downloads for processing
                target_path = f"data/daily_downloads/mapped_{csv_type}.csv"
                shutil.copy2(csv_file, target_path)

                # Clean the data using our enhanced pipeline
                clean_success = clean_csv_data(
                    csv_type=csv_type, input_file=target_path, output_file=target_path
                )

                if not clean_success:
                    logger.error(f"❌ Failed to clean {csv_type} data")
                    continue

                # Upload to results database
                upload_success = upload_csv_to_results_database(
                    csv_file=target_path, table_name=csv_type
                )

                if upload_success:
                    logger.info(f"✅ Successfully processed and uploaded {csv_type}")
                    success_count += 1
                else:
                    logger.error(f"❌ Failed to upload {csv_type} to database")

            except Exception as e:
                logger.error(f"❌ Error processing {csv_file}: {e}")
                continue

        logger.info(
            f"📊 Results for {os.path.basename(date_dir)}: "
            f"{success_count}/{total_files} files processed successfully"
        )
        return success_count > 0


def process_all_results():
    """Process all results data from processed directory"""
    logger.info("🚀 Starting Results Data Pipeline Processing")
    logger.info("=" * 60)

    processed_dir = "data/daily_downloads/processed"

    if not os.path.exists(processed_dir):
        logger.error(f"❌ Processed directory not found: {processed_dir}")
        return False

    # Get all date directories, sorted
    date_dirs = []
    for item in os.listdir(processed_dir):
        item_path = os.path.join(processed_dir, item)
        if os.path.isdir(item_path) and item.startswith("2025-08-"):
            date_dirs.append(item_path)

    date_dirs.sort()

    if not date_dirs:
        logger.error("❌ No date directories found in processed directory")
        return False

    logger.info(f"📅 Found {len(date_dirs)} date directories to process")

    # Process each date starting from 2025-08-20 (results from 19th)
    total_success = 0
    total_processed = 0

    for date_dir in date_dirs:
        date_name = os.path.basename(date_dir)
        logger.info(f"\n📋 Processing date directory: {date_name}")

        success = process_results_date(date_dir)
        total_processed += 1

        if success:
            total_success += 1
            logger.info(f"✅ {date_name} processed successfully")
        else:
            logger.error(f"❌ {date_name} processing failed")

    # Final summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 RESULTS PROCESSING SUMMARY")
    logger.info("=" * 60)
    logger.info(f"📅 Total dates processed: {total_processed}")
    logger.info(f"✅ Successful: {total_success}")
    logger.info(f"❌ Failed: {total_processed - total_success}")

    if total_success > 0:
        logger.info("🎉 Results data pipeline completed with some successes!")
        return True
    else:
        logger.error("💥 All results processing failed!")
        return False


def main():
    """Main function"""
    try:
        # Ensure log directory exists
        os.makedirs("data/logs", exist_ok=True)

        logger.info("🏇 Results Data Pipeline Processor")
        logger.info("Processing results data from processed directory...")
        logger.info("Target database: results_horse_racing_db")

        success = process_all_results()

        if success:
            print("\n🎉 Results processing pipeline completed successfully!")
            return 0
        else:
            print("\n❌ Results processing pipeline failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Pipeline failed with error: {e}")
        print(f"\n💥 Pipeline failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
