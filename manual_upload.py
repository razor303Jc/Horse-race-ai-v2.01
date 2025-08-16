#!/usr/bin/env python3
"""
Manual Database Upload Script
Horse Racing AI v2.02

Uploads today's downloaded data to PostgreSQL database.
Handles race_id format compatibility.
"""

import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ManualDataUploader:
    """Manual data uploader for today's downloaded data"""

    def __init__(self):
        self.db_config = {
            "host": "localhost",
            "port": 5433,
            "database": "horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def get_connection(self):
        """Get database connection"""
        return psycopg2.connect(**self.db_config)

    def clean_race_id(self, race_id):
        """Clean race_id format (remove .0 suffix)"""
        if isinstance(race_id, str) and race_id.endswith(".0"):
            return race_id[:-2]
        return str(race_id)

    def upload_csv_data(self, csv_path: str, table_name: str) -> bool:
        """Upload CSV data to specified table"""
        try:
            if not os.path.exists(csv_path):
                logger.warning(f"⚠️ File not found: {csv_path}")
                return False

            # Read CSV
            df = pd.read_csv(csv_path)
            if df.empty:
                logger.warning(f"⚠️ Empty file: {csv_path}")
                return False

            # Clean race_id if present
            if "race_id" in df.columns:
                df["race_id"] = df["race_id"].apply(self.clean_race_id)
            if "Race_ID" in df.columns:
                df["Race_ID"] = df["Race_ID"].apply(self.clean_race_id)

            logger.info(f"📊 Uploading {len(df)} records to {table_name}")

            conn = self.get_connection()
            cursor = conn.cursor()

            # Convert DataFrame to list of tuples
            values = [tuple(row) for row in df.values]
            columns = list(df.columns)

            # Create INSERT query with ON CONFLICT handling
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join([f'"{col}"' for col in columns])

            if table_name in [
                "races",
                "records",
                "horses",
                "jockeys_stats",
                "trainers_stats",
            ]:
                # Use ON CONFLICT DO NOTHING for main tables
                query = f"""
                    INSERT INTO {table_name} ({columns_str})
                    VALUES %s
                    ON CONFLICT DO NOTHING
                """
            else:
                # Simple insert for other tables
                query = f"INSERT INTO {table_name} ({columns_str}) VALUES %s"

            # Execute batch insert
            execute_values(cursor, query, values)
            conn.commit()

            affected_rows = cursor.rowcount
            cursor.close()
            conn.close()

            logger.info(
                f"✅ Successfully uploaded {affected_rows} records to {table_name}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Error uploading to {table_name}: {e}")
            return False

    def upload_from_manifest(self, manifest_path: str) -> Dict:
        """Upload data files listed in manifest"""
        try:
            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            results = {}
            total_uploaded = 0

            for table_name, file_paths in manifest.items():
                logger.info(f"🔄 Processing table: {table_name}")

                table_uploaded = 0
                for file_path in file_paths:
                    # Resolve full path (assuming relative to /app in container)
                    if not os.path.isabs(file_path):
                        full_path = f"/app/{file_path}"
                    else:
                        full_path = file_path

                    if self.upload_csv_data(full_path, table_name):
                        table_uploaded += 1

                results[table_name] = table_uploaded
                total_uploaded += table_uploaded

            logger.info(f"🎯 Upload Summary: {total_uploaded} files processed")
            return results

        except Exception as e:
            logger.error(f"❌ Error processing manifest: {e}")
            return {}

    def get_data_status(self):
        """Get current database status"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            status = {}
            tables = ["races", "records", "horses", "jockeys_stats", "trainers_stats"]

            for table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                status[table] = count

            # Get latest race date
            cursor.execute("SELECT MAX(date) FROM races")
            latest_date = cursor.fetchone()[0]
            status["latest_date"] = latest_date

            conn.close()
            return status

        except Exception as e:
            logger.error(f"❌ Error getting status: {e}")
            return {}


def main():
    """Main function"""
    uploader = ManualDataUploader()

    # Check if running inside Docker container
    in_container = os.path.exists("/app/data/daily_downloads")

    if in_container:
        # Running inside container
        manifest_path = "/app/data/daily_downloads/upload_manifest.json"
        logger.info("🐳 Running inside container")
    else:
        # Running on host - need to access container data
        logger.error("❌ This script needs to run inside the auto-downloader container")
        logger.info(
            "💡 Run: docker exec horserace-auto-downloader python /app/manual_upload.py"
        )
        return

    # Show current status
    logger.info("📊 Current Database Status:")
    status = uploader.get_data_status()
    for table, count in status.items():
        if table != "latest_date":
            logger.info(f"   {table}: {count} records")
    logger.info(f"   Latest date: {status.get('latest_date', 'Unknown')}")

    # Upload from manifest
    if os.path.exists(manifest_path):
        logger.info(f"📋 Processing manifest: {manifest_path}")
        results = uploader.upload_from_manifest(manifest_path)

        logger.info("🎯 Upload Results:")
        for table, files_uploaded in results.items():
            logger.info(f"   {table}: {files_uploaded} files uploaded")

        # Show updated status
        logger.info("\n📊 Updated Database Status:")
        new_status = uploader.get_data_status()
        for table, count in new_status.items():
            if table != "latest_date":
                old_count = status.get(table, 0)
                change = count - old_count
                logger.info(f"   {table}: {count} records (+{change})")
        logger.info(f"   Latest date: {new_status.get('latest_date', 'Unknown')}")

    else:
        logger.error(f"❌ Manifest not found: {manifest_path}")


if __name__ == "__main__":
    main()
