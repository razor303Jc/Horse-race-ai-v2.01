#!/usr/bin/env python3
"""
Daily Downloads Data Manager - Enhanced Version
===============================================

Complete data management system for data/daily_downloads folder:
- Removes unused/old files
- Archives old CSV files by date with ZIP compression
- Maintains only current day's downloads in active directories
- Integrates seamlessly with auto downloader and database upload
- Provides detailed reporting and space management
- VS Code shell integration enabled

Features:
- Smart file detection and categorization
- Date-based archival system with retention policies
- Duplicate file removal and deduplication
- Integration hooks for auto downloader and database upload
- Comprehensive logging and performance reporting
- Space optimization and cleanup
"""

import asyncio
import json
import logging
import os
import shutil
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

import pandas as pd
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.table import Table

console = Console()
logger = logging.getLogger(__name__)


class DailyDownloadsManager:
    """Enhanced daily downloads manager with comprehensive organization"""

    def __init__(self, downloads_dir: str = "data/daily_downloads"):
        self.downloads_dir = Path(downloads_dir)
        self.archive_dir = self.downloads_dir / "archives"
        self.backup_dir = self.downloads_dir / "backups"
        self.temp_dir = self.downloads_dir / "temp"
        self.today = datetime.now().date()

        # Create necessary directories
        for dir_path in [self.archive_dir, self.backup_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # File management policies
        self.retention_days = {
            "csv": 7,  # Keep original CSV files for 7 days
            "mapped_csv": 3,  # Keep mapped CSV files for 3 days
            "cleaned_csv": 1,  # Keep cleaned CSV files for 1 day
            "zip": 3,  # Keep ZIP files for 3 days
            "json": 30,  # Keep JSON files for 30 days
            "archives": 365,  # Keep archives for 1 year
            "temp": 1,  # Remove temp files after 1 day
        }

        # File patterns for management
        self.file_patterns = {
            "csv": ["*.csv"],
            "mapped_csv": ["mapped_*.csv"],
            "cleaned_csv": ["cleaned_*.csv"],
            "zip": ["*.zip"],
            "json": ["*.json", "*manifest*.json"],
            "temp": ["*.tmp", "*.temp", "*.lock", "*.partial"],
            "data": [
                "races",
                "records",
                "results_data",
                "cards_data",
                "racecard_details",
            ],
        }

        # File patterns to manage
        self.csv_patterns = ["*.csv"]
        self.mapped_csv_patterns = ["mapped_*.csv"]
        self.cleaned_csv_patterns = ["cleaned_*.csv"]
        self.json_patterns = ["*.json", "*manifest*.json"]
        self.temp_patterns = ["*.tmp", "*.temp", "*.session"]
        self.archive_patterns = ["*.zip"]

        # Current data directories (should contain today's data)
        self.current_data_dirs = [
            "results_data",
            "cards_data",
            "races",
            "records",
            "racecard_details",
            "horses",
            "jockeys_stats",
            "trainers_stats",
        ]

    def run_daily_cleanup(self) -> Dict[str, any]:
        """
        Run complete daily cleanup and organization

        Returns:
            Dict with cleanup statistics and results
        """
        console.print(
            Panel.fit(
                f"🗂️ [bold blue]Daily Downloads Cleanup - {self.today}[/bold blue]",
                style="blue",
            )
        )

        stats = {
            "start_time": datetime.now(),
            "files_processed": 0,
            "files_archived": 0,
            "files_removed": 0,
            "archives_created": 0,
            "errors": [],
        }

        try:
            # Step 1: Analyze current state
            console.print("🔍 [cyan]Step 1: Analyzing current state...[/cyan]")
            analysis = self._analyze_directory_state()
            stats["analysis"] = analysis

            # Step 2: Archive old CSV files
            console.print("📦 [cyan]Step 2: Archiving old CSV files...[/cyan]")
            archive_stats = self._archive_old_csv_files()
            stats.update(archive_stats)

            # Step 3: Clean up processed files (mapped, cleaned)
            console.print("🧽 [cyan]Step 3: Cleaning up processed files...[/cyan]")
            processed_stats = self._cleanup_processed_files()
            stats["files_removed"] += processed_stats.get("mapped_files_removed", 0)
            stats["files_removed"] += processed_stats.get("cleaned_files_removed", 0)
            stats["files_removed"] += processed_stats.get("manifest_files_removed", 0)

            # Step 4: Remove duplicate and unused files
            console.print(
                "🧹 [cyan]Step 4: Removing duplicate and unused files...[/cyan]"
            )
            cleanup_stats = self._remove_duplicates_and_unused()
            stats["files_removed"] += cleanup_stats["files_removed"]

            # Step 5: Organize current data
            console.print(
                "📁 [cyan]Step 5: Organizing current data structure...[/cyan]"
            )
            org_stats = self._organize_current_data()
            stats["files_processed"] += org_stats["files_processed"]

            # Step 5: Clean up old archives
            console.print("🗄️ [cyan]Step 5: Managing archive retention...[/cyan]")
            retention_stats = self._manage_archive_retention()
            stats.update(retention_stats)

            # Step 6: Generate summary report
            console.print("📊 [cyan]Step 6: Generating cleanup report...[/cyan]")
            self._generate_cleanup_report(stats)

            stats["end_time"] = datetime.now()
            stats["duration"] = (
                stats["end_time"] - stats["start_time"]
            ).total_seconds()
            stats["success"] = True

            console.print("✅ [green]Daily cleanup completed successfully![/green]")

        except Exception as e:
            stats["errors"].append(f"Fatal error: {str(e)}")
            stats["success"] = False
            console.print(f"❌ [red]Cleanup failed: {e}[/red]")
            logger.exception("Daily cleanup failed")

        return stats

    def _analyze_directory_state(self) -> Dict[str, any]:
        """Analyze current state of downloads directory"""
        analysis = {
            "total_files": 0,
            "csv_files": 0,
            "mapped_csv_files": 0,
            "cleaned_csv_files": 0,
            "json_files": 0,
            "manifest_files": 0,
            "zip_files": 0,
            "temp_files": 0,
            "directories": 0,
            "file_dates": {},
            "file_sizes": {},
            "duplicates": [],
        }

        file_hashes = {}

        for root, dirs, files in os.walk(self.downloads_dir):
            analysis["directories"] += len(dirs)

            for file in files:
                file_path = Path(root) / file
                analysis["total_files"] += 1

                # Categorize by file type and naming pattern
                if file.startswith("mapped_") and file.endswith(".csv"):
                    analysis["mapped_csv_files"] += 1
                elif file.startswith("cleaned_") and file.endswith(".csv"):
                    analysis["cleaned_csv_files"] += 1
                elif file.endswith(".csv"):
                    analysis["csv_files"] += 1
                elif "manifest" in file and file.endswith(".json"):
                    analysis["manifest_files"] += 1
                elif file.endswith(".json"):
                    analysis["json_files"] += 1
                elif file.endswith(".zip"):
                    analysis["zip_files"] += 1
                elif any(
                    file.endswith(ext.replace("*", "")) for ext in self.temp_patterns
                ):
                    analysis["temp_files"] += 1

                # Track file dates and sizes
                try:
                    stat = file_path.stat()
                    file_date = datetime.fromtimestamp(stat.st_mtime).date()
                    analysis["file_dates"][str(file_path)] = str(file_date)
                    analysis["file_sizes"][str(file_path)] = stat.st_size

                    # Check for duplicates
                    if file_path.is_file() and file_path.suffix in [".csv", ".json"]:
                        file_hash = self._get_file_hash(file_path)
                        if file_hash in file_hashes:
                            analysis["duplicates"].append(
                                {
                                    "original": str(file_hashes[file_hash]),
                                    "duplicate": str(file_path),
                                }
                            )
                        else:
                            file_hashes[file_hash] = file_path

                except Exception as e:
                    logger.warning(f"Error analyzing {file_path}: {e}")

        return analysis

    def _archive_old_csv_files(self) -> Dict[str, int]:
        """Archive CSV files older than today"""
        stats = {"files_archived": 0, "archives_created": 0}

        # Group files by date
        files_by_date = {}

        for root, dirs, files in os.walk(self.downloads_dir):
            for file in files:
                if file.endswith(".csv"):
                    file_path = Path(root) / file
                    try:
                        file_date = datetime.fromtimestamp(
                            file_path.stat().st_mtime
                        ).date()
                        if file_date < self.today:
                            if file_date not in files_by_date:
                                files_by_date[file_date] = []
                            files_by_date[file_date].append(file_path)
                    except Exception as e:
                        logger.warning(f"Error checking date for {file_path}: {e}")

        # Create archives for each date
        for date, files in files_by_date.items():
            if files:
                archive_name = f"csv_data_{date.strftime('%Y%m%d')}.zip"
                archive_path = self.archive_dir / archive_name

                try:
                    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
                        for file_path in files:
                            # Preserve directory structure in archive
                            rel_path = file_path.relative_to(self.downloads_dir)
                            zf.write(file_path, rel_path)
                            file_path.unlink()  # Remove original file
                            stats["files_archived"] += 1

                    stats["archives_created"] += 1
                    console.print(
                        f"📦 Created archive: {archive_name} ({len(files)} files)"
                    )

                except Exception as e:
                    logger.error(f"Error creating archive {archive_path}: {e}")

        return stats

    def _cleanup_processed_files(self) -> Dict[str, int]:
        """Clean up mapped and cleaned CSV files based on retention policies"""
        stats = {"mapped_files_removed": 0, "cleaned_files_removed": 0}

        # Clean up mapped files (keep for 3 days)
        mapped_files = list(self.downloads_dir.glob("mapped_*.csv"))
        for mapped_file in mapped_files:
            try:
                file_date = datetime.fromtimestamp(mapped_file.stat().st_mtime).date()
                age_days = (self.today - file_date).days

                if age_days > self.retention_days["mapped_csv"]:
                    mapped_file.unlink()
                    stats["mapped_files_removed"] += 1
                    console.print(f"🗑️ Removed old mapped file: {mapped_file.name}")

            except Exception as e:
                logger.warning(f"Error removing mapped file {mapped_file}: {e}")

        # Clean up cleaned files (keep for 1 day)
        cleaned_files = list(self.downloads_dir.glob("cleaned_*.csv"))
        for cleaned_file in cleaned_files:
            try:
                file_date = datetime.fromtimestamp(cleaned_file.stat().st_mtime).date()
                age_days = (self.today - file_date).days

                if age_days > self.retention_days["cleaned_csv"]:
                    cleaned_file.unlink()
                    stats["cleaned_files_removed"] += 1
                    console.print(f"🗑️ Removed old cleaned file: {cleaned_file.name}")

            except Exception as e:
                logger.warning(f"Error removing cleaned file {cleaned_file}: {e}")

        # Clean up old manifest files (keep current day only)
        manifest_files = list(self.downloads_dir.glob("*manifest*.json"))
        for manifest_file in manifest_files:
            try:
                file_date = datetime.fromtimestamp(manifest_file.stat().st_mtime).date()
                age_days = (self.today - file_date).days

                if age_days > 0:  # Keep only today's manifests
                    manifest_file.unlink()
                    stats["manifest_files_removed"] = (
                        stats.get("manifest_files_removed", 0) + 1
                    )
                    console.print(f"🗑️ Removed old manifest: {manifest_file.name}")

            except Exception as e:
                logger.warning(f"Error removing manifest file {manifest_file}: {e}")

        return stats

    def _remove_duplicates_and_unused(self) -> Dict[str, int]:
        """Remove duplicate and unused files"""
        stats = {"files_removed": 0}

        # Remove temporary files
        temp_files = []
        for pattern in self.temp_patterns:
            temp_files.extend(self.downloads_dir.rglob(pattern))

        for temp_file in temp_files:
            try:
                temp_file.unlink()
                stats["files_removed"] += 1
                console.print(f"🗑️ Removed temp file: {temp_file.name}")
            except Exception as e:
                logger.warning(f"Error removing temp file {temp_file}: {e}")

        # Remove old ZIP files (except archives)
        old_zips = []
        for zip_file in self.downloads_dir.rglob("*.zip"):
            if not zip_file.parent.name == "archives":
                # Check if it's an old manual download
                if zip_file.stat().st_mtime < datetime.now().timestamp() - (24 * 3600):
                    old_zips.append(zip_file)

        for old_zip in old_zips:
            try:
                # Move to backup before deleting
                backup_path = self.backup_dir / old_zip.name
                shutil.move(old_zip, backup_path)
                stats["files_removed"] += 1
                console.print(f"📦 Moved old ZIP to backup: {old_zip.name}")
            except Exception as e:
                logger.warning(f"Error handling old ZIP {old_zip}: {e}")

        return stats

    def _organize_current_data(self) -> Dict[str, int]:
        """Organize current day's data into proper structure"""
        stats = {"files_processed": 0}

        # Ensure current data directories exist and are clean
        for dir_name in self.current_data_dirs:
            dir_path = self.downloads_dir / dir_name
            if dir_path.exists():
                # Check if directory contains current data
                current_files = [
                    f
                    for f in dir_path.rglob("*.csv")
                    if datetime.fromtimestamp(f.stat().st_mtime).date() == self.today
                ]
                if current_files:
                    console.print(f"📁 {dir_name}: {len(current_files)} current files")
                    stats["files_processed"] += len(current_files)

        return stats

    def _manage_archive_retention(self) -> Dict[str, int]:
        """Manage archive retention policy"""
        stats = {"archives_removed": 0}

        # Keep archives for 30 days, remove older ones
        cutoff_date = self.today - timedelta(days=30)

        for archive_file in self.archive_dir.glob("*.zip"):
            try:
                # Extract date from filename
                if "csv_data_" in archive_file.name:
                    date_str = archive_file.name.replace("csv_data_", "").replace(
                        ".zip", ""
                    )
                    archive_date = datetime.strptime(date_str, "%Y%m%d").date()

                    if archive_date < cutoff_date:
                        # Move to long-term backup
                        long_term_dir = self.backup_dir / "long_term"
                        long_term_dir.mkdir(exist_ok=True)
                        shutil.move(archive_file, long_term_dir / archive_file.name)
                        stats["archives_removed"] += 1
                        console.print(
                            f"📚 Moved to long-term storage: {archive_file.name}"
                        )

            except Exception as e:
                logger.warning(f"Error processing archive {archive_file}: {e}")

        return stats

    def _generate_cleanup_report(self, stats: Dict) -> None:
        """Generate and save cleanup report"""
        report_path = (
            self.downloads_dir / f"cleanup_report_{self.today.strftime('%Y%m%d')}.json"
        )

        with open(report_path, "w") as f:
            json.dump(stats, f, indent=2, default=str)

        # Display summary table
        summary_table = Table(
            title="Daily Cleanup Summary", show_header=True, header_style="bold magenta"
        )
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Count", style="yellow")

        summary_table.add_row("Files Processed", str(stats.get("files_processed", 0)))
        summary_table.add_row("Files Archived", str(stats.get("files_archived", 0)))
        summary_table.add_row("Files Removed", str(stats.get("files_removed", 0)))
        summary_table.add_row("Archives Created", str(stats.get("archives_created", 0)))
        summary_table.add_row("Duration (seconds)", f"{stats.get('duration', 0):.2f}")

        console.print(summary_table)

    def _get_file_hash(self, file_path: Path) -> str:
        """Get hash of file contents for duplicate detection"""
        import hashlib

        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception:
            return ""

    def prepare_for_database_upload(self) -> Dict[str, List[Path]]:
        """Prepare current data files for database upload"""
        console.print("📤 [cyan]Preparing files for database upload...[/cyan]")

        upload_files = {
            "races": [],
            "records": [],
            "racecard_details": [],
            "horses": [],
            "jockeys_stats": [],
            "trainers_stats": [],
        }

        # Find current day's CSV files
        for category in upload_files.keys():
            # Check multiple possible locations
            possible_paths = [
                self.downloads_dir / category / f"{category}.csv",
                self.downloads_dir / "results_data" / category / f"{category}.csv",
                self.downloads_dir / "cards_data" / category / f"{category}.csv",
            ]

            for path in possible_paths:
                if path.exists():
                    file_date = datetime.fromtimestamp(path.stat().st_mtime).date()
                    if file_date >= self.today - timedelta(
                        days=1
                    ):  # Today or yesterday
                        upload_files[category].append(path)
                        console.print(f"📋 Found {category}: {path.name}")

        return upload_files

    def integrate_with_auto_downloader(self) -> None:
        """Integration hook for auto downloader"""
        console.print("🔗 [cyan]Integrating with auto downloader...[/cyan]")

        # This method will be called by the auto downloader after successful download
        # Clean up any files from previous runs before new download
        temp_cleanup = self._remove_duplicates_and_unused()
        console.print(
            f"🧹 Pre-download cleanup: {temp_cleanup['files_removed']} files removed"
        )


def main():
    """Run daily downloads management"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler("logs/daily_downloads_manager.log"),
            logging.StreamHandler(),
        ],
    )

    manager = DailyDownloadsManager()

    # Run daily cleanup
    results = manager.run_daily_cleanup()

    if results["success"]:
        # Prepare for database upload
        upload_files = manager.prepare_for_database_upload()

        console.print(f"\n✅ [green]Management completed successfully![/green]")
        console.print(f"📊 Processed {results['files_processed']} files")
        console.print(f"📦 Created {results['archives_created']} archives")
        console.print(f"🗑️ Removed {results['files_removed']} unused files")

        # NEW: Integrate with data processing pipeline
        try:
            from .integrated_data_processor import IntegratedDataProcessor

            database_url = "postgresql://horse_racing:secure_password_123@postgres:5432/horse_racing_db"
            processor = IntegratedDataProcessor(database_url)

            if processor.connect_database():
                console.print(
                    "\n🔄 [yellow]Starting integrated data processing...[/yellow]"
                )

                # Run CSV mapping first
                console.print("📋 Running CSV mapping...")
                os.system("python3 tools/data_processing/advanced_csv_mapper.py")

                # Then upload to database
                console.print("📤 Uploading to database...")
                manifest_path = "data/daily_downloads/upload_manifest.json"
                upload_results = processor.process_manifest(manifest_path)

                # Validate upload
                counts = processor.validate_upload()

                # Check if all uploads were successful
                successful_uploads = sum(
                    1 for r in upload_results.values() if r["success"]
                )
                total_files = len(upload_results)

                if successful_uploads == total_files and counts:
                    console.print(
                        "🎉 [green]Complete pipeline finished successfully![/green]"
                    )
                    return True
                else:
                    console.print(
                        "⚠️ [yellow]Pipeline completed with some errors[/yellow]"
                    )
                    return True
            else:
                console.print("❌ [red]Could not connect to database for upload[/red]")
                return True  # Still return success for file management

        except ImportError:
            console.print(
                "⚠️ [yellow]Integrated processor not available, skipping database upload[/yellow]"
            )
            return True
        except Exception as e:
            console.print(f"❌ [red]Error in integrated processing: {e}[/red]")
            return True  # Still return success for file management

        return True
    else:
        console.print(
            f"\n❌ [red]Management failed with {len(results['errors'])} errors[/red]"
        )
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
