#!/usr/bin/env python3
"""
CSV Backup System Demonstration
==============================

This script demonstrates the CSV backup functionality using existing ZIP files.
It shows how the system extracts, validates, and backs up CSV files.

Author: AI Assistant
Date: August 24, 2025
"""

import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools.pipeline.csv_backup_integration import CSVBackupIntegrator


def main():
    """Demonstrate CSV backup system with existing ZIP files"""
    print("🚀 CSV Backup System Demonstration")
    print("=" * 50)

    integrator = CSVBackupIntegrator()

    # Look for ZIP files to demonstrate with
    zip_files = []
    data_dir = Path("/home/jc/Documents/Horse-race-ai-v2.04/data")

    for zip_file in data_dir.rglob("*.zip"):
        if zip_file.is_file():
            zip_files.append(zip_file)

    if not zip_files:
        print("❌ No ZIP files found for demonstration")
        return

    # Use the first ZIP file found
    demo_zip = zip_files[0]
    print(f"📁 Demo ZIP file: {demo_zip.name}")
    print(f"📍 Location: {demo_zip}")

    # Determine data type from filename
    if "card" in demo_zip.name.lower():
        data_type = "cards"
    elif "result" in demo_zip.name.lower():
        data_type = "results"
    else:
        data_type = "cards"  # Default

    print(f"🏷️  Data type: {data_type}")

    # Use current date as expected date for demo
    expected_date = datetime.now().strftime("%Y-%m-%d")
    print(f"📅 Expected date: {expected_date}")

    print("\n🔄 Processing ZIP file with backup...")

    try:
        result = integrator.process_download_with_backup(
            demo_zip, data_type, expected_date
        )

        print("\n📊 Processing Results:")
        print(f"  ✅ Success: {result['success']}")
        print(
            f"  📦 ZIP Extracted: {result['backup_result'].get('zip_extracted', False)}"
        )
        print(
            f"  🗄️  Backup Created: {result['backup_result'].get('csv_backup_created', False)}"
        )
        print(
            f"  📈 CSV Files Found: {result['backup_result'].get('csv_files_count', 0)}"
        )

        if result.get("backup_result", {}).get("backup_archive_path"):
            backup_path = result["backup_result"]["backup_archive_path"]
            print(f"  💾 Backup Archive: {Path(backup_path).name}")

        if result.get("warnings"):
            print(f"  ⚠️  Warnings: {len(result['warnings'])}")
            for warning in result["warnings"]:
                print(f"    • {warning}")

        if result.get("errors"):
            print(f"  ❌ Errors: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"    • {error}")

        print(
            f"\n🚀 Continue Pipeline: {result.get('should_continue_pipeline', False)}"
        )

    except Exception as e:
        print(f"❌ Error during demonstration: {e}")

    # Show backup status after processing
    print("\n" + "=" * 50)
    print("📦 Current Backup Status:")

    try:
        status = integrator.get_backup_status()
        backup_status = status["backup_manager_status"]
        print(f"  📁 Backup Directory: {backup_status['backup_dir']}")
        print(f"  ✅ Directory Exists: {backup_status['backup_dir_exists']}")
        print(f"  📊 Total Backups: {backup_status['total_backups']}")

        if status.get("recent_backups"):
            print("\n📅 Recent Backups:")
            for backup in status["recent_backups"][:3]:
                print(f"    • {backup['archive_name']} ({backup['size_mb']} MB)")

    except Exception as e:
        print(f"❌ Error getting backup status: {e}")


if __name__ == "__main__":
    main()
