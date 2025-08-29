#!/usr/bin/env python3
"""
Pipeline Integration Example - Automated Cards Processing
Shows how to integrate the automated cards processor into the existing daily pipeline

This demonstrates how to replace manual upload scripts with the automated processor
that includes all the data processing fixes we discovered.
"""

import sys
import os
from pathlib import Path
import logging

# Add the tools directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04/tools/pipeline")

from automated_cards_processor import CardsDataProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def integrate_with_daily_pipeline(date_folders: list, target_database: str = "cards"):
    """
    Integration function for daily pipeline

    Args:
        date_folders: List of date folders to process (e.g., ['2025-08-22', '2025-08-24'])
        target_database: 'cards' or 'results' database
    """

    # Database configurations
    db_configs = {
        "cards": {
            "host": "postgres",
            "port": 5432,
            "database": "cards_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        },
        "results": {
            "host": "postgres",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        },
    }

    if target_database not in db_configs:
        logger.error(f"Unknown database: {target_database}")
        return False

    # Initialize processor
    processor = CardsDataProcessor(db_configs[target_database])

    # Process each date folder
    all_results = {"successful_dates": [], "failed_dates": [], "total_statistics": {}}

    for date_folder in date_folders:
        logger.info(f"🗓️  Processing date folder: {date_folder}")

        # Find CSV files for this date
        upload_path = Path(f"/tmp/historical_cards_upload")
        date_suffix = date_folder.replace("-", "")

        csv_files = {}

        # Map expected files
        file_mappings = {
            "races": f"races_{date_suffix}.csv",
            "racecard_details": f"racecard_details_{date_suffix}.csv",
            "horses": f"horses_{date_suffix}.csv",
            "jockeys_stats": f"jockeys_stats_{date_suffix}.csv",
            "trainers_stats": f"trainers_stats_{date_suffix}.csv",
        }

        # Check which files exist
        for table_name, filename in file_mappings.items():
            file_path = upload_path / filename
            if file_path.exists():
                csv_files[table_name] = file_path
                logger.info(f"  📂 Found: {filename}")
            else:
                logger.warning(f"  ❌ Missing: {filename}")

        if not csv_files:
            logger.error(f"No CSV files found for {date_folder}")
            all_results["failed_dates"].append(date_folder)
            continue

        # Process and upload
        try:
            results = processor.process_and_upload_all(csv_files)

            # Check if upload was successful
            if results["successful"] and not results["failed"]:
                all_results["successful_dates"].append(date_folder)
                all_results["total_statistics"][date_folder] = results["statistics"]

                logger.info(f"✅ Successfully processed {date_folder}")
                for table_name, count in results["successful"]:
                    logger.info(f"  📊 {table_name}: {count} records uploaded")

            else:
                all_results["failed_dates"].append(date_folder)
                logger.error(f"❌ Failed processing {date_folder}")

                if results["failed"]:
                    logger.error(f"  Failed tables: {results['failed']}")
                if results["warnings"]:
                    logger.warning(f"  Warnings: {results['warnings']}")

        except Exception as e:
            logger.error(f"Exception processing {date_folder}: {e}")
            all_results["failed_dates"].append(date_folder)

    # Final summary
    logger.info("\n📊 PIPELINE INTEGRATION SUMMARY")
    logger.info(f"✅ Successful dates: {all_results['successful_dates']}")
    logger.info(f"❌ Failed dates: {all_results['failed_dates']}")

    total_records = 0
    for date_folder, stats in all_results["total_statistics"].items():
        date_total = sum(table_stats["uploaded_rows"] for table_stats in stats.values())
        total_records += date_total
        logger.info(f"📅 {date_folder}: {date_total} total records")

    logger.info(f"🎯 Grand total: {total_records} records uploaded")

    return len(all_results["failed_dates"]) == 0


def replace_manual_upload_scripts():
    """
    Example of how to replace manual upload scripts with automated processor

    BEFORE (manual scripts):
    - upload_all_historical_cards.py
    - upload_cards_to_database.py

    AFTER (automated processor):
    - automated_cards_processor.py with configuration files
    """

    logger.info("🔄 Replacing manual upload process with automated processor...")

    # This would be the new approach:
    date_folders = ["2025-08-22", "2025-08-24"]  # Skip duplicate 2025-08-23

    success = integrate_with_daily_pipeline(date_folders, "cards")

    if success:
        logger.info("🎉 Automated processing completed successfully!")
        logger.info(
            "💡 Manual scripts can now be replaced with automated_cards_processor.py"
        )
    else:
        logger.error("❌ Automated processing had failures")
        logger.error("🔧 Check logs and fix issues before replacing manual scripts")

    return success


def daily_pipeline_integration_example():
    """
    Example of how this would be called from the daily pipeline
    """

    # This function would be called from the main daily pipeline script
    # instead of the manual upload scripts

    import datetime

    # Get today's date folder
    today = datetime.date.today()
    date_folder = today.strftime("%Y-%m-%d")

    logger.info(f"🔄 Daily pipeline processing for {date_folder}")

    # Process today's data
    success = integrate_with_daily_pipeline([date_folder], "cards")

    if success:
        logger.info("✅ Daily cards processing completed")
    else:
        logger.error("❌ Daily cards processing failed")
        # Here you would trigger alerts, fallback procedures, etc.

    return success


def migration_checklist():
    """
    Checklist for migrating from manual to automated processing
    """

    checklist_items = [
        "✅ Create configuration files (cards_column_mappings.json, cards_field_types.json)",
        "✅ Test automated processor with historical data",
        "⏳ Validate all data processing issues are resolved",
        "⏳ Update daily pipeline to use automated processor",
        "⏳ Add monitoring and alerting for processing failures",
        "⏳ Create rollback procedures if automated processing fails",
        "⏳ Document new process for team",
        "⏳ Remove or archive manual upload scripts",
    ]

    logger.info("\n📋 MIGRATION CHECKLIST:")
    for item in checklist_items:
        logger.info(f"  {item}")

    logger.info("\n💡 Next steps:")
    logger.info("  1. Test the automated processor thoroughly")
    logger.info("  2. Update the daily pipeline configuration")
    logger.info("  3. Add error monitoring and alerts")
    logger.info("  4. Train team on new automated process")


if __name__ == "__main__":
    logger.info("🚀 Starting pipeline integration example...")

    # Show how to replace manual scripts
    replace_manual_upload_scripts()

    # Show migration checklist
    migration_checklist()

    logger.info("📖 Integration example completed!")
    logger.info("📚 See DATA_PROCESSING_ISSUES_CARDS_UPLOAD.md for full documentation")
