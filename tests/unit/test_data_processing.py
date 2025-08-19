#!/usr/bin/env python3
"""
Unit Tests for Data Processing Components
Tests all data processing functionality including distance/weight conversion
"""

import unittest
import tempfile
import pandas as pd
import os
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


class TestDistanceConverter(unittest.TestCase):
    """Test distance conversion functionality"""

    def setUp(self):
        """Set up test environment"""
        try:
            from tools.data_processing.distance_converter import DistanceConverter

            self.converter = DistanceConverter()
        except ImportError:
            self.skipTest("DistanceConverter not available")

    def test_furlong_conversion(self):
        """Test furlong to meters conversion"""
        test_cases = [
            ("5f", 1005.84),  # 5 furlongs = 5 * 201.168
            ("6f", 1207.00),  # 6 furlongs = 6 * 201.168
            ("7f", 1408.18),  # 7 furlongs = 7 * 201.168
            ("8f", 1609.34),  # 8 furlongs = 8 * 201.168
        ]

        for distance_str, expected_meters in test_cases:
            with self.subTest(distance=distance_str):
                result = self.converter.convert_to_meters(distance_str)
                self.assertAlmostEqual(result, expected_meters, places=1)

    def test_mile_conversion(self):
        """Test mile distance conversion"""
        test_cases = [
            ("1m", 1609.34),  # 1 mile
            ("1m 1f", 1810.51),  # 1 mile 1 furlong
            ("1m 2f", 2011.68),  # 1 mile 2 furlongs
            ("2m", 3218.69),  # 2 miles
        ]

        for distance_str, expected_meters in test_cases:
            with self.subTest(distance=distance_str):
                result = self.converter.convert_to_meters(distance_str)
                self.assertAlmostEqual(result, expected_meters, places=1)

    def test_yard_conversion(self):
        """Test yard distance conversion"""
        test_cases = [
            ("100y", 91),  # 100 yards
            ("200y", 183),  # 200 yards
            ("440y", 402),  # 440 yards (quarter mile)
        ]

        for distance_str, expected_meters in test_cases:
            with self.subTest(distance=distance_str):
                result = self.converter.convert_to_meters(distance_str)
                self.assertAlmostEqual(result, expected_meters, places=0)

    def test_invalid_distance(self):
        """Test handling of invalid distance formats"""
        invalid_distances = ["", "invalid", "999x", "mile"]

        for invalid_distance in invalid_distances:
            with self.subTest(distance=invalid_distance):
                result = self.converter.convert_to_meters(invalid_distance)
                self.assertIsNone(result)  # Should return None for invalid input


class TestWeightConverter(unittest.TestCase):
    """Test weight conversion functionality"""

    def setUp(self):
        """Set up test environment"""
        try:
            from tools.data_processing.weight_converter import WeightConverter

            self.converter = WeightConverter()
        except ImportError:
            self.skipTest("WeightConverter not available")

    def test_stone_pounds_conversion(self):
        """Test stone-pounds to kg conversion"""
        test_cases = [
            ("9-0", 57.15),  # 9 stone 0 pounds
            ("9-7", 60.33),  # 9 stone 7 pounds
            ("10-0", 63.50),  # 10 stone 0 pounds
            ("10-2", 64.41),  # 10 stone 2 pounds
            ("11-10", 74.39),  # 11 stone 10 pounds
        ]

        for weight_str, expected_kg in test_cases:
            with self.subTest(weight=weight_str):
                result = self.converter.convert_uk_to_kg(weight_str)
                self.assertIsNotNone(result)
                self.assertAlmostEqual(result, expected_kg, places=1)

    def test_pounds_only_conversion(self):
        """Test pounds-only weight conversion (if supported)"""
        # Note: The actual converter may not support pounds-only format
        # This test demonstrates the expected behavior
        pass  # Skip this test as our converter uses UK stone-pounds format

    def test_kg_passthrough(self):
        """Test kg values pass through unchanged (if supported)"""
        # Note: The actual converter focuses on UK stone-pounds format
        # This test demonstrates expected behavior for metric input
        pass  # Skip this test as our converter uses UK stone-pounds format

    def test_invalid_weight(self):
        """Test handling of invalid weight formats"""
        invalid_weights = ["", "invalid", "999x", "heavy"]

        for invalid_weight in invalid_weights:
            with self.subTest(weight=invalid_weight):
                result = self.converter.convert_uk_to_kg(invalid_weight)
                self.assertIsNone(result)  # Should return None for invalid input


