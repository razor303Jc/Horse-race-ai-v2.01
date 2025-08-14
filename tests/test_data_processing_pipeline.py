#!/usr/bin/env python3
"""
Comprehensive Test Framework for Data Processing Pipeline
========================================================

Tests all components of the horse racing data processing pipeline:
1. CSV mapping and column alignment
2. Data cleaning and validation
3. Database upload and integrity
4. Pipeline integration and error handling
5. End-to-end workflow validation

This test suite ensures data quality and pipeline reliability.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from sqlalchemy import create_engine

# Import our modules
from tools.data_processing.integrated_data_processor import IntegratedDataProcessor


class TestDataProcessingPipeline(unittest.TestCase):
    """Test suite for the complete data processing pipeline."""

    def setUp(self):
        """Set up test environment."""
        # Create temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        self.test_db_url = "sqlite:///:memory:"  # In-memory SQLite for testing

        # Create test CSV data
        self.create_test_data()

        # Initialize processor
        self.processor = IntegratedDataProcessor(self.test_db_url)
        self.processor.connect_database()

    def tearDown(self):
        """Clean up test environment."""
        import shutil

        shutil.rmtree(self.test_dir)

    def create_test_data(self):
        """Create test CSV files with known data."""
        # Create test races data
        races_data = {
            "race_id": [1, 2, 1],  # Include duplicate for testing
            "race_number": [1, 2, 1],
            "race_time": ["14:15", "14:45", "14:15"],
            "course": ["Beverley", "Salisbury", "Beverley"],
            "race_name": ["Test Race 1", "Test Race 2", "Test Race 1"],
            "date": ["2025-08-13", "2025-08-13", "2025-08-13"],
        }

        # Create test records data with problematic values
        records_data = {
            "record_id": [1, 2, 3],
            "race_id": [1, 1, 2],
            "position": [1, 2, 1],
            "horse": ["Test Horse 1", "Test Horse 2", "Test Horse 3"],
            "age": [3, 4, 5],
            "weight": [60.0, 61.5, 59.0],
            "jockey": ["Test Jockey 1", "Test Jockey 2", "Test Jockey 3"],
            "trainer": ["Test Trainer 1", "Test Trainer 2", "Test Trainer 3"],
            "or_rating": ["85", "-", "90"],  # Include problematic "-" value
        }

        # Create test horses data
        horses_data = {
            "horse_id": [1, 2, 3, 1],  # Include duplicate
            "horse_name": [
                "Test Horse 1",
                "Test Horse 2",
                "Test Horse 3",
                "Test Horse 1",
            ],
            "age": [3, 4, 5, 3],
            "sex": ["colt", "filly", "gelding", "colt"],
            "color": ["bay", "chestnut", "grey", "bay"],
            "sire": ["Test Sire 1", "Test Sire 2", "Test Sire 3", "Test Sire 1"],
            "dam": ["Test Dam 1", "Test Dam 2", "Test Dam 3", "Test Dam 1"],
            "owner": ["Test Owner 1", "Test Owner 2", "Test Owner 3", "Test Owner 1"],
        }

        # Save test data as CSV files
        self.races_file = os.path.join(self.test_dir, "test_races.csv")
        self.records_file = os.path.join(self.test_dir, "test_records.csv")
        self.horses_file = os.path.join(self.test_dir, "test_horses.csv")

        pd.DataFrame(races_data).to_csv(self.races_file, index=False)
        pd.DataFrame(records_data).to_csv(self.records_file, index=False)
        pd.DataFrame(horses_data).to_csv(self.horses_file, index=False)

        # Create test manifest
        self.manifest_file = os.path.join(self.test_dir, "test_manifest.json")
        manifest = {
            "files": {
                self.races_file: {"table": "races"},
                self.records_file: {"table": "records"},
                self.horses_file: {"table": "horses"},
            }
        }

        with open(self.manifest_file, "w") as f:
            json.dump(manifest, f)

    def test_database_connection(self):
        """Test database connection functionality."""
        # Test successful connection
        processor = IntegratedDataProcessor(self.test_db_url)
        self.assertTrue(processor.connect_database())

        # Test failed connection
        processor_bad = IntegratedDataProcessor("invalid://connection")
        self.assertFalse(processor_bad.connect_database())

    def test_data_cleaning_records(self):
        """Test data cleaning for records table."""
        df = pd.read_csv(self.records_file)

        # Verify problematic data exists
        self.assertIn("-", df["or_rating"].values)

        # Clean data
        cleaned_df = self.processor.clean_data(df, "records")

        # Verify cleaning worked
        self.assertNotIn("-", cleaned_df["or_rating"].values)
        self.assertTrue(
            cleaned_df["or_rating"].isna().any()
        )  # Should have NaN where "-" was

    def test_data_cleaning_races_duplicates(self):
        """Test duplicate removal for races."""
        df = pd.read_csv(self.races_file)

        # Verify duplicates exist
        self.assertEqual(len(df), 3)
        self.assertEqual(len(df["race_id"].unique()), 2)  # 2 unique race_ids

        # Clean data
        cleaned_df = self.processor.clean_data(df, "races")

        # Verify duplicates removed
        self.assertEqual(len(cleaned_df), 2)  # Should have 2 rows now
        self.assertEqual(len(cleaned_df["race_id"].unique()), 2)

    def test_data_cleaning_horses_duplicates(self):
        """Test duplicate removal for horses."""
        df = pd.read_csv(self.horses_file)

        # Verify duplicates exist
        self.assertEqual(len(df), 4)
        self.assertEqual(len(df["horse_id"].unique()), 3)  # 3 unique horse_ids

        # Clean data
        cleaned_df = self.processor.clean_data(df, "horses")

        # Verify duplicates removed
        self.assertEqual(len(cleaned_df), 3)  # Should have 3 rows now
        self.assertEqual(len(cleaned_df["horse_id"].unique()), 3)

    def test_single_table_upload(self):
        """Test uploading a single table."""
        # Create tables in test database
        with self.processor.engine.connect() as conn:
            conn.execute(
                """
                CREATE TABLE races (
                    race_id INTEGER,
                    race_number INTEGER,
                    race_time TEXT,
                    course TEXT,
                    race_name TEXT,
                    date TEXT
                )
            """
            )
            conn.commit()

        # Test upload
        success, row_count = self.processor.upload_table(self.races_file, "races")

        self.assertTrue(success)
        self.assertEqual(row_count, 2)  # Should be 2 after deduplication

        # Verify data in database
        result = pd.read_sql(
            "SELECT COUNT(*) as count FROM races", self.processor.engine
        )
        self.assertEqual(result.iloc[0]["count"], 2)

    def test_manifest_processing(self):
        """Test processing upload manifest."""
        # Create tables in test database
        tables_sql = [
            """CREATE TABLE races (
                race_id INTEGER, race_number INTEGER, race_time TEXT,
                course TEXT, race_name TEXT, date TEXT
            )""",
            """CREATE TABLE records (
                record_id INTEGER, race_id INTEGER, position INTEGER,
                horse TEXT, age INTEGER, weight REAL, jockey TEXT,
                trainer TEXT, or_rating TEXT
            )""",
            """CREATE TABLE horses (
                horse_id INTEGER, horse_name TEXT, age INTEGER,
                sex TEXT, color TEXT, sire TEXT, dam TEXT, owner TEXT
            )""",
        ]

        for sql in tables_sql:
            with self.processor.engine.connect() as conn:
                conn.execute(sql)
                conn.commit()

        # Process manifest
        results = self.processor.process_manifest(self.manifest_file)

        # Verify results
        self.assertEqual(len(results), 3)
        self.assertTrue(all(r["success"] for r in results.values()))

        # Check expected row counts (after cleaning)
        expected_counts = {"races": 2, "records": 3, "horses": 3}
        for table, expected_count in expected_counts.items():
            self.assertEqual(results[table]["row_count"], expected_count)

    def test_upload_validation(self):
        """Test upload validation functionality."""
        # Create and populate test tables
        self.test_manifest_processing()  # This creates and populates tables

        # Validate upload
        counts = self.processor.validate_upload()

        # Check results
        expected_counts = {"races": 2, "records": 3, "horses": 3}
        for table, expected_count in expected_counts.items():
            self.assertEqual(counts[table], expected_count)

    def test_missing_file_handling(self):
        """Test handling of missing files."""
        missing_file = os.path.join(self.test_dir, "missing.csv")

        success, row_count = self.processor.upload_table(missing_file, "test_table")

        self.assertFalse(success)
        self.assertEqual(row_count, 0)

    def test_invalid_manifest_handling(self):
        """Test handling of invalid manifest files."""
        # Test missing manifest file
        missing_manifest = os.path.join(self.test_dir, "missing_manifest.json")
        results = self.processor.process_manifest(missing_manifest)
        self.assertEqual(results, {})

        # Test invalid JSON
        invalid_manifest = os.path.join(self.test_dir, "invalid_manifest.json")
        with open(invalid_manifest, "w") as f:
            f.write("invalid json content")

        results = self.processor.process_manifest(invalid_manifest)
        self.assertEqual(results, {})


class TestDataQuality(unittest.TestCase):
    """Test data quality and validation."""

    def test_csv_column_mapping_structure(self):
        """Test that CSV column mapping file has correct structure."""
        mapping_file = "config/csv_column_mapping.json"

        if os.path.exists(mapping_file):
            with open(mapping_file, "r") as f:
                mapping = json.load(f)

            # Check structure
            self.assertIn("table_mappings", mapping)

            for table_name, config in mapping["table_mappings"].items():
                self.assertIn("csv_files", config)
                self.assertIn("column_mapping", config)
                self.assertIsInstance(config["csv_files"], list)
                self.assertIsInstance(config["column_mapping"], dict)

    def test_data_consistency(self):
        """Test data consistency rules."""
        # This would test business logic rules like:
        # - Race dates are valid
        # - Horse ages are reasonable
        # - Jockey/trainer names are properly formatted
        pass

    def test_database_schema_compliance(self):
        """Test that generated CSV files comply with database schema."""
        # This would verify that:
        # - Column names match database schema
        # - Data types are compatible
        # - Required fields are not null
        pass


class TestPipelineIntegration(unittest.TestCase):
    """Test complete pipeline integration."""

    @patch("os.system")
    def test_daily_downloads_integration(self, mock_system):
        """Test integration with daily downloads manager."""
        from tools.data_processing.daily_downloads_manager import main as daily_main

        # Mock the CSV mapping subprocess call
        mock_system.return_value = 0

        # This would test the complete integration
        # For now, just verify the function exists and can be called
        self.assertTrue(callable(daily_main))


def run_integration_tests():
    """Run integration tests against actual database."""
    print("🧪 Running Integration Tests")
    print("=" * 50)

    # Database connection test
    database_url = (
        "postgresql://horse_racing:secure_password_123@localhost:5433/horse_racing_db"
    )
    processor = IntegratedDataProcessor(database_url)

    try:
        if processor.connect_database():
            print("✅ Database connection: PASSED")

            # Validate current data
            counts = processor.validate_upload()
            if counts:
                print("✅ Database validation: PASSED")
                total_rows = sum(counts.values())
                print(f"📊 Total rows in database: {total_rows:,}")

                # Check for expected data quality
                if total_rows > 10000:  # We expect significant data
                    print("✅ Data volume check: PASSED")
                else:
                    print(f"⚠️ Data volume check: WARNING (only {total_rows} rows)")
            else:
                print("❌ Database validation: FAILED")

        else:
            print("❌ Database connection: FAILED")

    except Exception as e:
        print(f"❌ Integration test error: {e}")


if __name__ == "__main__":
    # Run unit tests
    print("🧪 Running Unit Tests")
    print("=" * 50)
    unittest.main(argv=[""], exit=False, verbosity=2)

    print("\n" + "=" * 50)

    # Run integration tests
    run_integration_tests()
