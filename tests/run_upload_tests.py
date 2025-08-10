#!/usr/bin/env python3
"""
Test Runner for Data Upload Pipeline
====================================

Runs comprehensive tests for the data upload pipeline and generates reports.
"""

import argparse
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("test_results.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class TestRunner:
    """
    Comprehensive test runner for the data upload pipeline
    """

    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.01")
        self.tests_dir = self.project_root / "tests"
        self.reports_dir = self.project_root / "reports"
        self.reports_dir.mkdir(exist_ok=True)

    def run_unit_tests(self):
        """Run unit tests using pytest"""
        logger.info("Running unit tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    str(self.tests_dir / "test_data_upload_pipeline.py"),
                    "-v",
                    "--tb=short",
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            success = result.returncode == 0

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"unit_tests_{timestamp}.txt"

            with open(report_file, "w") as f:
                f.write(f"Unit Test Results - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
                f.write(f"\nReturn Code: {result.returncode}\n")

            if success:
                logger.info("✅ Unit tests passed")
            else:
                logger.error("❌ Unit tests failed")
                logger.error(f"Output: {result.stderr}")

            return success, report_file

        except Exception as e:
            logger.error(f"❌ Unit test execution failed: {e}")
            return False, None

    def run_integration_tests(self):
        """Run integration tests"""
        logger.info("Running integration tests...")

        try:
            result = subprocess.run(
                [
                    sys.executable,
                    str(self.tests_dir / "test_data_upload_integration.py"),
                ],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            success = result.returncode == 0

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"integration_tests_{timestamp}.txt"

            with open(report_file, "w") as f:
                f.write(f"Integration Test Results - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write("STDOUT:\n")
                f.write(result.stdout)
                f.write("\nSTDERR:\n")
                f.write(result.stderr)
                f.write(f"\nReturn Code: {result.returncode}\n")

            if success:
                logger.info("✅ Integration tests passed")
            else:
                logger.error("❌ Integration tests failed")
                logger.error(f"Output: {result.stderr}")

            return success, report_file

        except Exception as e:
            logger.error(f"❌ Integration test execution failed: {e}")
            return False, None

    def run_live_database_test(self):
        """Run live database test with actual upload"""
        logger.info("Running live database test...")

        try:
            # Import here to avoid import issues during testing
            from daily_data_uploader import DailyDataUploader

            uploader = DailyDataUploader()

            # Test database connection
            conn = uploader.get_database_connection()
            if not conn:
                logger.error("❌ Database connection failed")
                return False, None

            conn.close()
            logger.info("✅ Database connection successful")

            # Test finding CSV files
            available_tables = [
                "race_results",
                "horses",
                "races_cards",
                "jockey_stats",
                "trainer_stats",
                "racecard_details",
            ]

            found_files = {}
            for table in available_tables:
                files = uploader.find_csv_files(table)
                found_files[table] = len(files)
                if files:
                    logger.info(f"Found {len(files)} files for {table}")

            # Generate test report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"live_database_test_{timestamp}.txt"

            with open(report_file, "w") as f:
                f.write(f"Live Database Test Results - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write("Database Connection: SUCCESS\n\n")
                f.write("Available Files:\n")
                for table, count in found_files.items():
                    f.write(f"  {table}: {count} files\n")

                total_files = sum(found_files.values())
                f.write(f"\nTotal files available: {total_files}\n")

                if total_files > 0:
                    f.write("\n✅ Ready for data upload\n")
                else:
                    f.write("\n⚠️ No files found for upload\n")

            logger.info(
                f"Live test completed - found {sum(found_files.values())} files"
            )
            return True, report_file

        except Exception as e:
            logger.error(f"❌ Live database test failed: {e}")
            return False, None

    def run_performance_test(self):
        """Run performance tests on the upload pipeline"""
        logger.info("Running performance tests...")

        try:
            import time

            import pandas as pd

            from csv_column_mapper import ColumnMapper

            mapper = ColumnMapper()

            # Create large test dataset
            large_data = {
                "ID": list(range(50000)),
                "Race_ID": list(range(1000, 51000)),
                "Horse_ID": list(range(2000, 52000)),
                "Name": [f"Horse_{i}" for i in range(50000)],
                "jockey_ID": list(range(3000, 53000)),
                "jockey": [f"Jockey_{i}" for i in range(50000)],
                "trainer_ID": list(range(4000, 54000)),
                "trainer": [f"Trainer_{i}" for i in range(50000)],
                "Age": [5 + (i % 10) for i in range(50000)],
                "weight": [60.0 + (i % 20) for i in range(50000)],
                "Draw": [1 + (i % 20) for i in range(50000)],
                "Place": [1 + (i % 10) for i in range(50000)],
                "SP": [2.0 + (i % 50) / 10 for i in range(50000)],
                "finish_time": [120.0 + (i % 100) for i in range(50000)],
            }

            df = pd.DataFrame(large_data)

            # Test column mapping performance
            start_time = time.time()
            mapped_df = mapper.map_columns(df, "race_results")
            mapping_time = time.time() - start_time

            # Generate performance report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.reports_dir / f"performance_test_{timestamp}.txt"

            with open(report_file, "w") as f:
                f.write(f"Performance Test Results - {datetime.now()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(f"Dataset Size: {len(df):,} rows\n")
                f.write(f"Column Mapping Time: {mapping_time:.2f} seconds\n")
                f.write(f"Processing Rate: {len(df)/mapping_time:,.0f} rows/second\n")
                f.write(
                    f"Memory Usage: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB\n"
                )

                if mapping_time < 10:  # Should process 50k rows in under 10 seconds
                    f.write("\n✅ Performance: EXCELLENT\n")
                elif mapping_time < 30:
                    f.write("\n⚠️ Performance: ACCEPTABLE\n")
                else:
                    f.write("\n❌ Performance: POOR\n")

            logger.info(
                f"Performance test completed: {mapping_time:.2f}s for {len(df):,} rows"
            )
            return True, report_file

        except Exception as e:
            logger.error(f"❌ Performance test failed: {e}")
            return False, None

    def generate_comprehensive_report(self, test_results):
        """Generate comprehensive test report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"comprehensive_test_report_{timestamp}.md"

        passed_tests = sum(1 for success, _ in test_results.values() if success)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        with open(report_file, "w") as f:
            f.write(f"# Data Upload Pipeline Test Report\n\n")
            f.write(f"**Generated:** {datetime.now()}\n")
            f.write(
                f"**Success Rate:** {passed_tests}/{total_tests} ({success_rate:.1f}%)\n\n"
            )

            f.write("## Test Results Summary\n\n")
            for test_name, (success, report_path) in test_results.items():
                status = "✅ PASS" if success else "❌ FAIL"
                f.write(f"- **{test_name.replace('_', ' ').title()}:** {status}\n")
                if report_path:
                    f.write(f"  - Report: `{report_path.name}`\n")

            f.write("\n## Overall Assessment\n\n")
            if success_rate == 100:
                f.write(
                    "🎉 **EXCELLENT:** All tests passed! The data upload pipeline is fully operational.\n\n"
                )
            elif success_rate >= 80:
                f.write(
                    "⚠️ **GOOD:** Most tests passed with minor issues that should be addressed.\n\n"
                )
            elif success_rate >= 60:
                f.write(
                    "🔧 **NEEDS WORK:** Significant issues detected that require attention.\n\n"
                )
            else:
                f.write(
                    "🔥 **CRITICAL:** Multiple failures - pipeline needs major fixes.\n\n"
                )

            f.write("## Next Steps\n\n")
            if success_rate == 100:
                f.write("- Deploy to production environment\n")
                f.write("- Set up automated monitoring\n")
                f.write("- Schedule regular data uploads\n")
            else:
                f.write("- Review failed test reports\n")
                f.write("- Fix identified issues\n")
                f.write("- Re-run tests before deployment\n")

            f.write(f"\n## Report Files\n\n")
            for test_name, (_, report_path) in test_results.items():
                if report_path:
                    f.write(
                        f"- [{test_name.replace('_', ' ').title()}]({report_path.name})\n"
                    )

        logger.info(f"Comprehensive report saved: {report_file}")
        return report_file

    def run_all_tests(
        self,
        skip_unit=False,
        skip_integration=False,
        skip_live=False,
        skip_performance=False,
    ):
        """Run all tests and generate comprehensive report"""
        logger.info("🚀 Starting Comprehensive Data Upload Pipeline Tests")
        logger.info("=" * 70)

        test_results = {}

        # Run tests based on options
        if not skip_unit:
            test_results["unit_tests"] = self.run_unit_tests()

        if not skip_integration:
            test_results["integration_tests"] = self.run_integration_tests()

        if not skip_live:
            test_results["live_database_test"] = self.run_live_database_test()

        if not skip_performance:
            test_results["performance_test"] = self.run_performance_test()

        # Generate comprehensive report
        comprehensive_report = self.generate_comprehensive_report(test_results)

        # Final summary
        logger.info("=" * 70)
        logger.info("🎯 TEST EXECUTION COMPLETE")
        logger.info("=" * 70)

        passed_tests = sum(1 for success, _ in test_results.values() if success)
        total_tests = len(test_results)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

        logger.info(f"Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
        logger.info(f"Comprehensive Report: {comprehensive_report}")

        return test_results, comprehensive_report


def main():
    """Main function with command line arguments"""
    parser = argparse.ArgumentParser(description="Data Upload Pipeline Test Runner")

    parser.add_argument("--skip-unit", action="store_true", help="Skip unit tests")
    parser.add_argument(
        "--skip-integration", action="store_true", help="Skip integration tests"
    )
    parser.add_argument(
        "--skip-live", action="store_true", help="Skip live database tests"
    )
    parser.add_argument(
        "--skip-performance", action="store_true", help="Skip performance tests"
    )
    parser.add_argument(
        "--quick", action="store_true", help="Run only essential tests (unit + live)"
    )

    args = parser.parse_args()

    if args.quick:
        args.skip_integration = True
        args.skip_performance = True

    runner = TestRunner()
    test_results, report = runner.run_all_tests(
        skip_unit=args.skip_unit,
        skip_integration=args.skip_integration,
        skip_live=args.skip_live,
        skip_performance=args.skip_performance,
    )

    # Exit with appropriate code
    success_count = sum(1 for success, _ in test_results.values() if success)
    if success_count == len(test_results):
        sys.exit(0)  # All tests passed
    else:
        sys.exit(1)  # Some tests failed


if __name__ == "__main__":
    main()
