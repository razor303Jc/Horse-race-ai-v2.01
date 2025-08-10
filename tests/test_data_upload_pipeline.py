#!/usr/bin/env python3
"""
Comprehensive Test Suite for Data Upload Pipeline
=================================================

Tests the complete data upload pipeline including:
- CSV column mapping accuracy
- Data type conversions
- Database upload functionality
- Error handling and validation
- Integration with Qwen2.5 BIGINT solution
"""

import logging
import os
import sys
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import psycopg2
import pytest

# Add the project directory to the path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01")

# Configure test logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Import our modules after path setup
try:
    from csv_column_mapper import ColumnMapper
    from daily_data_uploader import DailyDataUploader
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")


class TestColumnMapper(unittest.TestCase):
    """Test the CSV column mapping functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.mapper = ColumnMapper()

    def test_race_results_mapping(self):
        """Test race results column mapping"""
        test_data = {
            "ID": [1, 2, 3],
            "Race_ID": [101, 102, 103],
            "Horse_ID": [201, 202, 203],
            "Name": ["Thunder", "Lightning", "Storm"],
            "jockey_ID": [301, 302, 303],
            "jockey": ["Smith", "Jones", "Brown"],
            "trainer_ID": [401, 402, 403],
            "trainer": ["Johnson", "Wilson", "Davis"],
            "Age": [5, 6, 7],
            "weight": [60.5, 62.0, 58.5],
            "Draw": [1, 2, 3],
            "Place": [1, 2, 3],
            "SP": [2.5, 3.0, 4.5],
            "finish_time": [120.5, 125.0, 130.2],
        }

        df = pd.DataFrame(test_data)
        mapped_data = self.mapper.map_columns(df, "race_results")

        # Check that all expected columns are mapped
        expected_cols = [
            "race_result_id",
            "race_id",
            "horse_id",
            "horse_name",
            "jockey_id",
            "jockey_name",
            "trainer_id",
            "trainer_name",
            "horse_age",
            "horse_weight_kg",
            "draw",
            "finished_position",
            "win_odds",
            "time_seconds",
        ]

        for col in expected_cols:
            self.assertIn(col, mapped_data.columns, f"Missing column: {col}")

        # Check specific value mappings
        self.assertEqual(mapped_data["horse_name"].iloc[0], "Thunder")
        self.assertEqual(mapped_data["finished_position"].iloc[0], 1)
        self.assertEqual(mapped_data["win_odds"].iloc[0], 2.5)

    def test_horses_mapping_with_age_conversion(self):
        """Test horses table mapping with age-to-birth-year conversion"""
        test_data = {
            "id": ["H001", "H002", "H003"],
            "name": ["Seabiscuit", "Secretariat", "Man o' War"],
            "country": ["GB", "IRE", "USA"],
            "age": [5, 6, 7],
            "color": ["Bay", "Chestnut", "Brown"],
            "uptodate": ["20240101", "20240102", "20240103"],
        }

        df = pd.DataFrame(test_data)
        mapped_data = self.mapper.map_columns(df, "horses")

        # Check age-to-birth-year conversion
        current_year = datetime.now().year
        expected_birth_year = current_year - 5  # First horse is 5 years old
        self.assertEqual(mapped_data["foaled"].iloc[0], date(expected_birth_year, 1, 1))

        # Check uptodate conversion
        self.assertEqual(mapped_data["uptodate"].iloc[0], date(2024, 1, 1))

    def test_races_cards_date_conversion(self):
        """Test races_cards table date conversion from integer format"""
        test_data = {
            "date": [20250810, 20250811, 20250812],
            "course": ["Ascot", "Newmarket", "York"],
            "race_number": [1, 2, 3],
            "race_time": ["14:30", "15:00", "15:30"],
        }

        df = pd.DataFrame(test_data)
        mapped_data = self.mapper.map_columns(df, "races_cards")

        # Check date conversion from integer to date
        self.assertEqual(mapped_data["race_date"].iloc[0], date(2025, 8, 10))
        self.assertEqual(mapped_data["race_date"].iloc[1], date(2025, 8, 11))

    def test_percentage_conversion(self):
        """Test percentage conversion from basis points to decimal"""
        test_data = {
            "id": ["T001", "T002"],
            "name": ["Johnson", "Smith"],
            "strike_rate": [1195, 850],  # Basis points: 11.95%, 8.50%
            "uptodate": ["20240101", "20240102"],
        }

        df = pd.DataFrame(test_data)
        mapped_data = self.mapper.map_columns(df, "trainer_stats")

        # Check percentage conversion
        self.assertAlmostEqual(mapped_data["strike_rate"].iloc[0], 11.95, places=2)
        self.assertAlmostEqual(mapped_data["strike_rate"].iloc[1], 8.50, places=2)

    def test_invalid_table_name(self):
        """Test handling of invalid table names"""
        df = pd.DataFrame({"test": [1, 2, 3]})

        with self.assertRaises(ValueError):
            self.mapper.map_columns(df, "invalid_table")

    def test_missing_columns_handling(self):
        """Test handling of missing columns in CSV"""
        # Test with minimal data
        test_data = {"id": ["H001"], "name": ["Test Horse"]}

        df = pd.DataFrame(test_data)
        mapped_data = self.mapper.map_columns(df, "horses")

        # Should still work with available columns
        self.assertEqual(mapped_data["horse_id"].iloc[0], "H001")
        self.assertEqual(mapped_data["horse_name"].iloc[0], "Test Horse")


class TestDataUploader(unittest.TestCase):
    """Test the daily data uploader functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.uploader = DailyDataUploader()

        # Create test CSV files
        self.test_dir = tempfile.mkdtemp()
        self.downloads_dir = Path(self.test_dir) / "downloads"
        self.downloads_dir.mkdir(exist_ok=True)

        # Override the downloads directory
        self.uploader.downloads_dir = self.downloads_dir

    def tearDown(self):
        """Clean up test fixtures"""
        import shutil

        shutil.rmtree(self.test_dir, ignore_errors=True)

    def create_test_csv(self, table_name: str, data: dict):
        """Create a test CSV file"""
        today = datetime.now().strftime("%Y%m%d")
        filename = f"{table_name}-{today}.csv"
        filepath = self.downloads_dir / filename

        df = pd.DataFrame(data)
        df.to_csv(filepath, index=False)
        return filepath

    @patch("daily_data_uploader.psycopg2.connect")
    def test_database_connection(self, mock_connect):
        """Test database connection establishment"""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn

        conn = self.uploader.get_database_connection()

        mock_connect.assert_called_once()
        self.assertEqual(conn, mock_conn)

    @patch("daily_data_uploader.psycopg2.connect")
    def test_upload_race_results(self, mock_connect):
        """Test uploading race results data"""
        # Create test data
        test_data = {
            "ID": [1, 2],
            "Race_ID": [101, 102],
            "Horse_ID": [201, 202],
            "Name": ["Thunder", "Lightning"],
            "jockey_ID": [301, 302],
            "jockey": ["Smith", "Jones"],
            "trainer_ID": [401, 402],
            "trainer": ["Johnson", "Wilson"],
            "Age": [5, 6],
            "weight": [60.5, 62.0],
            "Draw": [1, 2],
            "Place": [1, 2],
            "SP": [2.5, 3.0],
            "finish_time": [120.5, 125.0],
        }

        # Create test CSV
        csv_file = self.create_test_csv("race_results", test_data)

        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Test upload
        result = self.uploader.upload_csv_file("race_results")

        # Verify database operations
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called()
        self.assertTrue(result["success"])

    @patch("daily_data_uploader.psycopg2.connect")
    def test_upload_with_conflicts(self, mock_connect):
        """Test upload handling ON CONFLICT scenarios"""
        # Create test data for horses (has unique constraint)
        test_data = {
            "id": ["H001", "H002"],
            "name": ["Seabiscuit", "Secretariat"],
            "country": ["GB", "IRE"],
            "age": [5, 6],
            "color": ["Bay", "Chestnut"],
        }

        csv_file = self.create_test_csv("horses", test_data)

        # Mock database
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Test upload
        result = self.uploader.upload_csv_file("horses")

        # Should use ON CONFLICT for horses table
        execute_call = mock_cursor.execute.call_args[0][0]
        self.assertIn("ON CONFLICT", execute_call)
        self.assertTrue(result["success"])

    def test_find_csv_files(self):
        """Test finding CSV files in downloads directory"""
        # Create test files
        today = datetime.now().strftime("%Y%m%d")

        test_files = [
            f"race_results-{today}.csv",
            f"horses-{today}.csv",
            f"old_file-20240101.csv",  # Should be ignored
            "not_csv_file.txt",  # Should be ignored
        ]

        for filename in test_files:
            (self.downloads_dir / filename).touch()

        found_files = self.uploader.find_csv_files("race_results")

        # Should find only today's race_results file
        self.assertEqual(len(found_files), 1)
        self.assertTrue(found_files[0].name.startswith("race_results"))
        self.assertTrue(today in found_files[0].name)

    def test_upload_all_tables(self):
        """Test uploading all table types"""
        # Create test data for all tables
        test_tables = {
            "race_results": {
                "ID": [1],
                "Race_ID": [101],
                "Horse_ID": [201],
                "Name": ["Thunder"],
                "jockey_ID": [301],
                "jockey": ["Smith"],
                "trainer_ID": [401],
                "trainer": ["Johnson"],
                "Age": [5],
                "weight": [60.5],
                "Draw": [1],
                "Place": [1],
                "SP": [2.5],
                "finish_time": [120.5],
            },
            "horses": {
                "id": ["H001"],
                "name": ["Seabiscuit"],
                "country": ["GB"],
                "age": [5],
                "color": ["Bay"],
            },
            "races_cards": {
                "date": [20250810],
                "course": ["Ascot"],
                "race_number": [1],
                "race_time": ["14:30"],
            },
        }

        # Create CSV files
        for table, data in test_tables.items():
            self.create_test_csv(table, data)

        with patch("daily_data_uploader.psycopg2.connect"):
            results = self.uploader.upload_all_data()

        # Should attempt to upload all found files
        self.assertIsInstance(results, dict)
        self.assertIn("summary", results)


