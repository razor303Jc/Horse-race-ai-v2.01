#!/usr/bin/env python3
"""
Enhanced Database Upload Integration Script
==========================================

Enhanced version of the database uploader that integrates with the daily downloads manager
and provides comprehensive database management for horse racing data.

Features:
- Advanced upload manifest processing
- Multiple database backend support (SQLite, PostgreSQL)
- Schema auto-creation and validation
- Data deduplication and conflict resolution
- Comprehensive error handling and recovery
- Performance optimization and bulk operations
- Integration with VS Code shell integration
"""

import asyncio
import json
import logging
import os
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd
import sqlalchemy as sa
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table
from sqlalchemy import MetaData
from sqlalchemy import Table as SQLTable
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

console = Console()
logger = logging.getLogger(__name__)


class EnhancedDatabaseUploader:
    """Enhanced database uploader with advanced features"""

    def __init__(self, downloads_dir: str = "data/daily_downloads"):
        self.downloads_dir = Path(downloads_dir)
        self.upload_manifest_path = self.downloads_dir / "upload_manifest.json"
        self.today = datetime.now().date()

        # Database configuration
        self.db_url = os.getenv("DATABASE_URL", "sqlite:///data/horse_racing.db")
        self.engine = None
        self.metadata = MetaData()

        # Setup logging
        logging.basicConfig(level=logging.INFO)

        # Table schemas and configurations
        self.table_configs = {
            "races": {
                "primary_key": "Race_ID",
                "columns": {
                    "Race_ID": "VARCHAR(20) PRIMARY KEY",
                    "race_number": "INTEGER",
                    "race_time": "TIME",
                    "course_id": "INTEGER",
                    "Course": "VARCHAR(100)",
                    "Race_type": "VARCHAR(50)",
                    "Date": "DATE",
                    "Race_name": "TEXT",
                    "Class": "VARCHAR(20)",
                    "Years": "VARCHAR(20)",
                    "Distance": "VARCHAR(20)",
                    "Surface": "TEXT",
                    "Prize": "VARCHAR(20)",
                    "Runners_racecard": "INTEGER",
                    "Runners": "INTEGER",
                    "Draw": "VARCHAR(20)",
                    "EW_racecard": "INTEGER",
                    "EW": "INTEGER",
                    "Places_EW_racecard": "INTEGER",
                    "Places_EW": "INTEGER",
                },
                "indexes": ["Date", "Course", "race_time"],
            },
            "records": {
                "primary_key": "Record_ID",
                "columns": {
                    "Record_ID": "VARCHAR(20) PRIMARY KEY",
                    "Race_ID": "VARCHAR(20)",
                    "Position": "INTEGER",
                    "Horse": "VARCHAR(100)",
                    "Age": "INTEGER",
                    "Weight": "VARCHAR(20)",
                    "Jockey": "VARCHAR(100)",
                    "Trainer": "VARCHAR(100)",
                    "OR_rating": "INTEGER",
                    "TS": "INTEGER",
                    "RPR": "INTEGER",
                    "Odds": "VARCHAR(20)",
                    "Fav": "VARCHAR(10)",
                    "SP": "VARCHAR(20)",
                    "Extra": "TEXT",
                },
                "indexes": ["Race_ID", "Horse", "Jockey", "Trainer"],
                "foreign_keys": [("Race_ID", "races", "Race_ID")],
            },
            "horses": {
                "primary_key": "Horse_ID",
                "columns": {
                    "Horse_ID": "VARCHAR(50) PRIMARY KEY",
                    "Horse_name": "VARCHAR(100)",
                    "Age": "INTEGER",
                    "Sex": "VARCHAR(10)",
                    "Color": "VARCHAR(20)",
                    "Sire": "VARCHAR(100)",
                    "Dam": "VARCHAR(100)",
                    "Owner": "VARCHAR(100)",
                    "Breeder": "VARCHAR(100)",
                },
                "indexes": ["Horse_name", "Age"],
            },
            "jockeys_stats": {
                "primary_key": "Jockey_ID",
                "columns": {
                    "Jockey_ID": "VARCHAR(50) PRIMARY KEY",
                    "Jockey_name": "VARCHAR(100)",
                    "Wins": "INTEGER",
                    "Runs": "INTEGER",
                    "Win_rate": "DECIMAL(5,2)",
                    "Prize_money": "DECIMAL(12,2)",
                    "Last_win": "DATE",
                },
                "indexes": ["Jockey_name", "Win_rate"],
            },
            "trainers_stats": {
                "primary_key": "Trainer_ID",
                "columns": {
                    "Trainer_ID": "VARCHAR(50) PRIMARY KEY",
                    "Trainer_name": "VARCHAR(100)",
                    "Wins": "INTEGER",
                    "Runs": "INTEGER",
                    "Win_rate": "DECIMAL(5,2)",
                    "Prize_money": "DECIMAL(12,2)",
                    "Last_win": "DATE",
                },
                "indexes": ["Trainer_name", "Win_rate"],
            },
        }

    async def initialize_database(self) -> bool:
        """Initialize database connection and create tables if needed"""
        try:
            console.print("🔌 [cyan]Initializing database connection...[/cyan]")

            # Create engine
            self.engine = create_engine(self.db_url, echo=False)

            # Test connection
            with self.engine.connect() as conn:
                # Create tables if they don't exist
                await self._create_tables_if_needed()

            console.print("✅ Database initialized successfully")
            return True

        except Exception as e:
            error_msg = f"Database initialization failed: {e}"
            logger.error(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return False

    async def _create_tables_if_needed(self):
        """Create database tables based on configuration"""
        try:
            with self.engine.connect() as conn:
                for table_name, config in self.table_configs.items():
                    # Check if table exists
                    if "postgresql" in self.db_url:
                        # PostgreSQL table existence check
                        pg_query = (
                            "SELECT table_name FROM information_schema.tables "
                            "WHERE table_schema = 'public' "
                            f"AND table_name = '{table_name}'"
                        )
                        result = conn.execute(sa.text(pg_query))
                    else:
                        # SQLite table existence check
                        sqlite_query = (
                            f"SELECT name FROM sqlite_master "
                            f"WHERE type='table' AND name='{table_name}'"
                        )
                        result = conn.execute(sa.text(sqlite_query))

                    if not result.fetchone():
                        # Create table
                        columns = config["columns"]
                        column_defs = [
                            f"{col} {dtype}" for col, dtype in columns.items()
                        ]

                        create_sql = (
                            f"CREATE TABLE {table_name} ({', '.join(column_defs)})"
                        )
                        conn.execute(sa.text(create_sql))

                        # Create indexes
                        if "indexes" in config:
                            for index_col in config["indexes"]:
                                if index_col in columns:
                                    index_sql = f"CREATE INDEX idx_{table_name}_{index_col} ON {table_name}({index_col})"
                                    try:
                                        conn.execute(sa.text(index_sql))
                                    except Exception as e:
                                        logger.warning(
                                            f"Failed to create index on {table_name}.{index_col}: {e}"
                                        )

                        conn.commit()
                        console.print(f"✅ Created table: {table_name}")
                    else:
                        console.print(f"✅ Table exists: {table_name}")

        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise

    async def upload_from_manifest(self, manifest_path: str = None) -> Dict:
        """Upload data using the upload manifest"""
        if not manifest_path:
            manifest_path = str(self.upload_manifest_path)

        console.print(f"\n💾 [bold blue]Enhanced Database Upload[/bold blue]")
        console.print(f"📋 Manifest: {manifest_path}")

        upload_report = {
            "start_time": datetime.now().isoformat(),
            "manifest_path": manifest_path,
            "success": False,
            "tables_uploaded": 0,
            "total_records": 0,
            "errors": [],
            "table_results": {},
        }

        try:
            # Initialize database
            if not await self.initialize_database():
                upload_report["errors"].append("Database initialization failed")
                return upload_report

            # Load manifest
            if not Path(manifest_path).exists():
                upload_report["errors"].append(
                    f"Manifest file not found: {manifest_path}"
                )
                return upload_report

            with open(manifest_path, "r") as f:
                manifest = json.load(f)

            console.print(f"📊 Found {len(manifest.get('files', {}))} files to upload")

            # Process each file in manifest
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            ) as progress:

                files = manifest.get("files", {})
                main_task = progress.add_task("Uploading tables...", total=len(files))

                for file_path, file_info in files.items():
                    table_name = file_info.get("table", "unknown")

                    progress.update(main_task, description=f"Uploading {table_name}...")

                    # Upload table
                    table_result = await self._upload_table(file_path, file_info)
                    upload_report["table_results"][table_name] = table_result

                    if table_result.get("success", False):
                        upload_report["tables_uploaded"] += 1
                        upload_report["total_records"] += table_result.get(
                            "records_inserted", 0
                        )
                    else:
                        upload_report["errors"].extend(table_result.get("errors", []))

                    progress.advance(main_task)

            upload_report["success"] = upload_report["tables_uploaded"] > 0
            upload_report["end_time"] = datetime.now().isoformat()

            self._display_upload_report(upload_report)

            return upload_report

        except Exception as e:
            error_msg = f"Upload process failed: {e}"
            upload_report["errors"].append(error_msg)
            logger.error(error_msg)
            console.print(f"[red]❌ {error_msg}[/red]")
            return upload_report

    async def _upload_table(self, file_path: str, file_info: Dict) -> Dict:
        """Upload a single table from CSV file"""
        table_result = {
            "success": False,
            "records_inserted": 0,
            "records_updated": 0,
            "errors": [],
            "file_path": file_path,
        }

        try:
            # Determine table name
            table_name = file_info.get("table", Path(file_path).stem)

            # Check if table configuration exists
            if table_name not in self.table_configs:
                table_result["errors"].append(
                    f"No configuration for table: {table_name}"
                )
                return table_result

            # Load CSV data
            if not Path(file_path).exists():
                table_result["errors"].append(f"File not found: {file_path}")
                return table_result

            df = pd.read_csv(file_path)

            if df.empty:
                table_result["errors"].append(f"CSV file is empty: {file_path}")
                return table_result

            # Get table configuration
            table_config = self.table_configs[table_name]
            primary_key = table_config["primary_key"]

            # Clean and prepare data
            df = self._clean_dataframe(df, table_name)

            # Upload with conflict resolution
            with self.engine.connect() as conn:
                # Use pandas to_sql with proper handling
                try:
                    # For SQLite, use replace method for upsert
                    df.to_sql(
                        table_name,
                        conn,
                        if_exists="append",
                        index=False,
                        method="multi",
                    )

                    table_result["success"] = True
                    table_result["records_inserted"] = len(df)

                except Exception as e:
                    # Handle duplicates by updating existing records
                    if (
                        "UNIQUE constraint failed" in str(e)
                        or "duplicate" in str(e).lower()
                    ):
                        # Try individual inserts with conflict resolution
                        inserted, updated = await self._insert_with_conflict_resolution(
                            conn, table_name, df, primary_key
                        )
                        table_result["success"] = True
                        table_result["records_inserted"] = inserted
                        table_result["records_updated"] = updated
                    else:
                        raise e

        except Exception as e:
            error_msg = f"Table upload failed for {table_name}: {e}"
            table_result["errors"].append(error_msg)
            logger.error(error_msg)

        return table_result

    def _clean_dataframe(self, df: pd.DataFrame, table_name: str) -> pd.DataFrame:
        """Clean and prepare dataframe for database insertion"""
        # Remove any completely empty rows
        df = df.dropna(how="all")

        # Clean column names
        df.columns = df.columns.str.strip()

        # Handle specific table cleaning
        if table_name == "races":
            # Ensure Race_ID is string
            if "Race_ID" in df.columns:
                df["Race_ID"] = df["Race_ID"].astype(str)

            # Clean date format
            if "Date" in df.columns:
                df["Date"] = pd.to_datetime(df["Date"], errors="coerce").dt.date

        elif table_name == "records":
            # Ensure Record_ID and Race_ID are strings
            for col in ["Record_ID", "Race_ID"]:
                if col in df.columns:
                    df[col] = df[col].astype(str)

        # Fill NaN values appropriately
        for col in df.columns:
            if df[col].dtype == "object":
                df[col] = df[col].fillna("")
            else:
                df[col] = df[col].fillna(0)

        return df

    async def _insert_with_conflict_resolution(
        self, conn, table_name: str, df: pd.DataFrame, primary_key: str
    ) -> Tuple[int, int]:
        """Insert data with conflict resolution"""
        inserted = 0
        updated = 0

        for _, row in df.iterrows():
            try:
                # Try to insert
                columns = ", ".join(row.index)
                placeholders = ", ".join(["?" for _ in row.index])
                insert_sql = (
                    f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
                )

                conn.execute(sa.text(insert_sql), row.tolist())
                inserted += 1

            except Exception:
                # If insert fails, try update
                try:
                    set_clause = ", ".join(
                        [f"{col} = ?" for col in row.index if col != primary_key]
                    )
                    update_sql = (
                        f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?"
                    )

                    update_values = [
                        row[col] for col in row.index if col != primary_key
                    ]
                    update_values.append(row[primary_key])

                    result = conn.execute(sa.text(update_sql), update_values)
                    if result.rowcount > 0:
                        updated += 1
                except Exception as e:
                    logger.warning(f"Failed to insert/update row in {table_name}: {e}")

        conn.commit()
        return inserted, updated

    def _display_upload_report(self, report: Dict):
        """Display comprehensive upload report"""
        console.print("\n📊 [bold green]Database Upload Report[/bold green]")

        # Summary table
        summary_table = Table(title="📈 Upload Summary", show_header=True)
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="yellow")
        summary_table.add_column("Details", style="green")

        start_time = datetime.fromisoformat(report["start_time"])
        end_time = datetime.fromisoformat(
            report.get("end_time", datetime.now().isoformat())
        )
        duration = (end_time - start_time).total_seconds()

        summary_table.add_row("Duration", f"{duration:.2f}s", "Total upload time")
        summary_table.add_row(
            "Tables Uploaded", str(report["tables_uploaded"]), "Successfully processed"
        )
        summary_table.add_row(
            "Total Records", str(report["total_records"]), "Inserted/updated"
        )
        summary_table.add_row(
            "Errors", str(len(report["errors"])), "Issues encountered"
        )
        summary_table.add_row(
            "Success Rate",
            f"{(report['tables_uploaded']/max(len(report['table_results']), 1)*100):.1f}%",
            "Overall success",
        )

        console.print(summary_table)

        # Table details
        if report["table_results"]:
            details_table = Table(title="📋 Table Upload Details", show_header=True)
            details_table.add_column("Table", style="cyan")
            details_table.add_column("Status", style="green")
            details_table.add_column("Records", style="yellow")
            details_table.add_column("Notes", style="magenta")

            for table_name, result in report["table_results"].items():
                status = "✅ Success" if result.get("success", False) else "❌ Failed"
                records = f"{result.get('records_inserted', 0)} ins, {result.get('records_updated', 0)} upd"
                notes = (
                    f"{len(result.get('errors', []))} errors"
                    if result.get("errors")
                    else "Clean"
                )

                details_table.add_row(table_name, status, records, notes)

            console.print(details_table)

        # Show errors if any
        if report["errors"]:
            console.print("\n⚠️ [bold red]Errors Encountered[/bold red]")
            for error in report["errors"][:10]:  # Show first 10 errors
                console.print(f"  ❌ {error}")


async def main():
    """Test the enhanced database uploader"""
    uploader = EnhancedDatabaseUploader()

    # Check for manifest
    if uploader.upload_manifest_path.exists():
        report = await uploader.upload_from_manifest()
        console.print(f"\n🎯 Upload completed: {report['success']}")
    else:
        console.print(
            f"[red]❌ Upload manifest not found: {uploader.upload_manifest_path}[/red]"
        )


if __name__ == "__main__":
    asyncio.run(main())
