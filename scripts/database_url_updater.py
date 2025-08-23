#!/usr/bin/env python3
"""
Database URL Updater
==================

Updates all localhost database references to use Docker network names
for proper container-to-container communication.
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple, Dict


class DatabaseURLUpdater:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backup_dir = self.project_root / "backups" / "database_url_fixes"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # URL patterns to replace
        self.url_patterns = {
            # PostgreSQL patterns
            r"localhost:5432": "postgres:5432",
            r"localhost:5434": "postgres:5432",
            r"127\.0\.0\.1:5432": "postgres:5432",
            r"127\.0\.0\.1:5434": "postgres:5432",
            # Redis patterns
            r"localhost:6379": "redis:6379",
            r"localhost:6380": "redis:6379",
            r"127\.0\.0\.1:6379": "redis:6379",
            r"127\.0\.0\.1:6380": "redis:6379",
            # Database connection strings
            r"postgresql://([^@]+@)?localhost:5432": r"postgresql://\1postgres:5432",
            r"postgresql://([^@]+@)?localhost:5434": r"postgresql://\1postgres:5432",
            r"redis://([^@]*@)?localhost:6379": r"redis://\1redis:6379",
            r"redis://([^@]*@)?localhost:6380": r"redis://\1redis:6379",
        }

        # Directories to scan
        self.scan_dirs = ["api", "src", "tools", "docker", "scripts", "monitoring"]

        # File extensions to check
        self.file_extensions = [".py", ".yml", ".yaml", ".json", ".sh", ".env"]

    def backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification"""
        backup_path = self.backup_dir / file_path.relative_to(self.project_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file_path, backup_path)
        return backup_path

    def scan_file(self, file_path: Path) -> List[Tuple[str, str, int]]:
        """Scan file for URL patterns that need updating"""
        matches = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            for line_num, line in enumerate(content.split("\n"), 1):
                for pattern, replacement in self.url_patterns.items():
                    if re.search(pattern, line):
                        matches.append((pattern, line.strip(), line_num))

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

        return matches

    def update_file(self, file_path: Path) -> Tuple[bool, int]:
        """Update file with new URLs"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            replacements_made = 0

            for pattern, replacement in self.url_patterns.items():
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    replacements_made += len(re.findall(pattern, content))
                    content = new_content

            if content != original_content:
                # Backup original file
                self.backup_file(file_path)

                # Write updated content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                return True, replacements_made
            else:
                return False, 0

        except Exception as e:
            print(f"Error updating {file_path}: {e}")
            return False, 0

    def scan_project(self) -> Dict[str, List[Tuple[str, str, int]]]:
        """Scan entire project for files needing updates"""
        print("🔍 Scanning project for database URL references...")

        files_with_matches = {}
        total_files_scanned = 0

        for scan_dir in self.scan_dirs:
            dir_path = self.project_root / scan_dir
            if not dir_path.exists():
                continue

            for file_path in dir_path.rglob("*"):
                if file_path.is_file() and file_path.suffix in self.file_extensions:
                    total_files_scanned += 1
                    matches = self.scan_file(file_path)
                    if matches:
                        files_with_matches[str(file_path)] = matches

        print(f"📊 Scanned {total_files_scanned} files")
        print(f"🎯 Found {len(files_with_matches)} files with URL references")

        return files_with_matches

    def show_preview(self, files_with_matches: Dict[str, List[Tuple]]):
        """Show preview of changes before applying"""
        print("\n📋 PREVIEW OF CHANGES")
        print("=" * 60)

        for file_path, matches in files_with_matches.items():
            rel_path = Path(file_path).relative_to(self.project_root)
            print(f"\n📄 {rel_path}")
            print("-" * 40)

            for pattern, line_content, line_num in matches:
                print(f"  Line {line_num:3d}: {line_content}")
                # Show what it will become
                for p, r in self.url_patterns.items():
                    if re.search(p, line_content):
                        new_line = re.sub(p, r, line_content)
                        print(f"           → {new_line}")
                        break

    def apply_updates(
        self, files_with_matches: Dict[str, List[Tuple]]
    ) -> Dict[str, int]:
        """Apply URL updates to all files"""
        print("\n🔧 APPLYING UPDATES")
        print("=" * 40)

        results = {}
        total_replacements = 0

        for file_path in files_with_matches.keys():
            updated, count = self.update_file(Path(file_path))
            rel_path = Path(file_path).relative_to(self.project_root)

            if updated:
                results[str(rel_path)] = count
                total_replacements += count
                print(f"✅ {rel_path}: {count} replacements")
            else:
                print(f"⚠️  {rel_path}: No changes made")

        print(f"\n🎉 Total replacements: {total_replacements}")
        return results

    def restore_backups(self):
        """Restore files from backup"""
        print("🔄 Restoring files from backup...")

        if not self.backup_dir.exists():
            print("❌ No backup directory found")
            return

        restored_count = 0
        for backup_file in self.backup_dir.rglob("*"):
            if backup_file.is_file():
                # Calculate original file path
                rel_path = backup_file.relative_to(self.backup_dir)
                original_path = self.project_root / rel_path

                if original_path.exists():
                    shutil.copy2(backup_file, original_path)
                    restored_count += 1
                    print(f"✅ Restored {rel_path}")

        print(f"🎉 Restored {restored_count} files")

    def run_scan_only(self):
        """Run scan only without making changes"""
        files_with_matches = self.scan_project()

        if files_with_matches:
            self.show_preview(files_with_matches)
            print(f"\n💡 Found {len(files_with_matches)} files that need updates")
            print("💡 Run with --apply to make changes")
        else:
            print("✅ No localhost database URLs found - all good!")

    def run_full_update(self):
        """Run full scan and update process"""
        files_with_matches = self.scan_project()

        if not files_with_matches:
            print("✅ No localhost database URLs found - all good!")
            return

        self.show_preview(files_with_matches)

        # Confirm before applying
        response = input(f"\nApply updates to {len(files_with_matches)} files? (y/n): ")
        if response.lower() != "y":
            print("❌ Updates cancelled")
            return

        results = self.apply_updates(files_with_matches)

        print("\n📋 SUMMARY")
        print("=" * 40)
        print(f"✅ Updated {len(results)} files")
        print(f"🔄 Backups saved to: {self.backup_dir}")
        print("💡 Run with --restore to undo changes")


def main():
    import sys

    updater = DatabaseURLUpdater()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--apply":
            updater.run_full_update()
        elif sys.argv[1] == "--restore":
            updater.restore_backups()
        elif sys.argv[1] == "--scan":
            updater.run_scan_only()
        else:
            print("Usage: python database_url_updater.py [--scan|--apply|--restore]")
    else:
        print("🏇 Database URL Updater")
        print("=" * 40)
        print("Options:")
        print("  --scan     Scan for localhost URLs (no changes)")
        print("  --apply    Scan and apply updates")
        print("  --restore  Restore from backup")
        print()
        print("Running scan only...")
        updater.run_scan_only()


if __name__ == "__main__":
    main()
