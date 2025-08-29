#!/usr/bin/env python3
"""
Enhanced Cleanup System with Critical File Protection
Implements aggressive cleanup of unwanted files while protecting critical system files.
"""

import json
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Set
from datetime import datetime


class EnhancedCleanupSystem:
    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.cleanup_stats = {}
        self.protected_files = set()
        self.removed_files = []
        self.errors = []

        # Load critical files from cross-reference analysis
        self.load_critical_files()

    def load_critical_files(self) -> None:
        """Load critical files from cross-reference report."""
        report_path = self.base_path / "CRITICAL_FILES_CROSS_REFERENCE_REPORT.json"
        if report_path.exists():
            with open(report_path, "r") as f:
                data = json.load(f)

            # Add all critical files to protection
            for file_path in data.get("critical_files", {}):
                self.protected_files.add(str(self.base_path / file_path))

            print(
                f"✅ Loaded {len(self.protected_files)} critical files for protection"
            )
        else:
            print("⚠️  Critical files report not found - using basic protection")

    def is_safe_to_remove(self, file_path: Path) -> bool:
        """Check if file is safe to remove (not critical)."""
        file_str = str(file_path)

        # Never remove protected critical files
        if file_str in self.protected_files:
            return False

        # Never remove files in critical directories
        critical_dirs = [
            "api/",
            "src/",
            "tools/analysis/",
            "config/",
            "database/",
            "docker/",
            "scripts/",
        ]

        rel_path = str(file_path.relative_to(self.base_path))
        for critical_dir in critical_dirs:
            if rel_path.startswith(critical_dir):
                # But allow removal of known unwanted patterns in these dirs
                if not self.is_unwanted_pattern(file_path):
                    return False

        return True

    def is_unwanted_pattern(self, file_path: Path) -> bool:
        """Check if file matches unwanted patterns."""
        file_str = str(file_path).lower()
        name = file_path.name.lower()

        # Unwanted patterns (safe to remove)
        unwanted_patterns = [
            # Backup files
            "backup",
            ".backup",
            ".bak",
            "_backup_",
            # Temporary files
            "temp",
            "tmp",
            ".tmp",
            "_temp_",
            ".swp",
            ".swo",
            # Cache files
            "cache",
            "__pycache__",
            ".pyc",
            ".pyo",
            "_cacache",
            # Log files
            ".log",
            "_logs_",
            "/logs/",
            # Build artifacts
            ".egg-info",
            "/dist/",
            "/build/",
            # IDE files
            ".vscode",
            ".idea",
            # Version control artifacts (non-essential)
            ".git/objects/",
            ".git/logs/",
            ".git/hooks/",
            # Test coverage
            "coverage",
            ".coverage",
            "htmlcov",
            # Old versions
            "_old",
            "_v1",
            "_v2",
            "_deprecated",
        ]

        return any(pattern in file_str for pattern in unwanted_patterns)

    def cleanup_category(self, category: str, patterns: List[str]) -> Dict:
        """Cleanup files matching specific category patterns."""
        print(f"\n🗑️  Cleaning up {category}...")

        removed_count = 0
        removed_size = 0
        errors = []

        for pattern in patterns:
            matches = list(self.base_path.rglob(pattern))

            for file_path in matches:
                try:
                    if self.is_safe_to_remove(file_path):
                        if file_path.is_file():
                            size = file_path.stat().st_size
                            file_path.unlink()
                            removed_size += size
                            removed_count += 1
                            self.removed_files.append(
                                str(file_path.relative_to(self.base_path))
                            )
                        elif file_path.is_dir() and not any(file_path.iterdir()):
                            # Remove empty directories
                            file_path.rmdir()
                            removed_count += 1
                            self.removed_files.append(
                                str(file_path.relative_to(self.base_path))
                            )
                    else:
                        print(
                            f"   🛡️  Protected: {file_path.relative_to(self.base_path)}"
                        )

                except Exception as e:
                    error_msg = f"Error removing {file_path}: {e}"
                    errors.append(error_msg)
                    self.errors.append(error_msg)

        return {
            "removed_count": removed_count,
            "removed_size_mb": round(removed_size / (1024 * 1024), 2),
            "errors": errors,
        }

    def run_aggressive_cleanup(self, dry_run: bool = False) -> None:
        """Run aggressive cleanup with critical file protection."""
        print("🚀 STARTING ENHANCED CLEANUP WITH CRITICAL FILE PROTECTION")
        print("=" * 80)

        if dry_run:
            print("🔍 DRY RUN MODE - No files will be deleted")
        else:
            print("⚠️  LIVE MODE - Files will be permanently deleted")

        # Backup critical files list before cleanup
        backup_path = (
            self.base_path
            / f"cleanup_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(backup_path, "w") as f:
            json.dump(
                {
                    "protected_files": list(self.protected_files),
                    "timestamp": datetime.now().isoformat(),
                },
                f,
                indent=2,
            )

        print(f"📋 Protected files list backed up to: {backup_path.name}")

        # Cleanup categories with their patterns
        cleanup_categories = {
            "Backup Files": ["*backup*", "*-backup-*", "*.backup", "*.bak"],
            "Temporary Files": ["*temp*", "*tmp*", "*.tmp", ".*.swp", ".*.swo"],
            "Cache Files": ["*cache*", "*__pycache__*", "*.pyc", "*.pyo"],
            "Log Files": ["*.log", "*logs*", "*.out"],
            "Build Artifacts": ["dist/*", "build/*", "*.egg-info/*"],
            "IDE Files": [".vscode/*", ".idea/*"],
            "Test Coverage": ["coverage/*", ".coverage", "htmlcov/*"],
            "Old Versions": ["*_old", "*_v1", "*_v2", "*_deprecated"],
        }

        total_removed = 0
        total_size = 0

        for category, patterns in cleanup_categories.items():
            if not dry_run:
                result = self.cleanup_category(category, patterns)
                self.cleanup_stats[category] = result
                total_removed += result["removed_count"]
                total_size += result["removed_size_mb"]
            else:
                # Dry run - just count files
                count = 0
                size = 0
                for pattern in patterns:
                    matches = list(self.base_path.rglob(pattern))
                    for file_path in matches:
                        if self.is_safe_to_remove(file_path) and file_path.is_file():
                            count += 1
                            size += file_path.stat().st_size

                result = {
                    "would_remove_count": count,
                    "would_remove_size_mb": round(size / (1024 * 1024), 2),
                }
                self.cleanup_stats[category] = result
                total_removed += count
                total_size += result["would_remove_size_mb"]
                print(
                    f"   📊 Would remove {count} files ({result['would_remove_size_mb']} MB)"
                )

        # Generate cleanup report
        self.generate_cleanup_report(dry_run, total_removed, total_size)

    def generate_cleanup_report(
        self, dry_run: bool, total_removed: int, total_size: float
    ) -> None:
        """Generate comprehensive cleanup report."""
        print("\n" + "=" * 80)
        print("📊 CLEANUP SUMMARY REPORT")
        print("=" * 80)

        mode = "DRY RUN" if dry_run else "LIVE CLEANUP"
        action = "Would remove" if dry_run else "Removed"

        print(f"\n🎯 {mode} RESULTS:")
        print(f"   📁 {action}: {total_removed:,} files")
        print(
            f"   💾 Space {'saved' if not dry_run else 'would save'}: {total_size:.1f} MB"
        )
        print(f"   🛡️  Protected files: {len(self.protected_files):,}")

        if not dry_run and self.errors:
            print(f"   ⚠️  Errors: {len(self.errors)}")

        print(f"\n📋 BREAKDOWN BY CATEGORY:")
        for category, stats in self.cleanup_stats.items():
            if dry_run:
                count = stats.get("would_remove_count", 0)
                size = stats.get("would_remove_size_mb", 0)
                print(f"   • {category}: {count} files, {size:.1f} MB")
            else:
                count = stats.get("removed_count", 0)
                size = stats.get("removed_size_mb", 0)
                errors = len(stats.get("errors", []))
                status = f" ({errors} errors)" if errors > 0 else ""
                print(f"   • {category}: {count} files, {size:.1f} MB{status}")

        # Save detailed report
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "mode": mode,
            "total_files_processed": total_removed,
            "total_size_mb": total_size,
            "protected_files_count": len(self.protected_files),
            "cleanup_stats": self.cleanup_stats,
            "removed_files": self.removed_files if not dry_run else [],
            "errors": self.errors if not dry_run else [],
        }

        report_filename = (
            f"ENHANCED_CLEANUP_REPORT_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        with open(self.base_path / report_filename, "w") as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Detailed report saved to: {report_filename}")

        if not dry_run:
            print(f"\n✅ Cleanup completed successfully!")
            print(f"   🎉 Freed up {total_size:.1f} MB of disk space")
            if self.errors:
                print(f"   ⚠️  Review {len(self.errors)} errors in the report")
        else:
            print(f"\n🔍 Dry run completed - no files were modified")
            print(f"   🚀 Run with dry_run=False to perform actual cleanup")


def main():
    """Main execution function."""
    import sys

    cleanup_system = EnhancedCleanupSystem()

    # Check if user wants dry run or live cleanup
    dry_run = True  # Default to safe mode
    if len(sys.argv) > 1 and sys.argv[1] == "--live":
        dry_run = False
        print("⚠️  LIVE CLEANUP MODE SELECTED")
        response = input("Are you sure you want to delete files? (yes/no): ")
        if response.lower() != "yes":
            print("Cleanup cancelled.")
            return

    cleanup_system.run_aggressive_cleanup(dry_run=dry_run)


if __name__ == "__main__":
    main()
