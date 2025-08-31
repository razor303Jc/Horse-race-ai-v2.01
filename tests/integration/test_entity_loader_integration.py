"""
🧪 Entity Loader Integration Tests - v2.05
==========================================

Integration tests for the complete entity loader pipeline including
database operations, place code mapping, and index table maintenance.
"""

import pytest
import psycopg2
import pandas as pd
from unittest.mock import patch, Mock
import tempfile
import os
from pathlib import Path
import sys

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))


class TestDatabaseIntegration:
    """Integration tests for database operations"""

    @pytest.fixture
    def db_config(self):
        """Database configuration for testing"""
        return {
            "host": "localhost",
            "database": "results_horse_racing_db",
            "user": "horse_racing",
            "password": "horse_racing_password",
            "port": "5432",
        }

    @pytest.mark.integration
    def test_database_connectivity(self, db_config):
        """Test actual database connectivity"""
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for integration testing")

    @pytest.mark.integration
    def test_table_structure(self, db_config):
        """Test that all required tables exist with correct structure"""
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Test main tables exist
            required_tables = [
                "horses_entity",
                "jockeys_entity",
                "trainers_entity",
                "races",
                "race_results",
                "horses_index",
                "jockeys_index",
                "trainers_index",
            ]

            for table in required_tables:
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """,
                    (table,),
                )
                exists = cursor.fetchone()[0]
                assert exists, f"Table {table} does not exist"

            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for integration testing")

    @pytest.mark.integration
    def test_index_table_structure(self, db_config):
        """Test index table structure and constraints"""
        try:
            conn = psycopg2.connect(**db_config)
            cursor = conn.cursor()

            # Test horses_index structure
            cursor.execute(
                """
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'horses_index'
                ORDER BY ordinal_position;
            """
            )
            horses_columns = cursor.fetchall()

            expected_columns = [
                ("id", "integer"),
                ("horse_name", "character varying"),
                ("horse_id", "integer"),
            ]

            for expected in expected_columns:
                assert any(
                    col[0] == expected[0] for col in horses_columns
                ), f"Column {expected[0]} not found in horses_index"

            cursor.close()
            conn.close()
        except psycopg2.OperationalError:
            pytest.skip("Database not available for integration testing")


class TestPlaceCodeIntegration:
    """Integration tests for place code mapping in the pipeline"""

    @pytest.fixture
    def sample_csv_with_place_codes(self):
        """Create temporary CSV with place codes for testing"""
        data = {
            "Race ID": [1, 1, 1, 1, 1],
            "Horse Number": [1, 2, 3, 4, 5],
            "Place": ["1", "2", "F", "PU", "U"],
            "Draw": [1, 2, 3, 4, 5],
            "Horse ID": [101, 102, 103, 104, 105],
            "Name": ["Horse A", "Horse B", "Horse C", "Horse D", "Horse E"],
            "Country": ["GB", "IRE", "FR", "GB", "IRE"],
            "Age": [4, 5, 3, 6, 4],
            "Weight": [135, 140, 132, 145, 138],
            "SP": [5.0, 10.0, 15.0, 8.0, 12.0],
            "Jockey": ["Jockey 1", "Jockey 2", "Jockey 3", "Jockey 4", "Jockey 5"],
            "Trainer": [
                "Trainer A",
                "Trainer B",
                "Trainer C",
                "Trainer D",
                "Trainer E",
            ],
            "Fav": ["F", "2", "3", "4", "5"],
            "Distance Btn": [0, 1.5, "F", "PU", "U"],
        }

        df = pd.DataFrame(data)
        temp_file = tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()

        yield temp_file.name

        # Cleanup
        os.unlink(temp_file.name)

    def test_place_code_mapping_in_results(self, sample_csv_with_place_codes):
        """Test that place codes are correctly mapped when loading results"""
        from scripts.fixed_entity_loader_v2_05 import map_place_code

        # Read the test CSV
        df = pd.read_csv(sample_csv_with_place_codes)

        # Apply place code mapping as the loader would
        mapped_places = [map_place_code(str(place)) for place in df["Place"]]

        expected_places = [1, 2, 999, 998, 997]  # 1, 2, F, PU, U
        assert mapped_places == expected_places


class TestPipelineIntegration:
    """Test the complete pipeline integration"""

    @pytest.mark.integration
    @patch("scripts.fixed_entity_loader_v2_05.Path")
    def test_complete_pipeline_mock(self, mock_path):
        """Test complete pipeline with mocked file system"""
        # Mock CSV files existence
        mock_path.return_value.exists.return_value = True

        # Mock pandas read_csv for different files
        mock_data = {
            "horses.csv": pd.DataFrame(
                {
                    "Horse ID": [1, 2],
                    "Horse Name": ["Test Horse 1", "Test Horse 2"],
                    "Age": [4, 5],
                    "Sex": ["C", "F"],
                    "Trainer": ["Trainer A", "Trainer B"],
                    "Rating": [85, 92],
                }
            ),
            "results.csv": pd.DataFrame(
                {
                    "Race ID": [1, 1],
                    "Horse Number": [1, 2],
                    "Place": ["1", "F"],
                    "Draw": [1, 2],
                    "Horse ID": [1, 2],
                    "Name": ["Test Horse 1", "Test Horse 2"],
                    "Country": ["GB", "IRE"],
                    "Age": [4, 5],
                    "Weight": [135, 140],
                    "SP": [5.0, 10.0],
                    "Jockey": ["Jockey A", "Jockey B"],
                    "Trainer": ["Trainer A", "Trainer B"],
                    "Fav": ["F", "2"],
                    "Distance Btn": [0, "F"],
                }
            ),
        }

        with (
            patch("pandas.read_csv") as mock_read_csv,
            patch("scripts.fixed_entity_loader_v2_05.execute_sql") as mock_execute_sql,
            patch(
                "scripts.fixed_entity_loader_v2_05.update_index_tables"
            ) as mock_update_index,
        ):

            # Configure mocks
            mock_read_csv.side_effect = lambda path: mock_data.get(
                Path(path).name, pd.DataFrame()
            )
            mock_execute_sql.return_value = True
            mock_update_index.return_value = True

            # Import and run main
            from scripts.fixed_entity_loader_v2_05 import main

            with patch(
                "scripts.fixed_entity_loader_v2_05.verify_data_loading",
                return_value=15000,
            ):
                result = main()

            assert result == 0  # Success
            mock_update_index.assert_called_once()


class TestDataConsistency:
    """Test data consistency between tables"""

    @pytest.mark.integration
    def test_entity_consistency(self):
        """Test that entities are consistent between main and index tables"""
        pytest.skip("Requires test database with actual data")

        # This would test:
        # - All horses in race_results exist in horses_index
        # - All jockeys in race_results exist in jockeys_index
        # - All trainers in race_results exist in trainers_index

    @pytest.mark.integration
    def test_referential_integrity(self):
        """Test referential integrity constraints"""
        pytest.skip("Requires test database setup")

        # This would test:
        # - Foreign key constraints work
        # - Cascading deletes/updates
        # - Unique constraints


class TestPerformanceIntegration:
    """Performance tests for the integrated system"""

    @pytest.mark.slow
    @pytest.mark.integration
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        pytest.skip("Performance test - requires large test dataset")

    @pytest.mark.slow
    @pytest.mark.integration
    def test_index_update_performance(self):
        """Test index update performance with large datasets"""
        pytest.skip("Performance test - requires large test dataset")


class TestErrorRecovery:
    """Test error recovery and rollback scenarios"""

    @pytest.mark.integration
    def test_transaction_rollback(self):
        """Test that transactions rollback on error"""
        pytest.skip("Requires test database setup")

    @pytest.mark.integration
    def test_partial_load_recovery(self):
        """Test recovery from partial data loads"""
        pytest.skip("Requires test database setup")


class TestDataValidationIntegration:
    """Integration tests for data validation"""

    def test_place_code_validation_complete(self):
        """Test complete place code validation pipeline"""
        from scripts.fixed_entity_loader_v2_05 import map_place_code

        # Test all known place codes
        test_cases = [
            ("1", 1),
            ("2", 2),
            ("10", 10),
            ("F", 999),
            ("f", 999),
            ("PU", 998),
            ("pu", 998),
            ("U", 997),
            ("u", 997),
            ("RR", 996),
            ("rr", 996),
            ("invalid", 0),
            ("", 0),
            (None, 0),
        ]

        for input_val, expected in test_cases:
            result = map_place_code(input_val)
            assert (
                result == expected
            ), f"Failed for input {input_val}: expected {expected}, got {result}"

    def test_csv_edge_cases(self):
        """Test handling of CSV edge cases"""
        # Test empty values, special characters, etc.
        pass


# Fixtures for integration testing
@pytest.fixture(scope="session")
def test_database():
    """Set up test database for integration tests"""
    # This would set up a test database
    yield "test_db_connection"
    # Cleanup would happen here


@pytest.fixture
def clean_database_state():
    """Ensure clean database state for each test"""
    # This would clean/reset test database
    yield
    # Cleanup after test


@pytest.fixture
def sample_test_data():
    """Provide sample test data for integration tests"""
    return {
        "horses": [
            {"horse_id": 1, "horse_name": "Test Horse 1", "age": 4},
            {"horse_id": 2, "horse_name": "Test Horse 2", "age": 5},
        ],
        "jockeys": [
            {"jockey_id": 1, "jockey_name": "Test Jockey 1"},
            {"jockey_id": 2, "jockey_name": "Test Jockey 2"},
        ],
        "results": [
            {"race_id": 1, "horse_id": 1, "place": "1"},
            {"race_id": 1, "horse_id": 2, "place": "F"},
        ],
    }