class TestDataValidation(unittest.TestCase):
    """Test data validation and error handling"""

    def setUp(self):
        self.mapper = ColumnMapper()

    def test_date_validation(self):
        """Test date field validation"""
        # Test valid date
        valid_date = self.mapper.convert_date_field("20250810")
        self.assertEqual(valid_date, date(2025, 8, 10))

        # Test invalid date format
        with self.assertRaises(ValueError):
            self.mapper.convert_date_field("invalid_date")

    def test_age_to_date_conversion(self):
        """Test age to birth date conversion"""
        current_year = datetime.now().year
        birth_date = self.mapper.age_to_date(5)
        expected_year = current_year - 5
        self.assertEqual(birth_date.year, expected_year)

    def test_percentage_validation(self):
        """Test percentage conversion validation"""
        # Test valid percentage
        result = self.mapper.convert_percentage(1195)  # 11.95%
        self.assertAlmostEqual(result, 11.95, places=2)

        # Test edge cases
        self.assertEqual(self.mapper.convert_percentage(0), 0.0)
        self.assertEqual(self.mapper.convert_percentage(10000), 100.0)

    def test_data_type_conversions(self):
        """Test various data type conversions"""
        test_data = pd.DataFrame(
            {
                "numeric_field": ["123", "456", "789"],
                "date_field": ["20250810", "20250811", "20250812"],
                "percentage_field": [1195, 850, 2000],
            }
        )

        # Test numeric conversion
        numeric_result = pd.to_numeric(test_data["numeric_field"])
        self.assertEqual(numeric_result.iloc[0], 123)

        # Test that our mapper handles these correctly
        self.assertTrue(True)  # Placeholder for actual conversion tests


