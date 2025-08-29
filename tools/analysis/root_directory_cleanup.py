#!/usr/bin/env python3
"""
🗂️ Root Directory Cleanup Implementation
========================================

Performs the actual cleanup and organization of the root directory
while protecting essential files like docker-compose, .env, Makefile, etc.

Author: AI Assistant
Date: August 29, 2025
"""

import json
import shutil
import os
from pathlib import Path
from datetime import datetime


class RootDirectoryCleanup:
    def __init__(self, project_root):
        self.project_root = Path(project_root)
        self.actions_performed = []
        self.protected_files = []
        self.moved_files = []

    def load_analysis_results(self):
        """Load analysis results from JSON file"""
        results_file = self.project_root / "ROOT_CLEANUP_ANALYSIS.json"
        if not results_file.exists():
            raise FileNotFoundError("Run root_directory_analyzer.py first")

        with open(results_file, "r") as f:
            return json.load(f)

    def create_target_directories(self, analysis_results):
        """Create target directories for organization"""
        move_candidates = analysis_results.get("move_candidates", {})

        print("📁 Creating target directories...")

        for target_dir in move_candidates.keys():
            target_path = self.project_root / target_dir

            # Skip if directory already exists
            if target_path.exists():
                print(f"  ✅ {target_dir}/ already exists")
                continue

            # Create directory
            target_path.mkdir(exist_ok=True)
            print(f"  📁 Created {target_dir}/")
            self.actions_performed.append(f"Created directory: {target_dir}/")

    def move_files_by_priority(self, analysis_results, priority_level):
        """Move files of specific priority level"""
        move_candidates = analysis_results.get("move_candidates", {})

        print(f"📦 Moving {priority_level} priority files...")
        moved_count = 0

        for target_dir, files in move_candidates.items():
            target_path = self.project_root / target_dir

            for file_info in files:
                if file_info["priority"] != priority_level:
                    continue

                source_path = self.project_root / file_info["path"]
                dest_path = target_path / source_path.name

                if not source_path.exists():
                    print(f"  ⚠️  File not found: {file_info['path']}")
                    continue

                try:
                    # Move file
                    shutil.move(str(source_path), str(dest_path))
                    print(f"  📦 {file_info['path']} → {target_dir}/{source_path.name}")

                    self.moved_files.append(
                        {
                            "source": file_info["path"],
                            "destination": f"{target_dir}/{source_path.name}",
                            "priority": priority_level,
                            "type": file_info["type"],
                        }
                    )
                    moved_count += 1

                except Exception as e:
                    print(f"  ❌ Error moving {file_info['path']}: {e}")

        print(f"  ✅ Moved {moved_count} {priority_level} priority files")
        self.actions_performed.append(
            f"Moved {moved_count} {priority_level} priority files"
        )

    def handle_protected_files(self, analysis_results):
        """Verify protected files are staying in root"""
        protected_files = analysis_results.get("protected_files", [])

        print("🔒 Verifying protected files...")

        for pfile in protected_files:
            file_path = self.project_root / pfile["path"]
            if file_path.exists():
                print(f"  ✅ Protected: {pfile['path']} ({pfile['reason']})")
                self.protected_files.append(pfile["path"])
            else:
                print(f"  ⚠️  Missing protected file: {pfile['path']}")

        print(f"  ✅ {len(self.protected_files)} protected files verified")

    def cleanup_temp_directories(self, analysis_results):
        """Clean up temporary directories"""
        cleanup_opportunities = analysis_results.get("cleanup_opportunities", [])

        if not cleanup_opportunities:
            print("✅ No temporary directories to clean up")
            return

        print("🗑️  Cleaning up temporary directories...")

        for opportunity in cleanup_opportunities:
            if opportunity["type"] != "temp_directory":
                continue

            dir_path = self.project_root / opportunity["path"]

            if not dir_path.exists():
                print(f"  ⚠️  Directory not found: {opportunity['path']}")
                continue

            print(f"  🗑️  Remove {opportunity['path']}? ({opportunity['reason']})")
            response = input("    Remove? (y/N): ").strip().lower()

            if response == "y":
                try:
                    shutil.rmtree(dir_path)
                    print(f"  ❌ Removed: {opportunity['path']}")
                    self.actions_performed.append(
                        f"Removed temp directory: {opportunity['path']}"
                    )
                except Exception as e:
                    print(f"  ❌ Error removing {opportunity['path']}: {e}")
            else:
                print(f"  ⏭️  Skipped: {opportunity['path']}")

    def create_organization_summary(self):
        """Create summary of organization changes"""
        summary_content = [
            "# 🏠 Root Directory Cleanup Summary",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## 🔒 Protected Files (Stayed in Root)",
            "",
        ]

        for pfile in self.protected_files:
            summary_content.append(f"- `{pfile}` - Essential project file")

        summary_content.extend(["", "## 📦 Files Moved", ""])

        # Group moved files by destination
        by_destination = {}
        for moved_file in self.moved_files:
            dest_dir = moved_file["destination"].split("/")[0]
            if dest_dir not in by_destination:
                by_destination[dest_dir] = []
            by_destination[dest_dir].append(moved_file)

        for dest_dir, files in by_destination.items():
            summary_content.extend(
                [f"### 📁 {dest_dir}/", f"Moved {len(files)} files:", ""]
            )

            for moved_file in files[:10]:  # Show first 10
                summary_content.append(
                    f"- `{moved_file['source']}` → `{moved_file['destination']}`"
                )

            if len(files) > 10:
                summary_content.append(f"- ... and {len(files) - 10} more files")

            summary_content.append("")

        summary_content.extend(["## 🔧 Actions Performed", ""])

        for i, action in enumerate(self.actions_performed, 1):
            summary_content.append(f"{i}. {action}")

        summary_content.extend(
            [
                "",
                "## 📊 Results",
                "",
                f"- **Protected files**: {len(self.protected_files)}",
                f"- **Files moved**: {len(self.moved_files)}",
                f"- **Directories created**: {len([a for a in self.actions_performed if 'Created directory' in a])}",
                "",
                "## ✅ Benefits",
                "",
                "1. **Clean root directory** - Only essential files remain",
                "2. **Better organization** - Files in appropriate directories",
                "3. **Improved navigation** - Logical file structure",
                "4. **Protected essentials** - Docker, environment, and build files safe",
            ]
        )

        summary_path = self.project_root / "docs" / "ROOT_CLEANUP_SUMMARY.md"
        summary_path.write_text("\n".join(summary_content), encoding="utf-8")

        print(f"📊 Cleanup summary saved: docs/ROOT_CLEANUP_SUMMARY.md")

    def run_cleanup(self, dry_run=False):
        """Run the complete cleanup process"""
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            return

        print("🏠 Starting Root Directory Cleanup...")
        print("=" * 50)

        # Load analysis results
        analysis_results = self.load_analysis_results()

        # Show what will be protected
        print(
            f"🔒 Will protect {len(analysis_results['protected_files'])} essential files"
        )
        print(
            f"📦 Will move {sum(len(files) for files in analysis_results['move_candidates'].values())} files"
        )
        print()

        # Ask for confirmation
        response = input("Proceed with cleanup? (y/N): ").strip().lower()
        if response != "y":
            print("❌ Cleanup cancelled")
            return

        # Perform cleanup steps
        self.handle_protected_files(analysis_results)
        self.create_target_directories(analysis_results)

        # Move files by priority (high priority first)
        self.move_files_by_priority(analysis_results, "high")
        self.move_files_by_priority(analysis_results, "medium")
        self.move_files_by_priority(analysis_results, "low")

        # Clean up temporary directories
        self.cleanup_temp_directories(analysis_results)

        # Create summary
        self.create_organization_summary()

        print("\n🎉 ROOT DIRECTORY CLEANUP COMPLETE!")
        print(f"✅ Protected {len(self.protected_files)} essential files")
        print(f"📦 Moved {len(self.moved_files)} files to appropriate directories")
        print(f"🗂️  Root directory is now clean and organized!")


def main():
    """Main execution function"""
    project_root = Path(__file__).parent.parent.parent

    cleanup = RootDirectoryCleanup(project_root)

    print("🏠 Root Directory Cleanup Tool")
    print("=" * 40)
    print("This will:")
    print("1. Protect essential files (docker-compose, .env, Makefile, etc.)")
    print("2. Move scripts to scripts/ directory")
    print("3. Move documentation to docs/ directory")
    print("4. Move config files to config/ directory")
    print("5. Organize analysis tools")
    print("6. Clean up temporary directories")
    print()

    cleanup.run_cleanup(dry_run=False)


if __name__ == "__main__":
    main()
