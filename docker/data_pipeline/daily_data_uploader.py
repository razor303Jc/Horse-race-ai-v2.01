#!/usr/bin/env python3
"""
Daily Data Uploader - Upload Fresh Downloads to Database
========================================================

Uploads freshly downloaded CSV files to PostgreSQL database without resetting.
Uses Qwen2.5's BIGINT solution for reliable data processing.

Features:
- Processes today's downloaded CSV files
- Uses Qwen2.5's proven BIGINT handling
- Handles duplicate detection and updates
- Maintains existing data integrity
- Comprehensive logging and validation
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

from csv_column_mapper import ColumnMapper
from qwen_bigint_solution import QwenBigintSolver

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("daily_upload.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class DailyDataUploader:
    """
    Upload daily downloaded data to database without reset
    """

    def __init__(self):
        self.qwen_solver = QwenBigintSolver()
        self.column_mapper = ColumnMapper()

        # Database connection parameters
        self.db_params = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Daily download directories (from working auto downloader)
        self.daily_data_dir = Path("data/daily_downloads")

        # File mappings for daily uploads
        self.file_mappings = {
            "results_data/records/records.csv": "race_results",
            "cards_data/racecard_details/racecard_details.csv": "racecard_details",
            "results_data/horses/horses.csv": "horses",
            "cards_data/races/races.csv": "races_cards",
            "results_data/jockeys_stats/jockeys_stats.csv": "jockey_stats",
            "results_data/trainers_stats/trainers_stats.csv": "trainer_stats",
        }

    def get_connection(self):
        """Get database connection"""
        try:
            return psycopg2.connect(**self.db_params)
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            return None

    def check_daily_files(self):
        """Check which daily CSV files are available"""
        available_files = {}
        missing_files = []

        for relative_path, table_name in self.file_mappings.items():
            full_path = self.daily_data_dir / relative_path
            if full_path.exists():
                file_size = full_path.stat().st_size
                file_time = datetime.fromtimestamp(full_path.stat().st_mtime)
                available_files[relative_path] = {
                    "path": full_path,
                    "table": table_name,
                    "size": file_size,
                    "modified": file_time,
                }
                logger.info(
                    f"✅ Found: {relative_path} " f"({file_size:,} bytes, {file_time})"
                )
            else:
                missing_files.append(relative_path)
                logger.warning(f"❌ Missing: {relative_path}")

        return available_files, missing_files

    def get_table_info(self, table_name):
        """Get current record count for a table"""
        connection = self.get_connection()
        if not connection:
            return 0

        try:
            cursor = connection.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
            count = cursor.fetchone()[0]
            cursor.close()
            connection.close()
            return count
        except Exception as e:
            logger.error(f"Error getting count for {table_name}: {e}")
            if connection:
                connection.close()
            return 0

    def upload_dataframe_to_table(self, df, table_name, mode="append"):
        """
        Upload dataframe to database table

        Args:
            df: DataFrame to upload
            table_name: Target table name
            mode: "append" (default) or "replace"
        """
        connection = self.get_connection()
        if not connection:
            return False

        try:
            cursor = connection.cursor()

            # Get current record count
            before_count = self.get_table_info(table_name)

            if mode == "replace":
                # Clear table first if replace mode
                logger.info(f"🧹 Clearing {table_name} for fresh data...")
                cursor.execute(f"DELETE FROM {table_name}")
                connection.commit()

            # Convert DataFrame to values
            columns = list(df.columns)
            values = df.values.tolist()

            # Create placeholders for the insert statement
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)

            # Use appropriate INSERT strategy based on table
            if table_name in ["horses", "jockey_stats", "trainer_stats"]:
                # These tables have unique constraints
                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """
            else:
                # For tables without unique constraints, use simple INSERT
                insert_query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES ({placeholders})
                """

            # Execute batch insert
            cursor.executemany(insert_query, values)
            connection.commit()

            # Get final record count
            after_count = self.get_table_info(table_name)
            new_records = after_count - (before_count if mode == "append" else 0)

            cursor.close()
            connection.close()

            logger.info(
                f"✅ {table_name}: {len(df)} processed, "
                f"{new_records} new records added"
            )
            logger.info(f"   Before: {before_count:,}, After: {after_count:,}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload to {table_name}: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Error details: {str(e)}")
            if connection:
                connection.rollback()
                connection.close()
            return False

    def upload_daily_data(self, mode="append"):
        """
        Upload daily downloaded data

        Args:
            mode: "append" (default) or "replace"
        """
        logger.info(f"🚀 Starting daily data upload (mode: {mode})...")

        # Check available files
        available_files, missing_files = self.check_daily_files()

        if not available_files:
            logger.error("❌ No daily CSV files found!")
            return False, []

        if missing_files:
            logger.warning(f"⚠️  Missing {len(missing_files)} files: {missing_files}")

        total_files = len(available_files)
        successful_uploads = 0
        failed_uploads = []
        upload_summary = {}

        for relative_path, file_info in available_files.items():
            file_path = file_info["path"]
            table_name = file_info["table"]

            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"🔄 Processing: {relative_path} → {table_name}")
                logger.info(f"   File: {file_path}")
                logger.info(f"   Size: {file_info['size']:,} bytes")
                logger.info(f"   Modified: {file_info['modified']}")
                logger.info(f"{'='*60}")

                # Use Qwen2.5's solution to process the CSV
                df = self.qwen_solver.process_problematic_csv(
                    str(file_path), table_name
                )

                if df is None or len(df) == 0:
                    logger.warning(f"⚠️  No data to upload for {relative_path}")
                    failed_uploads.append((relative_path, "No data after processing"))
                    continue

                # Map CSV columns to database columns
                logger.info(f"🔄 Mapping columns for {table_name}...")
                original_cols = len(df.columns)
                df_mapped = self.column_mapper.map_dataframe_columns(df, table_name)

                if df_mapped.empty:
                    logger.warning(f"⚠️  No mappable columns for {relative_path}")
                    failed_uploads.append((relative_path, "No mappable columns"))
                    continue

                logger.info(f"   Original columns: {original_cols}")
                logger.info(f"   Mapped columns: {len(df_mapped.columns)}")

                # Validate mapped data
                if not self.column_mapper.validate_mapped_data(df_mapped, table_name):
                    logger.warning(f"⚠️  Data validation failed for {relative_path}")
                    failed_uploads.append((relative_path, "Data validation failed"))
                    continue

                # Upload to database
                success = self.upload_dataframe_to_table(df_mapped, table_name, mode)

                if success:
                    successful_uploads += 1
                    upload_summary[table_name] = {
                        "file": relative_path,
                        "rows_processed": len(df),
                        "status": "success",
                    }
                    logger.info(f"✅ SUCCESS: {relative_path}")
                else:
                    failed_uploads.append((relative_path, "Database upload failed"))
                    upload_summary[table_name] = {
                        "file": relative_path,
                        "rows_processed": len(df),
                        "status": "failed",
                    }
                    logger.error(f"❌ FAILED: Database upload for {relative_path}")

            except Exception as e:
                failed_uploads.append((relative_path, str(e)))
                upload_summary[table_name] = {
                    "file": relative_path,
                    "rows_processed": 0,
                    "status": "error",
                    "error": str(e),
                }
                logger.error(f"❌ FAILED: {relative_path} - {e}")

        # Summary report
        logger.info(f"\n{'='*60}")
        logger.info("🎯 DAILY UPLOAD SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Upload mode: {mode}")
        logger.info(f"Total files found: {total_files}")
        logger.info(f"Successful uploads: {successful_uploads}")
        logger.info(f"Failed uploads: {len(failed_uploads)}")
        logger.info(f"Success rate: {(successful_uploads/total_files)*100:.1f}%")

        if failed_uploads:
            logger.info("\n❌ Failed uploads:")
            for file_path, error in failed_uploads:
                logger.info(f"   {file_path}: {error}")

        # Show final database status
        self.show_database_summary()

        if successful_uploads == total_files:
            logger.info(
                f"\n🎉 PERFECT SUCCESS! All {total_files} files "
                f"uploaded successfully!"
            )

        return successful_uploads == total_files, upload_summary

    def show_database_summary(self):
        """Show current database record counts"""
        logger.info("\n📊 Current Database Status:")
        logger.info(f"{'='*40}")

        total_records = 0
        for table_name in self.file_mappings.values():
            count = self.get_table_info(table_name)
            logger.info(f"   {table_name}: {count:,} records")
            total_records += count

        logger.info(f"{'='*40}")
        logger.info(f"   TOTAL: {total_records:,} records")

    def validate_upload(self):
        """Validate that upload was successful"""
        logger.info("\n🔍 Validating upload success...")

        validation_passed = True
        for table_name in self.file_mappings.values():
            count = self.get_table_info(table_name)
            if count == 0:
                logger.warning(f"⚠️  {table_name} has no records!")
                validation_passed = False
            else:
                logger.info(f"✅ {table_name}: {count:,} records")

        return validation_passed


def main():
    """Main execution"""
    print("📈 Daily Data Uploader")
    print("Using Qwen2.5's proven BIGINT solution")
    print("=" * 60)

    uploader = DailyDataUploader()

    # Check what files are available
    logger.info("Step 1: Checking available daily files...")
    available_files, missing_files = uploader.check_daily_files()

    if not available_files:
        print("❌ No daily CSV files found. Run the auto downloader first.")
        return

    # Show current database status
    logger.info("Step 2: Current database status...")
    uploader.show_database_summary()

    # Upload data (append mode by default)
    logger.info("Step 3: Uploading daily data...")
    success, summary = uploader.upload_daily_data(mode="append")

    # Validate upload
    logger.info("Step 4: Validating upload...")
    validation_passed = uploader.validate_upload()

    # Final status
    print("\n🏁 FINAL STATUS:")
    print(f"   ✅ Upload success: {success}")
    print(f"   ✅ Validation passed: {validation_passed}")
    print(f"   📁 Files processed: {len(available_files)}")

    if missing_files:
        print(f"   ⚠️  Missing files: {len(missing_files)}")

    if success and validation_passed:
        print("\n🎉 DAILY UPLOAD COMPLETED SUCCESSFULLY!")
        print("   Fresh data has been added to the database!")
    else:
        print("\n⚠️  Some issues remain - check the log for details")


if __name__ == "__main__":
    main()
