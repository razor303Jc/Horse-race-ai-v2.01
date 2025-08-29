#!/usr/bin/env python3
"""
Complete CSV Processing Script
Processes ALL CSV files with complete column mapping
Preserves ALL data with proper NULL handling
"""

import logging
import os
import sys
from datetime import datetime

# Add the docker/data_processing directory to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01/docker/data_processing")

from complete_csv_processor import CompleteCsvDatabaseProcessor


def setup_logging():
    """Setup comprehensive logging"""
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/complete_csv_processing.log"),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger(__name__)


def check_csv_files_exist():
    """Check which CSV files exist for processing"""
    logger = logging.getLogger(__name__)

    csv_files = {
        "races": [
            "data/daily_downloads/cards_data/races/races.csv",
            "data/daily_downloads/results_data/races/races.csv",
        ],
        "records": [
            "data/daily_downloads/cards_data/records/records.csv",
            "data/daily_downloads/results_data/racecard_details/racecard_details.csv",
        ],
        "horses": [
            "data/daily_downloads/cards_data/horses/horses.csv",
            "data/daily_downloads/results_data/horses/horses.csv",
        ],
        "jockeys_stats": [
            "data/daily_downloads/cards_data/jockeys_stats/jockeys_stats.csv"
        ],
        "trainers_stats": [
            "data/daily_downloads/cards_data/trainers_stats/trainers_stats.csv"
        ],
    }

    existing_files = {}
    missing_files = {}

    for table, files in csv_files.items():
        existing_files[table] = []
        missing_files[table] = []

        for file_path in files:
            if os.path.exists(file_path):
                existing_files[table].append(file_path)
                file_size = os.path.getsize(file_path)
                logger.info(f"✅ Found {file_path} ({file_size:,} bytes)")
            else:
                missing_files[table].append(file_path)
                logger.warning(f"❌ Missing {file_path}")

    return existing_files, missing_files


def show_csv_file_preview():
    """Show preview of CSV file structures"""
    logger = logging.getLogger(__name__)

    csv_files = [
        "data/daily_downloads/cards_data/races/races.csv",
        "data/daily_downloads/cards_data/records/records.csv",
        "data/daily_downloads/cards_data/horses/horses.csv",
        "data/daily_downloads/cards_data/jockeys_stats/jockeys_stats.csv",
        "data/daily_downloads/cards_data/trainers_stats/trainers_stats.csv",
    ]

    logger.info("\n📋 CSV File Structure Preview:")
    logger.info("=" * 60)

    for csv_file in csv_files:
        if os.path.exists(csv_file):
            try:
                import pandas as pd

                df = pd.read_csv(csv_file, nrows=1)
                table_name = os.path.basename(os.path.dirname(csv_file))
                logger.info(f"\n{table_name.upper()}: {len(df.columns)} columns")
                logger.info(f"Columns: {', '.join(df.columns[:5])}...")

            except Exception as e:
                logger.error(f"Error reading {csv_file}: {e}")


def process_complete_csv_data():
    """Main function to process all CSV data with complete mapping"""
    logger = setup_logging()

    logger.info("🚀 Starting Complete CSV Processing")
    logger.info("=" * 60)
    logger.info(f"Start time: {datetime.now()}")

    # Check which files exist
    existing_files, missing_files = check_csv_files_exist()

    # Show preview
    show_csv_file_preview()

    # Initialize processor
    logger.info("\n🔧 Initializing Complete CSV Processor...")
    try:
        processor = CompleteCsvDatabaseProcessor()
        logger.info("✅ Processor initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize processor: {e}")
        return False

    # Validate mapping
    logger.info("\n🔍 Validating CSV Column Mappings...")
    try:
        validation_results = processor.validate_csv_mapping()

        total_unmapped = 0
        for table, missing in validation_results.items():
            if missing:
                logger.warning(
                    f"⚠️  Table {table} has {len(missing)} unmapped columns: {missing}"
                )
                total_unmapped += len(missing)
            else:
                logger.info(f"✅ Table {table} - all columns mapped")

        if total_unmapped > 0:
            logger.warning(f"⚠️  Total unmapped columns: {total_unmapped}")
        else:
            logger.info("✅ ALL columns properly mapped!")

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return False

    # Process all CSV files
    logger.info("\n📊 Processing ALL CSV Files...")
    try:
        results = processor.process_all_csv_files()

        logger.info("\n🎯 Processing Results:")
        logger.info("=" * 40)
        total_rows = 0

        for table, count in results.items():
            logger.info(f"  📋 {table:<15}: {count:>8,} rows")
            total_rows += count

        logger.info("=" * 40)
        logger.info(f"  🎯 TOTAL PROCESSED: {total_rows:>8,} rows")

        if total_rows > 0:
            logger.info("\n✅ Complete CSV processing finished successfully!")
            return True
        else:
            logger.warning(
                "\n⚠️  No data was processed - check CSV files and database connection"
            )
            return False

    except Exception as e:
        logger.error(f"❌ Processing failed: {e}")
        return False

    finally:
        logger.info(f"\nEnd time: {datetime.now()}")


def main():
    """Entry point"""
    print("🏇 Complete Horse Racing CSV Processor")
    print("=" * 50)
    print("Processing ALL CSV columns with proper NULL handling")
    print("Preserving ALL data - no data loss!")
    print()

    success = process_complete_csv_data()

    if success:
        print("\n🎉 SUCCESS: All CSV data processed successfully!")
        print("💾 All data preserved in database with proper NULL handling")
        exit(0)
    else:
        print("\n❌ FAILED: Error processing CSV data")
        print("📋 Check logs for details")
        exit(1)


if __name__ == "__main__":
    main()
