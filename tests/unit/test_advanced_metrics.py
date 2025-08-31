#!/usr/bin/env python3
"""
Unit Tests for Advanced Metrics System
=====================================
Tests the calculation logic of the advanced metrics without database dependencies
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime, date
from unittest.mock import Mock, patch, MagicMock
import sys
from pathlib import Path
from typing import List, Dict

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator


class TestAdvancedMetricsCalculations:
    """Test suite for advanced metrics calculation logic"""

    @pytest.fixture
    def sample_race_data(self) -> pd.DataFrame:
        """Create sample race data for testing"""
        data = {
            "race_id": [1, 1, 1, 2, 2, 2],
            "horse_name": ["Thunder", "Lightning", "Storm", "Fire", "Wind", "Spirit"],
            "race_date": [date(2024, 1, 1)] * 6,
            "place": [1, 2, 3, 1, 2, 3],
            "odds": [2.5, 3.0, 5.0, 1.8, 4.2, 8.0],
            "jockey_name": [
                "J.Smith",
                "M.Jones",
                "R.Brown",
                "K.Wilson",
                "L.Davis",
                "P.Miller",
            ],
            "trainer_name": [
                "A.Trainer",
                "B.Trainer",
                "C.Trainer",
                "D.Trainer",
                "E.Trainer",
                "F.Trainer",
            ],
            "weight_carried": [58.5, 59.0, 57.5, 58.0, 59.5, 57.0],
            "track": ["Ascot", "Ascot", "Ascot", "York", "York", "York"],
            "race_name": ["Race 1", "Race 1", "Race 1", "Race 2", "Race 2", "Race 2"],
            "race_class": [
                "Group 1",
                "Group 1",
                "Group 1",
                "Class 2",
                "Class 2",
                "Class 2",
            ],
            "distance": ["8f", "8f", "8f", "10f", "10f", "10f"],
            "won": [1, 0, 0, 1, 0, 0],
            "placed": [1, 1, 1, 1, 1, 1],
        }
        return pd.DataFrame(data)

    @pytest.fixture
    def populator(self):
        """Create a populator instance with mocked database connections"""
        with patch("psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            populator = DockerAdvancedMetricsPopulator()
            populator.results_conn = mock_conn
            populator.ai_conn = mock_conn
            populator.results_cursor = mock_cursor
            populator.ai_cursor = mock_cursor

            return populator

    def test_speed_ratings_calculation(self, populator, sample_race_data):
        """Test speed ratings calculation logic"""
        speed_ratings = populator.calculate_speed_ratings(sample_race_data)

        # Should return a list of dictionaries
        assert isinstance(speed_ratings, list)
        assert len(speed_ratings) == len(sample_race_data)

        # Check structure of first rating
        first_rating = speed_ratings[0]
        required_fields = [
            "horse_id",
            "race_id",
            "horse_name",
            "calculation_date",
            "speed_figure",
            "pace_rating",
        ]
        for field in required_fields:
            assert field in first_rating

        # Winners should have higher speed figures than non-winners
        winner_ratings = [
            r for r in speed_ratings if r["horse_name"] in ["Thunder", "Fire"]
        ]
        non_winner_ratings = [
            r for r in speed_ratings if r["horse_name"] not in ["Thunder", "Fire"]
        ]

        avg_winner_speed = np.mean([r["speed_figure"] for r in winner_ratings])
        avg_non_winner_speed = np.mean([r["speed_figure"] for r in non_winner_ratings])

        assert (
            avg_winner_speed > avg_non_winner_speed
        ), "Winners should have higher speed figures"

    def test_power_ratings_calculation(self, populator, sample_race_data):
        """Test power ratings calculation logic"""
        power_ratings = populator.calculate_power_ratings(sample_race_data)

        # Should return a list of dictionaries
        assert isinstance(power_ratings, list)
        assert len(power_ratings) == len(sample_race_data)

        # Check structure
        first_rating = power_ratings[0]
        required_fields = [
            "horse_id",
            "race_id",
            "horse_name",
            "calculation_date",
            "base_power_rating",
            "final_power_rating",
        ]
        for field in required_fields:
            assert field in first_rating

        # Power ratings should be within expected range
        for rating in power_ratings:
            assert 40 <= rating["final_power_rating"] <= 140
            assert 40 <= rating["base_power_rating"] <= 140

    def test_monte_carlo_calculation(self, populator, sample_race_data):
        """Test Monte Carlo simulation calculation"""
        monte_carlo_results = populator.calculate_monte_carlo_results(sample_race_data)

        # Should return a list of dictionaries
        assert isinstance(monte_carlo_results, list)
        assert len(monte_carlo_results) == len(sample_race_data)

        # Check structure
        first_result = monte_carlo_results[0]
        required_fields = [
            "simulation_session_id",
            "race_id",
            "horse_id",
            "horse_name",
            "simulation_date",
            "simulations_run",
            "win_probability",
            "place_probability",
        ]
        for field in required_fields:
            assert field in first_result

        # Probabilities should be valid
        for result in monte_carlo_results:
            assert 0 <= result["win_probability"] <= 1
            assert 0 <= result["place_probability"] <= 1
            assert result["place_probability"] >= result["win_probability"]

    def test_winner_probabilities(self, populator, sample_race_data):
        """Test that winners have higher probabilities than non-winners"""
        monte_carlo_results = populator.calculate_monte_carlo_results(sample_race_data)

        # Group by race
        race_1_results = [r for r in monte_carlo_results if r["race_id"] == 1]
        race_2_results = [r for r in monte_carlo_results if r["race_id"] == 2]

        # Winners should have higher win probabilities
        race_1_winner = next(r for r in race_1_results if r["horse_name"] == "Thunder")
        race_1_others = [r for r in race_1_results if r["horse_name"] != "Thunder"]

        for other in race_1_others:
            assert race_1_winner["win_probability"] >= other["win_probability"]

    def test_data_validation(self, populator):
        """Test data validation and error handling"""
        # Test with empty data
        empty_df = pd.DataFrame()
        speed_ratings = populator.calculate_speed_ratings(empty_df)
        assert speed_ratings == []

        # Test with invalid data
        invalid_data = pd.DataFrame(
            {
                "race_id": [1],
                "horse_name": [None],  # Invalid horse name
                "race_date": [date(2024, 1, 1)],
                "place": [1],
            }
        )

        speed_ratings = populator.calculate_speed_ratings(invalid_data)
        # Should handle gracefully and return empty or filtered results
        assert isinstance(speed_ratings, list)

    def test_calculation_consistency(self, populator, sample_race_data):
        """Test that calculations are consistent across multiple runs"""
        # Run calculations multiple times
        results_1 = populator.calculate_speed_ratings(sample_race_data)
        results_2 = populator.calculate_speed_ratings(sample_race_data)

        # Structure should be identical
        assert len(results_1) == len(results_2)

        # Horse IDs should be consistent
        horse_ids_1 = [r["horse_id"] for r in results_1]
        horse_ids_2 = [r["horse_id"] for r in results_2]
        assert horse_ids_1 == horse_ids_2

    @pytest.mark.parametrize(
        "position,expected_min_speed",
        [
            (1, 85),  # Winners should have high speed
            (2, 80),  # Second place should be good
            (3, 75),  # Third place should be decent
            (8, 50),  # Last place should be lower
        ],
    )
    def test_position_based_calculations(self, populator, position, expected_min_speed):
        """Test that finishing position affects calculated metrics appropriately"""
        test_data = pd.DataFrame(
            {
                "race_id": [1],
                "horse_name": ["Test Horse"],
                "race_date": [date(2024, 1, 1)],
                "place": [position],
                "odds": [3.0],
                "jockey_name": ["Test Jockey"],
                "trainer_name": ["Test Trainer"],
                "weight_carried": [58.0],
                "track": ["Test Track"],
                "race_name": ["Test Race"],
                "race_class": ["Class 1"],
                "distance": ["8f"],
                "won": [1 if position == 1 else 0],
                "placed": [1 if position <= 3 else 0],
            }
        )

        speed_ratings = populator.calculate_speed_ratings(test_data)
        assert len(speed_ratings) == 1

        # Speed figure should reflect position (with some randomness tolerance)
        speed_figure = speed_ratings[0]["speed_figure"]
        assert speed_figure >= expected_min_speed - 10  # Allow for randomness


class TestAdvancedMetricsIntegration:
    """Integration tests for the complete advanced metrics pipeline"""

    @pytest.fixture
    def mock_database_data(self):
        """Mock data that would come from the database"""
        return [
            (
                1,
                "Thunder Strike",
                date(2024, 1, 1),
                1,
                2.5,
                "J.Smith",
                "A.Trainer",
                58.5,
                "Ascot",
                "Test Race 1",
                "Group 1",
                "8f",
                1,
                1,
            ),
            (
                1,
                "Lightning Bolt",
                date(2024, 1, 1),
                2,
                3.0,
                "M.Jones",
                "B.Trainer",
                59.0,
                "Ascot",
                "Test Race 1",
                "Group 1",
                "8f",
                0,
                1,
            ),
            (
                2,
                "Storm Cloud",
                date(2024, 1, 2),
                1,
                1.8,
                "R.Brown",
                "C.Trainer",
                57.5,
                "York",
                "Test Race 2",
                "Class 2",
                "10f",
                1,
                1,
            ),
        ]

    def test_full_pipeline_execution(self, mock_database_data):
        """Test the complete pipeline from data extraction to metrics calculation"""
        with patch("psycopg2.connect") as mock_connect:
            # Setup mock database connections
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            # Mock the data retrieval
            mock_cursor.fetchall.return_value = mock_database_data

            populator = DockerAdvancedMetricsPopulator()

            # Mock successful database connection
            with patch.object(populator, "connect_databases", return_value=True):
                # Mock the pandas read_sql_query to return our test data
                test_df = pd.DataFrame(
                    mock_database_data,
                    columns=[
                        "race_id",
                        "horse_name",
                        "race_date",
                        "place",
                        "odds",
                        "jockey_name",
                        "trainer_name",
                        "weight_carried",
                        "track",
                        "race_name",
                        "race_class",
                        "distance",
                        "won",
                        "placed",
                    ],
                )

                with patch.object(
                    populator, "get_race_results_data", return_value=test_df
                ):
                    # Mock the insertion methods to return success
                    with (
                        patch.object(
                            populator, "insert_speed_ratings", return_value=True
                        ),
                        patch.object(
                            populator, "insert_power_ratings", return_value=True
                        ),
                        patch.object(
                            populator, "insert_monte_carlo_results", return_value=True
                        ),
                    ):

                        result = populator.run_full_population()

                        # Should return success
                        assert result["success"] is True
                        assert result["records_processed"] == 3
                        assert result["speed_ratings_created"] == 3
                        assert result["power_ratings_created"] == 3
                        assert result["monte_carlo_results_created"] == 3

    def test_database_connection_failure(self):
        """Test handling of database connection failures"""
        with patch("psycopg2.connect", side_effect=Exception("Connection failed")):
            populator = DockerAdvancedMetricsPopulator()

            result = populator.run_full_population()

            assert result["success"] is False
            assert "error" in result

    def test_empty_database_handling(self):
        """Test behavior when database has no data"""
        with patch("psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor

            populator = DockerAdvancedMetricsPopulator()

            # Mock empty data
            empty_df = pd.DataFrame()

            with (
                patch.object(populator, "connect_databases", return_value=True),
                patch.object(populator, "get_race_results_data", return_value=empty_df),
            ):

                result = populator.run_full_population()

                assert result["success"] is False
                assert "No race data found" in result["error"]


class TestAdvancedMetricsPerformance:
    """Performance tests for advanced metrics calculations"""

    def test_large_dataset_performance(self):
        """Test performance with larger datasets"""
        # Create a large dataset
        large_data = []
        for race_id in range(1, 101):  # 100 races
            for horse_num in range(1, 11):  # 10 horses per race
                large_data.append(
                    {
                        "race_id": race_id,
                        "horse_name": f"Horse_{race_id}_{horse_num}",
                        "race_date": date(2024, 1, 1),
                        "place": horse_num,
                        "odds": 2.0 + horse_num * 0.5,
                        "jockey_name": f"Jockey_{horse_num}",
                        "trainer_name": f"Trainer_{horse_num}",
                        "weight_carried": 58.0,
                        "track": "Test Track",
                        "race_name": f"Race {race_id}",
                        "race_class": "Class 1",
                        "distance": "8f",
                        "won": 1 if horse_num == 1 else 0,
                        "placed": 1 if horse_num <= 3 else 0,
                    }
                )

        large_df = pd.DataFrame(large_data)

        with patch("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            # Test speed ratings calculation time
            import time

            start_time = time.time()
            speed_ratings = populator.calculate_speed_ratings(large_df)
            speed_time = time.time() - start_time

            # Should complete within reasonable time (less than 5 seconds for 1000 records)
            assert speed_time < 5.0
            assert len(speed_ratings) == 1000

            # Test power ratings calculation time
            start_time = time.time()
            power_ratings = populator.calculate_power_ratings(large_df)
            power_time = time.time() - start_time

            assert power_time < 5.0
            assert len(power_ratings) == 1000

    def test_memory_usage(self):
        """Test that memory usage remains reasonable"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Create moderately large dataset
        data = []
        for i in range(500):
            data.append(
                {
                    "race_id": i // 10 + 1,
                    "horse_name": f"Horse_{i}",
                    "race_date": date(2024, 1, 1),
                    "place": (i % 10) + 1,
                    "odds": 2.0,
                    "jockey_name": "Test Jockey",
                    "trainer_name": "Test Trainer",
                    "weight_carried": 58.0,
                    "track": "Test Track",
                    "race_name": "Test Race",
                    "race_class": "Class 1",
                    "distance": "8f",
                    "won": 0,
                    "placed": 0,
                }
            )

        df = pd.DataFrame(data)

        with patch("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            # Run all calculations
            speed_ratings = populator.calculate_speed_ratings(df)
            power_ratings = populator.calculate_power_ratings(df)
            monte_carlo_results = populator.calculate_monte_carlo_results(df)

            final_memory = process.memory_info().rss
            memory_increase = final_memory - initial_memory

            # Memory increase should be reasonable (less than 100MB)
            assert memory_increase < 100 * 1024 * 1024


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
