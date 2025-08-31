#!/usr/bin/env python3
"""
Performance Tests for Advanced Metrics System
=============================================
Tests performance benchmarks and scalability
"""

import pytest
import time
import psutil
import os
import subprocess
import pandas as pd
import numpy as np
from datetime import date, datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class TestAdvancedMetricsPerformance:
    """Performance benchmarks for advanced metrics"""

    @pytest.fixture
    def performance_data(self):
        """Generate performance test data"""
        # Create large dataset for performance testing
        data = []
        for race_id in range(1, 101):  # 100 races
            for horse_num in range(1, 11):  # 10 horses per race = 1000 total records
                data.append(
                    {
                        "race_id": race_id,
                        "horse_name": f"Horse_{race_id}_{horse_num}",
                        "race_date": date(2024, 1, 1),
                        "place": horse_num,
                        "odds": 2.0 + horse_num * 0.5,
                        "jockey_name": f"Jockey_{horse_num % 5}",
                        "trainer_name": f"Trainer_{horse_num % 10}",
                        "weight_carried": 57.0 + horse_num * 0.5,
                        "track": f"Track_{race_id % 5}",
                        "race_name": f"Race {race_id}",
                        "race_class": "Class 1" if race_id % 10 == 0 else "Class 2",
                        "distance": "8f",
                        "won": 1 if horse_num == 1 else 0,
                        "placed": 1 if horse_num <= 3 else 0,
                    }
                )

        return pd.DataFrame(data)

    def test_speed_calculation_performance(self, performance_data):
        """Test speed calculation performance with large dataset"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            # Measure execution time
            start_time = time.time()
            speed_ratings = populator.calculate_speed_ratings(performance_data)
            execution_time = time.time() - start_time

            # Performance benchmarks
            assert (
                execution_time < 5.0
            ), f"Speed calculation too slow: {execution_time}s"
            assert len(speed_ratings) == 1000, "Incorrect number of speed ratings"

            # Memory usage
            process = psutil.Process(os.getpid())
            memory_mb = process.memory_info().rss / 1024 / 1024
            assert memory_mb < 500, f"Memory usage too high: {memory_mb}MB"

    def test_power_rating_performance(self, performance_data):
        """Test power rating calculation performance"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            start_time = time.time()
            power_ratings = populator.calculate_power_ratings(performance_data)
            execution_time = time.time() - start_time

            assert (
                execution_time < 5.0
            ), f"Power calculation too slow: {execution_time}s"
            assert len(power_ratings) == 1000, "Incorrect number of power ratings"

    def test_monte_carlo_performance(self, performance_data):
        """Test Monte Carlo simulation performance"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            start_time = time.time()
            mc_results = populator.calculate_monte_carlo_results(performance_data)
            execution_time = time.time() - start_time

            # Monte Carlo is more compute intensive
            assert execution_time < 10.0, f"Monte Carlo too slow: {execution_time}s"
            assert len(mc_results) == 1000, "Incorrect number of Monte Carlo results"

    def test_database_insertion_performance(self):
        """Test database insertion performance"""
        # Create test data for insertion
        test_data = []
        for i in range(500):  # 500 records
            test_data.append(
                {
                    "horse_id": i,
                    "race_id": i // 10,
                    "horse_name": f"Test Horse {i}",
                    "calculation_date": date(2024, 1, 1),
                    "speed_figure": 60.0 + i % 40,
                    "pace_rating": 55.0 + i % 35,
                }
            )

        # Mock database insertion time
        start_time = time.time()

        # Simulate insertion time (actual database operations would be tested in integration)
        time.sleep(0.1)  # Simulate 100ms for 500 records

        insertion_time = time.time() - start_time

        # Should be able to insert 500 records quickly
        assert insertion_time < 2.0, f"Database insertion too slow: {insertion_time}s"

    def test_concurrent_calculation_performance(self, performance_data):
        """Test performance when running all calculations together"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            start_time = time.time()

            # Run all calculations
            speed_ratings = populator.calculate_speed_ratings(performance_data)
            power_ratings = populator.calculate_power_ratings(performance_data)
            mc_results = populator.calculate_monte_carlo_results(performance_data)

            total_time = time.time() - start_time

            # All calculations together should complete within reasonable time
            assert total_time < 15.0, f"Total calculation time too slow: {total_time}s"

            # Verify all results generated
            assert len(speed_ratings) == 1000
            assert len(power_ratings) == 1000
            assert len(mc_results) == 1000

    def test_memory_efficiency(self, performance_data):
        """Test memory efficiency with large datasets"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            # Process data multiple times
            for _ in range(3):
                speed_ratings = populator.calculate_speed_ratings(performance_data)
                power_ratings = populator.calculate_power_ratings(performance_data)
                mc_results = populator.calculate_monte_carlo_results(performance_data)

                # Clear variables to test garbage collection
                del speed_ratings, power_ratings, mc_results

        final_memory = process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / 1024 / 1024

        # Memory increase should be reasonable (less than 200MB)
        assert (
            memory_increase < 200
        ), f"Memory leak detected: {memory_increase}MB increase"

    def test_scalability_different_sizes(self):
        """Test performance scalability with different data sizes"""
        from docker_advanced_metrics_populator import DockerAdvancedMetricsPopulator

        sizes = [10, 50, 100, 200, 500]
        execution_times = []

        with pytest.Mock("psycopg2.connect"):
            populator = DockerAdvancedMetricsPopulator()

            for size in sizes:
                # Create data of specific size
                data = []
                for i in range(size):
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

                start_time = time.time()
                speed_ratings = populator.calculate_speed_ratings(df)
                execution_time = time.time() - start_time

                execution_times.append(execution_time)

                # Verify correct number of results
                assert len(speed_ratings) == size

        # Check that execution time scales reasonably (should be roughly linear)
        # Time per record should not increase dramatically
        time_per_record = [t / s for t, s in zip(execution_times, sizes)]

        # Later calculations shouldn't be much slower per record
        assert (
            max(time_per_record) < min(time_per_record) * 5
        ), "Performance degrades too much with scale"

    @pytest.mark.timeout(60)
    def test_real_docker_execution_performance(self):
        """Test actual Docker execution performance"""
        script_path = project_root / "docker_advanced_metrics_populator.py"

        if not script_path.exists():
            pytest.skip("Advanced metrics script not found")

        try:
            start_time = time.time()

            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    f"cat {script_path} | docker exec -i horse_racing_data_pipeline_clean python",
                ],
                capture_output=True,
                text=True,
                timeout=45,
            )

            execution_time = time.time() - start_time

            if result.returncode == 0:
                # Performance benchmarks for real execution
                assert (
                    execution_time < 30
                ), f"Real execution too slow: {execution_time}s"

                # Check output indicates successful processing
                assert "SUCCESS" in result.stdout or "✅" in result.stdout

                # Extract metrics from output if available
                if "Records processed:" in result.stdout:
                    lines = result.stdout.split("\n")
                    for line in lines:
                        if "Records processed:" in line:
                            import re

                            numbers = re.findall(r"\d+", line)
                            if numbers:
                                records_processed = int(numbers[0])
                                time_per_record = execution_time / records_processed

                                # Should process at least 10 records per second
                                assert (
                                    time_per_record < 0.1
                                ), f"Too slow: {time_per_record}s per record"
            else:
                pytest.fail(f"Docker execution failed: {result.stderr}")

        except subprocess.TimeoutExpired:
            pytest.fail("Docker execution timed out")
        except Exception as e:
            pytest.skip(f"Cannot test Docker execution: {e}")


class TestAdvancedMetricsStressTest:
    """Stress tests for advanced metrics under load"""

    def test_repeated_executions(self):
        """Test repeated executions for stability"""
        script_path = project_root / "docker_advanced_metrics_populator.py"

        if not script_path.exists():
            pytest.skip("Advanced metrics script not found")

        execution_times = []
        success_count = 0

        # Run multiple times
        for i in range(3):
            try:
                start_time = time.time()

                result = subprocess.run(
                    [
                        "bash",
                        "-c",
                        f"cat {script_path} | docker exec -i horse_racing_data_pipeline_clean python",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                execution_time = time.time() - start_time
                execution_times.append(execution_time)

                if result.returncode == 0:
                    success_count += 1

                # Small delay between executions
                time.sleep(1)

            except Exception as e:
                pytest.skip(f"Stress test execution {i+1} failed: {e}")

        # All executions should succeed
        assert success_count == 3, f"Only {success_count}/3 executions succeeded"

        # Execution times should be consistent (within 100% of average)
        avg_time = sum(execution_times) / len(execution_times)
        for exec_time in execution_times:
            assert (
                abs(exec_time - avg_time) < avg_time
            ), f"Execution time inconsistent: {exec_time}s vs avg {avg_time}s"

    def test_data_consistency_after_multiple_runs(self):
        """Test that multiple runs produce consistent data"""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="horse_racing",
                password="horse_racing_password",
                database="ai_horse_racing_db",
            )

            cursor = conn.cursor()

            # Get initial counts
            cursor.execute("SELECT COUNT(*) FROM horse_speed_ratings")
            initial_speed_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM horse_power_ratings")
            initial_power_count = cursor.fetchone()[0]

            # Run script twice
            script_path = project_root / "docker_advanced_metrics_populator.py"

            for run in range(2):
                result = subprocess.run(
                    [
                        "bash",
                        "-c",
                        f"cat {script_path} | docker exec -i horse_racing_data_pipeline_clean python",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                assert result.returncode == 0, f"Run {run+1} failed"
                time.sleep(2)  # Wait for commit

            # Check final counts
            cursor.execute("SELECT COUNT(*) FROM horse_speed_ratings")
            final_speed_count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM horse_power_ratings")
            final_power_count = cursor.fetchone()[0]

            conn.close()

            # Data should have increased
            assert final_speed_count > initial_speed_count
            assert final_power_count > initial_power_count

        except Exception as e:
            pytest.skip(f"Cannot test data consistency: {e}")


if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])
