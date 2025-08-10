#!/usr/bin/env python3
"""
Simple Clean Slate Upload using Qwen2.5's solution
Direct database integration without complex dependencies
"""

import logging
import os
import sys
from pathlib import Path

import psycopg2

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

from qwen_bigint_solution import QwenBigintSolver

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class SimpleCleanSlateUploader:
    """
    Simple database reset and upload using Qwen2.5's solution
    """

    def __init__(self):
        self.qwen_solver = QwenBigintSolver()

        # Database connection parameters
        self.db_params = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Tables to clear
        self.tables_to_clear = [
            "race_results",
            "racecard_details",
            "horses",
            "races_cards",
            "jockey_stats",
            "trainer_stats",
        ]

        # File mappings
        self.file_mappings = {
            "data/horseracedatabase/results_data/records/records.csv": "race_results",
            "data/horseracedatabase/cards_data/racecard_details/racecard_details.csv": "racecard_details",
            "data/horseracedatabase/results_data/horses/horses.csv": "horses",
            "data/horseracedatabase/cards_data/races/races.csv": "races_cards",
            "data/horseracedatabase/results_data/jockeys_stats/jockeys_stats.csv": "jockey_stats",
            "data/horseracedatabase/results_data/trainers_stats/trainers_stats.csv": "trainer_stats",
        }

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_params)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def clear_all_tables(self):
        """Clear all data from database tables"""
        logger.info("🧹 Starting database cleanup...")

        connection = self.get_connection()
        if not connection:
            return False

        try:
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
            return True

        except Exception as e:
            logger.error(f"❌ Database cleanup failed: {e}")
            if connection:
                connection.close()
            return False

    def upload_dataframe_to_table(self, df, table_name):
        """Upload dataframe to database table"""
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Convert DataFrame to values
            columns = list(df.columns)
            values = df.values.tolist()

            # Create placeholders for the insert statement
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)

            insert_query = (
                f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})"
            )

            # Execute batch insert
            cursor.executemany(insert_query, values)
            connection.commit()

            cursor.close()
            connection.close()

            logger.info(f"✅ Uploaded {len(df)} rows to {table_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload to {table_name}: {e}")
            if connection:
                connection.rollback()
                connection.close()
            return False

    def upload_with_qwen_solution(self):
        """Upload all CSV files using Qwen2.5's solution"""
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

                # Upload to database
                success = self.upload_dataframe_to_table(df, table_name)

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
        """Verify upload success by counting records"""
        logger.info("\n🔍 Verifying upload success...")

        connection = self.get_connection()
        if not connection:
            return 0

        try:
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
            if connection:
                connection.close()
            return 0


def main():
    """Main execution"""
    print("🧬 Simple Clean Slate Upload")
    print("Using Qwen2.5's proven BIGINT solution")
    print("=" * 60)

    uploader = SimpleCleanSlateUploader()

    # Step 1: Clear all tables
    logger.info("Step 1: Clearing database tables...")
    if not uploader.clear_all_tables():
        print("❌ Database cleanup failed. Aborting.")
        return

    # Step 2: Upload fresh data
    logger.info("Step 2: Uploading fresh data...")
    successful, failed = uploader.upload_with_qwen_solution()

    # Step 3: Verify success
    logger.info("Step 3: Verifying upload...")
    total_records = uploader.verify_upload_success()

    # Final status
    print(f"\n🏁 FINAL STATUS:")
    print(f"   ✅ Successful uploads: {successful}/6")
    print(f"   ❌ Failed uploads: {len(failed)}")
    print(f"   📊 Total records: {total_records:,}")

    if successful == 6 and len(failed) == 0:
        print(f"\n🎉 MISSION ACCOMPLISHED!")
        print(f"   All files uploaded successfully with Qwen2.5's solution!")
        print(f"   Database is now clean and fully populated!")
    else:
        print(f"\n⚠️  Some issues remain - check the log for details")


if __name__ == "__main__":
    main()
