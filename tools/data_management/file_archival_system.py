#!/usr/bin/env python3
"""
📁 File Archival System for Horse Racing Data
Comprehensive archival system for managing downloaded racing data

Features:
- Automatic archival of existing files before new downloads
- Date-based organization and compression
- Secure archive storage with metadata
- Database integration for tracking archived data
- Archive verification and integrity checks

Author: AI Assistant
Date: August 17, 2025
"""

import os
import shutil
import zipfile
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import hashlib
import sqlite3


logger = logging.getLogger(__name__)


class FileArchivalSystem:
    """Manages archival of downloaded racing data files"""
    
    def __init__(self, project_root: Path, archive_root: Optional[Path] = None):
        self.project_root = Path(project_root)
        self.download_dir = self.project_root / "data" / "daily_downloads"
        
        # Default archive location
        if archive_root is None:
            self.archive_root = self.project_root / "data" / "archives"
        else:
            self.archive_root = Path(archive_root)
        
        # Create archive directories
        self.archive_root.mkdir(parents=True, exist_ok=True)
        self.metadata_dir = self.archive_root / "metadata"
        self.metadata_dir.mkdir(exist_ok=True)
        
        # Database for tracking archives
        self.db_path = self.archive_root / "archive_tracking.db"
        self._init_database()
    
    def _init_database(self):
        """Initialize archive tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archives (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    archive_date TEXT NOT NULL,
                    archive_filename TEXT NOT NULL,
                    source_directory TEXT NOT NULL,
                    file_count INTEGER NOT NULL,
                    total_size_bytes INTEGER NOT NULL,
                    compression_ratio REAL NOT NULL,
                    md5_hash TEXT NOT NULL,
                    created_timestamp TEXT NOT NULL,
                    metadata_file TEXT NOT NULL,
                    status TEXT DEFAULT 'active'
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS archived_files (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    archive_id INTEGER NOT NULL,
                    original_path TEXT NOT NULL,
                    file_size_bytes INTEGER NOT NULL,
                    last_modified TEXT NOT NULL,
                    md5_hash TEXT NOT NULL,
                    FOREIGN KEY (archive_id) REFERENCES archives (id)
                )
            """)
            
            conn.commit()
            logger.info("📊 Archive tracking database initialized")
    
    def get_file_info(self, file_path: Path) -> Dict:
        """Get comprehensive file information"""
        if not file_path.exists():
            return {}
        
        stat = file_path.stat()
        
        # Calculate MD5 hash
        md5_hash = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                md5_hash.update(chunk)
        
        return {
            "path": str(file_path),
            "size_bytes": stat.st_size,
            "last_modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "md5_hash": md5_hash.hexdigest()
        }
    
    def scan_download_directory(self) -> Dict[str, List[Dict]]:
        """Scan download directory and categorize files"""
        
        if not self.download_dir.exists():
            logger.warning(f"⚠️ Download directory not found: {self.download_dir}")
            return {}
        
        categorized_files = {
            "cards_data": [],
            "results_data": [],
            "other_files": []
        }
        
        # Scan for all files
        for file_path in self.download_dir.rglob("*"):
            if file_path.is_file():
                file_info = self.get_file_info(file_path)
                
                # Categorize by directory structure
                relative_path = file_path.relative_to(self.download_dir)
                
                if "cards_data" in str(relative_path):
                    categorized_files["cards_data"].append(file_info)
                elif "results_data" in str(relative_path):
                    categorized_files["results_data"].append(file_info)
                else:
                    categorized_files["other_files"].append(file_info)
        
        total_files = sum(len(files) for files in categorized_files.values())
        total_size = sum(
            file_info["size_bytes"] 
            for files in categorized_files.values() 
            for file_info in files
        )
        
        logger.info(f"📁 Scanned download directory: {total_files} files, {total_size / 1024 / 1024:.1f} MB")
        
        return categorized_files
    
    def create_archive(self, archive_date: str = None) -> Tuple[Path, Dict]:
        """Create compressed archive of current download files"""
        
        if archive_date is None:
            archive_date = datetime.now().strftime("%Y-%m-%d")
        
        # Scan files to archive
        categorized_files = self.scan_download_directory()
        
        if not any(categorized_files.values()):
            logger.warning("⚠️ No files found to archive")
            return None, {}
        
        # Create archive filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_filename = f"racing_data_archive_{archive_date}_{timestamp}.zip"
        archive_path = self.archive_root / archive_filename
        
        # Create metadata
        metadata = {
            "archive_date": archive_date,
            "created_timestamp": datetime.now().isoformat(),
            "source_directory": str(self.download_dir),
            "categorized_files": categorized_files,
            "total_files": sum(len(files) for files in categorized_files.values()),
            "archive_filename": archive_filename
        }
        
        # Create zip archive
        logger.info(f"📦 Creating archive: {archive_filename}")
        
        original_size = 0
        compressed_size = 0
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zipf:
            for file_category, files in categorized_files.items():
                for file_info in files:
                    file_path = Path(file_info["path"])
                    
                    if file_path.exists():
                        # Create archive path preserving structure
                        relative_path = file_path.relative_to(self.download_dir)
                        archive_file_path = f"{archive_date}/{relative_path}"
                        
                        zipf.write(file_path, archive_file_path)
                        original_size += file_info["size_bytes"]
        
        compressed_size = archive_path.stat().st_size
        compression_ratio = compressed_size / original_size if original_size > 0 else 0
        
        metadata.update({
            "original_size_bytes": original_size,
            "compressed_size_bytes": compressed_size,
            "compression_ratio": compression_ratio,
            "compression_percentage": (1 - compression_ratio) * 100
        })
        
        # Calculate archive hash
        archive_md5 = hashlib.md5()
        with open(archive_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                archive_md5.update(chunk)
        
        metadata["md5_hash"] = archive_md5.hexdigest()
        
        # Save metadata
        metadata_filename = f"metadata_{archive_date}_{timestamp}.json"
        metadata_path = self.metadata_dir / metadata_filename
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        metadata["metadata_file"] = str(metadata_path)
        
        logger.info(f"✅ Archive created: {archive_filename}")
        logger.info(f"   📊 Original size: {original_size / 1024 / 1024:.1f} MB")
        logger.info(f"   📦 Compressed size: {compressed_size / 1024 / 1024:.1f} MB")
        logger.info(f"   📈 Compression: {metadata['compression_percentage']:.1f}%")
        
        return archive_path, metadata
    
    def record_archive_in_database(self, metadata: Dict) -> int:
        """Record archive information in database"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert archive record
            cursor.execute("""
                INSERT INTO archives (
                    archive_date, archive_filename, source_directory,
                    file_count, total_size_bytes, compression_ratio,
                    md5_hash, created_timestamp, metadata_file
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                metadata["archive_date"],
                metadata["archive_filename"],
                metadata["source_directory"],
                metadata["total_files"],
                metadata["original_size_bytes"],
                metadata["compression_ratio"],
                metadata["md5_hash"],
                metadata["created_timestamp"],
                metadata["metadata_file"]
            ))
            
            archive_id = cursor.lastrowid
            
            # Insert individual file records
            for file_category, files in metadata["categorized_files"].items():
                for file_info in files:
                    cursor.execute("""
                        INSERT INTO archived_files (
                            archive_id, original_path, file_size_bytes,
                            last_modified, md5_hash
                        ) VALUES (?, ?, ?, ?, ?)
                    """, (
                        archive_id,
                        file_info["path"],
                        file_info["size_bytes"],
                        file_info["last_modified"],
                        file_info["md5_hash"]
                    ))
            
            conn.commit()
            
        logger.info(f"📊 Archive recorded in database with ID: {archive_id}")
        return archive_id
    
    def move_files_to_secure_location(self, secure_path: Optional[Path] = None):
        """Move archive files to secure location"""
        
        if secure_path is None:
            secure_path = self.archive_root / "secure_storage"
        
        secure_path = Path(secure_path)
        secure_path.mkdir(parents=True, exist_ok=True)
        
        # Move all archive files
        moved_files = []
        
        for archive_file in self.archive_root.glob("*.zip"):
            dest_path = secure_path / archive_file.name
            shutil.move(archive_file, dest_path)
            moved_files.append(dest_path)
            logger.info(f"🔒 Moved to secure storage: {archive_file.name}")
        
        # Move metadata directory
        secure_metadata_dir = secure_path / "metadata"
        if self.metadata_dir.exists() and self.metadata_dir != secure_metadata_dir:
            if secure_metadata_dir.exists():
                shutil.rmtree(secure_metadata_dir)
            shutil.move(self.metadata_dir, secure_metadata_dir)
            self.metadata_dir = secure_metadata_dir
            logger.info("🔒 Moved metadata to secure storage")
        
        return moved_files
    
    def clean_download_directory(self, preserve_structure: bool = True):
        """Clean download directory after archival"""
        
        if not self.download_dir.exists():
            return
        
        cleaned_files = []
        
        # Remove all files but preserve directory structure
        for file_path in self.download_dir.rglob("*"):
            if file_path.is_file():
                file_path.unlink()
                cleaned_files.append(str(file_path))
        
        # Remove empty directories if not preserving structure
        if not preserve_structure:
            for dir_path in self.download_dir.rglob("*"):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
        
        logger.info(f"🧹 Cleaned download directory: {len(cleaned_files)} files removed")
        return cleaned_files
    
    def get_archive_history(self, days: int = 30) -> List[Dict]:
        """Get archive history from database"""
        
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    id, archive_date, archive_filename, file_count,
                    total_size_bytes, compression_ratio, created_timestamp,
                    status
                FROM archives 
                WHERE created_timestamp > ?
                ORDER BY created_timestamp DESC
            """, (cutoff_date,))
            
            columns = [description[0] for description in cursor.description]
            archives = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return archives
    
    def archive_and_clean(self, archive_date: str = None, secure_path: Optional[Path] = None) -> Dict:
        """Complete archival workflow: archive, record, secure, clean"""
        
        logger.info("🚀 Starting complete archival workflow")
        
        # Create archive
        archive_path, metadata = self.create_archive(archive_date)
        
        if archive_path is None:
            return {"success": False, "message": "No files to archive"}
        
        # Record in database
        archive_id = self.record_archive_in_database(metadata)
        
        # Move to secure location
        moved_files = self.move_files_to_secure_location(secure_path)
        
        # Clean download directory
        cleaned_files = self.clean_download_directory()
        
        result = {
            "success": True,
            "archive_id": archive_id,
            "archive_filename": metadata["archive_filename"],
            "original_size_mb": metadata["original_size_bytes"] / 1024 / 1024,
            "compressed_size_mb": metadata["compressed_size_bytes"] / 1024 / 1024,
            "compression_percentage": metadata["compression_percentage"],
            "files_archived": metadata["total_files"],
            "files_cleaned": len(cleaned_files),
            "secure_files": len(moved_files)
        }
        
        logger.info("✅ Complete archival workflow finished")
        logger.info(f"   📦 Archive ID: {archive_id}")
        logger.info(f"   📁 Files archived: {result['files_archived']}")
        logger.info(f"   🧹 Files cleaned: {result['files_cleaned']}")
        logger.info(f"   🔒 Secure files: {result['secure_files']}")
        
        return result


def main():
    """Test the archival system"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s'
    )
    
    project_root = Path(__file__).parent.parent.parent
    
    # Create archival system
    archiver = FileArchivalSystem(project_root)
    
    print("📁 File Archival System Test")
    print("=" * 50)
    
    # Scan current files
    categorized_files = archiver.scan_download_directory()
    
    if any(categorized_files.values()):
        print(f"\n📊 Files found:")
        for category, files in categorized_files.items():
            if files:
                total_size = sum(f["size_bytes"] for f in files) / 1024 / 1024
                print(f"   {category}: {len(files)} files ({total_size:.1f} MB)")
        
        # Perform archival
        result = archiver.archive_and_clean()
        
        if result["success"]:
            print(f"\n✅ Archival complete:")
            print(f"   Archive ID: {result['archive_id']}")
            print(f"   Compression: {result['compression_percentage']:.1f}%")
            print(f"   Files archived: {result['files_archived']}")
    else:
        print("⚠️ No files found to archive")
    
    # Show archive history
    history = archiver.get_archive_history(7)
    if history:
        print(f"\n📚 Recent archives (last 7 days):")
        for archive in history[:5]:
            date = archive["archive_date"]
            files = archive["file_count"]
            size_mb = archive["total_size_bytes"] / 1024 / 1024
            print(f"   {date}: {files} files ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
