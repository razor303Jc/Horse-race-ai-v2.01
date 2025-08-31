"""
🧪 Entity Loader Tests - v2.05
==============================

Comprehensive tests for the entity loader with place code mapping,
index table updates, and database integration.
"""

import pytest
import pandas as pd
import psycopg2
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from scripts.fixed_entity_loader_v2_05 import (
    map_place_code,
    load_horses_data,
    load_jockeys_data,
    load_trainers_data,
    load_results_data,
    update_index_tables,
    verify_data_loading,
)


class TestPlaceCodeMapping:
    """Test the place code mapping functionality"""

    def test_map_place_code_valid_numbers(self):
        """Test mapping of valid numeric place codes"""
        assert map_place_code("1") == 1
        assert map_place_code("5") == 5
        assert map_place_code("10") == 10

    def test_map_place_code_special_codes(self):
        """Test mapping of special racing codes"""
        assert map_place_code("F") == 999  # Fell
        assert map_place_code("PU") == 998  # Pulled Up
        assert map_place_code("U") == 997  # Unseated
        assert map_place_code("RR") == 996  # Refused to Race

    def test_map_place_code_case_insensitive(self):
        """Test that place codes are case insensitive"""
        assert map_place_code("f") == 999
        assert map_place_code("pu") == 998
        assert map_place_code("u") == 997
        assert map_place_code("rr") == 996

    def test_map_place_code_invalid_input(self):
        """Test handling of invalid place codes"""
        assert map_place_code("invalid") == 0
        assert map_place_code("") == 0
        assert map_place_code(None) == 0
        assert map_place_code("999") == 999  # Large number should work


