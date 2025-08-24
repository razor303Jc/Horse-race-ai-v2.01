#!/usr/bin/env python3
"""
Real-Time Data Pipeline Testing with Monitoring
🧪 TEST: Monitor data cleaning and upload process with detailed reporting

This script will:
1. Monitor for new data files
2. Apply enhanced data cleaning pipeline
3. Test database upload
4. Generate comprehensive problem report
"""

import sys
import time
import json
import logging
from pathlib import Path
from datetime import datetime
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.data_processing.simplified_data_pipeline import SimplifiedDataPipeline


class RealTimeDataTester:
    """Real-time data pipeline testing with comprehensive monitoring"""

    def __init__(self):
        self.logger = self._setup_logging()
        self.test_results = {
            "test_start_time": datetime.now().isoformat(),
            "problems_found": [],
            "successful_operations": [],
            "data_quality_issues": [],
            "upload_issues": [],
            "performance_metrics": {},
        }
        self.data_dir = Path("data/daily_downloads")
        self.watch_files = [
            "complete_mapped_races.csv",
            "complete_mapped_records.csv",
            "complete_mapped_horses.csv",
            "complete_mapped_jockeys_stats.csv",
            "complete_mapped_trainers_stats.csv",
        ]

    def _setup_logging(self):
        """Setup comprehensive logging"""
        log_file = f"data/logs/realtime_pipeline_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(),
            ],
        )
        return logging.getLogger(__name__)

    def analyze_data_before_cleaning(self, file_path):
        """Analyze data quality issues before cleaning"""
        self.logger.info(f"🔍 Analyzing data quality for {file_path}")

        try:
            df = pd.read_csv(file_path)
            issues = []

            # Check for dash symbols
            dash_count = 0
            dash_columns = []
            for col in df.columns:
                col_dashes = (df[col].astype(str) == "-").sum()
                dash_count += col_dashes
                if col_dashes > 0:
                    dash_columns.append(f"{col}({col_dashes})")

            if dash_count > 0:
                issues.append(
                    f"Dash symbols: {dash_count} found in {len(dash_columns)} columns"
                )
                self.logger.warning(
                    f"  📊 Found {dash_count} dash symbols in: {', '.join(dash_columns[:5])}"
                )

            # Check for NULL values
            null_count = df.isnull().sum().sum()
            if null_count > 0:
                issues.append(f"NULL values: {null_count}")
                self.logger.warning(f"  📊 Found {null_count} NULL values")

            # Check for empty strings
            empty_count = 0
            for col in df.columns:
                empty_count += (df[col].astype(str) == "").sum()
            if empty_count > 0:
                issues.append(f"Empty strings: {empty_count}")

            # Check for weight format issues (UK format like "10-2")
            weight_issues = 0
            for col in df.columns:
                if "weight" in col.lower():
                    uk_format_pattern = df[col].astype(str).str.match(r"^\d+-\d+$")
                    weight_issues += uk_format_pattern.sum()
            if weight_issues > 0:
                issues.append(f"UK weight format: {weight_issues}")

            # Check for percentage strings
            percentage_issues = 0
            for col in df.columns:
                if df[col].dtype == "object":
                    pct_pattern = df[col].astype(str).str.contains("%", na=False)
                    percentage_issues += pct_pattern.sum()
            if percentage_issues > 0:
                issues.append(f"Percentage strings: {percentage_issues}")

            analysis = {
                "file": file_path.name,
                "rows": len(df),
                "columns": len(df.columns),
                "issues_found": issues,
                "total_issues": dash_count
                + null_count
                + empty_count
                + weight_issues
                + percentage_issues,
            }

            self.test_results["data_quality_issues"].append(analysis)
            self.logger.info(f"  📋 Analysis complete: {len(issues)} issue types found")

            return analysis

        except Exception as e:
            error_msg = f"Failed to analyze {file_path}: {e}"
            self.logger.error(f"❌ {error_msg}")
            self.test_results["problems_found"].append(error_msg)
            return None

    def wait_for_data_files(self, timeout_minutes=10):
        """Wait for data files to appear"""
        self.logger.info(
            f"⏳ Waiting for data files (timeout: {timeout_minutes} minutes)"
        )
        self.logger.info(f"📂 Monitoring directory: {self.data_dir}")
        self.logger.info(f"📋 Looking for files: {', '.join(self.watch_files)}")

        start_time = time.time()
        timeout_seconds = timeout_minutes * 60

        while time.time() - start_time < timeout_seconds:
            available_files = []
            for file_name in self.watch_files:
                file_path = self.data_dir / file_name
                if file_path.exists():
                    available_files.append(file_name)

            if len(available_files) > 0:
                self.logger.info(
                    f"✅ Found {len(available_files)} files: {', '.join(available_files)}"
                )
                return available_files

            self.logger.info("⏳ No files found yet, waiting 10 seconds...")
            time.sleep(10)

        self.logger.warning(f"⏰ Timeout reached after {timeout_minutes} minutes")
        return []

    def test_cleaning_pipeline(self):
        """Test the enhanced data cleaning pipeline"""
        self.logger.info("🧹 Testing Enhanced Data Cleaning Pipeline")

        try:
            start_time = time.time()

            # Initialize the simplified pipeline
            pipeline = SimplifiedDataPipeline()

            # Run the cleaning pipeline
            success = pipeline.run_data_cleaning_pipeline()

            end_time = time.time()
            processing_time = end_time - start_time

            self.test_results["performance_metrics"]["cleaning_time"] = processing_time

            if success:
                self.logger.info(
                    f"✅ Cleaning pipeline completed successfully in {processing_time:.2f} seconds"
                )
                self.test_results["successful_operations"].append(
                    f"Data cleaning completed in {processing_time:.2f}s"
                )
                return True
            else:
                error_msg = "Cleaning pipeline failed"
                self.logger.error(f"❌ {error_msg}")
                self.test_results["problems_found"].append(error_msg)
                if hasattr(pipeline, "errors") and pipeline.errors:
                    for error in pipeline.errors:
                        self.test_results["problems_found"].append(
                            f"Cleaning error: {error}"
                        )
                return False

        except Exception as e:
            error_msg = f"Cleaning pipeline crashed: {e}"
            self.logger.error(f"💥 {error_msg}")
            self.test_results["problems_found"].append(error_msg)
            return False

    def test_database_upload(self):
        """Test database upload process"""
        self.logger.info("📤 Testing Database Upload")

        try:
            # Import upload function
            from tools.data_processing.upload_mapped_data import upload_csv_to_database

            upload_tasks = [
                ("data/daily_downloads/complete_mapped_races.csv", "races"),
                ("data/daily_downloads/complete_mapped_records.csv", "records"),
                ("data/daily_downloads/complete_mapped_horses.csv", "horses"),
                (
                    "data/daily_downloads/complete_mapped_jockeys_stats.csv",
                    "jockeys_stats",
                ),
                (
                    "data/daily_downloads/complete_mapped_trainers_stats.csv",
                    "trainers_stats",
                ),
            ]

            successful_uploads = 0
            failed_uploads = 0

            for csv_file, table_name in upload_tasks:
                file_path = Path(csv_file)
                if file_path.exists():
                    try:
                        self.logger.info(
                            f"  📊 Testing upload: {csv_file} → {table_name}"
                        )

                        start_time = time.time()
                        upload_csv_to_database(csv_file, table_name)
                        end_time = time.time()

                        upload_time = end_time - start_time
                        successful_uploads += 1

                        success_msg = f"Upload {table_name}: {upload_time:.2f}s"
                        self.logger.info(f"  ✅ {success_msg}")
                        self.test_results["successful_operations"].append(success_msg)

                    except Exception as e:
                        error_msg = f"Upload {table_name} failed: {e}"
                        self.logger.error(f"  ❌ {error_msg}")
                        self.test_results["upload_issues"].append(error_msg)
                        failed_uploads += 1
                else:
                    warning_msg = f"File not found for upload: {csv_file}"
                    self.logger.warning(f"  ⚠️ {warning_msg}")
                    self.test_results["upload_issues"].append(warning_msg)
                    failed_uploads += 1

            self.test_results["performance_metrics"]["uploads"] = {
                "successful": successful_uploads,
                "failed": failed_uploads,
                "total": len(upload_tasks),
            }

            if failed_uploads == 0:
                self.logger.info("✅ All database uploads completed successfully")
                return True
            else:
                self.logger.warning(
                    f"⚠️ {failed_uploads} uploads failed, {successful_uploads} succeeded"
                )
                return False

        except Exception as e:
            error_msg = f"Database upload testing crashed: {e}"
            self.logger.error(f"💥 {error_msg}")
            self.test_results["problems_found"].append(error_msg)
            return False

    def generate_final_report(self):
        """Generate comprehensive final report"""
        self.test_results["test_end_time"] = datetime.now().isoformat()

        self.logger.info("\n" + "=" * 80)
        self.logger.info("📋 COMPREHENSIVE DATA PIPELINE TEST REPORT")
        self.logger.info("=" * 80)

        # Summary
        total_problems = len(self.test_results["problems_found"]) + len(
            self.test_results["upload_issues"]
        )
        total_successes = len(self.test_results["successful_operations"])

        self.logger.info(f"🎯 SUMMARY:")
        self.logger.info(f"  ✅ Successful operations: {total_successes}")
        self.logger.info(f"  ❌ Problems found: {total_problems}")

        # Data Quality Issues
        if self.test_results["data_quality_issues"]:
            self.logger.info(f"\n🔍 DATA QUALITY ANALYSIS:")
            for analysis in self.test_results["data_quality_issues"]:
                self.logger.info(
                    f"  📊 {analysis['file']}: {analysis['rows']} rows, {analysis['total_issues']} issues"
                )
                for issue in analysis["issues_found"]:
                    self.logger.info(f"    - {issue}")

        # Problems Found
        if self.test_results["problems_found"]:
            self.logger.info(f"\n❌ PROBLEMS ENCOUNTERED:")
            for i, problem in enumerate(self.test_results["problems_found"], 1):
                self.logger.info(f"  {i}. {problem}")

        # Upload Issues
        if self.test_results["upload_issues"]:
            self.logger.info(f"\n📤 UPLOAD ISSUES:")
            for i, issue in enumerate(self.test_results["upload_issues"], 1):
                self.logger.info(f"  {i}. {issue}")

        # Performance Metrics
        if self.test_results["performance_metrics"]:
            self.logger.info(f"\n⚡ PERFORMANCE METRICS:")
            metrics = self.test_results["performance_metrics"]
            if "cleaning_time" in metrics:
                self.logger.info(
                    f"  🧹 Cleaning time: {metrics['cleaning_time']:.2f} seconds"
                )
            if "uploads" in metrics:
                uploads = metrics["uploads"]
                self.logger.info(
                    f"  📤 Uploads: {uploads['successful']}/{uploads['total']} successful"
                )

        # Successful Operations
        if self.test_results["successful_operations"]:
            self.logger.info(f"\n✅ SUCCESSFUL OPERATIONS:")
            for i, success in enumerate(self.test_results["successful_operations"], 1):
                self.logger.info(f"  {i}. {success}")

        self.logger.info("=" * 80)

        # Save detailed report to file
        report_file = f"data/logs/pipeline_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, "w") as f:
            json.dump(self.test_results, f, indent=2)

        self.logger.info(f"📄 Detailed report saved to: {report_file}")

        return total_problems == 0

    def run_comprehensive_test(self):
        """Run the complete real-time data pipeline test"""
        self.logger.info("🚀 Starting Real-Time Data Pipeline Test")
        self.logger.info("=" * 60)

        try:
            # Step 1: Wait for data files
            self.logger.info("Step 1: Waiting for data files...")
            available_files = self.wait_for_data_files(timeout_minutes=15)

            if not available_files:
                self.test_results["problems_found"].append(
                    "No data files found within timeout period"
                )
                self.generate_final_report()
                return False

            # Step 2: Analyze data quality before cleaning
            self.logger.info("Step 2: Analyzing data quality...")
            for file_name in available_files:
                file_path = self.data_dir / file_name
                self.analyze_data_before_cleaning(file_path)

            # Step 3: Test cleaning pipeline
            self.logger.info("Step 3: Testing data cleaning...")
            cleaning_success = self.test_cleaning_pipeline()

            # Step 4: Test database upload
            self.logger.info("Step 4: Testing database upload...")
            upload_success = self.test_database_upload()

            # Step 5: Generate final report
            self.logger.info("Step 5: Generating final report...")
            overall_success = self.generate_final_report()

            if overall_success:
                self.logger.info("🎉 All tests passed successfully!")
                return True
            else:
                self.logger.warning(
                    "⚠️ Some issues were found. Check the report for details."
                )
                return False

        except Exception as e:
            error_msg = f"Test framework crashed: {e}"
            self.logger.error(f"💥 {error_msg}")
            self.test_results["problems_found"].append(error_msg)
            self.generate_final_report()
            return False


def main():
    """Run the real-time data pipeline test"""
    print("🧪 Real-Time Data Pipeline Testing")
    print("=" * 50)
    print("📋 This test will:")
    print("  1. Monitor for new data files")
    print("  2. Analyze data quality issues")
    print("  3. Test enhanced data cleaning")
    print("  4. Test database upload")
    print("  5. Generate comprehensive report")
    print("\n⏳ Test starting...")

    tester = RealTimeDataTester()
    success = tester.run_comprehensive_test()

    if success:
        print("\n🎉 Real-time pipeline test completed successfully!")
        return 0
    else:
        print("\n❌ Real-time pipeline test found issues. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit(main())
