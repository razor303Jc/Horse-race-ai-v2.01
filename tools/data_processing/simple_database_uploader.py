#!/usr/bin/env python3
"""
Simple Database Upload Integration Script
========================================

Minimal working uploader for testing the separated cards/results pipeline.
Uploads processed CSV data to PostgreSQL with simple schemas.
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import psycopg2
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from sqlalchemy import create_engine

console = Console()
logger = logging.getLogger(__name__)


class SimpleUploader:
    """Simple database uploader for separated cards/results data"""

    def __init__(self):
        """Initialize uploader with database connection"""
        self.upload_manifest_path = Path(
            "/app/data/daily_downloads/mapped_upload_manifest.json"
        )

        # Use environment variables for database connection
        self.db_url = (
            f"postgresql://{os.getenv('DB_USER', 'horse_racing')}:"
            f"{os.getenv('DB_PASSWORD', 'secure_password_123')}@"
            f"{os.getenv('DB_HOST', 'horse_racing_postgres_clean')}:"
            f"{os.getenv('DB_PORT', '5432')}/"
            f"{os.getenv('DB_NAME', 'horse_racing_db')}"
        )

        # Simple table schemas without foreign keys
        self.table_schemas = {
            "card_races": """
                CREATE TABLE IF NOT EXISTS card_races (
                    race_id BIGINT PRIMARY KEY,
                    race_number INTEGER,
                    race_time TEXT,
                    course_id BIGINT,
                    course TEXT,
                    race_type TEXT,
                    date DATE,
                    race_name TEXT,
                    class TEXT,
                    years TEXT,
                    distance TEXT,
                    surface TEXT,
                    prize TEXT,
                    runners_racecard INTEGER,
                    runners INTEGER,
                    draw TEXT,
                    ew_racecard TEXT,
                    ew INTEGER,
                    places_ew_racecard TEXT,
                    places_ew INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "card_records": """
                CREATE TABLE IF NOT EXISTS card_records (
                    record_id BIGINT PRIMARY KEY,
                    race_id BIGINT,
                    horse_name TEXT,
                    jockey TEXT,
                    trainer TEXT,
                    position INTEGER,
                    starting_price TEXT,
                    weight TEXT,
                    age INTEGER,
                    form TEXT,
                    extra TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "card_horses": """
                CREATE TABLE IF NOT EXISTS card_horses (
                    horse_id BIGINT PRIMARY KEY,
                    name TEXT,
                    age INTEGER,
                    sex TEXT,
                    colour TEXT,
                    sire TEXT,
                    dam TEXT,
                    trainer TEXT,
                    owner TEXT,
                    country TEXT,
                    rating TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "result_races": """
                CREATE TABLE IF NOT EXISTS result_races (
                    race_id BIGINT PRIMARY KEY,
                    race_number INTEGER,
                    race_time TEXT,
                    course_id BIGINT,
                    course TEXT,
                    race_type TEXT,
                    date DATE,
                    race_name TEXT,
                    class TEXT,
                    years TEXT,
                    distance TEXT,
                    surface TEXT,
                    prize TEXT,
                    runners_racecard INTEGER,
                    runners INTEGER,
                    draw TEXT,
                    ew_racecard TEXT,
                    ew INTEGER,
                    places_ew_racecard TEXT,
                    places_ew INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "jockeys_stats": """
                CREATE TABLE IF NOT EXISTS jockeys_stats (
                    jockey_id BIGINT PRIMARY KEY,
                    name TEXT,
                    wins INTEGER,
                    runs INTEGER,
                    win_percentage DECIMAL(5,2),
                    strike_rate DECIMAL(5,2),
                    prize_money TEXT,
                    last_14_days TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "trainers_stats": """
                CREATE TABLE IF NOT EXISTS trainers_stats (
                    trainer_id BIGINT PRIMARY KEY,
                    name TEXT,
                    wins INTEGER,
                    runs INTEGER,
                    win_percentage DECIMAL(5,2),
                    strike_rate DECIMAL(5,2),
                    prize_money TEXT,
                    last_14_days TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "racecard_details": """
                CREATE TABLE IF NOT EXISTS racecard_details (
                    record_id BIGINT PRIMARY KEY,
                    race_id BIGINT,
                    horse_name TEXT,
                    jockey TEXT,
                    trainer TEXT,
                    position INTEGER,
                    starting_price TEXT,
                    weight TEXT,
                    age INTEGER,
                    form TEXT,
                    extra TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
        }

    def run_upload_process(self) -> Dict[str, Any]:
        """Run complete database upload process"""
        console.print(Panel.fit("📤 Database Upload Process", style="blue"))

        stats = {
            "start_time": datetime.now(),
            "tables_processed": 0,
            "records_uploaded": 0,
            "errors": [],
            "success": False,
        }

        try:
            # Step 1: Check for upload manifest
            console.print("📋 Checking upload manifest...")
            if not self.upload_manifest_path.exists():
                raise FileNotFoundError(
                    f"Upload manifest not found: {self.upload_manifest_path}"
                )

            upload_files = self._load_upload_manifest()
            console.print(f"✅ Found {len(upload_files)} data types")

            # Step 2: Initialize database
            console.print("🗄️ Initializing database...")
            self._initialize_database()
            console.print("✅ Database initialized")

            # Step 3: Process files
            console.print("📊 Processing data files...")

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:

                for data_type, file_paths in upload_files.items():
                    if file_paths and data_type in self.table_schemas:
                        task = progress.add_task(
                            f"Processing {data_type}...", total=len(file_paths)
                        )

                        for file_path in file_paths:
                            try:
                                records_count = self._upload_data_file(
                                    data_type, Path(file_path)
                                )
                                stats["records_uploaded"] += records_count
                                progress.update(task, advance=1)

                            except Exception as e:
                                error_msg = f"Error uploading {file_path}: {str(e)}"
                                stats["errors"].append(error_msg)
                                logger.error(error_msg)
                                progress.update(task, advance=1)

                        stats["tables_processed"] += 1

            # Step 4: Verify uploads
            verification = self._verify_uploads()
            stats.update(verification)

            stats["success"] = len(stats["errors"]) == 0
            stats["end_time"] = datetime.now()
            stats["duration"] = (
                stats["end_time"] - stats["start_time"]
            ).total_seconds()

            if stats["success"]:
                console.print("✅ Upload completed successfully!")
                console.print(
                    f"📊 Uploaded {stats['records_uploaded']} records "
                    f"to {stats['tables_processed']} tables"
                )
            else:
                console.print(f"⚠️ Upload completed with {len(stats['errors'])} errors")
                for error in stats["errors"]:
                    console.print(f"   • {error}")

        except Exception as e:
            stats["errors"].append(str(e))
            stats["success"] = False
            console.print(f"❌ Upload failed: {e}")

        return stats

    def _load_upload_manifest(self) -> Dict[str, List[str]]:
        """Load upload manifest (handles both old and new formats)"""
        try:
            with open(self.upload_manifest_path, "r") as f:
                manifest = json.load(f)

            # Handle new format (tables)
            if "tables" in manifest:
                upload_files = {}
                for table_name, table_info in manifest["tables"].items():
                    upload_files[table_name] = table_info.get("files", [])
                return upload_files

            # Handle old format (files)
            elif "files" in manifest:
                upload_files = {}
                for file_path, file_info in manifest["files"].items():
                    table_name = file_info.get("table")
                    if table_name:
                        if table_name not in upload_files:
                            upload_files[table_name] = []
                        upload_files[table_name].append(file_path)
                return upload_files

            # Fallback for direct dictionary format
            else:
                return manifest

        except Exception as e:
            raise Exception(f"Failed to load upload manifest: {e}")

    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database with required tables"""
        conn = psycopg2.connect(self.db_url)
        with conn.cursor() as cursor:
            # Create tables with new schema (don't drop existing ones)
            for table_name, schema in self.table_schemas.items():
                cursor.execute(schema)
        conn.commit()
        conn.close()

    def _upload_data_file(self, data_type: str, file_path: Path) -> int:
        """Upload a single CSV file to the PostgreSQL database"""
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        try:
            df = pd.read_csv(file_path)
            if df.empty:
                logger.warning(f"Empty CSV file: {file_path}")
                return 0

            # Upload to database using SQLAlchemy
            engine = create_engine(self.db_url)
            df.to_sql(data_type, engine, if_exists="append", index=False, chunksize=100)
            return len(df)

        except Exception as e:
            raise Exception(f"Failed to upload {file_path}: {e}")

    def _verify_uploads(self) -> Dict[str, int]:
        """Verify uploaded data in PostgreSQL"""
        verification = {}
        conn = psycopg2.connect(self.db_url)
        with conn.cursor() as cursor:
            for table_name in self.table_schemas.keys():
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                    result = cursor.fetchone()
                    count = result[0] if result else 0
                    verification[f"{table_name}_count"] = count
                except Exception as e:
                    verification[f"{table_name}_count"] = 0
                    logger.warning(f"Could not verify {table_name}: {e}")
        conn.close()
        return verification


def main():
    """Run database upload process"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler()],
    )

    uploader = SimpleUploader()
    results = uploader.run_upload_process()

    if results["success"]:
        console.print("✅ Upload completed successfully!")
        return True
    else:
        console.print(f"❌ Upload failed with {len(results['errors'])} errors")
        for error in results["errors"]:
            console.print(f"   • {error}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
