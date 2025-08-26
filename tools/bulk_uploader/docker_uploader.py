#!/usr/bin/env python3
"""
Bulk Uploader for Daily Downloads - Docker Container Version
Processes files from data/daily_downloads/processed (excluding non_target)
Designed to work within Docker network with PostgreSQL container
"""

import os
import sys
import json
import pandas as pd
import psycopg2
import psycopg2.extras
from pathlib import Path
from datetime import datetime
import logging
from typing import Dict, List, Optional, Tuple, Any


def setup_logging():
    """Setup logging for container environment"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )


class DockerBulkUploader:
    """Simplified bulk uploader for Docker environment"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.db_config = {
            "host": "postgres",  # Docker service name
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

        # Column mappings from existing patterns
        self.column_mappings = {
            "horses": {
                "id": "horse_id",
                "name": "horse_name",
                "UptoDate": "uptodate",
                "uptodate": "uptodate",
            },
            "jockeys_stats": {
                "UptoDate": "uptodate",
                "Jockey_ID": "jockey_id",
                "Name": "jockey_name",
            },
            "trainers_stats": {
                "UptoDate": "uptodate",
                "Trainer_ID": "trainer_id",
                "Name": "trainer_name",
            },
            "records": {"id": "record_id", "Race_ID": "race_id"},
            "races": {"Race_ID": "race_id"},
        }

        # Upload order for foreign key constraints
        self.upload_order = [
            "races",
            "horses",
            "jockeys_stats",
            "trainers_stats",
            "records",
        ]

    def test_connection(self) -> bool:
        """Test database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                result = cur.fetchone()
                self.logger.info(f"Database connection test result: {result}")
            conn.close()
            return True
        except Exception as e:
            self.logger.error(f"Database connection failed: {e}")
            return False

    def get_connection(self):
        """Get database connection"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            return conn
        except Exception as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise

    def discover_csv_files(self, root_path: Path) -> List[Path]:
        """Discover CSV files excluding non_target directory"""
        files = []

        for file_path in root_path.rglob("*.csv"):
            # Exclude non_target directory
            if "non_target" in str(file_path):
                continue
            files.append(file_path)

        return sorted(files)

    def classify_file(self, file_path: Path) -> Optional[str]:
        """Classify file to determine target table"""
        file_name = file_path.name.lower()

        classification_rules = {
            "horses": ["horse", "mapped_horses"],
            "jockeys_stats": ["jockey", "mapped_jockeys_stats"],
            "trainers_stats": ["trainer", "mapped_trainers_stats"],
            "races": ["race", "mapped_races"],
            "records": ["record", "result", "mapped_records"],
        }

        for table_name, keywords in classification_rules.items():
            if any(keyword in file_name for keyword in keywords):
                return table_name

        return None

    def get_table_schema(self, table_name: str) -> Dict[str, Dict]:
        """Get database schema for table"""
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns 
                    WHERE table_name = %s AND table_schema = 'public'
                    ORDER BY ordinal_position
                """,
                    (table_name,),
                )

                schema = {}
                for row in cur.fetchall():
                    schema[row[0]] = {"type": row[1], "nullable": row[2] == "YES"}
            conn.close()
            return schema
        except Exception as e:
            self.logger.error(f"Error getting schema for {table_name}: {e}")
            return {}

    def validate_and_process_csv(
        self, file_path: Path, table_name: str
    ) -> Tuple[bool, pd.DataFrame, str]:
        """Validate and process CSV file"""
        try:
            self.logger.info(f"Processing {file_path.name} for table {table_name}")

            # Load CSV
            df = pd.read_csv(file_path)
            self.logger.info(f"Loaded {len(df)} rows from {file_path.name}")

            # Apply column mappings
            table_mappings = self.column_mappings.get(table_name, {})
            if table_mappings:
                df = df.rename(columns=table_mappings)
                self.logger.info(f"Applied column mappings: {table_mappings}")

            # Remove empty rows
            initial_rows = len(df)
            df = df.dropna(how="all")
            removed_rows = initial_rows - len(df)
            if removed_rows > 0:
                self.logger.info(f"Removed {removed_rows} empty rows")

            # Get table schema for data type handling
            schema = self.get_table_schema(table_name)

            # Handle NULL values for non-nullable columns
            for col, schema_info in schema.items():
                if col in df.columns and not schema_info["nullable"]:
                    if schema_info["type"] in ["integer", "bigint", "smallint"]:
                        df[col] = df[col].fillna(0)
                    elif schema_info["type"] in [
                        "text",
                        "varchar",
                        "character varying",
                    ]:
                        df[col] = df[col].fillna("")
                    elif schema_info["type"] == "boolean":
                        df[col] = df[col].fillna(False)

            self.logger.info(
                f"Successfully processed {len(df)} records for {table_name}"
            )
            return True, df, ""

        except Exception as e:
            error_msg = f"Error processing {file_path}: {str(e)}"
            self.logger.error(error_msg)
            return False, pd.DataFrame(), error_msg

    def upload_dataframe(
        self, df: pd.DataFrame, table_name: str
    ) -> Tuple[bool, int, str]:
        """Upload DataFrame to database table"""
        try:
            conn = self.get_connection()
            uploaded_count = 0

            with conn:
                columns = list(df.columns)

                # Convert DataFrame to list of tuples
                data_tuples = []
                for _, row in df.iterrows():
                    row_data = []
                    for col in columns:
                        value = row[col]
                        if pd.isna(value):
                            row_data.append(None)
                        else:
                            row_data.append(value)
                    data_tuples.append(tuple(row_data))

                # Build bulk insert query with conflict handling
                placeholders = ",".join(["%s"] * len(columns))
                columns_str = ",".join(columns)
                query = f"""
                    INSERT INTO {table_name} ({columns_str}) 
                    VALUES ({placeholders})
                    ON CONFLICT DO NOTHING
                """

                # Execute bulk insert in batches
                batch_size = 1000
                total_batches = (len(data_tuples) + batch_size - 1) // batch_size

                with conn.cursor() as cur:
                    for i in range(0, len(data_tuples), batch_size):
                        batch = data_tuples[i : i + batch_size]
                        current_batch = (i // batch_size) + 1

                        try:
                            psycopg2.extras.execute_values(
                                cur, query, batch, template=None, page_size=batch_size
                            )

                            uploaded_count += len(batch)
                            self.logger.info(
                                f"Uploaded batch {current_batch}/{total_batches} "
                                f"({uploaded_count}/{len(data_tuples)} records)"
                            )

                        except Exception as e:
                            self.logger.error(f"Error in batch {current_batch}: {e}")
                            continue

                conn.commit()
                self.logger.info(
                    f"Successfully uploaded {uploaded_count} records to {table_name}"
                )
                return True, uploaded_count, f"Uploaded {uploaded_count} records"

        except Exception as e:
            error_msg = f"Upload failed for {table_name}: {str(e)}"
            self.logger.error(error_msg)
            try:
                conn.rollback()
            except:
                pass
            return False, 0, error_msg

    def clear_table_data(self, table_name: str) -> bool:
        """Clear all data from table (for reupload)"""
        try:
            conn = self.get_connection()
            with conn:
                with conn.cursor() as cur:
                    # Disable foreign key checks temporarily
                    cur.execute("SET session_replication_role = replica;")
                    cur.execute(f"DELETE FROM {table_name}")
                    cur.execute("SET session_replication_role = DEFAULT;")

                conn.commit()
                self.logger.info(f"Cleared all data from {table_name}")
                return True

        except Exception as e:
            self.logger.error(f"Failed to clear {table_name}: {e}")
            try:
                conn.rollback()
            except:
                pass
            return False

    def process_daily_downloads(self, clear_tables: bool = False):
        """Process files from daily downloads processed directory"""
        processed_dir = Path("/app/data/daily_downloads/processed")

        if not processed_dir.exists():
            self.logger.error(f"Processed directory not found: {processed_dir}")
            return False

        # Discover CSV files (excluding non_target)
        self.logger.info("Discovering CSV files...")
        csv_files = self.discover_csv_files(processed_dir)

        if not csv_files:
            self.logger.info("No CSV files found to process")
            return True

        self.logger.info(f"Found {len(csv_files)} CSV files to process")

        # Group files by table
        files_by_table = {}
        for file_path in csv_files:
            table_name = self.classify_file(file_path)
            if table_name:
                if table_name not in files_by_table:
                    files_by_table[table_name] = []
                files_by_table[table_name].append(file_path)
                self.logger.info(f"Classified {file_path.name} → {table_name}")
            else:
                self.logger.warning(f"Could not classify file: {file_path.name}")

        if not files_by_table:
            self.logger.warning("No files could be classified for processing")
            return False

        # Clear tables if requested
        if clear_tables:
            self.logger.info("Clearing existing table data...")
            # Clear in reverse order due to foreign keys
            for table_name in reversed(self.upload_order):
                if table_name in files_by_table:
                    if not self.clear_table_data(table_name):
                        self.logger.error(f"Failed to clear {table_name}")
                        return False

        # Process files in upload order
        total_uploaded = 0
        total_files = 0
        results = {}

        for table_name in self.upload_order:
            if table_name not in files_by_table:
                continue

            files = files_by_table[table_name]
            table_uploaded = 0
            table_files = 0

            self.logger.info(f"\nProcessing {len(files)} files for {table_name} table:")

            for file_path in files:
                total_files += 1
                table_files += 1

                # Process file
                success, df, error = self.validate_and_process_csv(
                    file_path, table_name
                )
                if not success:
                    self.logger.error(f"Failed to process {file_path.name}: {error}")
                    continue

                # Upload to database
                upload_success, uploaded_count, upload_msg = self.upload_dataframe(
                    df, table_name
                )
                if upload_success:
                    total_uploaded += uploaded_count
                    table_uploaded += uploaded_count
                    self.logger.info(
                        f"✅ {file_path.name}: {uploaded_count} records uploaded"
                    )
                else:
                    self.logger.error(f"❌ {file_path.name}: {upload_msg}")

            results[table_name] = {
                "files_processed": table_files,
                "records_uploaded": table_uploaded,
            }

            self.logger.info(
                f"Table {table_name} summary: {table_uploaded} records from {table_files} files"
            )

        # Final summary
        self.logger.info(f"\n📊 BULK UPLOAD SUMMARY:")
        self.logger.info(f"   Total files processed: {total_files}")
        self.logger.info(f"   Total records uploaded: {total_uploaded}")

        for table_name, result in results.items():
            self.logger.info(
                f"   {table_name}: {result['records_uploaded']} records from {result['files_processed']} files"
            )

        return True


def main():
    """Main entry point"""
    print("🚀 Docker Bulk Uploader for Daily Downloads")
    print("=" * 50)

    setup_logging()

    # Initialize uploader
    uploader = DockerBulkUploader()

    # Test database connection
    print("🔌 Testing database connection...")
    if not uploader.test_connection():
        print("❌ Database connection failed")
        return 1

    print("✅ Database connection successful")

    # Check for clear tables flag
    clear_tables = os.environ.get("CLEAR_TABLES", "false").lower() == "true"

    if clear_tables:
        print("⚠️  CLEAR_TABLES=true - Will clear existing data before upload")
        confirm = input("Are you sure you want to clear all table data? (yes/no): ")
        if confirm.lower() != "yes":
            print("❌ Operation cancelled")
            return 0

    # Process daily downloads
    print("🚀 Processing daily downloads...")
    try:
        success = uploader.process_daily_downloads(clear_tables=clear_tables)

        if success:
            print("✅ Bulk upload completed successfully")
            return 0
        else:
            print("❌ Bulk upload failed")
            return 1

    except Exception as e:
        print(f"❌ Bulk upload failed with exception: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
