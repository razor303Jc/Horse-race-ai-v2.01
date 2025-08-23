#!/usr/bin/env python3
"""
Upload Fix Integration Test
==========================

Tests and fixes the actual upload issues using the existing test framework.
"""

import pytest
import pandas as pd
import psycopg2
from pathlib import Path
import sys
import logging
import os
from urllib.parse import urlparse

# Add project directory to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use DATABASE_URL from environment like Docker containers do
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://horse_racing:secure_password_123@localhost:5432/horse_racing_db",
)

# Parse DATABASE_URL
parsed_url = urlparse(DATABASE_URL)
DATABASE_CONFIG = {
    "host": parsed_url.hostname or "localhost",
    "port": parsed_url.port or 5432,
    "database": parsed_url.path.lstrip("/") if parsed_url.path else "horse_racing_db",
    "user": parsed_url.username or "horse_racing",
    "password": parsed_url.password or "secure_password_123",
}


class TestUploadIntegration:
    """Test upload system integration with proper fixes"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.data_dir = Path(
            "/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads"
        )
        self.upload_files = {
            "races": "complete_mapped_races.csv",
            "horses": "complete_mapped_horses.csv",
            "jockeys_stats": "complete_mapped_jockeys_stats.csv",
            "trainers_stats": "complete_mapped_trainers_stats.csv",
            "records": "complete_mapped_records.csv",
            "racecard_details": "mapped_racecard_details.csv",  # This was missing!
        }

    def test_database_connection(self):
        """Test database connection with correct configuration"""
        logger.info("🧪 Testing database connection...")

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            with conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                logger.info(f"✅ Connected to: {version}")
            conn.close()
            assert True
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
            pytest.fail(f"Database connection failed: {e}")

    def test_csv_files_exist(self):
        """Test that all required CSV files exist"""
        logger.info("🧪 Testing CSV file availability...")

        missing_files = []
        for table, filename in self.upload_files.items():
            file_path = self.data_dir / filename
            if not file_path.exists():
                missing_files.append(str(file_path))
                logger.warning(f"⚠️ Missing: {file_path}")
            else:
                # Check file has data
                df = pd.read_csv(file_path)
                logger.info(f"✅ Found: {filename} ({len(df)} rows)")

        if missing_files:
            pytest.fail(f"Missing CSV files: {missing_files}")

    def test_table_schemas_exist(self):
        """Test that all required database tables exist"""
        logger.info("🧪 Testing database table schemas...")

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)
            with conn.cursor() as cur:
                for table in self.upload_files.keys():
                    cur.execute(
                        """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        );
                    """,
                        (table,),
                    )
                    exists = cur.fetchone()[0]
                    if exists:
                        logger.info(f"✅ Table exists: {table}")
                    else:
                        logger.error(f"❌ Table missing: {table}")
                        pytest.fail(f"Table {table} does not exist")
            conn.close()
        except Exception as e:
            pytest.fail(f"Schema check failed: {e}")

    def test_upload_foreign_key_dependencies(self):
        """Test upload order respects foreign key dependencies"""
        logger.info("🧪 Testing upload order for foreign key dependencies...")

        # Correct order: independent tables first, then dependent tables
        upload_order = [
            ("horses", "complete_mapped_horses.csv"),
            ("jockeys_stats", "complete_mapped_jockeys_stats.csv"),
            ("trainers_stats", "complete_mapped_trainers_stats.csv"),
            ("races", "complete_mapped_races.csv"),
            (
                "racecard_details",
                "mapped_racecard_details.csv",
            ),  # Depends on races, horses, jockeys, trainers
            ("records", "complete_mapped_records.csv"),  # Depends on racecard_details
        ]

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)

            for table, filename in upload_order:
                file_path = self.data_dir / filename
                if not file_path.exists():
                    logger.warning(f"⚠️ Skipping missing file: {filename}")
                    continue

                df = pd.read_csv(file_path)
                if len(df) == 0:
                    logger.warning(f"⚠️ Skipping empty file: {filename}")
                    continue

                logger.info(f"📤 Uploading {filename} to {table} ({len(df)} rows)")

                # Check current count
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    before_count = cur.fetchone()[0]

                # Upload with proper error handling
                success = self._upload_csv_to_table(conn, file_path, table)
                if not success:
                    pytest.fail(f"Upload failed for {table}")

                # Verify upload
                with conn.cursor() as cur:
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    after_count = cur.fetchone()[0]

                uploaded = after_count - before_count
                logger.info(
                    f"✅ Uploaded {uploaded} rows to {table} (total: {after_count})"
                )

            conn.close()

        except Exception as e:
            logger.error(f"❌ Upload test failed: {e}")
            pytest.fail(f"Upload dependency test failed: {e}")

    def _upload_csv_to_table(self, conn, csv_file, table_name):
        """Helper method to upload CSV to table with proper error handling"""
        try:
            df = pd.read_csv(csv_file)

            # Handle NULL values
            insert_data = []
            for _, row in df.iterrows():
                row_data = []
                for col in df.columns:
                    val = row[col]
                    if pd.isna(val) or val == "" or val == "None":
                        row_data.append(None)
                    else:
                        row_data.append(val)
                insert_data.append(tuple(row_data))

            # Build INSERT with ON CONFLICT handling
            columns = df.columns.tolist()
            cols_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))

            with conn.cursor() as cur:
                # Use INSERT ... ON CONFLICT DO NOTHING to handle duplicates
                query = f"""
                    INSERT INTO {table_name} ({cols_str}) 
                    VALUES %s 
                    ON CONFLICT DO NOTHING
                """

                from psycopg2.extras import execute_values

                execute_values(cur, query, insert_data, page_size=1000)
                conn.commit()

            return True

        except Exception as e:
            logger.error(f"❌ Upload failed for {table_name}: {e}")
            conn.rollback()
            return False

    def test_ai_predictions_data_availability(self):
        """Test that AI predictions can find today's race data"""
        logger.info("🧪 Testing AI predictions data availability...")

        try:
            conn = psycopg2.connect(**DATABASE_CONFIG)

            # Check for today's race data
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT COUNT(*) FROM racecard_details 
                    WHERE race_date = CURRENT_DATE
                """
                )
                todays_races = cur.fetchone()[0]

                cur.execute("SELECT COUNT(*) FROM racecard_details")
                total_races = cur.fetchone()[0]

                logger.info(
                    f"📊 Race card data: {total_races} total, {todays_races} for today"
                )

                if total_races == 0:
                    pytest.fail("No race card data found - AI predictions cannot work")

                if todays_races == 0:
                    logger.warning(
                        "⚠️ No race data for today - check if data is current"
                    )

            conn.close()

        except Exception as e:
            pytest.fail(f"AI predictions data check failed: {e}")

    @pytest.mark.integration
    def test_complete_upload_pipeline(self):
        """Complete integration test of the upload pipeline"""
        logger.info("🧪 Testing complete upload pipeline...")

        # Run all the individual tests
        self.test_database_connection()
        self.test_csv_files_exist()
        self.test_table_schemas_exist()
        self.test_upload_foreign_key_dependencies()
        self.test_ai_predictions_data_availability()

        logger.info("✅ Complete upload pipeline test passed!")


def run_upload_fixes():
    """Run upload fixes directly without pytest fixtures"""
    logger.info("🏇 Horse Racing Upload Fix Integration")
    logger.info("=" * 50)

    # Setup data
    data_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data/daily_downloads")
    upload_files = {
        "races": "complete_mapped_races.csv",
        "horses": "complete_mapped_horses.csv",
        "jockeys_stats": "complete_mapped_jockeys_stats.csv",
        "trainers_stats": "complete_mapped_trainers_stats.csv",
        "records": "complete_mapped_records.csv",
        "racecard_details": "mapped_racecard_details.csv",  # This was missing!
    }

    try:
        # Test 1: Database connection
        logger.info("🧪 Testing database connection...")
        conn = psycopg2.connect(**DATABASE_CONFIG)
        with conn.cursor() as cur:
            cur.execute("SELECT version();")
            version = cur.fetchone()[0]
            logger.info(f"✅ Connected to: {version}")
        conn.close()

        # Test 2: Check CSV files
        logger.info("🧪 Checking CSV file availability...")
        missing_files = []
        for table, filename in upload_files.items():
            file_path = data_dir / filename
            if not file_path.exists():
                missing_files.append(str(file_path))
                logger.warning(f"⚠️ Missing: {file_path}")
            else:
                df = pd.read_csv(file_path)
                logger.info(f"✅ Found: {filename} ({len(df)} rows)")

        if missing_files:
            logger.error(f"❌ Missing CSV files: {missing_files}")
            return False

        # Test 3: Upload with correct order
        logger.info("🧪 Uploading data in correct dependency order...")
        upload_order = [
            ("horses", "complete_mapped_horses.csv"),
            ("jockeys_stats", "complete_mapped_jockeys_stats.csv"),
            ("trainers_stats", "complete_mapped_trainers_stats.csv"),
            ("races", "complete_mapped_races.csv"),
            ("racecard_details", "mapped_racecard_details.csv"),
            ("records", "complete_mapped_records.csv"),
        ]

        conn = psycopg2.connect(**DATABASE_CONFIG)

        for table, filename in upload_order:
            file_path = data_dir / filename
            if not file_path.exists():
                logger.warning(f"⚠️ Skipping missing file: {filename}")
                continue

            df = pd.read_csv(file_path)
            if len(df) == 0:
                logger.warning(f"⚠️ Skipping empty file: {filename}")
                continue

            logger.info(f"📤 Uploading {filename} to {table} ({len(df)} rows)")

            # Check before count
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                before_count = cur.fetchone()[0]

            # Upload
            success = upload_csv_to_table(conn, file_path, table)
            if not success:
                logger.error(f"❌ Upload failed for {table}")
                return False

            # Check after count
            with conn.cursor() as cur:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                after_count = cur.fetchone()[0]

            uploaded = after_count - before_count
            logger.info(
                f"✅ Uploaded {uploaded} rows to {table} (total: {after_count})"
            )

        # Test 4: Check AI predictions data
        logger.info("🧪 Checking AI predictions data availability...")
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM racecard_details")
            total_races = cur.fetchone()[0]
            logger.info(f"📊 Race card data: {total_races} total entries")

            if total_races == 0:
                logger.error("❌ No race card data found - AI predictions cannot work")
                return False

        conn.close()
        logger.info("✅ ALL UPLOAD FIXES COMPLETED SUCCESSFULLY!")
        return True

    except Exception as e:
        logger.error(f"❌ Upload fix failed: {e}")
        return False


def upload_csv_to_table(conn, csv_file, table_name):
    """Upload CSV to table with proper error handling"""
    try:
        df = pd.read_csv(csv_file)

        # Handle NULL values
        insert_data = []
        for _, row in df.iterrows():
            row_data = []
            for col in df.columns:
                val = row[col]
                if pd.isna(val) or val == "" or val == "None":
                    row_data.append(None)
                else:
                    row_data.append(val)
            insert_data.append(tuple(row_data))

        # Build INSERT with conflict handling
        columns = df.columns.tolist()
        cols_str = ", ".join(columns)

        with conn.cursor() as cur:
            from psycopg2.extras import execute_values

            query = f"""
                INSERT INTO {table_name} ({cols_str}) 
                VALUES %s 
                ON CONFLICT DO NOTHING
            """
            execute_values(cur, query, insert_data, page_size=1000)
            conn.commit()

        return True

    except Exception as e:
        logger.error(f"❌ Upload failed for {table_name}: {e}")
        conn.rollback()
        return False


if __name__ == "__main__":
    success = run_upload_fixes()
    if not success:
        sys.exit(1)
