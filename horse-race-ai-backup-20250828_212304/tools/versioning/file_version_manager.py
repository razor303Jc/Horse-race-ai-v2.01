#!/usr/bin/env python3
"""
🗂️ Horse Racing AI - File Version Manager
Implements file versioning and change tracking system

This tool:
1. Tracks file versions with metadata
2. Creates automatic backups before changes
3. Monitors file dependencies and usage
4. Provides rollback capabilities
5. Generates change impact analysis

Author: AI Assistant
Date: August 26, 2025
Version: 1.0.0
"""

import json
import os
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class FileVersionManager:
    """Manages file versions, metadata, and change tracking"""

    def __init__(self, project_root: Optional[str] = None):
        default_root = "/home/jc/Documents/Horse-race-ai-v2.04"
        self.project_root = Path(project_root or default_root)

        # Version tracking paths
        self.version_dir = self.project_root / "data" / "versions"
        self.backup_dir = self.project_root / "data" / "backups"
        self.metadata_file = self.version_dir / "file_metadata.json"
        self.usage_log = self.version_dir / "usage_log.json"

        # Create directories
        self.version_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Load existing metadata
        self.metadata = self.load_metadata()
        self.usage_data = self.load_usage_data()

    def load_metadata(self) -> Dict:
        """Load file metadata from storage"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading metadata: {e}")

        return {
            "files": {},
            "dependencies": {},
            "entry_points": [],
            "last_updated": datetime.now().isoformat(),
        }

    def save_metadata(self):
        """Save metadata to storage"""
        self.metadata["last_updated"] = datetime.now().isoformat()
        with open(self.metadata_file, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def load_usage_data(self) -> Dict:
        """Load usage tracking data"""
        if self.usage_log.exists():
            try:
                with open(self.usage_log, "r") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Error loading usage data: {e}")

        return {"access_log": [], "import_tracking": {}, "execution_log": []}

    def save_usage_data(self):
        """Save usage data to storage"""
        with open(self.usage_log, "w") as f:
            json.dump(self.usage_data, f, indent=2)

    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file for change detection"""
        if not file_path.exists():
            return ""

        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def get_file_info(self, file_path: Path) -> Dict:
        """Get comprehensive file information"""
        if not file_path.exists():
            return {}

        stat = file_path.stat()
        return {
            "size": stat.st_size,
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "hash": self.calculate_file_hash(file_path),
            "relative_path": str(file_path.relative_to(self.project_root)),
        }

    def register_file(self, file_path: Path, metadata: Optional[Dict] = None) -> str:
        """Register a file in the version system and return version ID"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        relative_path = str(file_path.relative_to(self.project_root))

        # Generate version ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = self.calculate_file_hash(file_path)[:8]
        version_id = f"v{timestamp}_{file_hash}"

        # Get file info
        file_info = self.get_file_info(file_path)

        # Create file metadata entry
        if relative_path not in self.metadata["files"]:
            self.metadata["files"][relative_path] = {
                "versions": [],
                "dependencies": [],
                "dependents": [],
                "status": "active",
                "risk_level": "medium",
                "entry_point": False,
                "last_accessed": None,
                "creation_date": datetime.now().isoformat(),
            }

        # Add version
        version_entry = {
            "version_id": version_id,
            "timestamp": datetime.now().isoformat(),
            "file_info": file_info,
            "metadata": metadata or {},
            "backup_path": None,
        }

        self.metadata["files"][relative_path]["versions"].append(version_entry)

        # Save metadata
        self.save_metadata()

        logger.info(f"📝 Registered file: {relative_path} (version: {version_id})")
        return version_id

    def create_backup(self, file_path: Path, version_id: str) -> Path:
        """Create backup of file before modification"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        relative_path = file_path.relative_to(self.project_root)

        # Create backup directory structure
        backup_path = self.backup_dir / version_id / relative_path
        backup_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy file to backup
        shutil.copy2(file_path, backup_path)

        # Update metadata with backup path
        file_metadata = self.metadata["files"].get(str(relative_path), {})
        for version in file_metadata.get("versions", []):
            if version["version_id"] == version_id:
                version["backup_path"] = str(backup_path.relative_to(self.project_root))
                break

        self.save_metadata()

        logger.info(f"💾 Created backup: {backup_path}")
        return backup_path

    def track_file_access(self, file_path: Path, context: str = "unknown"):
        """Track when files are accessed"""
        if not file_path.exists():
            return

        relative_path = str(file_path.relative_to(self.project_root))

        access_entry = {
            "file": relative_path,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "hash": self.calculate_file_hash(file_path),
        }

        self.usage_data["access_log"].append(access_entry)

        # Update last accessed in metadata
        if relative_path in self.metadata["files"]:
            self.metadata["files"][relative_path]["last_accessed"] = access_entry[
                "timestamp"
            ]

        # Keep only last 1000 access entries to prevent log bloat
        if len(self.usage_data["access_log"]) > 1000:
            self.usage_data["access_log"] = self.usage_data["access_log"][-1000:]

        self.save_usage_data()
        self.save_metadata()

    def set_file_status(self, file_path: Path, status: str, risk_level: str = None):
        """Set file status (active, deprecated, testing)"""
        relative_path = str(file_path.relative_to(self.project_root))

        if relative_path not in self.metadata["files"]:
            self.register_file(file_path)

        self.metadata["files"][relative_path]["status"] = status
        if risk_level:
            self.metadata["files"][relative_path]["risk_level"] = risk_level

        self.save_metadata()
        logger.info(f"🏷️ Set {relative_path} status: {status}")

    def mark_as_entry_point(self, file_path: Path):
        """Mark file as system entry point"""
        relative_path = str(file_path.relative_to(self.project_root))

        if relative_path not in self.metadata["files"]:
            self.register_file(file_path)

        self.metadata["files"][relative_path]["entry_point"] = True

        if relative_path not in self.metadata["entry_points"]:
            self.metadata["entry_points"].append(relative_path)

        self.save_metadata()
        logger.info(f"🚪 Marked as entry point: {relative_path}")

    def add_dependency(self, file_path: Path, dependency_path: Path):
        """Record that file_path depends on dependency_path"""
        relative_path = str(file_path.relative_to(self.project_root))
        dependency_relative = str(dependency_path.relative_to(self.project_root))

        # Ensure both files are registered
        if relative_path not in self.metadata["files"]:
            self.register_file(file_path)
        if dependency_relative not in self.metadata["files"]:
            self.register_file(dependency_path)

        # Add dependency
        if (
            dependency_relative
            not in self.metadata["files"][relative_path]["dependencies"]
        ):
            self.metadata["files"][relative_path]["dependencies"].append(
                dependency_relative
            )

        # Add reverse dependency
        if (
            relative_path
            not in self.metadata["files"][dependency_relative]["dependents"]
        ):
            self.metadata["files"][dependency_relative]["dependents"].append(
                relative_path
            )

        self.save_metadata()

    def check_safe_to_modify(self, file_path: Path) -> Dict:
        """Check if file is safe to modify/remove"""
        relative_path = str(file_path.relative_to(self.project_root))

        if relative_path not in self.metadata["files"]:
            return {
                "safe": True,
                "risk_level": "low",
                "reasons": ["File not tracked - likely safe to modify"],
                "dependents": [],
                "entry_point": False,
            }

        file_meta = self.metadata["files"][relative_path]

        reasons = []
        risk_level = file_meta.get("risk_level", "medium")

        # Check if it's an entry point
        is_entry_point = file_meta.get("entry_point", False)
        if is_entry_point:
            reasons.append("File is marked as system entry point")
            risk_level = "critical"

        # Check dependents
        dependents = file_meta.get("dependents", [])
        if dependents:
            reasons.append(f"File has {len(dependents)} dependent files")
            if len(dependents) > 5:
                risk_level = "high"

        # Check recent access
        last_accessed = file_meta.get("last_accessed")
        if last_accessed:
            last_access_date = datetime.fromisoformat(last_accessed)
            days_since_access = (datetime.now() - last_access_date).days
            if days_since_access < 7:
                reasons.append("File accessed recently (within 7 days)")

        # Check status
        status = file_meta.get("status", "active")
        if status == "deprecated":
            reasons.append("File marked as deprecated - safe to remove")
            risk_level = "low"
        elif status == "testing":
            reasons.append("File in testing status")

        safe = risk_level in ["low"] and not is_entry_point and len(dependents) == 0

        return {
            "safe": safe,
            "risk_level": risk_level,
            "reasons": reasons,
            "dependents": dependents,
            "entry_point": is_entry_point,
            "status": status,
            "last_accessed": last_accessed,
        }

    def get_removal_candidates(self) -> List[Dict]:
        """Get list of files that are candidates for removal"""
        candidates = []

        for file_path, metadata in self.metadata["files"].items():
            if metadata.get("status") == "deprecated":
                safety_check = self.check_safe_to_modify(self.project_root / file_path)
                candidates.append(
                    {
                        "file": file_path,
                        "reason": "Marked as deprecated",
                        "safety": safety_check,
                    }
                )

            # Check for unused files (no dependents, not entry point, old access)
            elif len(metadata.get("dependents", [])) == 0 and not metadata.get(
                "entry_point", False
            ):

                last_accessed = metadata.get("last_accessed")
                if not last_accessed:
                    candidates.append(
                        {
                            "file": file_path,
                            "reason": "Never accessed, no dependents",
                            "safety": self.check_safe_to_modify(
                                self.project_root / file_path
                            ),
                        }
                    )
                else:
                    last_access_date = datetime.fromisoformat(last_accessed)
                    days_since_access = (datetime.now() - last_access_date).days
                    if days_since_access > 30:
                        candidates.append(
                            {
                                "file": file_path,
                                "reason": f"Not accessed for {days_since_access} days, no dependents",
                                "safety": self.check_safe_to_modify(
                                    self.project_root / file_path
                                ),
                            }
                        )

        return candidates

    def rollback_file(self, file_path: Path, version_id: str) -> bool:
        """Rollback file to specific version"""
        relative_path = str(file_path.relative_to(self.project_root))

        if relative_path not in self.metadata["files"]:
            logger.error(f"File not found in version system: {relative_path}")
            return False

        # Find version
        file_metadata = self.metadata["files"][relative_path]
        backup_path = None

        for version in file_metadata["versions"]:
            if version["version_id"] == version_id:
                backup_path = version.get("backup_path")
                break

        if not backup_path:
            logger.error(f"No backup found for version {version_id}")
            return False

        backup_file = self.project_root / backup_path
        if not backup_file.exists():
            logger.error(f"Backup file not found: {backup_file}")
            return False

        # Create backup of current version before rollback
        current_version_id = self.register_file(
            file_path, {"rollback_preparation": True}
        )
        self.create_backup(file_path, current_version_id)

        # Restore from backup
        shutil.copy2(backup_file, file_path)

        logger.info(f"🔄 Rolled back {relative_path} to version {version_id}")
        return True

    def generate_usage_report(self) -> Dict:
        """Generate comprehensive usage report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_files": len(self.metadata["files"]),
            "entry_points": len(self.metadata["entry_points"]),
            "removal_candidates": len(self.get_removal_candidates()),
            "files_by_status": {},
            "files_by_risk": {},
            "dependency_stats": {},
            "access_stats": {},
        }

        # Count by status
        status_counts = {}
        risk_counts = {}
        dependency_lengths = []

        for file_path, metadata in self.metadata["files"].items():
            status = metadata.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1

            risk = metadata.get("risk_level", "unknown")
            risk_counts[risk] = risk_counts.get(risk, 0) + 1

            dependency_lengths.append(len(metadata.get("dependencies", [])))

        report["files_by_status"] = status_counts
        report["files_by_risk"] = risk_counts

        # Dependency statistics
        if dependency_lengths:
            report["dependency_stats"] = {
                "avg_dependencies": sum(dependency_lengths) / len(dependency_lengths),
                "max_dependencies": max(dependency_lengths),
                "min_dependencies": min(dependency_lengths),
            }

        # Access statistics
        access_log = self.usage_data.get("access_log", [])
        if access_log:
            recent_accesses = [
                entry
                for entry in access_log
                if (datetime.now() - datetime.fromisoformat(entry["timestamp"])).days
                <= 7
            ]
            report["access_stats"] = {
                "total_accesses": len(access_log),
                "recent_accesses": len(recent_accesses),
                "unique_files_accessed": len(
                    set(entry["file"] for entry in access_log)
                ),
            }

        return report

    def export_version_data(self, output_path: Optional[Path] = None) -> Path:
        """Export all version data to JSON file"""
        if output_path is None:
            output_path = (
                self.version_dir
                / f"version_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            )

        export_data = {
            "metadata": self.metadata,
            "usage_data": self.usage_data,
            "export_timestamp": datetime.now().isoformat(),
            "project_root": str(self.project_root),
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2)

        logger.info(f"📤 Exported version data to: {output_path}")
        return output_path

    def scan_and_register_project(self, extensions: Optional[List[str]] = None):
        """Scan project and register all files"""
        if extensions is None:
            extensions = [".py", ".sh", ".yml", ".yaml", ".json", ".md"]

        logger.info("🔍 Scanning project for file registration...")

        registered_count = 0
        exclude_dirs = {
            ".git",
            "__pycache__",
            ".pytest_cache",
            ".venv",
            "venv",
            "node_modules",
        }

        for root, dirs, files in os.walk(self.project_root):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                file_path = Path(root) / file

                # Check if file has desired extension
                if any(file.endswith(ext) for ext in extensions):
                    try:
                        relative_path = str(file_path.relative_to(self.project_root))

                        # Skip if already registered and unchanged
                        if relative_path in self.metadata["files"]:
                            current_hash = self.calculate_file_hash(file_path)
                            last_version = self.metadata["files"][relative_path][
                                "versions"
                            ][-1]
                            if last_version["file_info"]["hash"] == current_hash:
                                continue

                        # Register file
                        self.register_file(
                            file_path,
                            {
                                "auto_registered": True,
                                "scan_timestamp": datetime.now().isoformat(),
                            },
                        )
                        registered_count += 1

                    except Exception as e:
                        logger.warning(f"Error registering {file_path}: {e}")

        logger.info(f"✅ Registered {registered_count} files")


def main():
    """Main entry point for file version manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Manage file versions and tracking")
    parser.add_argument("--project-root", help="Project root directory")
    parser.add_argument(
        "--scan", action="store_true", help="Scan and register all files"
    )
    parser.add_argument("--report", action="store_true", help="Generate usage report")
    parser.add_argument(
        "--candidates", action="store_true", help="Show removal candidates"
    )
    parser.add_argument("--export", action="store_true", help="Export version data")

    args = parser.parse_args()

    try:
        manager = FileVersionManager(args.project_root)

        if args.scan:
            print("🔍 Scanning and registering project files...")
            manager.scan_and_register_project()
            print("✅ Scan complete")

        if args.report:
            print("📊 Generating usage report...")
            report = manager.generate_usage_report()
            print(f"📁 Total files: {report['total_files']}")
            print(f"🚪 Entry points: {report['entry_points']}")
            print(f"🗑️ Removal candidates: {report['removal_candidates']}")
            print(f"📈 Files by status: {report['files_by_status']}")

        if args.candidates:
            print("🗑️ Removal candidates:")
            candidates = manager.get_removal_candidates()
            for candidate in candidates:
                safety = candidate["safety"]
                risk_icon = {
                    "low": "🟢",
                    "medium": "🟡",
                    "high": "🟠",
                    "critical": "🔴",
                }.get(safety["risk_level"], "❓")
                print(f"  {risk_icon} {candidate['file']} - {candidate['reason']}")

        if args.export:
            print("📤 Exporting version data...")
            export_path = manager.export_version_data()
            print(f"✅ Exported to: {export_path}")

        return 0

    except KeyboardInterrupt:
        print("\n🛑 Operation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
