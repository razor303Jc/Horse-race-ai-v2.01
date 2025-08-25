#!/usr/bin/env python3
"""
Fixed Results Upload Pipeline with Dependency Ordering
Ensures races are uploaded before records to prevent foreign key constraint violations
"""

import os
import sys
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from tools.data_processing.upload_results_data import (
    upload_csv_to_results_database,
    test_connection
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/fixed_results_upload.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


def upload_results_with_dependency_order():
    """Upload results files in correct dependency order to prevent FK violations"""
    logger.info("🚀 Starting Fixed Results Upload with Dependency Ordering")
    logger.info("=" * 60)

    # Test database connection first
    logger.info("🔍 Testing database connection...")
    if not test_connection():
        logger.error("❌ Database connection failed - aborting upload")
        return False

    # Define upload order - parent tables MUST be uploaded before child tables
    # This prevents foreign key constraint violations
    upload_order = [
        # 1. Independent tables (no foreign key dependencies)
        ("data/daily_downloads/mapped_horses.csv", "horses"),
        ("data/daily_downloads/mapped_jockeys_stats.csv", "jockeys_stats"),
        ("data/daily_downloads/mapped_trainers_stats.csv", "trainers_stats"),

        # 2. Races table (referenced by records table)
        ("data/daily_downloads/mapped_races.csv", "races"),

        # 3. Records table (depends on races table via race_id foreign key)
        ("data/daily_downloads/mapped_records.csv", "records"),
    ]

    successful_uploads = 0
    total_files = len(upload_order)
    failed_uploads = []

    for csv_file, table_name in upload_order:
        logger.info(f"\n📄 Processing: {csv_file} → {table_name}")

        if not os.path.exists(csv_file):
            logger.warning(f"⚠️ File not found: {csv_file}")
            failed_uploads.append((csv_file, table_name, "File not found"))
            continue

        # Attempt upload with detailed logging
        try:
            success = upload_csv_to_results_database(csv_file, table_name)

            if success:
                logger.info(f"✅ Successfully uploaded {table_name}")
                successful_uploads += 1
            else:
                logger.error(f"❌ Failed to upload {table_name}")
                failed_uploads.append(
                    (csv_file, table_name, "Upload function returned False")
                )

                # For critical dependencies, abort if races table fails
                if table_name == "races":
                    logger.error(
                        "🚨 CRITICAL: Races table upload failed - "
                        "aborting to prevent constraint violations"
                    )
                    break

        except Exception as e:
            logger.error(f"❌ Exception during {table_name} upload: {e}")
            failed_uploads.append((csv_file, table_name, str(e)))

            # For critical dependencies, abort if races table fails
            if table_name == "races":
                logger.error(
                    "🚨 CRITICAL: Races table upload failed - "
                    "aborting to prevent constraint violations"
                )
                break
    # Upload summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 UPLOAD SUMMARY")
    logger.info("=" * 60)
    logger.info(f"✅ Successful uploads: {successful_uploads}/{total_files}")

    if failed_uploads:
        logger.error(f"❌ Failed uploads: {len(failed_uploads)}")
        for csv_file, table_name, error in failed_uploads:
            logger.error(f"   - {table_name}: {error}")
    else:
        logger.info("🎉 All uploads completed successfully!")

    # Return success if all uploads succeeded
    return len(failed_uploads) == 0


def validate_database_state():
    """Validate the current database state to check for constraint issues"""
    logger.info("\n🔍 Validating database state...")

    try:
        import psycopg2
        from tools.data_processing.upload_results_data import DATABASE_CONFIG

        conn = psycopg2.connect(**DATABASE_CONFIG)
        cursor = conn.cursor()

        # Check for orphaned records (records without corresponding races)
        cursor.execute("""
            SELECT COUNT(*) as orphaned_records
            FROM records r
            LEFT JOIN races ra ON r.race_id = ra.race_id
            WHERE ra.race_id IS NULL
        """)
        orphaned_count = cursor.fetchone()[0]

        if orphaned_count > 0:
            logger.warning(
                f"⚠️ Found {orphaned_count} orphaned records "
                "(no corresponding race)"
            )
        else:
            logger.info("✅ No orphaned records found")

        # Check recent race and record counts
        cursor.execute("SELECT COUNT(*) FROM races WHERE date >= '2025-08-22'")
        recent_races = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) FROM records r
            JOIN races ra ON r.race_id = ra.race_id
            WHERE ra.date >= '2025-08-22'
        """)
        recent_records = cursor.fetchone()[0]

        logger.info(
            f"📊 Recent data (Aug 22+): {recent_races} races, "
            f"{recent_records} records"
        )

        cursor.close()
        conn.close()

        return orphaned_count == 0

    except Exception as e:
        logger.error(f"❌ Database validation failed: {e}")
        return False


if __name__ == "__main__":
    # Validate current state first
    logger.info("🔍 Step 1: Validating current database state")
    validate_database_state()

    # Run fixed upload
    logger.info("\n🔧 Step 2: Running dependency-ordered upload")
    success = upload_results_with_dependency_order()

    # Final validation
    logger.info("\n🔍 Step 3: Final validation")
    final_state = validate_database_state()

    if success and final_state:
        logger.info(
            "\n🎉 SUCCESS: Results upload completed with no constraint violations!"
        )
        sys.exit(0)
    else:
        logger.error("\n❌ FAILED: Issues remain - check logs for details")
        sys.exit(1)