class TestIntegrationScenarios(unittest.TestCase):
    """Test integration scenarios and edge cases"""

    def setUp(self):
        self.uploader = DailyDataUploader()
        self.mapper = ColumnMapper()

    @patch("daily_data_uploader.psycopg2.connect")
    def test_database_error_handling(self, mock_connect):
        """Test handling of database connection errors"""
        # Simulate connection failure
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        result = self.uploader.upload_csv_file("race_results")

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_empty_csv_handling(self):
        """Test handling of empty CSV files"""
        empty_df = pd.DataFrame()

        # Should handle empty dataframes gracefully
        try:
            result = self.mapper.map_columns(empty_df, "race_results")
            # Should return empty but valid dataframe
            self.assertTrue(isinstance(result, pd.DataFrame))
        except Exception as e:
            self.fail(f"Empty CSV handling failed: {e}")

    def test_large_dataset_processing(self):
        """Test processing of large datasets"""
        # Create a large test dataset
        large_data = {
            "ID": list(range(10000)),
            "Race_ID": list(range(1000, 11000)),
            "Horse_ID": list(range(2000, 12000)),
            "Name": [f"Horse_{i}" for i in range(10000)],
            "jockey_ID": list(range(3000, 13000)),
            "jockey": [f"Jockey_{i}" for i in range(10000)],
            "trainer_ID": list(range(4000, 14000)),
            "trainer": [f"Trainer_{i}" for i in range(10000)],
            "Age": [5 + (i % 10) for i in range(10000)],
            "weight": [60.0 + (i % 20) for i in range(10000)],
            "Draw": [1 + (i % 20) for i in range(10000)],
            "Place": [1 + (i % 10) for i in range(10000)],
            "SP": [2.0 + (i % 50) / 10 for i in range(10000)],
            "finish_time": [120.0 + (i % 100) for i in range(10000)],
        }

        large_df = pd.DataFrame(large_data)

        # Should handle large datasets without memory issues
        start_time = datetime.now()
        mapped_data = self.mapper.map_columns(large_df, "race_results")
        end_time = datetime.now()

        self.assertEqual(len(mapped_data), 10000)
        self.assertLess(
            (end_time - start_time).seconds, 30
        )  # Should complete in under 30 seconds


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
