#!/usr/bin/env python3
"""
👀 Root Directory Cleanup Preview
=================================

Shows what will be moved and what will be protected in root cleanup.

Author: AI Assistant
Date: August 29, 2025
"""

import json
from pathlib import Path


def preview_root_cleanup():
    """Preview root directory cleanup plan"""
    project_root = Path(__file__).parent.parent.parent
    results_file = project_root / "ROOT_CLEANUP_ANALYSIS.json"

    if not results_file.exists():
        print("❌ Analysis results not found. Run root_directory_analyzer.py first")
        return

    with open(results_file, "r") as f:
        analysis = json.load(f)

    print("👀 ROOT DIRECTORY CLEANUP PREVIEW")
    print("=" * 50)
    print(f"Current files in root: {analysis['total_files']}")
    print()

    # Show protected files
    protected_files = analysis.get("protected_files", [])
    print("🔒 PROTECTED FILES (WILL STAY IN ROOT):")
    for pfile in protected_files:
        print(f"  ✅ {pfile['path']} - {pfile['reason']}")
    print()

    # Show move plan by priority
    move_candidates = analysis.get("move_candidates", {})

    print("📦 FILES TO MOVE:")

    priorities = ["high", "medium", "low"]
    for priority in priorities:
        files_at_priority = []

        for target_dir, files in move_candidates.items():
            priority_files = [f for f in files if f["priority"] == priority]
            if priority_files:
                files_at_priority.extend([(target_dir, f) for f in priority_files])

        if files_at_priority:
            print(f"\n{priority.upper()} PRIORITY ({len(files_at_priority)} files):")

            # Group by destination
            by_dest = {}
            for target_dir, file_info in files_at_priority:
                if target_dir not in by_dest:
                    by_dest[target_dir] = []
                by_dest[target_dir].append(file_info)

            for target_dir, files in by_dest.items():
                print(f"  📁 → {target_dir}/ ({len(files)} files)")
                for file_info in files[:5]:  # Show first 5
                    print(f"    • {file_info['path']}")
                if len(files) > 5:
                    print(f"    ... and {len(files) - 5} more files")

    # Show cleanup opportunities
    cleanup_opportunities = analysis.get("cleanup_opportunities", [])
    if cleanup_opportunities:
        print(f"\n🗑️  CLEANUP OPPORTUNITIES:")
        for opportunity in cleanup_opportunities:
            print(f"  ❓ {opportunity['path']} - {opportunity['reason']}")

    print(f"\n📊 FINAL RESULT:")
    print(f"  Root files after cleanup: {len(protected_files)}")
    total_move = sum(len(files) for files in move_candidates.values())
    print(f"  Files to be moved: {total_move}")
    print(f"  Organization: Much improved!")

    print(f"\n🔧 TO PROCEED:")
    print("  python3 tools/analysis/root_directory_cleanup.py")


if __name__ == "__main__":
    preview_root_cleanup()
