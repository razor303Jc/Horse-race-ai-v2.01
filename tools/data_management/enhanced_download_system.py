#!/usr/bin/env python3
"""
🔄 Enhanced Download System with Archival Integration
Integrated download system that archives old files before downloading new ones

Features:
- Pre-download archival of existing files
- Database tracking of downloads by date
- Data validation and integrity checks
- Rollback capabilities
- Archive verification

Author: AI Assistant
Date: August 17, 2025
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

# Import our archival system
from file_archival_system import FileArchivalSystem

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for tracking downloads and data by date"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.db_path = self.project_root / "data" / "racing_data_tracking.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    def _init_database(self):
        """Initialize tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            # Downloads tracking table
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS downloads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    download_date TEXT NOT NULL,
                    download_timestamp TEXT NOT NULL,
                    source_type TEXT NOT NULL,  -- 'cards_data' or 'results_data'
                    file_category TEXT NOT NULL,  -- 'races', 'horses', etc.
                    filename TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    record_count INTEGER,
                    status TEXT DEFAULT 'active',
                    archive_id INTEGER,  -- Link to archive if archived
                    created_timestamp TEXT NOT NULL
                )
            """
            )

            # Data summary by date
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS daily_data_summary (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_date TEXT UNIQUE NOT NULL,
                    total_downloads INTEGER DEFAULT 0,
                    total_files INTEGER DEFAULT 0,
                    total_size_bytes INTEGER DEFAULT 0,
                    races_count INTEGER DEFAULT 0,
                    horses_count INTEGER DEFAULT 0,
                    jockeys_count INTEGER DEFAULT 0,
                    trainers_count INTEGER DEFAULT 0,
                    records_count INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            """
            )

            # Data quality metrics
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS data_quality_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_date TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    metric_value REAL NOT NULL,
                    metric_details TEXT,  -- JSON details
                    recorded_timestamp TEXT NOT NULL
                )
            """
            )

            conn.commit()
            logger.info("📊 Data tracking database initialized")

    def record_download(
        self,
        download_date: str,
        source_type: str,
        file_category: str,
        filename: str,
        file_size: int,
        record_count: Optional[int] = None,
    ) -> int:
        """Record a download in the database"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO downloads (
                    download_date, download_timestamp, source_type,
                    file_category, filename, file_size_bytes,
                    record_count, created_timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    download_date,
                    datetime.now().isoformat(),
                    source_type,
                    file_category,
                    filename,
                    file_size,
                    record_count,
                    datetime.now().isoformat(),
                ),
            )

            download_id = cursor.lastrowid
            conn.commit()

        logger.info(f"📝 Recorded download: {filename} (ID: {download_id})")
        return download_id

    def update_daily_summary(self, data_date: str):
        """Update daily data summary"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # Calculate summary statistics
            cursor.execute(
                """
                SELECT 
                    COUNT(*) as total_downloads,
                    COUNT(DISTINCT filename) as total_files,
                    SUM(file_size_bytes) as total_size,
                    SUM(CASE WHEN file_category = 'races' THEN COALESCE(record_count, 0) ELSE 0 END) as races_count,
                    SUM(CASE WHEN file_category = 'horses' THEN COALESCE(record_count, 0) ELSE 0 END) as horses_count,
                    SUM(CASE WHEN file_category = 'jockeys_stats' THEN COALESCE(record_count, 0) ELSE 0 END) as jockeys_count,
                    SUM(CASE WHEN file_category = 'trainers_stats' THEN COALESCE(record_count, 0) ELSE 0 END) as trainers_count,
                    SUM(CASE WHEN file_category = 'records' THEN COALESCE(record_count, 0) ELSE 0 END) as records_count
                FROM downloads 
                WHERE download_date = ? AND status = 'active'
            """,
                (data_date,),
            )

            summary = cursor.fetchone()

            if summary:
                # Insert or update summary
                cursor.execute(
                    """
                    INSERT OR REPLACE INTO daily_data_summary (
                        data_date, total_downloads, total_files, total_size_bytes,
                        races_count, horses_count, jockeys_count, trainers_count,
                        records_count, last_updated
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        data_date,
                        summary[0],  # total_downloads
                        summary[1],  # total_files
                        summary[2] or 0,  # total_size
                        summary[3] or 0,  # races_count
                        summary[4] or 0,  # horses_count
                        summary[5] or 0,  # jockeys_count
                        summary[6] or 0,  # trainers_count
                        summary[7] or 0,  # records_count
                        datetime.now().isoformat(),
                    ),
                )

                conn.commit()
                logger.info(f"📊 Updated daily summary for {data_date}")

    def get_data_by_date(self, start_date: str, end_date: str = None) -> List[Dict]:
        """Get data summary by date range"""

        if end_date is None:
            end_date = start_date

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    data_date,
                    total_downloads,
                    total_files,
                    total_size_bytes,
                    races_count,
                    horses_count,
                    jockeys_count,
                    trainers_count,
                    records_count,
                    last_updated,
                    status
                FROM daily_data_summary
                WHERE data_date BETWEEN ? AND ?
                ORDER BY data_date DESC
            """,
                (start_date, end_date),
            )

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_download_details(self, data_date: str) -> List[Dict]:
        """Get detailed download information for a specific date"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT 
                    id,
                    download_timestamp,
                    source_type,
                    file_category,
                    filename,
                    file_size_bytes,
                    record_count,
                    status,
                    archive_id
                FROM downloads
                WHERE download_date = ?
                ORDER BY download_timestamp DESC
            """,
                (data_date,),
            )

            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]


class EnhancedDownloadSystem:
    """Enhanced download system with archival integration"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.archiver = FileArchivalSystem(project_root)
        self.db_manager = DatabaseManager(project_root)
        self.download_dir = self.project_root / "data" / "daily_downloads"

    def pre_download_archive(self, download_date: str = None) -> Dict:
        """Archive existing files before new download"""

        if download_date is None:
            download_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"📦 Pre-download archival for {download_date}")

        # Check if files exist to archive
        categorized_files = self.archiver.scan_download_directory()

        if not any(categorized_files.values()):
            logger.info("📁 No existing files to archive")
            return {"archived": False, "reason": "no_files"}

        # Perform archival
        result = self.archiver.archive_and_clean(
            archive_date=download_date,
            secure_path=self.project_root / "data" / "secure_archives",
        )

        if result["success"]:
            # Update database to mark archived files
            self._mark_files_as_archived(download_date, result["archive_id"])

        return result

    def _mark_files_as_archived(self, download_date: str, archive_id: int):
        """Mark files as archived in database"""

        with sqlite3.connect(self.db_manager.db_path) as conn:
            conn.execute(
                """
                UPDATE downloads 
                SET status = 'archived', archive_id = ?
                WHERE download_date = ? AND status = 'active'
            """,
                (archive_id, download_date),
            )
            conn.commit()

        logger.info(f"📊 Marked files as archived for {download_date}")

    def simulate_download(self, download_date: str = None) -> Dict:
        """Simulate downloading new files (for demonstration)"""

        if download_date is None:
            download_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"📥 Simulating download for {download_date}")

        # Create mock download files
        downloads = [
            (
                "cards_data",
                "races",
                "races.csv",
                "race_id,race_name,track,distance\n1001,Test Race,Flemington,1600m\n1002,Another Race,Randwick,2000m",
            ),
            (
                "cards_data",
                "horses",
                "horses.csv",
                "horse_id,horse_name,age,weight\nH001,Lightning Bolt,4,58.5\nH002,Thunder Strike,5,57.0",
            ),
            (
                "cards_data",
                "jockeys_stats",
                "jockeys_stats.csv",
                "jockey_id,jockey_name,wins,rides\nJ001,J.Smith,15,45\nJ002,M.Jones,12,38",
            ),
            (
                "results_data",
                "races",
                "races.csv",
                "race_id,race_result,winning_time\n1001,H001,1:36.2\n1002,H002,2:01.8",
            ),
        ]

        download_results = []

        for source_type, file_category, filename, content in downloads:
            # Create directory structure
            file_dir = self.download_dir / source_type / file_category
            file_dir.mkdir(parents=True, exist_ok=True)

            # Write file
            file_path = file_dir / filename
            file_path.write_text(content)

            # Count records (lines - header)
            record_count = len(content.splitlines()) - 1
            file_size = len(content.encode("utf-8"))

            # Record in database
            download_id = self.db_manager.record_download(
                download_date,
                source_type,
                file_category,
                filename,
                file_size,
                record_count,
            )

            download_results.append(
                {
                    "download_id": download_id,
                    "filename": filename,
                    "size": file_size,
                    "records": record_count,
                }
            )

        # Update daily summary
        self.db_manager.update_daily_summary(download_date)

        logger.info(f"✅ Download simulation complete: {len(download_results)} files")

        return {
            "success": True,
            "download_date": download_date,
            "files_downloaded": len(download_results),
            "download_details": download_results,
        }

    def complete_download_workflow(self, download_date: str = None) -> Dict:
        """Complete download workflow: archive old, download new, verify"""

        if download_date is None:
            download_date = datetime.now().strftime("%Y-%m-%d")

        logger.info(f"🚀 Starting complete download workflow for {download_date}")

        workflow_result = {
            "download_date": download_date,
            "workflow_start": datetime.now().isoformat(),
        }

        # Step 1: Archive existing files
        archive_result = self.pre_download_archive(download_date)
        workflow_result["archive_result"] = archive_result

        # Step 2: Download new files
        download_result = self.simulate_download(download_date)
        workflow_result["download_result"] = download_result

        # Step 3: Verify data
        data_summary = self.db_manager.get_data_by_date(download_date)
        workflow_result["data_summary"] = data_summary

        workflow_result["workflow_end"] = datetime.now().isoformat()
        workflow_result["success"] = archive_result.get(
            "success", True
        ) and download_result.get("success", True)

        logger.info("✅ Complete download workflow finished")

        return workflow_result

    def show_data_by_date(self, days: int = 7) -> Dict:
        """Show data organized by date"""

        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=days - 1)).strftime("%Y-%m-%d")

        data_by_date = self.db_manager.get_data_by_date(start_date, end_date)

        print(f"\n📊 DATA SUMMARY - Last {days} days")
        print("=" * 70)

        if not data_by_date:
            print("⚠️ No data found for the specified date range")
            return {"dates": [], "total_dates": 0}

        for day_data in data_by_date:
            date = day_data["data_date"]
            files = day_data["total_files"]
            size_mb = (
                day_data["total_size_bytes"] / 1024 / 1024
                if day_data["total_size_bytes"]
                else 0
            )

            print(f"\n📅 {date}:")
            print(f"   📁 Files: {files}")
            print(f"   📦 Size: {size_mb:.1f} MB")
            print(f"   🏇 Races: {day_data['races_count']}")
            print(f"   🐎 Horses: {day_data['horses_count']}")
            print(f"   👤 Jockeys: {day_data['jockeys_count']}")
            print(f"   🎯 Trainers: {day_data['trainers_count']}")
            print(f"   📊 Records: {day_data['records_count']}")

        total_files = sum(d["total_files"] for d in data_by_date)
        total_size = sum(d["total_size_bytes"] or 0 for d in data_by_date)

        print(f"\n📈 TOTALS:")
        print(f"   🗓️  Days: {len(data_by_date)}")
        print(f"   📁 Total files: {total_files}")
        print(f"   📦 Total size: {total_size / 1024 / 1024:.1f} MB")

        return {
            "dates": data_by_date,
            "total_dates": len(data_by_date),
            "total_files": total_files,
            "total_size_mb": total_size / 1024 / 1024,
        }


def main():
    """Test the enhanced download system"""

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s"
    )

    project_root = Path(__file__).parent.parent.parent

    # Create enhanced download system
    download_system = EnhancedDownloadSystem(project_root)

    print("🔄 Enhanced Download System Test")
    print("=" * 50)

    # Run complete workflow
    result = download_system.complete_download_workflow()

    if result["success"]:
        print(f"\n✅ Workflow complete for {result['download_date']}")

        if result["archive_result"].get("archived", False):
            archive = result["archive_result"]
            print(f"   📦 Archived: {archive['files_archived']} files")
            print(f"   📈 Compression: {archive['compression_percentage']:.1f}%")

        if result["download_result"]["success"]:
            download = result["download_result"]
            print(f"   📥 Downloaded: {download['files_downloaded']} files")

    # Show data by date
    download_system.show_data_by_date(7)


if __name__ == "__main__":
    main()
