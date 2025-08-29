#!/usr/bin/env python3
"""
Integrated Data Processing Pipeline
==================================

Complete pipeline that handles:
1. CSV mapping and column alignment
2. Data cleaning and validation
3. Database upload with error handling
4. Pipeline integration for daily downloads

This module integrates into the main daily downloads workflow.
"""

import json
import logging
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from sqlalchemy import create_engine

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class IntegratedDataProcessor:
    """
    Integrated data processor that handles the complete pipeline from
    CSV mapping through database upload.
    """

    def __init__(self, database_url: str):
        """Initialize with database connection."""
        self.database_url = database_url
        self.engine = None

    def connect_database(self) -> bool:
        """Establish database connection."""
        try:
            self.engine = create_engine(self.database_url)
            logger.info("✅ Connected to PostgreSQL database")
            return True
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return False

    def clean_data(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """
        Clean data based on table-specific requirements.

        Args:
            df: DataFrame to clean
            table_name: Target table name

        Returns:
            Cleaned DataFrame
        """
        cleaned_df = df.copy()

        if table_name == "records":
            # Fix or_rating column - replace "-" with None
            if "or_rating" in cleaned_df.columns:
                before_count = len(cleaned_df[cleaned_df["or_rating"] == "-"])
                cleaned_df["or_rating"] = cleaned_df["or_rating"].replace("-", None)
                logger.info(f"🧹 Fixed {before_count} '-' values in or_rating column")

        elif table_name == "races":
            # Remove duplicates based on race_id
            before_count = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates(subset=["race_id"], keep="first")
            after_count = len(cleaned_df)
            if before_count != after_count:
                logger.info(f"🧹 Removed {before_count - after_count} duplicate races")

        elif table_name == "horses":
            # Remove duplicates based on horse_id
            before_count = len(cleaned_df)
            cleaned_df = cleaned_df.drop_duplicates(subset=["horse_id"], keep="first")
            after_count = len(cleaned_df)
            if before_count != after_count:
                logger.info(f"🧹 Removed {before_count - after_count} duplicate horses")

        return cleaned_df

    def upload_table(
        self, file_path: str, table_name: str, if_exists: str = "append"
    ) -> Tuple[bool, int]:
        """
        Upload a single CSV file to database with cleaning.

        Args:
            file_path: Path to CSV file
            table_name: Target table name
            if_exists: What to do if table exists ('append', 'replace', 'fail')

        Returns:
            Tuple of (success, row_count)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                return False, 0

            # Read CSV
            df = pd.read_csv(file_path)
            original_count = len(df)
            logger.info(f"📄 Loaded {original_count} rows from {file_path}")

            # Clean data
            df_cleaned = self.clean_data(df, table_name)
            cleaned_count = len(df_cleaned)

            # Upload to database
            df_cleaned.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            logger.info(
                f"✅ Successfully uploaded {cleaned_count} rows to {table_name}"
            )

            return True, cleaned_count

        except Exception as e:
            logger.error(f"❌ Error uploading {file_path} to {table_name}: {e}")
            return False, 0

    def process_manifest(self, manifest_path: str) -> Dict[str, Dict]:
        """
        Process upload manifest and upload all files.

        Args:
            manifest_path: Path to upload manifest JSON

        Returns:
            Dictionary with upload results for each table
        """
        results = {}

        try:
            # Load manifest
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            logger.info(f"📋 Loaded manifest with {len(manifest['files'])} files")

            # Process each file
            total_rows = 0
            successful_tables = 0

            for file_path, config in manifest["files"].items():
                table_name = config["table"]
                logger.info(f"🔄 Processing {file_path} → {table_name}")

                success, row_count = self.upload_table(file_path, table_name)

                results[table_name] = {
                    "file_path": file_path,
                    "success": success,
                    "row_count": row_count,
                }

                if success:
                    total_rows += row_count
                    successful_tables += 1

            logger.info(f"📊 Upload Summary:")
            logger.info(
                f"   ✅ Successful tables: {successful_tables}/{len(manifest['files'])}"
            )
            logger.info(f"   📈 Total rows uploaded: {total_rows}")

            return results

        except Exception as e:
            logger.error(f"❌ Error processing manifest: {e}")
            return {}

    def validate_upload(self) -> Dict[str, int]:
        """
        Validate upload by checking row counts in database.

        Returns:
            Dictionary with table names and row counts
        """
        try:
            query = """
            SELECT 'races' as table_name, COUNT(*) as count FROM races 
            UNION ALL SELECT 'records', COUNT(*) FROM records 
            UNION ALL SELECT 'horses', COUNT(*) FROM horses 
            UNION ALL SELECT 'jockeys_stats', COUNT(*) FROM jockeys_stats 
            UNION ALL SELECT 'trainers_stats', COUNT(*) FROM trainers_stats;
            """

            result = pd.read_sql(query, self.engine)
            counts = dict(zip(result["table_name"], result["count"]))

            logger.info("📊 Database validation results:")
            total_rows = 0
            for table, count in counts.items():
                logger.info(f"   {table}: {count:,} rows")
                total_rows += count

            logger.info(f"   📈 Total rows in database: {total_rows:,}")

            return counts

        except Exception as e:
            logger.error(f"❌ Error validating upload: {e}")
            return {}


def main():
    """Main pipeline execution."""
    # Database configuration
    database_url = (
        "postgresql://horse_racing:secure_password_123@postgres:5432/horse_racing_db"
    )

    # Initialize processor
    processor = IntegratedDataProcessor(database_url)

    # Connect to database
    if not processor.connect_database():
        sys.exit(1)

    # Process upload manifest
    manifest_path = "data/daily_downloads/upload_manifest.json"
    results = processor.process_manifest(manifest_path)

    # Validate upload
    counts = processor.validate_upload()

    # Summary
    successful_uploads = sum(1 for r in results.values() if r["success"])
    total_files = len(results)

    if successful_uploads == total_files and counts:
        logger.info("🎉 Pipeline completed successfully!")
        return True
    else:
        logger.error("❌ Pipeline completed with errors")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
