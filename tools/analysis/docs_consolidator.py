#!/usr/bin/env python3
"""
🗂️ Documentation Consolidation Implementation
=============================================

Practical implementation of documentation consolidation based on analysis.
This script will perform the actual reorganization with user confirmation.

Consolidation Actions:
1. Remove empty files immediately
2. Consolidate TODO lists into master document
3. Archive completion reports
4. Create summary indexes

Author: AI Assistant
Date: August 29, 2025
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import os


class DocsConsolidator:
    def __init__(self, docs_path):
        self.docs_path = Path(docs_path)
        self.archive_path = self.docs_path / "archive"
        self.summaries_path = self.docs_path / "summaries"
        self.actions_performed = []

    def load_analysis_results(self):
        """Load analysis results from JSON file"""
        results_file = self.docs_path / "CONSOLIDATION_ANALYSIS_RESULTS.json"
        if not results_file.exists():
            raise FileNotFoundError("Run docs_consolidation_analyzer.py first")

        with open(results_file, "r") as f:
            return json.load(f)

    def create_directories(self):
        """Create necessary directories for reorganization"""
        self.archive_path.mkdir(exist_ok=True)
        self.summaries_path.mkdir(exist_ok=True)

        # Create subdirectories
        (self.archive_path / "completion_reports").mkdir(exist_ok=True)
        (self.archive_path / "old_todos").mkdir(exist_ok=True)
        (self.archive_path / "implementation_history").mkdir(exist_ok=True)

        print("📁 Created archive and summary directories")
        self.actions_performed.append("Created directory structure")

    def remove_empty_files(self, analysis_results):
        """Remove empty files immediately"""
        empty_files = analysis_results.get("empty_files", [])

        if not empty_files:
            print("✅ No empty files found")
            return

        print(f"🗑️  Removing {len(empty_files)} empty files...")

        for empty_file in empty_files:
            file_path = self.docs_path / empty_file["path"]
            if file_path.exists():
                file_path.unlink()
                print(f"  ❌ Removed: {empty_file['path']}")
                self.actions_performed.append(
                    f"Removed empty file: {empty_file['path']}"
                )

        print(f"✅ Removed {len(empty_files)} empty files")

    def consolidate_todo_lists(self, analysis_results):
        """Consolidate TODO lists into master document"""
        todo_files = analysis_results["categories"].get("todo_lists", [])

        if len(todo_files) < 3:
            print("✅ TODO consolidation not needed (< 3 files)")
            return

        print(f"📝 Consolidating {len(todo_files)} TODO lists...")

        # Create master TODO document
        master_content = [
            "# 📋 Master TODO List - Consolidated",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Source**: Consolidated from {len(todo_files)} TODO documents",
            "",
            "## 🎯 Active TODOs",
            "",
        ]

        # Process each TODO file
        for i, todo_file in enumerate(todo_files, 1):
            file_path = self.docs_path / todo_file["path"]

            if file_path.exists():
                try:
                    content = file_path.read_text(encoding="utf-8")

                    # Extract title and TODO items
                    lines = content.split("\n")
                    title = todo_file["content_summary"]["title"] or f"TODO List {i}"

                    master_content.extend(
                        [f"### {i}. {title}", f"*Source: {todo_file['path']}*", ""]
                    )

                    # Extract TODO items (lines with - [ ] or - [x] or - TODO or numbered items)
                    in_todo_section = False
                    for line in lines:
                        line = line.strip()
                        if any(
                            keyword in line.upper()
                            for keyword in ["TODO", "TASK", "- [ ]", "- [X]"]
                        ):
                            in_todo_section = True

                        if in_todo_section and (
                            line.startswith("- ")
                            or line.startswith("* ")
                            or (line and line[0].isdigit() and "." in line[:3])
                        ):
                            master_content.append(f"  {line}")

                    master_content.extend(["", "---", ""])

                    # Move original file to archive
                    archive_dest = self.archive_path / "old_todos" / file_path.name
                    shutil.move(str(file_path), str(archive_dest))
                    print(f"  📦 Archived: {todo_file['path']}")

                except Exception as e:
                    print(f"  ❌ Error processing {todo_file['path']}: {e}")
                    continue

        # Save master TODO
        master_path = self.docs_path / "MASTER_TODO_CONSOLIDATED.md"
        master_path.write_text("\n".join(master_content), encoding="utf-8")

        print(f"✅ Created master TODO: {master_path.name}")
        self.actions_performed.append(
            f"Consolidated {len(todo_files)} TODO lists into master document"
        )

    def archive_completion_reports(self, analysis_results):
        """Archive old completion reports"""
        completion_files = analysis_results["categories"].get("completion_reports", [])

        if len(completion_files) < 5:
            print("✅ Completion report archival not needed (< 5 files)")
            return

        print(f"📦 Archiving {len(completion_files)} completion reports...")

        # Create completion index
        index_content = [
            "# 📊 Completion Reports Index",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Reports**: {len(completion_files)}",
            "",
            "## 📋 Archived Reports",
            "",
        ]

        archived_count = 0
        for completion_file in completion_files:
            file_path = self.docs_path / completion_file["path"]

            if file_path.exists():
                try:
                    # Create index entry
                    title = (
                        completion_file["content_summary"]["title"] or file_path.stem
                    )
                    size = completion_file["size"]
                    modified = datetime.fromtimestamp(
                        completion_file["modified"]
                    ).strftime("%Y-%m-%d")

                    index_content.extend(
                        [
                            f"### {title}",
                            f"- **File**: `{completion_file['path']}`",
                            f"- **Date**: {modified}",
                            f"- **Size**: {size:,} bytes",
                            f"- **Archived**: `archive/completion_reports/{file_path.name}`",
                            "",
                        ]
                    )

                    # Move to archive
                    archive_dest = (
                        self.archive_path / "completion_reports" / file_path.name
                    )
                    shutil.move(str(file_path), str(archive_dest))
                    archived_count += 1
                    print(f"  📦 Archived: {completion_file['path']}")

                except Exception as e:
                    print(f"  ❌ Error archiving {completion_file['path']}: {e}")
                    continue

        # Save completion index
        index_path = self.summaries_path / "COMPLETION_REPORTS_INDEX.md"
        index_path.write_text("\n".join(index_content), encoding="utf-8")

        print(f"✅ Archived {archived_count} completion reports")
        print(f"✅ Created completion index: {index_path.name}")
        self.actions_performed.append(f"Archived {archived_count} completion reports")

    def create_implementation_index(self, analysis_results):
        """Create index for implementation documentation"""
        impl_files = analysis_results["categories"].get("implementation_docs", [])

        if len(impl_files) < 3:
            print("✅ Implementation index not needed (< 3 files)")
            return

        print(f"📑 Creating implementation documentation index...")

        index_content = [
            "# 🔧 Implementation Documentation Index",
            f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Total Documents**: {len(impl_files)}",
            "",
            "## 📚 Implementation Documents",
            "",
        ]

        # Group by subdirectory
        by_location = {}
        for impl_file in impl_files:
            location = (
                str(Path(impl_file["path"]).parent)
                if "/" in impl_file["path"]
                else "root"
            )
            if location not in by_location:
                by_location[location] = []
            by_location[location].append(impl_file)

        for location, files in by_location.items():
            index_content.extend([f"### 📂 {location.title()}", ""])

            for impl_file in files:
                title = (
                    impl_file["content_summary"]["title"]
                    or Path(impl_file["path"]).stem
                )
                size = impl_file["size"]
                modified = datetime.fromtimestamp(impl_file["modified"]).strftime(
                    "%Y-%m-%d"
                )

                index_content.extend(
                    [
                        f"#### {title}",
                        f"- **File**: [`{impl_file['path']}`]({impl_file['path']})",
                        f"- **Date**: {modified}",
                        f"- **Size**: {size:,} bytes",
                        f"- **Description**: {impl_file['content_summary']['description'][:100]}...",
                        "",
                    ]
                )

        # Save implementation index
        index_path = self.summaries_path / "IMPLEMENTATION_DOCS_INDEX.md"
        index_path.write_text("\n".join(index_content), encoding="utf-8")

        print(f"✅ Created implementation index: {index_path.name}")
        self.actions_performed.append(f"Created implementation documentation index")

    def generate_consolidation_summary(self, original_analysis):
        """Generate final consolidation summary"""
        summary_content = [
            "# 📊 Documentation Consolidation Summary",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Original Files**: {original_analysis['total_files']}",
            f"**Original Size**: {original_analysis['total_size']:,} bytes",
            "",
            "## 🔧 Actions Performed",
            "",
        ]

        for i, action in enumerate(self.actions_performed, 1):
            summary_content.append(f"{i}. {action}")

        # Calculate current stats
        current_files = len(list(self.docs_path.rglob("*.md")))
        current_size = sum(f.stat().st_size for f in self.docs_path.rglob("*.md"))

        reduction_files = original_analysis["total_files"] - current_files
        reduction_size = original_analysis["total_size"] - current_size

        summary_content.extend(
            [
                "",
                "## 📈 Results",
                "",
                f"- **Files After**: {current_files}",
                f"- **Size After**: {current_size:,} bytes",
                f"- **Files Reduced**: {reduction_files} ({reduction_files/original_analysis['total_files']*100:.1f}%)",
                f"- **Size Reduced**: {reduction_size:,} bytes ({reduction_size/original_analysis['total_size']*100:.1f}%)",
                "",
                "## 📁 New Structure",
                "",
                "- `docs/` - Active documentation",
                "- `docs/archive/` - Archived historical documents",
                "- `docs/summaries/` - Consolidated summaries and indexes",
                "",
                "## ✅ Benefits",
                "",
                "1. **Reduced clutter** - Removed redundant and empty files",
                "2. **Better organization** - Consolidated related documents",
                "3. **Improved navigation** - Created summary indexes",
                "4. **Preserved history** - Archived important historical documents",
            ]
        )

        summary_path = self.docs_path / "CONSOLIDATION_SUMMARY.md"
        summary_path.write_text("\n".join(summary_content), encoding="utf-8")

        print(f"\n📊 CONSOLIDATION COMPLETE!")
        print(
            f"Files: {original_analysis['total_files']} → {current_files} ({reduction_files} reduced)"
        )
        print(
            f"Size: {original_analysis['total_size']:,} → {current_size:,} bytes ({reduction_size:,} reduced)"
        )
        print(f"Summary saved: {summary_path.name}")

    def run_consolidation(self, dry_run=False):
        """Run the complete consolidation process"""
        if dry_run:
            print("🔍 DRY RUN MODE - No changes will be made")
            return

        print("🗂️  Starting Documentation Consolidation...")
        print("=" * 50)

        # Load analysis results
        analysis_results = self.load_analysis_results()

        # Create directory structure
        self.create_directories()

        # Perform consolidation actions
        self.remove_empty_files(analysis_results)
        self.consolidate_todo_lists(analysis_results)
        self.archive_completion_reports(analysis_results)
        self.create_implementation_index(analysis_results)

        # Generate summary
        self.generate_consolidation_summary(analysis_results)


def main():
    """Main execution function"""
    docs_path = Path(__file__).parent.parent.parent / "docs"

    consolidator = DocsConsolidator(docs_path)

    # Ask for user confirmation
    print("📚 Documentation Consolidation Tool")
    print("=" * 40)
    print("This will:")
    print("1. Remove empty files")
    print("2. Consolidate TODO lists into master document")
    print("3. Archive old completion reports")
    print("4. Create documentation indexes")
    print()

    response = input("Proceed with consolidation? (y/N): ").strip().lower()

    if response == "y":
        consolidator.run_consolidation(dry_run=False)
    else:
        print("❌ Consolidation cancelled")


if __name__ == "__main__":
    main()
