#!/usr/bin/env python3
"""
CSV Backup Integration - Pipeline Integration Layer
==================================================

Integrates CSV backup functionality with the existing pipeline system.
Called after ZIP file extraction to create raw CSV backups.

Author: AI Assistant
Date: August 24, 2025
"""

import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path - required for module imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Local imports after path setup
from tools.data_processing.csv_backup_manager import CSVBackupManager  # noqa: E402

logger = logging.getLogger(__name__)


class CSVBackupIntegrator:
    """Integrates CSV backup functionality with existing pipeline"""

    def __init__(self, base_path: str = "/home/jc/Documents/Horse-race-ai-v2.04"):
        self.base_path = Path(base_path)
        self.backup_manager = CSVBackupManager(base_path)
        # Note: Using backup manager's built-in validation for now

    def process_download_with_backup(
        self,
        zip_path: Path,
        data_type: str,
        expected_date: Optional[str] = None,
        automated: bool = True,
    ) -> Dict[str, Any]:
        """
        Process downloaded ZIP file with validation and backup creation

        Args:
            zip_path: Path to downloaded ZIP file
            data_type: Type of data ('cards' or 'results')
            expected_date: Expected date in YYYY-MM-DD format
            automated: If True, auto-continue on date mismatch; if False, prompt user

        Returns:
            Comprehensive processing result with validation and backup status
        """
        result = {
            "success": False,
            "zip_file": str(zip_path),
            "data_type": data_type,
            "expected_date": expected_date,
            "validation_result": {},
            "backup_result": {},
            "errors": [],
            "warnings": [],
            "should_continue_pipeline": False,
        }

        try:
            logger.info("Processing %s ZIP file: %s", data_type, zip_path.name)

            # Extract and backup ZIP file with built-in validation
            backup_result = self.backup_manager.extract_and_backup_zip(
                zip_path, data_type, expected_date
            )
            result["backup_result"] = backup_result

            if not backup_result.get("success", False):
                result["errors"].append("CSV backup creation failed")
                result["errors"].extend(backup_result.get("errors", []))
                logger.error("Backup failed for %s", zip_path.name)
                return result

            # Check for date mismatches in the file analysis
            file_analysis = backup_result.get("file_analysis", {})
            detected_date = file_analysis.get("detected_date")

            # Create a validation result for compatibility
            validation_result = {
                "valid": backup_result.get("zip_extracted", False),
                "detected_date": detected_date,
                "file_analysis": file_analysis,
                "warnings": backup_result.get("warnings", []),
            }
            result["validation_result"] = validation_result

            if expected_date and detected_date != expected_date:
                warning_msg = (
                    f"Date mismatch: Expected {expected_date}, "
                    f"but ZIP contains {detected_date} data"
                )
                result["warnings"].append(warning_msg)
                logger.warning(warning_msg)

                if automated:
                    # In automated mode, log the warning but continue processing
                    auto_msg = (
                        f"Automated mode: continuing processing despite "
                        f"date mismatch for {zip_path.name}"
                    )
                    logger.info(auto_msg)
                    result["should_continue_pipeline"] = True
                else:
                    # Interactive mode: ask user whether to continue
                    print(f"\n⚠️  {warning_msg}")
                    print(f"📁 ZIP file: {zip_path.name}")
                    analysis = file_analysis
                    print(f"📊 File analysis: {analysis}")

                    try:
                        choice = input("\nContinue with pipeline processing? (y/N): ")
                        user_choice = choice.lower()
                        if user_choice not in ["y", "yes"]:
                            msg = "User chose to skip pipeline processing"
                            result["warnings"].append(msg)
                            log_msg = "User skipped pipeline processing for %s"
                            logger.info(log_msg, zip_path.name)
                            result["should_continue_pipeline"] = False
                        else:
                            result["should_continue_pipeline"] = True
                    except EOFError:
                        # Handle EOF error gracefully in automated environments
                        eof_msg = "EOF error reading user input, defaulting to continue"
                        logger.warning(eof_msg)
                        result["should_continue_pipeline"] = True
            else:
                result["should_continue_pipeline"] = True

            # Compile final result
            result["success"] = backup_result.get("success", False)

            if result["success"]:
                logger.info("Successfully processed %s with backup", zip_path.name)
                print(f"✅ Processing complete: {zip_path.name}")
                archive_name = backup_result.get("archive_name", "Unknown")
                print(f"� CSV backup: {archive_name}")
                extract_path = backup_result.get("extraction_path", "Unknown")
                print(f"📁 Extracted to: {extract_path}")

                if result["should_continue_pipeline"]:
                    print("🚀 Ready for pipeline processing")
                else:
                    print("⏸️  Pipeline processing skipped (date mismatch)")

        except Exception as e:
            error_msg = f"Unexpected error processing {zip_path.name}: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg, exc_info=True)

        return result

    def backup_existing_extraction(
        self,
        extraction_dir: Path,
        data_type: str,
        original_zip_name: str,
        file_date: str,
    ) -> Dict[str, Any]:
        """
        Create backup of already extracted CSV files

        Useful when ZIP was extracted but backup wasn't created
        """
        result = {
            "success": False,
            "backup_created": False,
            "errors": [],
            "backup_path": None,
        }

        try:
            csv_files = self.backup_manager._find_csv_files(extraction_dir)

            if not csv_files:
                result["errors"].append(f"No CSV files found in {extraction_dir}")
                return result

            backup_result = self.backup_manager._create_csv_backup(
                csv_files, data_type, original_zip_name, file_date
            )

            result.update(backup_result)
            result["backup_created"] = backup_result.get("success", False)

            if result["backup_created"]:
                archive_name = backup_result.get("archive_name")
                logger.info("Created backup for existing extraction: %s", archive_name)

        except Exception as e:
            error_msg = f"Failed to backup existing extraction: {e}"
            result["errors"].append(error_msg)
            logger.error(error_msg)

        return result

    def get_backup_status(self) -> Dict[str, Any]:
        """Get comprehensive backup status"""
        return {
            "backup_manager_status": {
                "backup_dir": str(self.backup_manager.raw_csv_backup_dir),
                "backup_dir_exists": self.backup_manager.raw_csv_backup_dir.exists(),
                "total_backups": len(self.backup_manager.list_csv_backups()),
            },
            "recent_backups": self.backup_manager.list_csv_backups()[:5],
        }


def main():
    """Simple CLI interface for CSV backup integration"""
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="CSV Backup Integration")
    parser.add_argument("command", choices=["process", "backup", "status"])
    parser.add_argument("--zip-path", type=Path)
    parser.add_argument("--data-type", choices=["cards", "results"])
    parser.add_argument("--expected-date")

    args = parser.parse_args()
    integrator = CSVBackupIntegrator()

    if args.command == "process":
        if not args.zip_path or not args.data_type:
            print("Error: --zip-path and --data-type required")
            sys.exit(1)

        expected_date = args.expected_date or datetime.now().strftime("%Y-%m-%d")
        result = integrator.process_download_with_backup(
            args.zip_path, args.data_type, expected_date
        )

        print("\n📋 Processing Result:")
        print(f"  Success: {result['success']}")
        print(f"  Continue Pipeline: {result['should_continue_pipeline']}")

    elif args.command == "status":
        status = integrator.get_backup_status()
        print("\n� Backup Integration Status:")
        backup_status = status["backup_manager_status"]
        print(f"  Backup Directory: {backup_status['backup_dir']}")
        print(f"  Directory Exists: {backup_status['backup_dir_exists']}")
        print(f"  Total Backups: {backup_status['total_backups']}")


if __name__ == "__main__":
    main()
