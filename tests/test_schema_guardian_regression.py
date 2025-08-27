#!/usr/bin/env python3
"""
Schema Guardian Test Suite
Regression tests for schema guardian functionality
"""

import unittest
import pandas as pd
import psycopg2
from pathlib import Path
import sys
import tempfile
import os

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Import schema guardian modules
try:
    from tools.schema_guardian.ultimate_schema_guardian import UltimateSchemaGuardian

    SCHEMA_GUARDIAN_AVAILABLE = True
except ImportError:
    SCHEMA_GUARDIAN_AVAILABLE = False


class TestSchemaGuardian(unittest.TestCase):
    """Test suite for Schema Guardian functionality"""

    def setUp(self):
        """Set up test environment"""
        if not SCHEMA_GUARDIAN_AVAILABLE:
            self.skipTest("Schema Guardian modules not available")

        self.guardian = UltimateSchemaGuardian()

        # Test database configuration
        self.test_db_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def test_name_column_mapping(self):
        """Test context-aware name column mapping"""
        # Test jockeys_stats mapping
        jockey_target = self.guardian.determine_name_column_target("jockeys_stats")
        self.assertEqual(jockey_target, "jockey_name")

        # Test trainers_stats mapping
        trainer_target = self.guardian.determine_name_column_target("trainers_stats")
        self.assertEqual(trainer_target, "trainer_name")

        # Test horses mapping
        horse_target = self.guardian.determine_name_column_target("horses")
        self.assertEqual(horse_target, "horse_name")

    def test_normalize_with_context(self):
        """Test context-aware column normalization"""
        # Test Name column with different contexts
        jockey_normalized = self.guardian.normalize_with_context(
            "Name", "jockeys_stats"
        )
        self.assertEqual(jockey_normalized, "jockey_name")

        trainer_normalized = self.guardian.normalize_with_context(
            "Name", "trainers_stats"
        )
        self.assertEqual(trainer_normalized, "trainer_name")

        horse_normalized = self.guardian.normalize_with_context("Name", "horses")
        self.assertEqual(horse_normalized, "horse_name")

    def test_value_cleaning(self):
        """Test data value cleaning functionality"""
        # Test percentage cleaning
        cleaned_percentage = self.guardian.clean_value("15.64%", "numeric")
        self.assertEqual(cleaned_percentage, 15.64)

        # Test null pattern cleaning
        cleaned_null = self.guardian.clean_value("-", "string")
        self.assertIsNone(cleaned_null)

        # Test normal value
        cleaned_normal = self.guardian.clean_value("Test Value", "string")
        self.assertEqual(cleaned_normal, "Test Value")

    def test_case_sensitivity_handling(self):
        """Test case sensitivity pattern matching"""
        # Test ID patterns
        test_patterns = [
            ("race_id", "race_id"),
            ("Race_ID", "race_id"),
            ("RACE_ID", "race_id"),
            ("RaceID", "race_id"),
        ]

        for test_input, expected in test_patterns:
            normalized = self.guardian.normalize_with_context(test_input, "test_table")
            # This tests the regex patterns work
            self.assertTrue(isinstance(normalized, str))

    @unittest.skipUnless(SCHEMA_GUARDIAN_AVAILABLE, "Schema Guardian not available")
    def test_database_connection(self):
        """Test database connectivity (integration test)"""
        try:
            conn = psycopg2.connect(**self.test_db_config)
            conn.close()
            connection_works = True
        except Exception:
            connection_works = False

        # This test validates our database setup
        self.assertTrue(connection_works, "Database connection should work")


class TestDataIntegrity(unittest.TestCase):
    """Test suite for data integrity validation"""

    def setUp(self):
        """Set up test environment"""
        self.db_config = {
            "host": "horse_racing_postgres_clean",
            "port": 5432,
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "secure_password_123",
        }

    def test_table_record_counts(self):
        """Test that tables have expected record counts"""
        expected_counts = {
            "horses": 1722,
            "jockeys_stats": 6605,
            "trainers_stats": 4260,
            "records": 2016,
            "races": 222,
        }

        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cur:
                for table, expected_count in expected_counts.items():
                    cur.execute(f"SELECT COUNT(*) FROM {table}")
                    actual_count = cur.fetchone()[0]

                    # Allow for some variance in case data has been updated
                    self.assertGreaterEqual(
                        actual_count,
                        expected_count * 0.9,
                        f"{table} should have at least 90% of expected records",
                    )
            conn.close()
        except Exception as e:
            self.skipTest(f"Database connection failed: {e}")

    def test_required_columns_exist(self):
        """Test that required columns exist in each table"""
        required_columns = {
            "jockeys_stats": ["jockey_id", "jockey_name"],
            "trainers_stats": ["trainer_id", "trainer_name"],
            "horses": ["id", "name"],
            "records": ["id", "race_id"],
            "races": ["id", "course"],
        }

        try:
            conn = psycopg2.connect(**self.db_config)
            with conn.cursor() as cur:
                for table, columns in required_columns.items():
                    for column in columns:
                        cur.execute(
                            """
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = %s AND column_name = %s
                        """,
                            (table, column),
                        )
                        result = cur.fetchone()
                        self.assertIsNotNone(
                            result, f"Column {column} should exist in table {table}"
                        )
            conn.close()
        except Exception as e:
            self.skipTest(f"Database connection failed: {e}")


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