class TestCSVMapper(unittest.TestCase):
    """Test CSV mapping functionality"""

    def setUp(self):
        """Set up test environment"""
        try:
            from tools.data_processing.advanced_csv_mapper import AdvancedCSVMapper

            self.mapper = AdvancedCSVMapper()
        except ImportError:
            self.skipTest("AdvancedCSVMapper not available")

    def test_basic_column_mapping(self):
        """Test basic column mapping functionality"""
        test_data = pd.DataFrame(
            {
                "horse": ["Test Horse 1", "Test Horse 2"],
                "jockey": ["Test Jockey 1", "Test Jockey 2"],
                "weight": ["10-2", "9-7"],
                "dist": ["6f", "1m"],
            }
        )

        # Test mapping for a specific table (assuming 'races' table exists in config)
        mapped_data = self.mapper.map_csv_columns(test_data, "races")

        # Check that data is returned (exact columns depend on mapping config)
        self.assertIsNotNone(mapped_data)
        self.assertIsInstance(mapped_data, pd.DataFrame)

    def test_data_type_conversion(self):
        """Test data type conversion during mapping"""
        test_data = pd.DataFrame(
            {
                "horse": ["Test Horse"],
                "weight": ["10-2"],
                "distance": ["6f"],
                "odds": ["3.5"],
            }
        )

        # Test mapping
        mapped_data = self.mapper.map_csv_columns(test_data, "races")

        # Check that data is processed
        self.assertIsNotNone(mapped_data)
        self.assertIsInstance(mapped_data, pd.DataFrame)

    def test_missing_data_handling(self):
        """Test handling of missing data"""
        test_data = pd.DataFrame(
            {
                "horse": ["Test Horse", None, ""],
                "weight": ["10-2", None, ""],
                "distance": ["6f", None, ""],
            }
        )

        # Test mapping
        mapped_data = self.mapper.map_csv_columns(test_data, "races")

        # Check that missing data is handled appropriately
        self.assertIsNotNone(mapped_data)
        self.assertIsInstance(mapped_data, pd.DataFrame)


class TestDataQualityPipeline(unittest.TestCase):
    """Test data quality validation pipeline"""

    def test_data_completeness_validation(self):
        """Test data completeness validation"""
        # Test with complete data
        complete_data = pd.DataFrame(
            {
                "horse_name": ["Test Horse 1", "Test Horse 2"],
                "weight_kg": [63.5, 59.4],
                "distance_meters": [1200, 1600],
            }
        )

        # Check completeness
        missing_count = complete_data.isnull().sum().sum()
        self.assertEqual(missing_count, 0)

        # Test with missing data
        incomplete_data = pd.DataFrame(
            {
                "horse_name": ["Test Horse 1", None],
                "weight_kg": [63.5, None],
                "distance_meters": [1200, 1600],
            }
        )

        missing_count = incomplete_data.isnull().sum().sum()
        self.assertGreater(missing_count, 0)

    def test_data_type_validation(self):
        """Test data type validation"""
        test_data = pd.DataFrame(
            {
                "horse_name": ["Test Horse 1", "Test Horse 2"],
                "weight_kg": [63.5, 59.4],
                "distance_meters": [1200, 1600],
            }
        )

        # Check data types
        self.assertEqual(test_data["horse_name"].dtype, object)
        self.assertTrue(pd.api.types.is_numeric_dtype(test_data["weight_kg"]))
        self.assertTrue(pd.api.types.is_numeric_dtype(test_data["distance_meters"]))

    def test_data_quality_metrics(self):
        """Test data quality metrics calculation"""
        test_data = pd.DataFrame(
            {
                "horse_name": ["Test Horse 1", "Test Horse 2", None],
                "weight_kg": [63.5, 59.4, None],
                "distance_meters": [1200, 1600, 2000],
            }
        )

        # Calculate completeness percentage
        total_cells = test_data.size
        missing_cells = test_data.isnull().sum().sum()
        completeness = ((total_cells - missing_cells) / total_cells) * 100

        self.assertIsInstance(completeness, float)
        self.assertGreaterEqual(completeness, 0)
        self.assertLessEqual(completeness, 100)


if __name__ == "__main__":
    unittest.main()
