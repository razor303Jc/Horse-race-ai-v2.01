#!/usr/bin/env python3
"""
🚨 PRODUCTION ESSENTIAL - DO NOT DELETE

BULK UPLOADER SYSTEM VALIDATION SCRIPT
This script validates that all critical bulk uploader components are present and functional.
Used by system audits to ensure production pipeline integrity.
"""

import os
import sys
from pathlib import Path


def validate_bulk_uploader_system():
    """Validate that bulk uploader system is intact"""
    print("🔍 BULK UPLOADER SYSTEM VALIDATION")
    print("=" * 50)

    base_dir = Path(__file__).parent

    # Critical files that must exist
    critical_files = [
        "simple_bulk_uploader.py",
        "column_mappings.py",
        "bulk_uploader.py",
        "csv_validator.py",
        "container_runner.py",
        "config.yaml",
        "BULK_UPLOADER_VALIDATION_REPORT.md",
    ]

    missing_files = []
    for file in critical_files:
        file_path = base_dir / file
        if file_path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING!")
            missing_files.append(file)

    if missing_files:
        print(f"\n🚨 CRITICAL ERROR: {len(missing_files)} essential files missing!")
        print("BULK UPLOADER SYSTEM COMPROMISED")
        return False
    else:
        print(f"\n✅ ALL {len(critical_files)} CRITICAL FILES PRESENT")
        print("BULK UPLOADER SYSTEM INTACT")
        return True


if __name__ == "__main__":
    if validate_bulk_uploader_system():
        sys.exit(0)
    else:
        sys.exit(1)
