#!/usr/bin/env python3
"""
Database Upload Integration Script
=================================

Integrates with the daily downloads manager to upload organized race data to the database.
Uses the upload manifest created by the auto downloader for efficient data handling.

Features:
- Reads upload manifest from auto downloader
- Handles multiple data types (races, records, cards, etc.)
- Implements database schema management
- Provides comprehensive error handling and logging
- Integrates with existing database infrastructure
"""

import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlalchemy import create_engine

# Load environment variables
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    # dotenv not available in production container
    pass

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

console = Console()
logger = logging.getLogger(__name__)


class DatabaseUploader:
    """Uploads organized race data to database"""

    def __init__(self):
        """Initialize uploader with database connection"""
        # Set upload manifest path to absolute path in container
        self.upload_manifest_path = Path(
            "/app/data/daily_downloads/mapped_upload_manifest.json"
        )
        self.downloads_dir = Path("/app/data/daily_downloads")

        # Use DATABASE_URL from environment file
        self.db_url = os.getenv(
            "DATABASE_URL",
            "postgresql://horse_racing:secure_password_123@postgres:5432/"
            "horse_racing_db",
        )

        # Table schemas for PostgreSQL - Separated cards and results data
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            """
                    age INTEGER,
                    sex TEXT,
                    color TEXT,
                    sire TEXT,
                    dam TEXT,
                    trainer TEXT,
                    owner TEXT,
                    breeder TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "jockeys_stats": """
                CREATE TABLE IF NOT EXISTS jockeys_stats (
                    jockey_id INTEGER PRIMARY KEY,
                    jockey_name TEXT UNIQUE,
                    wins INTEGER DEFAULT 0,
                    runs INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    place_rate REAL DEFAULT 0.0,
                    total_prize_money REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
            "trainers_stats": """
                CREATE TABLE IF NOT EXISTS trainers_stats (
                    trainer_id INTEGER PRIMARY KEY,
                    trainer_name TEXT UNIQUE,
                    wins INTEGER DEFAULT 0,
                    runs INTEGER DEFAULT 0,
                    win_rate REAL DEFAULT 0.0,
                    place_rate REAL DEFAULT 0.0,
                    total_prize_money REAL DEFAULT 0.0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """,
        }

    def run_upload_process(self) -> Dict[str, Any]:
        """
        Run complete database upload process

        Returns:
            Dict with upload statistics and results
        """
        console.print(
            Panel.fit(
                f"📤 [bold blue]Database Upload Process - {datetime.now().date()}[/bold blue]",
                style="blue",
            )
        )

        stats = {
            "start_time": datetime.now(),
            "tables_processed": 0,
            "records_uploaded": 0,
            "errors": [],
            "success": False,
        }

        try:
            # Step 1: Check for upload manifest
            console.print("📋 [cyan]Step 1: Checking upload manifest...[/cyan]")
            if not self.upload_manifest_path.exists():
                raise FileNotFoundError(
                    f"Upload manifest not found: {self.upload_manifest_path}"
                )

            upload_files = self._load_upload_manifest()
            console.print(
                f"✅ Found upload manifest with {len(upload_files)} data types"
            )

            # Step 2: Initialize database
            console.print("🗄️ [cyan]Step 2: Initializing database...[/cyan]")
            self._initialize_database()
            console.print("✅ Database initialized successfully")

            # Step 3: Process each data type in dependency order
            console.print("📊 [cyan]Step 3: Processing data files...[/cyan]")

            # Define table upload order to respect foreign key constraints
            table_order = [
                "races",          # Must be first (no dependencies)
                "horses",         # Can be independent
                "jockeys_stats",  # Can be independent  
                "trainers_stats", # Can be independent
                "records",        # Depends on races (race_id foreign key)
                "racecard_details" # May depend on races
            ]

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                console=console,
            ) as progress:

                # Process tables in dependency order
                for data_type in table_order:
                    if data_type in upload_files and upload_files[data_type]:
                        file_paths = upload_files[data_type]
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
                        progress.update(task, completed=len(file_paths))
                
                # Handle any remaining tables not in the defined order
                for data_type, file_paths in upload_files.items():
                    if data_type not in table_order and file_paths:
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
                        progress.update(task, completed=len(file_paths))

            # Step 4: Verify uploads
            console.print("✅ [cyan]Step 4: Verifying uploads...[/cyan]")
            verification_stats = self._verify_uploads()
            stats.update(verification_stats)

            # Step 5: Generate upload report
            console.print("📊 [cyan]Step 5: Generating upload report...[/cyan]")
            self._generate_upload_report(stats)

            stats["end_time"] = datetime.now()
            stats["duration"] = (
                stats["end_time"] - stats["start_time"]
            ).total_seconds()
            stats["success"] = len(stats["errors"]) == 0

            if stats["success"]:
                console.print(
                    "✅ [green]Database upload completed successfully![/green]"
                )
            else:
                console.print(
                    f"⚠️ [yellow]Upload completed with {len(stats['errors'])} errors[/yellow]"
                )

        except Exception as e:
            stats["errors"].append(f"Fatal error: {str(e)}")
            stats["success"] = False
            console.print(f"❌ [red]Upload failed: {e}[/red]")
            logger.exception("Database upload failed")

        return stats

    def _load_upload_manifest(self) -> Dict[str, List[str]]:
        """Load upload manifest created by auto downloader"""
        try:
            with open(self.upload_manifest_path, "r") as f:
                manifest = json.load(f)

            # Extract files from the manifest structure
            if "files" in manifest:
                # Group files by table type
                upload_files = {}
                for file_path, file_info in manifest["files"].items():
                    table_name = file_info.get("table", "unknown")
                    if table_name not in upload_files:
                        upload_files[table_name] = []
                    # Convert relative paths to absolute paths in container
                    abs_file_path = f"/app/{file_path}"
                    upload_files[table_name].append(abs_file_path)
                return upload_files
            else:
                # Fallback for older manifest format
                return manifest

        except Exception as e:
            raise Exception(f"Failed to load upload manifest: {e}")

    def _initialize_database(self) -> None:
        """Initialize PostgreSQL database with required tables"""
        conn = psycopg2.connect(self.db_url)
        with conn.cursor() as cursor:
            # Drop existing tables to ensure clean schema
            cursor.execute("DROP TABLE IF EXISTS racecard_details CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS records CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS horses CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS races CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS jockeys_stats CASCADE;")
            cursor.execute("DROP TABLE IF EXISTS trainers_stats CASCADE;")

            # Create tables with new schema
            for table_name, schema in self.table_schemas.items():
                cursor.execute(schema)
        conn.commit()
        conn.close()

    def _upload_data_file(self, data_type: str, file_path: Path) -> int:
        """Upload a single CSV file to the PostgreSQL database"""
        if not file_path.exists():
            raise FileNotFoundError(f"Data file not found: {file_path}")

        # Read CSV file
        try:
            df = pd.read_csv(file_path)
            if df.empty:
                logger.warning(f"Empty CSV file: {file_path}")
                return 0

            # Deduplicate data based on primary key
            if data_type == "horses" and "horse_id" in df.columns:
                original_count = len(df)
                df = df.drop_duplicates(subset=["horse_id"], keep="first")
                dedup_count = len(df)
                if original_count != dedup_count:
                    logger.warning(
                        f"Removed {original_count - dedup_count} duplicate "
                        f"horse_ids from {file_path}"
                    )

        except Exception as e:
            raise Exception(f"Failed to read CSV {file_path}: {e}")

        # Upload to PostgreSQL database
        return self._upload_to_postgresql(data_type, df)

    def _upload_to_postgresql(self, table_name: str, df: pd.DataFrame) -> int:
        """Upload DataFrame to PostgreSQL database"""
        engine = create_engine(self.db_url)
        # Use smaller batch size to avoid SQL parameter limit issues
        batch_size = 100
        df.to_sql(
            table_name, engine, if_exists="append", index=False, chunksize=batch_size
        )
        return len(df)

    def _verify_uploads(self) -> Dict[str, int]:
        """Verify uploaded data in PostgreSQL"""
        verification = {}

        conn = psycopg2.connect(self.db_url)
        with conn.cursor() as cursor:
            for table_name in self.table_schemas.keys():
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                result = cursor.fetchone()
                count = result[0] if result else 0
                verification[f"{table_name}_count"] = count
        conn.close()

        return verification

    def _generate_upload_report(self, stats: Dict) -> None:
        """Generate and save upload report"""
        report_path = (
            self.downloads_dir
            / f"upload_report_{datetime.now().date().strftime('%Y%m%d')}.json"
        )

        with open(report_path, "w") as f:
            json.dump(stats, f, indent=2, default=str)

        # Display summary table
        summary_table = Table(
            title="Database Upload Summary",
            show_header=True,
            header_style="bold magenta",
        )
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="yellow")

        summary_table.add_row("Tables Processed", str(stats.get("tables_processed", 0)))
        summary_table.add_row("Records Uploaded", str(stats.get("records_uploaded", 0)))
        summary_table.add_row("Errors", str(len(stats.get("errors", []))))
        summary_table.add_row("Duration (seconds)", f"{stats.get('duration', 0):.2f}")
        summary_table.add_row("Success", "✅ Yes" if stats.get("success") else "❌ No")

        console.print(summary_table)


def main():
    """Run database upload process"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/database_upload.log"),
            logging.StreamHandler(),
        ],
    )

    uploader = DatabaseUploader()
    results = uploader.run_upload_process()

    if results["success"]:
        console.print("\n✅ [green]Upload completed successfully![/green]")
        console.print(
            f"📊 Uploaded {results['records_uploaded']} records to "
            f"{results['tables_processed']} tables"
        )
        return True
    else:
        console.print(
            f"\n❌ [red]Upload failed with {len(results['errors'])} errors[/red]"
        )
        for error in results["errors"]:
            console.print(f"   • {error}")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
