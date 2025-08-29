#!/usr/bin/env python3
"""
👀 Documentation Consolidation Preview
=====================================

Shows what will be consolidated without making any changes.
This allows you to review the consolidation plan before execution.

Author: AI Assistant
Date: August 29, 2025
"""

import json
from pathlib import Path
from datetime import datetime


def preview_consolidation():
    """Preview what consolidation will do"""
    docs_path = Path(__file__).parent.parent.parent / "docs"
    results_file = docs_path / "CONSOLIDATION_ANALYSIS_RESULTS.json"

    if not results_file.exists():
        print("❌ Analysis results not found. Run docs_consolidation_analyzer.py first")
        return

    with open(results_file, "r") as f:
        analysis = json.load(f)

    print("👀 DOCUMENTATION CONSOLIDATION PREVIEW")
    print("=" * 50)
    print(
        f"Current State: {analysis['total_files']} files, {analysis['total_size']:,} bytes"
    )
    print()

    # Preview empty file removal
    empty_files = analysis.get("empty_files", [])
    if empty_files:
        print("🗑️  EMPTY FILES TO REMOVE:")
        for empty_file in empty_files:
            print(f"  ❌ {empty_file['path']}")
        print()

    # Preview TODO consolidation
    todo_files = analysis["categories"].get("todo_lists", [])
    if len(todo_files) >= 3:
        print(f"📝 TODO LISTS TO CONSOLIDATE ({len(todo_files)} files):")
        total_todo_size = sum(f["size"] for f in todo_files)
        print(f"  Total size: {total_todo_size:,} bytes")
        for todo_file in todo_files[:10]:  # Show first 10
            title = todo_file["content_summary"]["title"] or "Untitled"
            print(f"  • {todo_file['path']} - {title[:50]}...")
        if len(todo_files) > 10:
            print(f"  ... and {len(todo_files) - 10} more files")
        print(f"  → Will create: MASTER_TODO_CONSOLIDATED.md")
        print(f"  → Will archive originals to: archive/old_todos/")
        print()

    # Preview completion report archival
    completion_files = analysis["categories"].get("completion_reports", [])
    if len(completion_files) >= 5:
        print(f"📦 COMPLETION REPORTS TO ARCHIVE ({len(completion_files)} files):")
        total_completion_size = sum(f["size"] for f in completion_files)
        print(f"  Total size: {total_completion_size:,} bytes")
        for comp_file in completion_files[:5]:  # Show first 5
            title = comp_file["content_summary"]["title"] or "Untitled"
            modified = datetime.fromtimestamp(comp_file["modified"]).strftime(
                "%Y-%m-%d"
            )
            print(f"  • {comp_file['path']} ({modified}) - {title[:40]}...")
        if len(completion_files) > 5:
            print(f"  ... and {len(completion_files) - 5} more files")
        print(f"  → Will create: summaries/COMPLETION_REPORTS_INDEX.md")
        print(f"  → Will archive to: archive/completion_reports/")
        print()

    # Preview implementation index
    impl_files = analysis["categories"].get("implementation_docs", [])
    if len(impl_files) >= 3:
        print(f"📑 IMPLEMENTATION DOCS FOR INDEX ({len(impl_files)} files):")
        for impl_file in impl_files:
            title = impl_file["content_summary"]["title"] or "Untitled"
            print(f"  • {impl_file['path']} - {title[:50]}...")
        print(f"  → Will create: summaries/IMPLEMENTATION_DOCS_INDEX.md")
        print()

    # Calculate potential savings
    potential_reduction = 0
    files_affected = 0

    if empty_files:
        files_affected += len(empty_files)

    if len(todo_files) >= 3:
        potential_reduction += sum(f["size"] for f in todo_files) * 0.7
        files_affected += len(todo_files) - 1  # -1 because we create master

    if len(completion_files) >= 5:
        potential_reduction += sum(f["size"] for f in completion_files) * 0.8
        files_affected += len(completion_files) - 1  # -1 because we create index

    print("📊 ESTIMATED IMPACT:")
    print(f"  Files reduced: ~{files_affected}")
    print(
        f"  Size reduction: ~{potential_reduction:,.0f} bytes ({potential_reduction/analysis['total_size']*100:.1f}%)"
    )
    print()

    print("📁 NEW DIRECTORY STRUCTURE:")
    print("  docs/")
    print("  ├── archive/")
    print("  │   ├── completion_reports/")
    print("  │   ├── old_todos/")
    print("  │   └── implementation_history/")
    print("  ├── summaries/")
    print("  │   ├── COMPLETION_REPORTS_INDEX.md")
    print("  │   └── IMPLEMENTATION_DOCS_INDEX.md")
    print("  ├── MASTER_TODO_CONSOLIDATED.md")
    print("  └── [remaining active docs]")
    print()

    print("🔧 TO PROCEED:")
    print("  python3 tools/analysis/docs_consolidator.py")


if __name__ == "__main__":
    preview_consolidation()
