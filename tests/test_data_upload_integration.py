#!/usr/bin/env python3
"""
Integration Test for Data Upload Pipeline
=========================================

Tests the complete end-to-end data upload pipeline with real database interaction.
This test requires a running PostgreSQL database.
"""

import logging
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import psycopg2

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

from csv_column_mapper import ColumnMapper
from daily_data_uploader import DailyDataUploader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataUploadIntegrationTest:
    """
    Integration test for the complete data upload pipeline
    """

    def __init__(self):
        self.uploader = DailyDataUploader()
        self.mapper = ColumnMapper()
        self.test_dir = None

    def setup_test_environment(self):
        """Set up test environment with sample data"""
        logger.info("Setting up test environment...")

        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        test_downloads_dir = Path(self.test_dir) / "downloads"
        test_downloads_dir.mkdir(exist_ok=True)

        # Override downloads directory for testing
        self.uploader.downloads_dir = test_downloads_dir

        return test_downloads_dir

    def create_sample_data(self, downloads_dir):
        """Create sample CSV files for testing"""
        logger.info("Creating sample CSV data...")

        today = datetime.now().strftime("%Y%m%d")

        # Sample race results data
        race_results_data = {
            "ID": [1, 2, 3, 4, 5],
            "Race_ID": [101, 101, 102, 102, 103],
            "Horse_ID": [201, 202, 203, 204, 205],
            "Name": [
                "Thunder Bay",
                "Lightning Strike",
                "Storm Cloud",
                "Wind Walker",
                "Fire Spirit",
            ],
            "jockey_ID": [301, 302, 303, 301, 302],
            "jockey": ["J. Smith", "A. Jones", "B. Brown", "J. Smith", "A. Jones"],
            "trainer_ID": [401, 402, 403, 401, 402],
            "trainer": [
                "T. Johnson",
                "M. Wilson",
                "P. Davis",
                "T. Johnson",
                "M. Wilson",
            ],
            "Age": [5, 6, 4, 7, 5],
            "weight": [60.5, 62.0, 58.5, 61.0, 59.5],
            "Draw": [1, 2, 3, 4, 5],
            "Place": [1, 2, 3, 4, 5],
            "SP": [2.5, 3.0, 4.5, 5.0, 7.5],
            "finish_time": [120.5, 125.0, 130.2, 135.1, 140.8],
        }

        # Sample horses data
        horses_data = {
            "id": ["H201", "H202", "H203", "H204", "H205"],
            "name": [
                "Thunder Bay",
                "Lightning Strike",
                "Storm Cloud",
                "Wind Walker",
                "Fire Spirit",
            ],
            "country": ["GB", "IRE", "USA", "FR", "GB"],
            "age": [5, 6, 4, 7, 5],
            "color": ["Bay", "Chestnut", "Brown", "Black", "Grey"],
            "uptodate": ["20250801", "20250802", "20250803", "20250804", "20250805"],
        }

        # Sample races cards data
        races_cards_data = {
            "date": [20250810, 20250810, 20250811],
            "course": ["Ascot", "Newmarket", "York"],
            "race_number": [1, 2, 1],
            "race_time": ["14:30", "15:00", "14:30"],
        }

        # Sample jockey stats data
        jockey_stats_data = {
            "id": ["J301", "J302", "J303"],
            "name": ["J. Smith", "A. Jones", "B. Brown"],
            "strike_rate": [1195, 850, 1050],  # Basis points
            "uptodate": ["20250801", "20250802", "20250803"],
        }

        # Sample trainer stats data
        trainer_stats_data = {
            "id": ["T401", "T402", "T403"],
            "name": ["T. Johnson", "M. Wilson", "P. Davis"],
            "strike_rate": [1580, 920, 1240],  # Basis points
            "uptodate": ["20250801", "20250802", "20250803"],
        }

        # Sample racecard details data
        racecard_details_data = {
            "race_id": [101, 102, 103],
            "course": ["Ascot", "Newmarket", "York"],
            "race_time": ["14:30", "15:00", "14:30"],
            "race_class": [1, 2, 1],
            "distance": [1600, 2000, 1800],
        }

        # Create CSV files
        datasets = {
            "race_results": race_results_data,
            "horses": horses_data,
            "races_cards": races_cards_data,
            "jockey_stats": jockey_stats_data,
            "trainer_stats": trainer_stats_data,
            "racecard_details": racecard_details_data,
        }

        created_files = []
        for table_name, data in datasets.items():
            filename = f"{table_name}-{today}.csv"
            filepath = downloads_dir / filename

            df = pd.DataFrame(data)
            df.to_csv(filepath, index=False)
            created_files.append(filepath)
            logger.info(f"Created test file: {filepath}")

        return created_files

    def test_database_connection(self):
        """Test database connection"""
        logger.info("Testing database connection...")

        try:
            conn = self.uploader.get_database_connection()
            if conn:
                logger.info("✅ Database connection successful")
                conn.close()
                return True
            else:
                logger.error("❌ Database connection failed")
                return False
        except Exception as e:
            logger.error(f"❌ Database connection error: {e}")
            return False

    def test_column_mapping(self):
        """Test column mapping for all table types"""
        logger.info("Testing column mapping...")

        success_count = 0
        total_tables = len(self.mapper.column_mappings)

        for table_name in self.mapper.column_mappings.keys():
            try:
                # Create minimal test data
                if table_name == "race_results":
                    test_data = {
                        "ID": [1],
                        "Race_ID": [101],
                        "Horse_ID": [201],
                        "Name": ["Test"],
                    }
                elif table_name == "horses":
                    test_data = {"id": ["H001"], "name": ["Test Horse"], "age": [5]}
                elif table_name == "races_cards":
                    test_data = {"date": [20250810], "course": ["Test Course"]}
                else:
                    test_data = {"id": ["T001"], "name": ["Test"]}

                df = pd.DataFrame(test_data)
                mapped_df = self.mapper.map_columns(df, table_name)

                if len(mapped_df) > 0:
                    logger.info(f"✅ Column mapping successful for {table_name}")
                    success_count += 1
                else:
                    logger.warning(
                        f"⚠️ Column mapping returned empty result for {table_name}"
                    )

            except Exception as e:
                logger.error(f"❌ Column mapping failed for {table_name}: {e}")

        logger.info(
            f"Column mapping results: {success_count}/{total_tables} tables successful"
        )
        return success_count == total_tables

    def test_data_upload(self, test_files):
        """Test data upload for all created test files"""
        logger.info("Testing data upload...")

        upload_results = []

        for file_path in test_files:
            table_name = file_path.stem.split("-")[
                0
            ]  # Extract table name from filename

            try:
                logger.info(f"Uploading {table_name}...")
                result = self.uploader.upload_csv_file(table_name)

                if result.get("success", False):
                    logger.info(
                        f"✅ Upload successful for {table_name}: {result.get('rows_processed', 0)} rows"
                    )
                    upload_results.append(True)
                else:
                    logger.error(
                        f"❌ Upload failed for {table_name}: {result.get('error', 'Unknown error')}"
                    )
                    upload_results.append(False)

            except Exception as e:
                logger.error(f"❌ Upload exception for {table_name}: {e}")
                upload_results.append(False)

        success_count = sum(upload_results)
        total_files = len(test_files)

        logger.info(f"Upload results: {success_count}/{total_files} files successful")
        return success_count, total_files

    def test_complete_pipeline(self):
        """Test the complete upload pipeline"""
        logger.info("Testing complete upload pipeline...")

        try:
            results = self.uploader.upload_all_data()

            if results.get("success", False):
                summary = results.get("summary", {})
                logger.info(f"✅ Complete pipeline successful!")
                logger.info(f"Files processed: {summary.get('files_processed', 0)}")
                logger.info(f"Total rows: {summary.get('total_rows', 0)}")
                return True
            else:
                logger.error(
                    f"❌ Complete pipeline failed: {results.get('error', 'Unknown error')}"
                )
                return False

        except Exception as e:
            logger.error(f"❌ Complete pipeline exception: {e}")
            return False

    def cleanup_test_environment(self):
        """Clean up test environment"""
        if self.test_dir:
            import shutil

            shutil.rmtree(self.test_dir, ignore_errors=True)
            logger.info("Cleaned up test environment")

    def run_integration_tests(self):
        """Run all integration tests"""
        logger.info("🚀 Starting Data Upload Pipeline Integration Tests")
        logger.info("=" * 60)

        test_results = {}

        try:
            # Setup
            downloads_dir = self.setup_test_environment()
            test_files = self.create_sample_data(downloads_dir)

            # Test 1: Database Connection
            test_results["database_connection"] = self.test_database_connection()

            # Test 2: Column Mapping
            test_results["column_mapping"] = self.test_column_mapping()

            # Test 3: Individual File Uploads
            success_count, total_files = self.test_data_upload(test_files)
            test_results["individual_uploads"] = success_count == total_files

            # Test 4: Complete Pipeline
            test_results["complete_pipeline"] = self.test_complete_pipeline()

        except Exception as e:
            logger.error(f"❌ Integration test setup failed: {e}")
            test_results["setup"] = False

        finally:
            # Cleanup
            self.cleanup_test_environment()

        # Results Summary
        logger.info("=" * 60)
        logger.info("🎯 INTEGRATION TEST RESULTS")
        logger.info("=" * 60)

        passed_tests = 0
        total_tests = len(test_results)

        for test_name, passed in test_results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            logger.info(f"{test_name.replace('_', ' ').title()}: {status}")
            if passed:
                passed_tests += 1

        logger.info("=" * 60)
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        logger.info(
            f"Overall Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)"
        )

        if success_rate == 100:
            logger.info("🎉 ALL INTEGRATION TESTS PASSED!")
        elif success_rate >= 80:
            logger.info("⚠️ Most tests passed - minor issues detected")
        else:
            logger.info("🔥 Multiple test failures - pipeline needs attention")

        return test_results


def main():
    """Run the integration tests"""
    tester = DataUploadIntegrationTest()
    results = tester.run_integration_tests()

    # Exit with appropriate code
    if all(results.values()):
        sys.exit(0)  # Success
    else:
        sys.exit(1)  # Failure


if __name__ == "__main__":
    main()
