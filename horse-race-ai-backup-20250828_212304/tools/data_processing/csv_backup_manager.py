#!/usr/bin/env python3
"""
CSV Backup Manager - Enhanced Raw Data Archival
==============================================

Creates backup archives of raw CSV files after ZIP extraction.
Maintains both original ZIP archive and separate CSV backups.

Author: AI Assistant
Date: August 24, 2025
"""

import json
import logging
import shutil
import sqlite3
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
from rich.console import Console
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class CSVBackupManager:
    """
    Manages backup and archival of raw CSV files extracted from ZIP downloads

    Uses SQLite3 for backup tracking and metadata storage.
    Note: SQLite3 is ONLY for backup tracking - all horse racing data
    remains in PostgreSQL docker containers.
    """

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.downloads_dir = self.base_path / "data/daily_downloads"
        self.backup_dir = self.downloads_dir / "backups"
        self.raw_csv_backup_dir = self.backup_dir / "raw_csv_archives"

        # SQLite database for backup tracking ONLY (not horse racing data)
        self.backup_db_path = self.backup_dir / "backup_tracking.db"

        # Create backup directories
        self.raw_csv_backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SQLite tracking database
        self._init_backup_database()

        # Working directories for extracted CSV files
        self.cards_dir = self.downloads_dir / "cards_data"
        self.results_dir = self.downloads_dir / "results_data"

    def _init_backup_database(self):
        """
        Initialize SQLite database for backup tracking
        Note: This SQLite DB is ONLY for backup metadata - NOT horse racing data
        """
        with sqlite3.connect(self.backup_db_path) as conn:
            cursor = conn.cursor()

            # Create backup tracking table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS backup_archives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    archive_name TEXT NOT NULL,
                    archive_path TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    file_date TEXT NOT NULL,
                    original_zip_name TEXT NOT NULL,
                    created_timestamp TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    csv_files_count INTEGER NOT NULL,
                    detected_date TEXT,
                    first_race_time TEXT,
                    last_race_time TEXT,
                    total_races INTEGER,
                    courses TEXT,
                    status TEXT DEFAULT 'active',
                    notes TEXT
                )
            """
            )

            # Create CSV files tracking table
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS backup_csv_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    backup_id INTEGER NOT NULL,
                    filename TEXT NOT NULL,
                    relative_path TEXT NOT NULL,
                    size_bytes INTEGER NOT NULL,
                    records_count INTEGER,
                    columns_list TEXT,
                    date_values TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_archives (id)
                )
            """
            )

            # Create backup operations log
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS backup_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation_type TEXT NOT NULL,
                    backup_id INTEGER,
                    timestamp TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    error_message TEXT,
                    FOREIGN KEY (backup_id) REFERENCES backup_archives (id)
                )
            """
            )

            conn.commit()
            logger.info("Backup tracking database initialized: %s", self.backup_db_path)

    def extract_and_backup_zip(
        self, zip_path: Path, data_type: str, target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Extract ZIP file and create backup of raw CSV files"""
        result = {
            "success": False,
            "zip_extracted": False,
            "csv_backup_created": False,
            "csv_files_count": 0,
            "backup_archive_path": None,
            "extraction_path": None,
            "errors": [],
            "warnings": [],
            "file_analysis": {},
        }

        try:
            # Determine extraction directory
            if data_type.lower() == "cards":
                extract_dir = self.cards_dir
            elif data_type.lower() == "results":
                extract_dir = self.results_dir
            else:
                result["errors"].append(f"Unknown data type: {data_type}")
                return result

            # Clear and recreate extraction directory
            if extract_dir.exists():
                shutil.rmtree(extract_dir)
            extract_dir.mkdir(parents=True, exist_ok=True)

            # Extract ZIP file
            console.print(f"📦 Extracting {zip_path.name} to {extract_dir.name}/")

            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

            result["zip_extracted"] = True
            result["extraction_path"] = str(extract_dir)

            # Find all CSV files in extracted directory
            csv_files = self._find_csv_files(extract_dir)
            result["csv_files_count"] = len(csv_files)

            if not csv_files:
                result["warnings"].append("No CSV files found in extracted ZIP")
                return result

            # Analyze CSV files for date validation
            file_analysis = self._analyze_csv_files(csv_files, target_date)
            result["file_analysis"] = file_analysis

            # Store file analysis for database recording
            self._current_file_analysis = file_analysis

            # Create CSV backup archive
            backup_result = self._create_csv_backup(
                csv_files,
                data_type,
                zip_path.name,
                target_date or file_analysis.get("detected_date", "unknown"),
            )

            if backup_result["success"]:
                result["csv_backup_created"] = True
                result["backup_archive_path"] = backup_result["archive_path"]
                console.print(f"✅ CSV backup: {backup_result['archive_name']}")
            else:
                result["errors"].extend(backup_result["errors"])

            result["success"] = result["zip_extracted"] and result["csv_backup_created"]

        except (zipfile.BadZipFile, FileNotFoundError, PermissionError) as e:
            error_msg = f"Failed to extract and backup {zip_path.name}: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)

        return result

    def _find_csv_files(self, directory: Path) -> List[Path]:
        """Recursively find all CSV files in directory"""
        return sorted([item for item in directory.rglob("*.csv") if item.is_file()])

    def _analyze_csv_files(
        self, csv_files: List[Path], target_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze CSV files for date information and content validation"""
        analysis = {
            "total_files": len(csv_files),
            "files_analyzed": 0,
            "detected_date": None,
            "date_consistency": True,
            "first_race_time": None,
            "last_race_time": None,
            "total_races": 0,
            "courses": [],
            "file_details": [],
        }

        race_times = []
        all_dates = set()
        courses = set()
        total_races = 0

        for csv_file in csv_files:
            try:
                if "race" in csv_file.name.lower():
                    df = pd.read_csv(csv_file)
                    analysis["files_analyzed"] += 1

                    file_detail = {
                        "filename": csv_file.name,
                        "path": str(csv_file.relative_to(csv_file.parents[2])),
                        "records": len(df),
                        "columns": list(df.columns),
                    }

                    if "Date" in df.columns:
                        dates_in_file = set(df["Date"].dropna().unique())
                        all_dates.update(dates_in_file)
                        file_detail["dates"] = list(dates_in_file)

                    if "race_time" in df.columns:
                        times = df["race_time"].dropna().tolist()
                        race_times.extend(times)
                        file_detail["race_times"] = times

                    if "Course" in df.columns:
                        file_courses = set(df["Course"].dropna().unique())
                        courses.update(file_courses)
                        file_detail["courses"] = list(file_courses)

                    total_races += len(df)
                    analysis["file_details"].append(file_detail)

            except (
                pd.errors.EmptyDataError,
                pd.errors.ParserError,
                UnicodeDecodeError,
            ) as e:
                logger.warning("Could not analyze %s: %s", csv_file, e)

        if all_dates:
            if len(all_dates) == 1:
                analysis["detected_date"] = list(all_dates)[0]
                analysis["date_consistency"] = True
            else:
                analysis["detected_date"] = sorted(all_dates)[-1]
                analysis["date_consistency"] = False

        if race_times:
            try:
                time_objects = []
                for time_str in race_times:
                    try:
                        time_obj = datetime.strptime(time_str, "%H:%M")
                        time_objects.append(time_obj)
                    except ValueError:
                        continue

                if time_objects:
                    time_objects.sort()
                    analysis["first_race_time"] = time_objects[0].strftime("%H:%M")
                    analysis["last_race_time"] = time_objects[-1].strftime("%H:%M")
            except (ValueError, TypeError) as e:
                logger.warning("Error analyzing race times: %s", e)

        analysis["total_races"] = total_races
        analysis["courses"] = sorted(list(courses))
        return analysis

    def _create_csv_backup(
        self,
        csv_files: List[Path],
        data_type: str,
        original_zip_name: str,
        file_date: str,
    ) -> Dict[str, Any]:
        """Create a backup archive of raw CSV files"""
        result = {
            "success": False,
            "archive_path": None,
            "archive_name": None,
            "files_archived": 0,
            "errors": [],
        }

        try:
            backup_date_dir = self.raw_csv_backup_dir / file_date
            backup_date_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%H%M%S")
            archive_name = f"raw_csv_{data_type}_{file_date}_{timestamp}.zip"
            archive_path = backup_date_dir / archive_name

            with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as backup_zip:
                metadata = {
                    "backup_created": datetime.now().isoformat(),
                    "original_zip": original_zip_name,
                    "data_type": data_type,
                    "file_date": file_date,
                    "csv_files_count": len(csv_files),
                    "csv_files": [],
                }

                for csv_file in csv_files:
                    try:
                        base_extract_dir = csv_file.parents[1]
                        rel_path = csv_file.relative_to(base_extract_dir)
                        backup_zip.write(csv_file, rel_path)
                        result["files_archived"] += 1

                        metadata["csv_files"].append(
                            {
                                "filename": csv_file.name,
                                "path": str(rel_path),
                                "size_bytes": csv_file.stat().st_size,
                            }
                        )

                    except (OSError, ValueError) as e:
                        error_msg = f"Failed to add {csv_file} to backup: {e}"
                        result["errors"].append(error_msg)
                        logger.warning(error_msg)

                backup_zip.writestr(
                    "backup_metadata.json", json.dumps(metadata, indent=2)
                )

            result["success"] = True
            result["archive_path"] = str(archive_path)
            result["archive_name"] = archive_name

            # Record backup in SQLite tracking database
            self._record_backup_in_database(
                archive_name,
                archive_path,
                data_type,
                file_date,
                original_zip_name,
                metadata,
                csv_files,
            )

            logger.info(
                "Created CSV backup: %s (%d files)",
                archive_name,
                result["files_archived"],
            )

        except (zipfile.BadZipFile, OSError, PermissionError) as e:
            error_msg = f"Failed to create CSV backup: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)

        return result

    def _record_backup_in_database(
        self,
        archive_name: str,
        archive_path: Path,
        data_type: str,
        file_date: str,
        original_zip_name: str,
        metadata: Dict,
        csv_files: List[Path],
    ):
        """
        Record backup information in SQLite tracking database
        Note: SQLite is ONLY for backup tracking - NOT horse racing data
        """
        try:
            with sqlite3.connect(self.backup_db_path) as conn:
                cursor = conn.cursor()

                # Get file analysis from the current extraction
                file_analysis = getattr(self, "_current_file_analysis", {})

                # Insert backup archive record
                cursor.execute(
                    """
                    INSERT INTO backup_archives (
                        archive_name, archive_path, data_type, file_date,
                        original_zip_name, created_timestamp, size_bytes,
                        csv_files_count, detected_date, first_race_time,
                        last_race_time, total_races, courses
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        archive_name,
                        str(archive_path),
                        data_type,
                        file_date,
                        original_zip_name,
                        datetime.now().isoformat(),
                        archive_path.stat().st_size,
                        len(csv_files),
                        file_analysis.get("detected_date"),
                        file_analysis.get("first_race_time"),
                        file_analysis.get("last_race_time"),
                        file_analysis.get("total_races", 0),
                        json.dumps(file_analysis.get("courses", [])),
                    ),
                )

                backup_id = cursor.lastrowid

                # Insert CSV file records
                for csv_file_info in metadata.get("csv_files", []):
                    # Try to get additional info from file analysis
                    file_detail = None
                    for detail in file_analysis.get("file_details", []):
                        if detail.get("filename") == csv_file_info["filename"]:
                            file_detail = detail
                            break

                    cursor.execute(
                        """
                        INSERT INTO backup_csv_files (
                            backup_id, filename, relative_path, size_bytes,
                            records_count, columns_list, date_values
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                        (
                            backup_id,
                            csv_file_info["filename"],
                            csv_file_info["path"],
                            csv_file_info["size_bytes"],
                            file_detail.get("records") if file_detail else None,
                            (
                                json.dumps(file_detail.get("columns", []))
                                if file_detail
                                else None
                            ),
                            (
                                json.dumps(file_detail.get("dates", []))
                                if file_detail
                                else None
                            ),
                        ),
                    )

                # Log the operation
                cursor.execute(
                    """
                    INSERT INTO backup_operations (
                        operation_type, backup_id, timestamp, status, details
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        "create_backup",
                        backup_id,
                        datetime.now().isoformat(),
                        "success",
                        f"Created backup archive with {len(csv_files)} CSV files",
                    ),
                )

                conn.commit()
                logger.info("Recorded backup in tracking database: %s", archive_name)

        except sqlite3.Error as e:
            logger.error("Failed to record backup in database: %s", e)

    def list_csv_backups(
        self, data_type: Optional[str] = None, date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List available CSV backups with metadata from SQLite database"""
        backups = []

        try:
            with sqlite3.connect(self.backup_db_path) as conn:
                cursor = conn.cursor()

                # Build query with optional filters
                query = """
                    SELECT 
                        id, archive_name, archive_path, data_type, file_date,
                        original_zip_name, created_timestamp, size_bytes,
                        csv_files_count, detected_date, first_race_time,
                        last_race_time, total_races, courses, status
                    FROM backup_archives 
                    WHERE status = 'active'
                """
                params = []

                if data_type:
                    query += " AND data_type = ?"
                    params.append(data_type)

                if date:
                    query += " AND file_date = ?"
                    params.append(date)

                query += " ORDER BY created_timestamp DESC"

                cursor.execute(query, params)
                rows = cursor.fetchall()

                for row in rows:
                    # Convert row to dictionary
                    backup_info = {
                        "id": row[0],
                        "archive_name": row[1],
                        "archive_path": row[2],
                        "data_type": row[3],
                        "date": row[4],
                        "original_zip": row[5],
                        "backup_created": row[6],
                        "size_mb": round(row[7] / (1024 * 1024), 2),
                        "csv_files_count": row[8],
                        "detected_date": row[9],
                        "first_race_time": row[10],
                        "last_race_time": row[11],
                        "total_races": row[12] or 0,
                        "courses": json.loads(row[13]) if row[13] else [],
                        "status": row[14],
                    }

                    # Check if archive file still exists
                    archive_path = Path(backup_info["archive_path"])
                    if archive_path.exists():
                        # Update size in case file size changed
                        actual_size = archive_path.stat().st_size
                        backup_info["size_mb"] = round(actual_size / (1024 * 1024), 2)
                        backups.append(backup_info)
                    else:
                        # Mark as missing in database
                        self._mark_backup_missing(backup_info["id"])

        except sqlite3.Error as e:
            logger.error("Failed to query backup database: %s", e)
            # Fallback to filesystem scanning if database fails
            return self._list_backups_from_filesystem(data_type, date)

        return backups

    def _mark_backup_missing(self, backup_id: int):
        """Mark a backup as missing in the database"""
        try:
            with sqlite3.connect(self.backup_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "UPDATE backup_archives SET status = 'missing' WHERE id = ?",
                    (backup_id,),
                )
                cursor.execute(
                    """
                    INSERT INTO backup_operations (
                        operation_type, backup_id, timestamp, status, details
                    ) VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        "mark_missing",
                        backup_id,
                        datetime.now().isoformat(),
                        "warning",
                        "Archive file no longer exists on filesystem",
                    ),
                )
                conn.commit()
        except sqlite3.Error as e:
            logger.error("Failed to mark backup as missing: %s", e)

    def _list_backups_from_filesystem(
        self, data_type: Optional[str] = None, date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Fallback method to list backups from filesystem when SQLite fails"""
        backups = []
        search_dirs = []

        if date:
            date_dir = self.raw_csv_backup_dir / date
            if date_dir.exists():
                search_dirs.append(date_dir)
        else:
            search_dirs = [d for d in self.raw_csv_backup_dir.iterdir() if d.is_dir()]

        for date_dir in search_dirs:
            for backup_file in date_dir.glob("raw_csv_*.zip"):
                try:
                    with zipfile.ZipFile(backup_file, "r") as backup_zip:
                        if "backup_metadata.json" in backup_zip.namelist():
                            metadata_str = backup_zip.read(
                                "backup_metadata.json"
                            ).decode("utf-8")
                            metadata = json.loads(metadata_str)

                            if data_type and metadata.get("data_type") != data_type:
                                continue

                            backup_info = {
                                "archive_path": str(backup_file),
                                "archive_name": backup_file.name,
                                "date": date_dir.name,
                                "size_mb": round(
                                    backup_file.stat().st_size / (1024 * 1024), 2
                                ),
                                **metadata,
                            }
                            backups.append(backup_info)

                except (
                    zipfile.BadZipFile,
                    json.JSONDecodeError,
                    UnicodeDecodeError,
                ) as e:
                    logger.warning(
                        "Could not read metadata from %s: %s", backup_file, e
                    )

        return sorted(backups, key=lambda x: x.get("backup_created", ""), reverse=True)

    def cleanup_old_backups(self, days_to_keep: int = 30) -> Dict[str, Any]:
        """Clean up CSV backups older than specified days using SQLite tracking"""
        result = {"backups_removed": 0, "space_freed_mb": 0, "errors": []}
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        cutoff_str = cutoff_date.isoformat()

        try:
            with sqlite3.connect(self.backup_db_path) as conn:
                cursor = conn.cursor()

                # Find old backups
                cursor.execute(
                    """
                    SELECT id, archive_path, size_bytes 
                    FROM backup_archives 
                    WHERE created_timestamp < ? AND status = 'active'
                """,
                    (cutoff_str,),
                )

                old_backups = cursor.fetchall()

                for backup_id, archive_path, size_bytes in old_backups:
                    try:
                        archive_file = Path(archive_path)
                        if archive_file.exists():
                            archive_file.unlink()

                        # Mark as deleted in database
                        cursor.execute(
                            "UPDATE backup_archives SET status = 'deleted' WHERE id = ?",
                            (backup_id,),
                        )

                        # Log the operation
                        cursor.execute(
                            """
                            INSERT INTO backup_operations (
                                operation_type, backup_id, timestamp, status, details
                            ) VALUES (?, ?, ?, ?, ?)
                        """,
                            (
                                "cleanup",
                                backup_id,
                                datetime.now().isoformat(),
                                "success",
                                f"Deleted backup older than {days_to_keep} days",
                            ),
                        )

                        result["backups_removed"] += 1
                        result["space_freed_mb"] += round(size_bytes / (1024 * 1024), 2)

                    except OSError as e:
                        error_msg = f"Error deleting {archive_path}: {e}"
                        result["errors"].append(error_msg)
                        logger.warning(error_msg)

                conn.commit()

        except sqlite3.Error as e:
            error_msg = f"Database error during cleanup: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)

        return result

    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get comprehensive backup statistics from SQLite database"""
        stats = {
            "total_backups": 0,
            "active_backups": 0,
            "missing_backups": 0,
            "deleted_backups": 0,
            "total_size_mb": 0,
            "by_data_type": {},
            "by_date": {},
            "oldest_backup": None,
            "newest_backup": None,
        }

        try:
            with sqlite3.connect(self.backup_db_path) as conn:
                cursor = conn.cursor()

                # Overall statistics
                cursor.execute(
                    """
                    SELECT 
                        status,
                        COUNT(*) as count,
                        SUM(size_bytes) as total_size
                    FROM backup_archives 
                    GROUP BY status
                """
                )

                for status, count, total_size in cursor.fetchall():
                    if status == "active":
                        stats["active_backups"] = count
                        stats["total_size_mb"] = round(
                            (total_size or 0) / (1024 * 1024), 2
                        )
                    elif status == "missing":
                        stats["missing_backups"] = count
                    elif status == "deleted":
                        stats["deleted_backups"] = count

                    stats["total_backups"] += count

                # By data type
                cursor.execute(
                    """
                    SELECT data_type, COUNT(*), SUM(size_bytes)
                    FROM backup_archives 
                    WHERE status = 'active'
                    GROUP BY data_type
                """
                )

                for data_type, count, total_size in cursor.fetchall():
                    stats["by_data_type"][data_type] = {
                        "count": count,
                        "size_mb": round((total_size or 0) / (1024 * 1024), 2),
                    }

                # By date
                cursor.execute(
                    """
                    SELECT file_date, COUNT(*), SUM(size_bytes)
                    FROM backup_archives 
                    WHERE status = 'active'
                    GROUP BY file_date
                    ORDER BY file_date DESC
                """
                )

                for file_date, count, total_size in cursor.fetchall():
                    stats["by_date"][file_date] = {
                        "count": count,
                        "size_mb": round((total_size or 0) / (1024 * 1024), 2),
                    }

                # Date range
                cursor.execute(
                    """
                    SELECT MIN(created_timestamp), MAX(created_timestamp)
                    FROM backup_archives 
                    WHERE status = 'active'
                """
                )

                oldest, newest = cursor.fetchone()
                stats["oldest_backup"] = oldest
                stats["newest_backup"] = newest

        except sqlite3.Error as e:
            logger.error("Failed to get backup statistics: %s", e)

        return stats

    def display_backup_status(self):
        """Display backup status with rich formatting using SQLite statistics"""
        console.print("\n" + "=" * 70)
        console.print(
            "📦 CSV BACKUP MANAGER STATUS (SQLite Tracked)",
            style="bold blue",
            justify="center",
        )
        console.print("=" * 70)

        # Get statistics from SQLite database
        stats = self.get_backup_statistics()

        if stats["active_backups"] == 0:
            console.print("📭 No active CSV backups found", style="yellow")
            return

        table = Table(title="Backup Summary (SQLite Tracked)")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Active Archives", str(stats["active_backups"]))
        table.add_row("Total Size", f"{stats['total_size_mb']:.1f} MB")
        table.add_row("Backup Dates", str(len(stats["by_date"])))

        if stats["missing_backups"] > 0:
            table.add_row("Missing Files", str(stats["missing_backups"]), style="red")

        if stats["deleted_backups"] > 0:
            table.add_row("Deleted Archives", str(stats["deleted_backups"]))

        if stats["oldest_backup"] and stats["newest_backup"]:
            table.add_row("Oldest Backup", stats["oldest_backup"][:19])
            table.add_row("Newest Backup", stats["newest_backup"][:19])

        console.print(table)

        # Show breakdown by data type
        if stats["by_data_type"]:
            console.print("\n📊 By Data Type:")
            for data_type, type_stats in stats["by_data_type"].items():
                console.print(
                    f"  • {data_type}: {type_stats['count']} archives "
                    f"({type_stats['size_mb']:.1f} MB)"
                )

        # Show recent backups
        recent_backups = self.list_csv_backups()[:5]
        if recent_backups:
            console.print("\n📅 Recent Backups:")
            for backup in recent_backups:
                console.print(
                    f"  • {backup['archive_name']} " f"({backup['size_mb']:.1f} MB)"
                )

        # Show database info
        console.print(f"\n🗄️ Backup Database: {self.backup_db_path}")
        console.print(f"📁 Archive Directory: {self.raw_csv_backup_dir}")


def main():
    """CLI interface for CSV Backup Manager"""
    import sys

    manager = CSVBackupManager()

    if len(sys.argv) < 2:
        manager.display_backup_status()
        return

    command = sys.argv[1].lower()

    if command == "status":
        manager.display_backup_status()
    elif command == "list":
        data_type = sys.argv[2] if len(sys.argv) > 2 else None
        backups = manager.list_csv_backups(data_type=data_type)
        title = f"\n📋 CSV Backups{f' ({data_type})' if data_type else ''}:"
        console.print(title)
        for backup in backups[:10]:
            console.print(
                f"  • {backup['archive_name']} " f"({backup['size_mb']:.1f} MB)"
            )
    elif command == "cleanup":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
        result = manager.cleanup_old_backups(days_to_keep=days)
        console.print(f"🗑️ Cleaned up {result['backups_removed']} old backups")
        console.print(f"💾 Freed {result['space_freed_mb']:.1f} MB of space")
    else:
        console.print(
            "Usage: python csv_backup_manager.py " "[status|list|cleanup] [options]"
        )


if __name__ == "__main__":
    main()
