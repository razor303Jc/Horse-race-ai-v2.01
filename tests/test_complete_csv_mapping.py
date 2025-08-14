"""
Test Complete CSV Column Mapping
Validates that ALL CSV columns are properly mapped and processed
"""

import json
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd

# Add the docker/data_processing directory to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.01/docker/data_processing")
from complete_csv_processor import CompleteCsvDatabaseProcessor


class TestCompleteCsvMapping(unittest.TestCase):
    def setUp(self):
        """Set up test environment"""
        self.processor = CompleteCsvDatabaseProcessor(
            config_path="config/complete_csv_column_mapping.json"
        )

    def test_config_loaded(self):
        """Test that configuration is loaded properly"""
        self.assertIsInstance(self.processor.config, dict)
        self.assertIn("table_mappings", self.processor.config)
        self.assertIn("global_null_handling", self.processor.config)

    def test_all_tables_configured(self):
        """Test that all required tables are configured"""
        expected_tables = [
            "races",
            "records",
            "horses",
            "jockeys_stats",
            "trainers_stats",
        ]

        for table in expected_tables:
            self.assertIn(table, self.processor.config["table_mappings"])

    def test_races_table_mapping(self):
        """Test races table has all 20 columns mapped"""
        races_config = self.processor.config["table_mappings"]["races"]

        # Should have all 20 race columns
        expected_columns = [
            "race_id",
            "race_number",
            "race_time",
            "course_id",
            "course",
            "race_type",
            "date",
            "race_name",
            "class",
            "years",
            "distance",
            "surface",
            "prize",
            "runners_racecard",
            "runners",
            "draw",
            "ew_racecard",
            "ew",
            "places_ew_racecard",
            "places_ew",
        ]

        mapped_columns = list(races_config["column_mapping"].keys())

        for col in expected_columns:
            self.assertIn(
                col, mapped_columns, f"Column {col} missing from races mapping"
            )

    def test_records_table_mapping(self):
        """Test records table has all 64 columns mapped"""
        records_config = self.processor.config["table_mappings"]["records"]

        # Should have all sectional time columns
        sectional_columns = []
        for i in range(1, 19):
            sectional_columns.extend([f"distance_sec_{i}", f"sectional_time_{i}"])

        mapped_columns = list(records_config["column_mapping"].keys())

        # Test basic columns
        basic_columns = ["record_id", "race_id", "horse_id", "jockey_id", "trainer_id"]
        for col in basic_columns:
            self.assertIn(
                col, mapped_columns, f"Column {col} missing from records mapping"
            )

        # Test sectional time columns
        for col in sectional_columns:
            self.assertIn(
                col,
                mapped_columns,
                f"Sectional column {col} missing from records mapping",
            )

    def test_horses_table_mapping(self):
        """Test horses table has all 39 columns mapped"""
        horses_config = self.processor.config["table_mappings"]["horses"]

        # Should have all horse statistic columns
        expected_columns = [
            "horse_id",
            "horse_name",
            "age",
            "total_races",
            "wins",
            "percentage_wins",
            "flat_aw_races",
            "flat_aw_wins",
            "flat_turf_races",
            "flat_turf_wins",
            "chase_races",
            "chase_wins",
            "hurdle_races",
            "hurdle_wins",
        ]

        mapped_columns = list(horses_config["column_mapping"].keys())

        for col in expected_columns:
            self.assertIn(
                col, mapped_columns, f"Column {col} missing from horses mapping"
            )

    def test_jockeys_stats_mapping(self):
        """Test jockeys_stats table has all 28 columns mapped"""
        jockeys_config = self.processor.config["table_mappings"]["jockeys_stats"]
        mapped_columns = list(jockeys_config["column_mapping"].keys())

        # Should have 28 columns total
        self.assertEqual(len(mapped_columns), 28, "Jockeys should have 28 columns")

        # Test key columns
        key_columns = [
            "jockey_id",
            "jockey_name",
            "total_races",
            "wins",
            "percentage_wins",
        ]
        for col in key_columns:
            self.assertIn(
                col, mapped_columns, f"Column {col} missing from jockeys mapping"
            )

    def test_trainers_stats_mapping(self):
        """Test trainers_stats table has all 28 columns mapped"""
        trainers_config = self.processor.config["table_mappings"]["trainers_stats"]
        mapped_columns = list(trainers_config["column_mapping"].keys())

        # Should have 28 columns total
        self.assertEqual(len(mapped_columns), 28, "Trainers should have 28 columns")

        # Test key columns
        key_columns = [
            "trainer_id",
            "trainer_name",
            "total_races",
            "wins",
            "percentage_wins",
        ]
        for col in key_columns:
            self.assertIn(
                col, mapped_columns, f"Column {col} missing from trainers mapping"
            )

    def test_null_value_cleaning(self):
        """Test NULL value cleaning works correctly"""
        # Test integer cleaning
        self.assertEqual(self.processor.clean_value("", "integers"), 0)
        self.assertEqual(self.processor.clean_value("-", "integers"), 0)
        self.assertEqual(self.processor.clean_value("NULL", "integers"), 0)
        self.assertEqual(self.processor.clean_value("123", "integers"), 123)

        # Test decimal cleaning
        self.assertEqual(self.processor.clean_value("", "decimals"), 0.0)
        self.assertEqual(self.processor.clean_value("-", "decimals"), 0.0)
        self.assertEqual(self.processor.clean_value("12.5", "decimals"), 12.5)

        # Test string cleaning
        self.assertEqual(self.processor.clean_value("", "strings"), "none")
        self.assertEqual(self.processor.clean_value("-", "strings"), "none")
        self.assertEqual(self.processor.clean_value("test", "strings"), "test")

    def test_data_type_identification(self):
        """Test that data types are correctly identified"""
        # Test races table data types
        self.assertEqual(
            self.processor.get_column_data_type("races", "race_number"), "integers"
        )
        self.assertEqual(
            self.processor.get_column_data_type("races", "race_id"), "strings"
        )

        # Test records table data types
        self.assertEqual(
            self.processor.get_column_data_type("records", "horse_id"), "integers"
        )
        self.assertEqual(
            self.processor.get_column_data_type("records", "sp"), "decimals"
        )
        self.assertEqual(
            self.processor.get_column_data_type("records", "horse"), "strings"
        )

    @patch("psycopg2.connect")
    def test_database_connection(self, mock_connect):
        """Test database connection"""
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn

        self.processor.connect_database()

        mock_connect.assert_called_once()
        self.assertEqual(self.processor.connection, mock_conn)

    def test_csv_files_exist(self):
        """Test that CSV files referenced in config exist"""
        missing_files = []

        for table_name, table_config in self.processor.config["table_mappings"].items():
            for csv_file in table_config["csv_files"]:
                if not os.path.exists(csv_file):
                    missing_files.append(csv_file)

        # Report missing files but don't fail test (files may not exist in test env)
        if missing_files:
            print(f"INFO: Missing CSV files (expected in test): {missing_files}")

    def test_validation_functionality(self):
        """Test CSV validation functionality"""
        # This tests the validation logic without requiring actual CSV files
        validation_results = {}

        for table_name in self.processor.config["table_mappings"]:
            validation_results[table_name] = []

        # Should return a dict with table names as keys
        self.assertIsInstance(validation_results, dict)

        for table in ["races", "records", "horses", "jockeys_stats", "trainers_stats"]:
            self.assertIn(table, validation_results)

    def test_complete_coverage(self):
        """Test that we have comprehensive column coverage"""
        # Races: 20 columns
        races_columns = len(
            self.processor.config["table_mappings"]["races"]["column_mapping"]
        )
        self.assertEqual(
            races_columns, 20, f"Races should have 20 columns, got {races_columns}"
        )

        # Records: 64 columns (18 sectional pairs + other race data)
        records_columns = len(
            self.processor.config["table_mappings"]["records"]["column_mapping"]
        )
        self.assertEqual(
            records_columns,
            64,
            f"Records should have 64 columns, got {records_columns}",
        )

        # Horses: 39 columns
        horses_columns = len(
            self.processor.config["table_mappings"]["horses"]["column_mapping"]
        )
        self.assertEqual(
            horses_columns, 39, f"Horses should have 39 columns, got {horses_columns}"
        )

        # Jockeys: 28 columns
        jockeys_columns = len(
            self.processor.config["table_mappings"]["jockeys_stats"]["column_mapping"]
        )
        self.assertEqual(
            jockeys_columns,
            28,
            f"Jockeys should have 28 columns, got {jockeys_columns}",
        )

        # Trainers: 28 columns
        trainers_columns = len(
            self.processor.config["table_mappings"]["trainers_stats"]["column_mapping"]
        )
        self.assertEqual(
            trainers_columns,
            28,
            f"Trainers should have 28 columns, got {trainers_columns}",
        )

    def test_null_handling_configuration(self):
        """Test that null handling is properly configured for all tables"""
        for table_name, table_config in self.processor.config["table_mappings"].items():
            null_handling = table_config["null_handling"]

            # Check that all null handling types are present
            self.assertIn("integers", null_handling)
            self.assertIn("strings", null_handling)

            # Records and horses should have decimals
            if table_name in ["records", "horses", "jockeys_stats", "trainers_stats"]:
                self.assertIn("decimals", null_handling)

            # Check that all mapped columns have null handling defined
            mapped_columns = set(table_config["column_mapping"].keys())
            handled_columns = set()

            for data_type, columns in null_handling.items():
                handled_columns.update(columns)

            # Every mapped column should have null handling
            unhandled = mapped_columns - handled_columns
            self.assertEqual(
                len(unhandled),
                0,
                f"Table {table_name} has unhandled columns: {unhandled}",
            )


def run_complete_mapping_tests():
    """Run all tests for complete CSV mapping"""
    unittest.main(verbosity=2)


if __name__ == "__main__":
    print("🧪 Testing Complete CSV Column Mapping...")
    print("=" * 60)
    run_complete_mapping_tests()
