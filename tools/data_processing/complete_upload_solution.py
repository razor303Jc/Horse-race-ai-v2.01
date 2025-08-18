#!/usr/bin/env python3
"""
Complete Upload Solution: Qwen2.5's BIGINT + Column Mapping
Final integration that handles both data processing and schema alignment
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
from psycopg2.extras import execute_values

from column_mapper import ColumnMapper

# Import our solutions
from smart_csv_processor import SmartCSVProcessor

# Database configuration
DATABASE_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "horse_racing_db",
    "user": "horse_racing",
    "password": "secure_password_123",
}

# CSV file paths
CSV_FILES = {
    "race_results": "project_root / 'data' / horseracedatabase/results_project_root / 'data' / records/records.csv",
    "racecard_details": "project_root / 'data' / horseracedatabase/cards_project_root / 'data' / racecard_details/racecard_details.csv",
    "horses": "project_root / 'data' / horseracedatabase/results_project_root / 'data' / horses/horses.csv",
    "races_cards": "project_root / 'data' / horseracedatabase/cards_project_root / 'data' / races/races.csv",
    "jockey_stats": "project_root / 'data' / horseracedatabase/results_project_root / 'data' / jockeys_stats/jockeys_stats.csv",
    "trainer_stats": "project_root / 'data' / horseracedatabase/results_project_root / 'data' / trainers_stats/trainers_stats.csv",
}

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedUploader:
    """
    Combines Qwen2.5's BIGINT solution with column mapping
    """

    def __init__(self):
        self.smart_processor = SmartCSVProcessor()
        self.column_mapper = ColumnMapper()
        self.connection = None

    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(**DATABASE_CONFIG)
            logger.info("✅ Database connected successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            return False

    def clear_all_tables(self):
        """Clear all data from tables"""
        if not self.connection:
            logger.error("No database connection")
            return False

        tables = [
            "race_results",
            "racecard_details",
            "horses",
            "races_cards",
            "jockey_stats",
            "trainer_stats",
        ]

        try:
            cursor = self.connection.cursor()
            for table in tables:
                cursor.execute(f"DELETE FROM {table}")
                logger.info(f"🧹 Cleared table: {table}")

            self.connection.commit()
            cursor.close()
            logger.info("✅ All tables cleared successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to clear tables: {e}")
            self.connection.rollback()
            return False

    def process_and_upload_file(self, file_path, table_name):
        """
        Process CSV file using Qwen2.5's solution and upload with column mapping
        """
        logger.info(f"🔄 Processing {file_path} for table {table_name}")

        if not os.path.exists(file_path):
            logger.warning(f"⚠️ File not found: {file_path}")
            return False

        try:
            # Step 1: Use Smart processor for data processing
            df = self.smart_processor.process_csv_smart(file_path, table_name)

            if df is None or df.empty:
                logger.warning(f"⚠️ No data processed from {file_path}")
                return False

            logger.info(
                f"📊 Smart processed: {df.shape[0]} rows, " f"{df.shape[1]} columns"
            )

            # Step 2: Apply column mapping
            mapped_df = self.column_mapper.map_columns(df, table_name)

            if mapped_df.empty:
                logger.warning(f"⚠️ No data after column mapping for {table_name}")
                return False

            logger.info(
                f"🗂️ Column mapped: {mapped_df.shape[0]} rows, "
                f"{mapped_df.shape[1]} columns"
            )

            # Step 3: Upload to database
            return self.upload_dataframe(mapped_df, table_name)

        except Exception as e:
            logger.error(f"❌ Failed to process {file_path}: {e}")
            return False

    def upload_dataframe(self, df, table_name):
        """Upload DataFrame to database table"""
        if not self.connection:
            logger.error("No database connection")
            return False

        try:
            cursor = self.connection.cursor()

            # Prepare data for upload
            columns = list(df.columns)
            column_str = ", ".join(columns)

            # Convert DataFrame to list of tuples, handling None values
            data_tuples = []
            for _, row in df.iterrows():
                # Convert row to tuple, replacing any nan with None
                tuple_row = tuple(None if pd.isna(val) else val for val in row)
                data_tuples.append(tuple_row)

            # Create SQL insert statement with simpler approach
            placeholders = ", ".join(["%s"] * len(columns))
            insert_sql = (
                f"INSERT INTO {table_name} ({column_str}) VALUES ({placeholders})"
            )

            logger.info(f"📝 SQL: {insert_sql}")
            logger.info(
                f"📊 Sample data: {data_tuples[0] if data_tuples else 'No data'}"
            )

            # Execute batch insert using executemany instead of execute_values
            cursor.executemany(insert_sql, data_tuples)

            self.connection.commit()
            cursor.close()

            logger.info(f"✅ Uploaded {len(data_tuples)} records to {table_name}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to upload to {table_name}: {e}")
            self.connection.rollback()
            return False

    def process_all_files(self):
        """Process all CSV files and upload to database"""
        if not self.connect_database():
            return False

        # Clear existing data
        if not self.clear_all_tables():
            return False

        success_count = 0
        total_count = len(CSV_FILES)

        logger.info(f"🚀 Starting upload of {total_count} files...")

        for table_name, file_path in CSV_FILES.items():
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing: {table_name} <- {file_path}")
            logger.info(f"{'='*60}")

            if self.process_and_upload_file(file_path, table_name):
                success_count += 1
                logger.info(f"✅ SUCCESS: {table_name}")
            else:
                logger.error(f"❌ FAILED: {table_name}")

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"UPLOAD SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"✅ Successful: {success_count}/{total_count}")
        logger.info(f"❌ Failed: {total_count - success_count}/{total_count}")

        if success_count == total_count:
            logger.info("🎉 ALL FILES UPLOADED SUCCESSFULLY!")
            return True
        else:
            logger.warning("⚠️ Some files failed to upload")
            return False

    def close_connection(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            logger.info("🔌 Database connection closed")


def main():
    """Main execution function"""
    print("🐎 Horse Racing Data Upload - Complete Solution")
    print("=" * 60)
    print("Qwen2.5's BIGINT Solution + Column Mapping Integration")
    print("=" * 60)

    uploader = IntegratedUploader()

    try:
        success = uploader.process_all_files()

        if success:
            print("\n🎉 DATA PIPELINE COMPLETE!")
            print("✅ All CSV files processed and uploaded successfully")
            print("🔗 Ready for ML pipeline development")
        else:
            print("\n⚠️ PIPELINE INCOMPLETE")
            print("❌ Some files failed - check logs for details")

    except Exception as e:
        logger.error(f"❌ Critical error: {e}")
        print(f"\n💥 CRITICAL ERROR: {e}")

    finally:
        uploader.close_connection()


if __name__ == "__main__":
    main()
