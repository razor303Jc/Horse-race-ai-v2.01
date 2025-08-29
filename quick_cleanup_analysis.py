#!/usr/bin/env python3
"""
Quick Cleanup Analysis
Fast analysis of cleanup potential based on cross-reference findings.
"""

import json
from pathlib import Path
from collections import defaultdict


def quick_cleanup_analysis():
    """Quick analysis of cleanup potential."""
    base_path = Path("/home/jc/Documents/Horse-race-ai-v2.04")

    print("🔍 QUICK CLEANUP ANALYSIS")
    print("=" * 50)

    # Load critical files for protection
    report_path = base_path / "CRITICAL_FILES_CROSS_REFERENCE_REPORT.json"
    protected_files = set()

    if report_path.exists():
        with open(report_path, "r") as f:
            data = json.load(f)

        for file_path in data.get("critical_files", {}):
            protected_files.add(file_path)

        print(f"✅ {len(protected_files)} critical files identified for protection")

        # Show cleanup stats from the report
        unwanted_stats = data.get("unwanted_files_stats", {})
        total_files = data.get("total_unwanted_files", 0)
        total_size = data.get("total_potential_savings_mb", 0)

        print(f"\n📊 CLEANUP POTENTIAL:")
        print(f"   🗑️  Unwanted files: {total_files:,}")
        print(f"   💾 Potential savings: {total_size:.1f} MB")

        print(f"\n📋 CLEANUP BREAKDOWN:")
        for category, stats in sorted(
            unwanted_stats.items(), key=lambda x: x[1]["size_mb"], reverse=True
        ):
            files = stats["files"]
            size_mb = stats["size_mb"]
            print(f"   • {category}: {files:,} files ({size_mb:.1f} MB)")

        print(f"\n🛡️  PROTECTION SUMMARY:")
        protection_recs = data.get("protection_recommendations", {})

        critical_never_delete = protection_recs.get("critical_never_delete", [])
        important_careful_review = protection_recs.get("important_careful_review", [])

        print(f"   🔴 Critical (Never Delete): {len(critical_never_delete)} files")
        for file_path in critical_never_delete[:5]:
            print(f"      - {file_path}")
        if len(critical_never_delete) > 5:
            print(f"      ... and {len(critical_never_delete) - 5} more")

        print(
            f"\n   🟡 Important (Careful Review): {len(important_careful_review)} files"
        )
        for file_path in important_careful_review[:5]:
            print(f"      - {file_path}")
        if len(important_careful_review) > 5:
            print(f"      ... and {len(important_careful_review) - 5} more")

        print(f"\n💡 RECOMMENDATIONS:")
        print(
            f"   1. 🔧 Implement elevated protection for {len(critical_never_delete)} critical files"
        )
        print(f"   2. 🗑️  Safe to cleanup: {total_files:,} unwanted files")
        print(f"   3. 💾 Potential space savings: {total_size:.1f} MB")
        print(f"   4. 🎯 Focus on largest categories: Build Artifacts, Backup Files")

        # Generate simple cleanup commands
        print(f"\n🚀 SAFE CLEANUP COMMANDS:")
        print(f"   # Remove backup files (safe)")
        print(f"   find . -name '*backup*' -type f | head -10")
        print(f"   ")
        print(f"   # Remove cache files (safe)")
        print(f"   find . -name '__pycache__' -type d | head -10")
        print(f"   ")
        print(f"   # Remove build artifacts (safe)")
        print(f"   find . -name '*.egg-info' -type d | head -10")

    else:
        print("❌ Cross-reference report not found")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    quick_cleanup_analysis()
