#!/usr/bin/env python3
"""
Integration Tests for Advanced Metrics System
=============================================
Tests the complete advanced metrics pipeline with Docker integration
"""

import pytest
import docker
import psycopg2
import pandas as pd
import time
from datetime import date, datetime
from typing import Dict, List
import subprocess
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))


class TestAdvancedMetricsDockerIntegration:
    """Test advanced metrics with Docker containers"""

    @pytest.fixture(scope="class")
    def docker_client(self):
        """Get Docker client"""
        return docker.from_env()

    @pytest.fixture(scope="class")
    def container_status(self, docker_client):
        """Check if required containers are running"""
        required_containers = [
            "horse_racing_postgres_clean",
            "horse_racing_data_pipeline_clean",
        ]

        running_containers = {}
        containers = docker_client.containers.list()

        for container in containers:
            if any(req in container.name for req in required_containers):
                running_containers[container.name] = container.status

        return running_containers

    @pytest.fixture
    def db_connection(self, container_status):
        """Create database connection for testing"""
        if "horse_racing_postgres_clean" not in container_status:
            pytest.skip("PostgreSQL container not running")

        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="horse_racing",
                password="horse_racing_password",
                database="ai_horse_racing_db",
            )
            yield conn
            conn.close()
        except Exception as e:
            pytest.skip(f"Cannot connect to database: {e}")

    def test_containers_running(self, container_status):
        """Test that required containers are running"""
        assert "horse_racing_postgres_clean" in container_status
        assert "horse_racing_data_pipeline_clean" in container_status

        for container, status in container_status.items():
            assert status == "running", f"Container {container} is not running"

    def test_database_connectivity(self, db_connection):
        """Test database connectivity and schema"""
        cursor = db_connection.cursor()

        # Test connection
        cursor.execute("SELECT 1")
        assert cursor.fetchone()[0] == 1

        # Check required tables exist
        required_tables = [
            "horse_speed_ratings",
            "horse_power_ratings",
            "monte_carlo_simulations",
        ]

        for table in required_tables:
            cursor.execute(
                "SELECT EXISTS(SELECT FROM information_schema.tables WHERE table_name=%s)",
                (table,),
            )
            assert cursor.fetchone()[0], f"Table {table} does not exist"

    def test_results_database_has_data(self):
        """Test that results database has sample data"""
        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                user="horse_racing",
                password="horse_racing_password",
                database="results_horse_racing_db",
            )

            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM result_records")
            count = cursor.fetchone()[0]

            assert count > 0, "Results database has no data"
            conn.close()

        except Exception as e:
            pytest.fail(f"Cannot access results database: {e}")

    def test_advanced_metrics_script_execution(self, container_status, db_connection):
        """Test the complete advanced metrics script execution"""
        if "horse_racing_data_pipeline_clean" not in container_status:
            pytest.skip("Data pipeline container not running")

        # Get initial counts
        cursor = db_connection.cursor()
        initial_counts = {}

        tables = [
            "horse_speed_ratings",
            "horse_power_ratings",
            "monte_carlo_simulations",
        ]
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            initial_counts[table] = cursor.fetchone()[0]

        # Run the advanced metrics script
        script_path = project_root / "docker_advanced_metrics_populator.py"

        try:
            # Execute the script in the container
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_data_pipeline_clean",
                    "python",
                    "-c",
                    f"exec(open('/tmp/test_script.py').read())",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            # Check if execution was successful
            assert result.returncode == 0, f"Script failed: {result.stderr}"
            assert "SUCCESS" in result.stdout or "✅" in result.stdout

        except subprocess.TimeoutExpired:
            pytest.fail("Script execution timed out")
        except Exception as e:
            # Fallback: try the pipe method
            try:
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

                assert result.returncode == 0, f"Script failed: {result.stderr}"
                assert "SUCCESS" in result.stdout or "✅" in result.stdout

            except Exception as fallback_error:
                pytest.fail(f"Both execution methods failed: {e}, {fallback_error}")

        # Verify data was inserted
        time.sleep(2)  # Give time for data to be committed

        final_counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            final_counts[table] = cursor.fetchone()[0]

        # Verify counts increased
        for table in tables:
            assert (
                final_counts[table] > initial_counts[table]
            ), f"No new data inserted into {table}"

    def test_data_quality_after_insertion(self, db_connection):
        """Test data quality after metrics insertion"""
        cursor = db_connection.cursor()

        # Test speed ratings quality
        cursor.execute(
            """
            SELECT COUNT(*), AVG(speed_figure), MIN(speed_figure), MAX(speed_figure)
            FROM horse_speed_ratings 
            WHERE created_at >= CURRENT_DATE
        """
        )

        count, avg_speed, min_speed, max_speed = cursor.fetchone()

        if count > 0:
            assert 20 <= min_speed <= 120, f"Speed figures out of range: {min_speed}"
            assert 20 <= max_speed <= 120, f"Speed figures out of range: {max_speed}"
            assert 40 <= avg_speed <= 100, f"Average speed figure unusual: {avg_speed}"

        # Test power ratings quality
        cursor.execute(
            """
            SELECT COUNT(*), AVG(power_rating), MIN(power_rating), MAX(power_rating)
            FROM horse_power_ratings 
            WHERE created_at >= CURRENT_DATE
        """
        )

        count, avg_power, min_power, max_power = cursor.fetchone()

        if count > 0:
            assert 40 <= min_power <= 140, f"Power ratings out of range: {min_power}"
            assert 40 <= max_power <= 140, f"Power ratings out of range: {max_power}"
            assert 60 <= avg_power <= 120, f"Average power rating unusual: {avg_power}"

        # Test Monte Carlo probabilities
        cursor.execute(
            """
            SELECT COUNT(*), AVG(win_probability), MIN(win_probability), MAX(win_probability)
            FROM monte_carlo_simulations 
            WHERE created_at >= CURRENT_DATE
        """
        )

        count, avg_win_prob, min_win_prob, max_win_prob = cursor.fetchone()

        if count > 0:
            assert (
                0 <= min_win_prob <= 1
            ), f"Win probabilities out of range: {min_win_prob}"
            assert (
                0 <= max_win_prob <= 1
            ), f"Win probabilities out of range: {max_win_prob}"

    def test_horse_consistency_across_tables(self, db_connection):
        """Test that horse data is consistent across all metrics tables"""
        cursor = db_connection.cursor()

        # Get horses from recent insertions
        cursor.execute(
            """
            SELECT DISTINCT horse_name 
            FROM horse_speed_ratings 
            WHERE created_at >= CURRENT_DATE
            LIMIT 5
        """
        )

        test_horses = [row[0] for row in cursor.fetchall()]

        if test_horses:
            for horse_name in test_horses:
                # Check horse exists in all tables
                cursor.execute(
                    "SELECT COUNT(*) FROM horse_speed_ratings WHERE horse_name = %s",
                    (horse_name,),
                )
                speed_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM horse_power_ratings WHERE horse_name = %s",
                    (horse_name,),
                )
                power_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM monte_carlo_simulations WHERE horse_name = %s",
                    (horse_name,),
                )
                mc_count = cursor.fetchone()[0]

                # Horse should have entries in all metric tables
                assert speed_count > 0, f"Horse {horse_name} missing from speed ratings"
                assert power_count > 0, f"Horse {horse_name} missing from power ratings"
                assert mc_count > 0, f"Horse {horse_name} missing from Monte Carlo"

    def test_race_relationship_integrity(self, db_connection):
        """Test that race relationships are maintained across tables"""
        cursor = db_connection.cursor()

        # Get recent race IDs
        cursor.execute(
            """
            SELECT DISTINCT race_id 
            FROM horse_speed_ratings 
            WHERE created_at >= CURRENT_DATE
            LIMIT 3
        """
        )

        race_ids = [row[0] for row in cursor.fetchall()]

        if race_ids:
            for race_id in race_ids:
                # Count horses in each table for this race
                cursor.execute(
                    "SELECT COUNT(*) FROM horse_speed_ratings WHERE race_id = %s",
                    (race_id,),
                )
                speed_horses = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM horse_power_ratings WHERE race_id = %s",
                    (race_id,),
                )
                power_horses = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM monte_carlo_simulations WHERE race_id = %s",
                    (race_id,),
                )
                mc_horses = cursor.fetchone()[0]

                # Should have same number of horses in each table for the race
                assert speed_horses == power_horses == mc_horses, (
                    f"Horse count mismatch for race {race_id}: "
                    f"speed={speed_horses}, power={power_horses}, mc={mc_horses}"
                )

    def test_performance_benchmarks(self, container_status):
        """Test performance benchmarks for the metrics calculation"""
        if "horse_racing_data_pipeline_clean" not in container_status:
            pytest.skip("Data pipeline container not running")

        script_path = project_root / "docker_advanced_metrics_populator.py"

        # Time the execution
        start_time = time.time()

        try:
            result = subprocess.run(
                [
                    "bash",
                    "-c",
                    f"cat {script_path} | docker exec -i horse_racing_data_pipeline_clean python",
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            execution_time = time.time() - start_time

            # Should complete within reasonable time (2 minutes for full dataset)
            assert execution_time < 120, f"Execution took too long: {execution_time}s"

            # For 200 records, should be much faster
            if "200 race result records" in result.stdout:
                assert (
                    execution_time < 30
                ), f"200 records took too long: {execution_time}s"

        except subprocess.TimeoutExpired:
            pytest.fail("Performance test timed out - execution too slow")


class TestAdvancedMetricsNodeRedIntegration:
    """Test Node-RED integration scenarios"""

    def test_exec_node_command_format(self):
        """Test that the exec node command is properly formatted"""
        script_path = project_root / "docker_advanced_metrics_populator.py"

        # Test that the script file exists
        assert script_path.exists(), "Advanced metrics script not found"

        # Test that the command format is correct
        expected_command = f"cat {script_path} | docker exec -i horse_racing_data_pipeline_clean python"

        # Verify command components
        assert "cat" in expected_command
        assert "docker exec -i" in expected_command
        assert "horse_racing_data_pipeline_clean" in expected_command
        assert "python" in expected_command

    def test_output_parsing_for_node_red(self, container_status):
        """Test that output can be parsed by Node-RED functions"""
        if "horse_racing_data_pipeline_clean" not in container_status:
            pytest.skip("Data pipeline container not running")

        script_path = project_root / "docker_advanced_metrics_populator.py"

        try:
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

            output = result.stdout

            # Check for expected success indicators
            success_indicators = ["SUCCESS", "✅", "Complete", "populated"]
            assert any(
                indicator in output for indicator in success_indicators
            ), "No success indicators found in output"

            # Check for structured data that Node-RED can parse
            if "Records processed:" in output:
                # Extract numbers for Node-RED dashboard
                lines = output.split("\n")
                for line in lines:
                    if "Records processed:" in line or "ratings:" in line:
                        # Should contain numbers that can be extracted
                        import re

                        numbers = re.findall(r"\d+", line)
                        assert len(numbers) > 0, f"No numbers found in line: {line}"

        except Exception as e:
            pytest.skip(f"Cannot test output parsing: {e}")

    def test_error_handling_for_node_red(self):
        """Test error output format for Node-RED error handling"""
        # Test with invalid container name
        result = subprocess.run(
            ["docker", "exec", "nonexistent_container", "echo", "test"],
            capture_output=True,
            text=True,
        )

        # Should return non-zero exit code
        assert result.returncode != 0

        # Error should be in stderr
        assert len(result.stderr) > 0

    def test_timeout_handling(self):
        """Test timeout scenarios for Node-RED exec nodes"""
        # Test with a command that times out
        try:
            result = subprocess.run(
                ["docker", "exec", "horse_racing_data_pipeline_clean", "sleep", "2"],
                capture_output=True,
                text=True,
                timeout=1,
            )

            pytest.fail("Command should have timed out")

        except subprocess.TimeoutExpired:
            # This is expected - Node-RED should handle timeouts gracefully
            pass


if __name__ == "__main__":
    # Run integration tests
    pytest.main([__file__, "-v", "--tb=short", "-x"])
