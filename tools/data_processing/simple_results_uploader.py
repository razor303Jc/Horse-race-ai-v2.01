#!/usr/bin/env python3
"""
Simple Results Data Uploader
Process existing cleaned CSV files and upload to results_horse_racing_db
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.data_processing.upload_results_data import upload_csv_to_results_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("data/logs/simple_results_upload.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def upload_existing_mapped_files():
    """Upload the existing mapped CSV files to results database"""
    logger.info("🚀 Starting Results Data Upload")
    logger.info("=" * 50)

    # Define the file mappings
    file_mappings = {
        "data/daily_downloads/mapped_races.csv": "races",
        "data/daily_downloads/mapped_records.csv": "records",
        "data/daily_downloads/mapped_horses.csv": "horses",
        "data/daily_downloads/mapped_jockeys_stats.csv": "jockeys_stats",
        "data/daily_downloads/mapped_trainers_stats.csv": "trainers_stats",
    }

    successful_uploads = 0
    total_files = len(file_mappings)

    for csv_file, table_name in file_mappings.items():
        if not os.path.exists(csv_file):
            logger.warning(f"⚠️ File not found: {csv_file}")
            continue

        logger.info(f"📤 Uploading {csv_file} to {table_name}")

        try:
            success = upload_csv_to_results_database(csv_file, table_name)

            if success:
                logger.info(f"✅ Successfully uploaded {table_name}")
                successful_uploads += 1
            else:
                logger.error(f"❌ Failed to upload {table_name}")

        except Exception as e:
            logger.error(f"❌ Error uploading {csv_file}: {e}")

    # Summary
    logger.info("\n" + "=" * 50)
    logger.info("📋 UPLOAD SUMMARY")
    logger.info("=" * 50)
    logger.info(f"📊 Total files: {total_files}")
    logger.info(f"✅ Successful uploads: {successful_uploads}")
    logger.info(f"❌ Failed uploads: {total_files - successful_uploads}")

    if successful_uploads > 0:
        logger.info("🎉 Results upload completed with some successes!")
        return True
    else:
        logger.error("💥 All uploads failed!")
        return False


def main():
    """Main function"""
    try:
        # Ensure log directory exists
        os.makedirs("data/logs", exist_ok=True)

        logger.info("🏇 Simple Results Data Uploader")
        logger.info("Uploading existing mapped CSV files to results_horse_racing_db")

        success = upload_existing_mapped_files()

        if success:
            print("\n🎉 Results upload completed successfully!")
            return 0
        else:
            print("\n❌ Results upload failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Upload failed with error: {e}")
        print(f"\n💥 Upload failed with error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