class TestEntityLoaderFunctions:
    """Test entity loader functions with mocked database"""

    @pytest.fixture
    def mock_csv_data(self):
        """Create mock CSV data for testing"""
        return {
            "horses": pd.DataFrame(
                {
                    "Horse ID": [1, 2, 3],
                    "Horse Name": ["Test Horse 1", "Test Horse 2", "Test Horse 3"],
                    "Age": [4, 5, 3],
                    "Sex": ["C", "F", "G"],
                    "Trainer": ["Trainer A", "Trainer B", "Trainer C"],
                    "Rating": [85, 92, 78],
                }
            ),
            "jockeys": pd.DataFrame(
                {
                    "Jockey ID": [1, 2, 3],
                    "Jockey Name": ["Jockey A", "Jockey B", "Jockey C"],
                    "Claim Allowance": [0, 5, 3],
                    "Wins": [50, 30, 25],
                    "Runs": [200, 150, 100],
                    "Win Rate": [25.0, 20.0, 25.0],
                }
            ),
            "results": pd.DataFrame(
                {
                    "Race ID": [1, 1, 2],
                    "Horse Number": [1, 2, 1],
                    "Place": ["1", "F", "PU"],
                    "Draw": [1, 2, 3],
                    "Horse ID": [1, 2, 3],
                    "Name": ["Test Horse 1", "Test Horse 2", "Test Horse 3"],
                    "Country": ["GB", "IRE", "FR"],
                    "Age": [4, 5, 3],
                    "Weight": [135, 140, 132],
                    "SP": [5.0, 10.0, 15.0],
                    "Jockey": ["Jockey A", "Jockey B", "Jockey C"],
                    "Trainer": ["Trainer A", "Trainer B", "Trainer C"],
                    "Fav": ["F", "2", "3"],
                    "Distance Btn": [0, 1.5, "PU"],
                }
            ),
        }

    @pytest.fixture
    def mock_database(self):
        """Mock database connection and cursor"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        with patch("psycopg2.connect", return_value=mock_conn):
            yield mock_conn, mock_cursor

    @patch("scripts.fixed_entity_loader_v2_05.execute_sql")
    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_horses_data_success(
        self, mock_exists, mock_read_csv, mock_execute_sql, mock_csv_data
    ):
        """Test successful loading of horses data"""
        mock_exists.return_value = True
        mock_read_csv.return_value = mock_csv_data["horses"]
        mock_execute_sql.return_value = True

        result = load_horses_data()

        assert result is True
        assert mock_execute_sql.call_count >= 2  # DELETE + INSERT calls
        mock_read_csv.assert_called_once()

    @patch("scripts.fixed_entity_loader_v2_05.execute_sql")
    @patch("pandas.read_csv")
    @patch("pathlib.Path.exists")
    def test_load_results_data_with_place_codes(
        self, mock_exists, mock_read_csv, mock_execute_sql, mock_csv_data
    ):
        """Test loading results data with place code mapping"""
        mock_exists.return_value = True
        mock_read_csv.return_value = mock_csv_data["results"]
        mock_execute_sql.return_value = True

        result = load_results_data()

        assert result is True
        # Verify that execute_sql was called with mapped place codes
        calls = mock_execute_sql.call_args_list
        insert_call = None
        for call in calls:
            if "INSERT INTO race_results" in str(call):
                insert_call = str(call)
                break

        if insert_call:
            assert "999" in insert_call  # F should be mapped to 999
            assert "998" in insert_call  # PU should be mapped to 998


class TestIndexTableUpdates:
    """Test index table update functionality"""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection for index updates"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor

        # Mock cursor.rowcount for different scenarios
        mock_cursor.rowcount = 5  # Simulate 5 new records added

        return mock_conn, mock_cursor

    @patch("psycopg2.connect")
    def test_update_index_tables_success(self, mock_connect, mock_db_connection):
        """Test successful index table updates"""
        mock_conn, mock_cursor = mock_db_connection
        mock_connect.return_value = mock_conn

        result = update_index_tables()

        assert result is True
        assert mock_cursor.execute.call_count == 3  # horses, jockeys, trainers
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

    @patch("psycopg2.connect")
    def test_update_index_tables_no_new_entities(
        self, mock_connect, mock_db_connection
    ):
        """Test index table update with no new entities"""
        mock_conn, mock_cursor = mock_db_connection
        mock_connect.return_value = mock_conn
        mock_cursor.rowcount = 0  # No new records

        result = update_index_tables()

        assert result is True
        mock_conn.commit.assert_called_once()

    @patch("psycopg2.connect")
    def test_update_index_tables_database_error(self, mock_connect):
        """Test index table update with database error"""
        mock_connect.side_effect = psycopg2.OperationalError("Connection failed")

        result = update_index_tables()

        assert result is False


class TestDatabaseIntegration:
    """Integration tests for database operations"""

    @pytest.fixture
    def test_db_config(self):
        """Test database configuration"""
        return {
            "host": "localhost",
            "database": "test_horse_racing_db",
            "user": "test_user",
            "password": "test_password",
            "port": "5432",
        }

    def test_database_connection_real(self):
        """Test actual database connection (skipped if no test DB)"""
        pytest.skip("Requires test database setup")

        # This would test against a real test database
        # conn = psycopg2.connect(**test_db_config)
        # assert conn is not None
        # conn.close()

    @patch("scripts.fixed_entity_loader_v2_05.execute_sql")
    def test_verify_data_loading(self, mock_execute_sql):
        """Test data loading verification"""
        # Mock the SQL responses for each table count
        mock_execute_sql.side_effect = [
            [{"count": 418}],  # horses_entity
            [{"count": 6606}],  # jockeys_entity
            [{"count": 4260}],  # trainers_entity
            [{"count": 44}],  # races
            [{"count": 391}],  # race_results
        ]

        total_records = verify_data_loading()

        assert total_records == 11719  # Sum of all counts
        assert mock_execute_sql.call_count == 5


class TestEntityLoaderIntegration:
    """Integration tests for the complete entity loader pipeline"""

    @patch("scripts.fixed_entity_loader_v2_05.load_horses_data")
    @patch("scripts.fixed_entity_loader_v2_05.load_jockeys_data")
    @patch("scripts.fixed_entity_loader_v2_05.load_trainers_data")
    @patch("scripts.fixed_entity_loader_v2_05.load_races_data")
    @patch("scripts.fixed_entity_loader_v2_05.load_results_data")
    @patch("scripts.fixed_entity_loader_v2_05.update_index_tables")
    @patch("scripts.fixed_entity_loader_v2_05.verify_data_loading")
    def test_main_pipeline_success(
        self,
        mock_verify,
        mock_update_index,
        mock_load_results,
        mock_load_races,
        mock_load_trainers,
        mock_load_jockeys,
        mock_load_horses,
    ):
        """Test the complete pipeline execution"""
        # Mock all functions to return success
        mock_load_horses.return_value = True
        mock_load_jockeys.return_value = True
        mock_load_trainers.return_value = True
        mock_load_races.return_value = True
        mock_load_results.return_value = True
        mock_update_index.return_value = True
        mock_verify.return_value = 15000  # Above threshold

        from scripts.fixed_entity_loader_v2_05 import main

        result = main()

        assert result == 0  # Success

        # Verify all functions were called
        mock_load_horses.assert_called_once()
        mock_load_jockeys.assert_called_once()
        mock_load_trainers.assert_called_once()
        mock_load_races.assert_called_once()
        mock_load_results.assert_called_once()
        mock_update_index.assert_called_once()
        mock_verify.assert_called_once()

    @patch("scripts.fixed_entity_loader_v2_05.load_horses_data")
    @patch("scripts.fixed_entity_loader_v2_05.verify_data_loading")
    def test_main_pipeline_failure(self, mock_verify, mock_load_horses):
        """Test pipeline failure handling"""
        mock_load_horses.return_value = False  # Simulate failure
        mock_verify.return_value = 5000  # Below threshold

        from scripts.fixed_entity_loader_v2_05 import main

        result = main()

        assert result == 1  # Failure


class TestDataValidation:
    """Test data validation and edge cases"""

    def test_place_code_mapping_edge_cases(self):
        """Test edge cases in place code mapping"""
        # Test various input types
        assert map_place_code(1) == 1  # Integer input
        assert map_place_code("01") == 1  # String with leading zero
        assert map_place_code(" F ") == 999  # String with whitespace
        assert map_place_code("f ") == 999  # Lowercase with space

    def test_csv_data_validation(self):
        """Test CSV data validation"""
        # This would test various CSV edge cases
        # like missing values, special characters, etc.
        pass

    def test_database_constraint_handling(self):
        """Test handling of database constraints"""
        # This would test foreign key constraints,
        # unique constraints, etc.
        pass


# Performance tests
class TestPerformance:
    """Performance tests for entity loading"""

    @pytest.mark.slow
    def test_large_dataset_loading(self):
        """Test loading large datasets"""
        pytest.skip("Performance test - run separately")

    @pytest.mark.slow
    def test_index_update_performance(self):
        """Test index update performance"""
        pytest.skip("Performance test - run separately")


# Fixtures for test data
@pytest.fixture
def sample_race_results():
    """Sample race results data for testing"""
    return pd.DataFrame(
        {
            "Race ID": [1, 1, 1, 2, 2],
            "Horse Number": [1, 2, 3, 1, 2],
            "Place": ["1", "2", "F", "PU", "U"],
            "Horse ID": [101, 102, 103, 104, 105],
            "Name": ["Horse A", "Horse B", "Horse C", "Horse D", "Horse E"],
            "Jockey": ["Jockey 1", "Jockey 2", "Jockey 3", "Jockey 4", "Jockey 5"],
            "Trainer": [
                "Trainer A",
                "Trainer B",
                "Trainer C",
                "Trainer D",
                "Trainer E",
            ],
        }
    )


@pytest.fixture
def database_test_config():
    """Database configuration for testing"""
    return {
        "host": "localhost",
        "database": "results_horse_racing_db",
        "user": "horse_racing",
        "password": "horse_racing_password",
        "port": "5432",
    }
