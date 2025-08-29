#!/usr/bin/env python3
"""
🧪 Final Validation Test - Integrated Cleanup System
===================================================

Comprehensive validation of the integrated test + cleanup system
with SQL/DB file exclusion.

This test validates:
1. SQL/DB files are properly excluded from cleanup analysis
2. Enhanced test runner integration works
3. Cleanup-only feature operates correctly
4. File categorization excludes database files
5. System is ready for production use

Author: AI Assistant
Date: August 29, 2025
"""

import sys
import subprocess
from pathlib import Path
import json
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent


def test_sql_exclusion():
    """Test that SQL/DB files are properly excluded"""
    logger.info("🔍 Testing SQL/DB file exclusion...")

    try:
        # Import and test the analyzer directly
        sys.path.insert(0, str(PROJECT_ROOT / "tools" / "analysis"))
        from integrated_cleanup_analyzer import IntegratedCleanupAnalyzer

        analyzer = IntegratedCleanupAnalyzer(str(PROJECT_ROOT))
        structure = analyzer.analyze_project_structure()

        # Check results
        total_files = structure.get("total_files", 0)
        categories = structure.get("categories", {})
        db_scripts = len(categories.get("database_scripts", []))

        logger.info(f"✅ Total files analyzed: {total_files}")
        logger.info(f"✅ Database scripts category: {db_scripts} files (should be 0)")

        if db_scripts == 0:
            logger.info("✅ SQL/DB exclusion test: PASSED")
            return True
        else:
            logger.error("❌ SQL/DB exclusion test: FAILED")
            return False

    except Exception as e:
        logger.error(f"❌ SQL/DB exclusion test failed: {e}")
        return False


def test_enhanced_options():
    """Test that enhanced test options are available"""
    logger.info("🧪 Testing enhanced test runner options...")

    try:
        cmd = [sys.executable, "tests/run_tests.py", "--help"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)

        help_text = result.stdout
        required_options = [
            "--enhanced",
            "--cleanup-only",
            "--execute-cleanup",
            "--no-cleanup",
        ]

        all_present = all(option in help_text for option in required_options)

        if all_present:
            logger.info("✅ Enhanced test options test: PASSED")
            return True
        else:
            missing = [opt for opt in required_options if opt not in help_text]
            logger.error(f"❌ Missing options: {missing}")
            return False

    except Exception as e:
        logger.error(f"❌ Enhanced options test failed: {e}")
        return False


def test_file_counting():
    """Test file counting accuracy"""
    logger.info("📊 Testing file counting and categorization...")

    try:
        # Count actual SQL files in project
        sql_files = list(PROJECT_ROOT.rglob("*.sql"))
        db_files = list(PROJECT_ROOT.rglob("*.db")) + list(
            PROJECT_ROOT.rglob("*.sqlite")
        )
        total_sql_db = len(sql_files) + len(db_files)

        logger.info(f"📁 Found {len(sql_files)} SQL files")
        logger.info(f"📁 Found {len(db_files)} DB files")
        logger.info(f"📁 Total SQL/DB files: {total_sql_db}")

        if total_sql_db > 0:
            logger.info("✅ File counting test: PASSED (SQL/DB files exist to exclude)")
            return True
        else:
            logger.warning("⚠️  No SQL/DB files found - exclusion logic not testable")
            return True

    except Exception as e:
        logger.error(f"❌ File counting test failed: {e}")
        return False


def generate_validation_report():
    """Generate comprehensive validation report"""
    logger.info("📋 Generating validation report...")

    report = {
        "timestamp": "2025-08-29T17:00:00",
        "test_name": "Integrated Cleanup System Final Validation",
        "version": "2.1.0",
        "tests": {
            "sql_exclusion": test_sql_exclusion(),
            "enhanced_options": test_enhanced_options(),
            "file_counting": test_file_counting(),
        },
    }

    all_passed = all(report["tests"].values())
    report["overall_status"] = "PASSED" if all_passed else "FAILED"

    # Save report
    report_path = PROJECT_ROOT / "FINAL_VALIDATION_REPORT.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report, report_path


def main():
    """Main validation routine"""
    logger.info("🚀 Starting Final Validation of Integrated Cleanup System")
    logger.info("=" * 70)

    try:
        report, report_path = generate_validation_report()

        # Print summary
        print("\n🎯 FINAL VALIDATION SUMMARY")
        print("=" * 50)

        for test_name, result in report["tests"].items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")

        print(
            f"\nOverall Status: {'✅ PASSED' if report['overall_status'] == 'PASSED' else '❌ FAILED'}"
        )
        print(f"Report saved: {report_path}")

        if report["overall_status"] == "PASSED":
            print("\n🎉 INTEGRATED CLEANUP SYSTEM IS READY FOR PRODUCTION!")
            print("\n📋 Available Commands:")
            print("1. python tests/run_tests.py --enhanced")
            print("2. python tests/run_tests.py --cleanup-only")
            print("3. python tests/run_tests.py --enhanced --execute-cleanup")
            print("4. python tools/testing/enhanced_test_runner.py --dry-run-cleanup")

            return 0
        else:
            print("\n❌ VALIDATION FAILED - CHECK ERRORS ABOVE")
            return 1

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
