#!/usr/bin/env python3
"""
Clean Slate Database Reset and Fresh Upload
Using Qwen2.5's BIGINT solution for a complete fresh start
"""

import logging
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from pathlib import Path

import pandas as pd
import psycopg2

# Add the src directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01/src")

# Import the database manager and Qwen's solution
try:
    from database.database_manager import DatabaseManager
    from qwen_bigint_solution import QwenBigintSolver
except ImportError as e:
    print(f"Import error: {e}")
    print(
        "Please ensure the database_manager.py and qwen_bigint_solution.py are available"
    )
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("clean_slate_upload.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class CleanSlateUploader:
    """
    Complete database reset and fresh upload using Qwen2.5's solution
    """

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.qwen_solver = QwenBigintSolver()
        self.tables_to_clear = [
            "race_results",
            "racecard_details",
            "horses",
            "races_cards",
            "jockey_stats",
            "trainer_stats",
        ]

        # File mappings using Qwen2.5's working paths
        self.file_mappings = {
            "project_root / 'data' / horseracedatabase/results_project_root / 'data' / records/records.csv": "race_results",
            "project_root / 'data' / horseracedatabase/cards_project_root / 'data' / racecard_details/racecard_details.csv": "racecard_details",
            "project_root / 'data' / horseracedatabase/results_project_root / 'data' / horses/horses.csv": "horses",
            "project_root / 'data' / horseracedatabase/cards_project_root / 'data' / races/races.csv": "races_cards",
            "project_root / 'data' / horseracedatabase/results_project_root / 'data' / jockeys_stats/jockeys_stats.csv": "jockey_stats",
            "project_root / 'data' / horseracedatabase/results_project_root / 'data' / trainers_stats/trainers_stats.csv": "trainer_stats",
        }

    def clear_all_tables(self):
        """
        Clear all data from database tables for a fresh start
        """
        logger.info("🧹 Starting database table cleanup...")

        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()

            # Disable foreign key checks temporarily
            cursor.execute("SET session_replication_role = replica;")

            for table in self.tables_to_clear:
                try:
                    logger.info(f"Clearing table: {table}")
                    cursor.execute(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE;")
                    connection.commit()
                    logger.info(f"✅ Cleared {table}")
                except Exception as e:
                    logger.warning(f"⚠️  Could not clear {table}: {e}")
                    connection.rollback()

            # Re-enable foreign key checks
            cursor.execute("SET session_replication_role = DEFAULT;")
            connection.commit()

            cursor.close()
            connection.close()

            logger.info("🧹 Database cleanup completed!")

        except Exception as e:
            logger.error(f"❌ Database cleanup failed: {e}")
            return False

        return True

    def upload_with_qwen_solution(self):
        """
        Upload all CSV files using Qwen2.5's proven solution
        """
        logger.info("🚀 Starting fresh upload with Qwen2.5's solution...")

        total_files = len(self.file_mappings)
        successful_uploads = 0
        failed_uploads = []

        for file_path, table_name in self.file_mappings.items():
            if not Path(file_path).exists():
                logger.warning(f"⚠️  File not found: {file_path}")
                failed_uploads.append((file_path, "File not found"))
                continue

            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 Processing: {file_path} → {table_name}")
                logger.info(f"{'='*60}")

                # Use Qwen2.5's solution to process the CSV
                df = self.qwen_solver.process_problematic_csv(file_path, table_name)

                # Upload to database using the database manager
                success = self.db_manager.upload_dataframe_to_table(df, table_name)

                if success:
                    successful_uploads += 1
                    logger.info(f"✅ SUCCESS: {file_path}")
                    logger.info(f"   📊 Uploaded {len(df)} rows to {table_name}")
                else:
                    failed_uploads.append((file_path, "Database upload failed"))
                    logger.error(f"❌ FAILED: Database upload for {file_path}")

            except Exception as e:
                failed_uploads.append((file_path, str(e)))
                logger.error(f"❌ FAILED: {file_path} - {e}")

        # Summary report
        logger.info(f"\n{'='*60}")
        logger.info(f"🎯 UPLOAD SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Total files: {total_files}")
        logger.info(f"Successful uploads: {successful_uploads}")
        logger.info(f"Failed uploads: {len(failed_uploads)}")
        logger.info(f"Success rate: {(successful_uploads/total_files)*100:.1f}%")

        if failed_uploads:
            logger.info(f"\n❌ Failed uploads:")
            for file_path, error in failed_uploads:
                logger.info(f"   {file_path}: {error}")

        if successful_uploads == total_files:
            logger.info(
                f"\n🎉 PERFECT SUCCESS! All {total_files} files uploaded successfully!"
            )

        return successful_uploads, failed_uploads

    def verify_upload_success(self):
        """
        Verify that data was successfully uploaded to all tables
        """
        logger.info("\n🔍 Verifying upload success...")

        try:
            connection = self.db_manager.get_connection()
            cursor = connection.cursor()

            total_records = 0
            for table in self.tables_to_clear:
                cursor.execute(f"SELECT COUNT(*) FROM {table};")
                count = cursor.fetchone()[0]
                logger.info(f"   {table}: {count:,} records")
                total_records += count

            cursor.close()
            connection.close()

            logger.info(f"\n📊 Total records in database: {total_records:,}")
            return total_records

        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return 0


def main():
    """
    Main execution: Clear database and upload fresh data
    """
    print("🧬 Clean Slate Database Reset & Upload")
    print("Using Qwen2.5's proven BIGINT solution")
    print("=" * 60)

    uploader = CleanSlateUploader()

    # Step 1: Clear all tables
    if not uploader.clear_all_tables():
        print("❌ Database cleanup failed. Aborting.")
        return

    # Step 2: Upload fresh data
    successful, failed = uploader.upload_with_qwen_solution()

    # Step 3: Verify success
    total_records = uploader.verify_upload_success()

    # Final status
    print(f"\n🏁 FINAL STATUS:")
    print(f"   ✅ Successful uploads: {successful}")
    print(f"   ❌ Failed uploads: {len(failed)}")
    print(f"   📊 Total records: {total_records:,}")

    if successful == 6 and len(failed) == 0:
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"   All files uploaded successfully with Qwen2.5's solution!")
    else:
        print(f"\n⚠️  Some issues remain - check the log for details")


if __name__ == "__main__":
    main()
