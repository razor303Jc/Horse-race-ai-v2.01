#!/usr/bin/env python3
"""
Simple Integration Test for Current Data Upload System
=====================================================

Tests the actual current implementation of the data upload system.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_current_uploader():
    """Test the current data uploader implementation"""
    logger.info("🧪 Testing Current Data Upload Implementation")
    logger.info("=" * 60)

    try:
        # Import the current uploader
        from daily_data_uploader import DailyDataUploader

        uploader = DailyDataUploader()
        logger.info("✅ DailyDataUploader imported successfully")

        # Test database connection
        logger.info("Testing database connection...")
        conn = uploader.get_connection()
        if conn:
            conn.close()
            logger.info("✅ Database connection successful")
        else:
            logger.error("❌ Database connection failed")
            return False

        # Check for available files
        logger.info("Checking for available CSV files...")
        available_files, missing_files = uploader.check_daily_files()

        total_available = len(available_files)
        total_missing = len(missing_files)

        logger.info(f"📊 File Status:")
        logger.info(f"   Available: {total_available} files")
        logger.info(f"   Missing: {total_missing} files")

        if available_files:
            logger.info("Available files:")
            for file_path, info in available_files.items():
                logger.info(
                    f"  - {file_path} → {info['table']} ({info['size']:,} bytes)"
                )

        if missing_files:
            logger.info("Missing files:")
            for file_path in missing_files:
                logger.info(f"  - {file_path}")

        # Test upload if files are available
        if total_available > 0:
            logger.info("🚀 Testing data upload...")
            success, summary = uploader.upload_daily_data(mode="append")

            if success:
                logger.info("✅ Data upload test successful!")
                logger.info("Upload summary:")
                for table, stats in summary.items():
                    logger.info(f"  - {table}: {stats}")
            else:
                logger.error("❌ Data upload test failed")
                return False
        else:
            logger.info("⚠️ No files available for upload test")

        # Test database summary
        logger.info("Testing database summary...")
        uploader.show_database_summary()

        logger.info("✅ All tests completed successfully!")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False


def test_column_mapper():
    """Test the column mapper"""
    logger.info("🧪 Testing Column Mapper")
    logger.info("=" * 40)

    try:
        from csv_column_mapper import ColumnMapper

        mapper = ColumnMapper()
        logger.info("✅ ColumnMapper imported successfully")

        # Check available mappings
        if hasattr(mapper, "column_mappings"):
            tables = list(mapper.column_mappings.keys())
            logger.info(f"📊 Available table mappings: {len(tables)}")
            for table in tables:
                logger.info(f"  - {table}")
        elif hasattr(mapper, "table_mappings"):
            tables = list(mapper.table_mappings.keys())
            logger.info(f"📊 Available table mappings: {len(tables)}")
            for table in tables:
                logger.info(f"  - {table}")
        else:
            logger.warning("⚠️ No table mappings found")

        logger.info("✅ Column mapper test completed!")
        return True

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Test failed with exception: {e}")
        return False


def test_system_integration():
    """Test overall system integration"""
    logger.info("🧪 Testing System Integration")
    logger.info("=" * 50)

    try:
        # Test imports
        from csv_column_mapper import ColumnMapper
        from daily_data_uploader import DailyDataUploader

        # Test basic functionality
        uploader = DailyDataUploader()
        mapper = ColumnMapper()

        # Check database
        conn = uploader.get_connection()
        database_ok = conn is not None
        if conn:
            conn.close()

        # Check downloads directory
        downloads_ok = uploader.daily_data_dir.exists()

        # Check for CSV files
        available_files, _ = uploader.check_daily_files()
        files_ok = len(available_files) > 0

        # Results
        results = {
            "Database Connection": database_ok,
            "Downloads Directory": downloads_ok,
            "CSV Files Available": files_ok,
            "Modules Import": True,
        }

        logger.info("Integration Test Results:")
        passed_tests = 0
        for test_name, passed in results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"  {test_name}: {status}")
            if passed:
                passed_tests += 1

        success_rate = (passed_tests / len(results)) * 100
        logger.info(
            f"Overall Success Rate: {passed_tests}/{len(results)} ({success_rate:.1f}%)"
        )

        if success_rate >= 75:
            logger.info("🎉 System integration looks good!")
            return True
        else:
            logger.warning("⚠️ System integration needs attention")
            return False

    except Exception as e:
        logger.error(f"❌ Integration test failed: {e}")
        return False


def main():
    """Run all simple tests"""
    logger.info("🚀 Starting Simple Data Upload Integration Tests")
    logger.info("=" * 70)

    start_time = datetime.now()

    tests = [
        ("Column Mapper", test_column_mapper),
        ("Current Uploader", test_current_uploader),
        ("System Integration", test_system_integration),
    ]

    results = {}

    for test_name, test_func in tests:
        logger.info(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False

    # Final summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    logger.info("\n" + "=" * 70)
    logger.info("🎯 FINAL TEST RESULTS")
    logger.info("=" * 70)

    passed_tests = sum(results.values())
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{test_name}: {status}")

    logger.info("=" * 70)
    logger.info(f"Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    logger.info(f"Duration: {duration:.2f} seconds")

    if success_rate == 100:
        logger.info("🎉 ALL TESTS PASSED! System is ready!")
    elif success_rate >= 75:
        logger.info("✅ Most tests passed - system is mostly ready")
    else:
        logger.info("⚠️ Multiple test failures - system needs attention")

    # Exit with appropriate code
    if success_rate >= 75:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
