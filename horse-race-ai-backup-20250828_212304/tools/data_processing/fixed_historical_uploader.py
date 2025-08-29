#!/usr/bin/env python3
"""
Fixed Historical Results Uploader
Upload the complete historical data with proper order and schema
"""

import pandas as pd
import logging
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.data_processing.upload_results_data import upload_csv_to_results_database

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def fix_and_upload_historical_data():
    """Fix schema issues and upload all historical data in correct order"""
    logger.info("🔧 Fixing and Uploading Complete Historical Results Data")
    logger.info("=" * 60)

    # Process files in dependency order (races first, then records)
    files_to_process = [
        ("data/daily_downloads/complete_races.csv", "races"),
        ("data/daily_downloads/complete_records.csv", "records"),
    ]

    results = {}

    for csv_file, table_name in files_to_process:
        logger.info(f"\n📋 Processing {table_name}")

        try:
            # Load the CSV
            df = pd.read_csv(csv_file)
            logger.info(f"📊 Loaded {len(df)} rows for {table_name}")

            # Remove source_date column if it exists
            if "source_date" in df.columns:
                df = df.drop("source_date", axis=1)
                logger.info("🗑️ Removed source_date column")

            # Save cleaned CSV
            fixed_file = csv_file.replace(".csv", "_fixed.csv")
            df.to_csv(fixed_file, index=False)
            logger.info(f"💾 Saved fixed data to {fixed_file}")

            # Upload to database
            logger.info(f"📤 Uploading {table_name} to results database...")
            success = upload_csv_to_results_database(fixed_file, table_name)

            if success:
                results[table_name] = {"status": "success", "rows": len(df)}
                logger.info(f"✅ Successfully uploaded {len(df)} {table_name}")
            else:
                results[table_name] = {"status": "failed", "rows": len(df)}
                logger.error(f"❌ Failed to upload {table_name}")

        except Exception as e:
            logger.error(f"❌ Error processing {table_name}: {e}")
            results[table_name] = {"status": "error", "error": str(e)}

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📋 HISTORICAL DATA UPLOAD SUMMARY")
    logger.info("=" * 60)

    total_rows = 0
    successful_uploads = 0

    for table_name, result in results.items():
        status = result["status"]
        if status == "success":
            rows = result["rows"]
            logger.info(f"✅ {table_name}: {rows} rows uploaded successfully")
            total_rows += rows
            successful_uploads += 1
        elif status == "failed":
            logger.error(f"❌ {table_name}: {result['rows']} rows failed to upload")
        elif status == "error":
            logger.error(f"💥 {table_name}: Error - {result['error']}")

    logger.info(f"\n📊 FINAL TOTALS:")
    logger.info(f"📈 Total rows uploaded: {total_rows}")
    logger.info(f"✅ Successful tables: {successful_uploads}/{len(files_to_process)}")

    return successful_uploads > 0


def main():
    """Main function"""
    try:
        logger.info("🏇 Fixed Historical Results Uploader")
        logger.info("Uploading complete historical results data (Aug 19-23)")

        success = fix_and_upload_historical_data()

        if success:
            print("\n🎉 Historical results upload completed successfully!")
            return 0
        else:
            print("\n❌ Historical results upload failed!")
            return 1

    except Exception as e:
        logger.error(f"💥 Upload failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
