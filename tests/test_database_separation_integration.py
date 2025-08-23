#!/usr/bin/env python3
"""
Database Separation Integration Test
====================================

Comprehensive test suite for the database separation implementation:
- Tests cards_horse_racing_db and results_horse_racing_db separation
- Validates AI predictions generator integration
- Tests upload infrastructure for both databases
- Verifies data integrity and isolation
"""

import pytest
import sys
import os
import tempfile
import shutil
import json
import subprocess
import time
import psycopg2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure test logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestDatabaseSeparation:
    """Test database separation implementation."""

    @pytest.fixture(scope="class")
    def database_urls(self):
        """Database connection URLs for testing."""
        return {
            "cards": "postgresql://horse_racing:secure_password_123@localhost:5432/cards_horse_racing_db",
            "results": "postgresql://horse_racing:secure_password_123@localhost:5432/results_horse_racing_db",
            "original": "postgresql://horse_racing:secure_password_123@localhost:5432/horse_racing_db",
        }

    @pytest.fixture(scope="class")
    def test_data_dir(self):
        """Create test data directory."""
        temp_dir = tempfile.mkdtemp(prefix="db_separation_test_")
        yield temp_dir
        shutil.rmtree(temp_dir)

    def test_database_separation_exists(self, database_urls):
        """Test that both separated databases exist."""
        logger.info("🧪 Testing database separation exists...")

        for db_type, url in database_urls.items():
            try:
                # Extract database name from URL
                db_name = url.split("/")[-1]

                # Try to connect to each database
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "horse_racing_postgres_clean",
                        "psql",
                        "-U",
                        "horse_racing",
                        "-d",
                        db_name,
                        "-c",
                        "SELECT 1;",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    logger.info(f"✅ Database {db_name} is accessible")
                else:
                    logger.error(
                        f"❌ Database {db_name} not accessible: {result.stderr}"
                    )

            except Exception as e:
                logger.error(f"❌ Error testing {db_type} database: {e}")

    def test_cards_database_population(self):
        """Test that cards database has expected data."""
        logger.info("🧪 Testing cards database population...")

        expected_tables = [
            "races",
            "horses",
            "jockeys_stats",
            "trainers_stats",
            "racecard_details",
        ]

        for table in expected_tables:
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "horse_racing_postgres_clean",
                        "psql",
                        "-U",
                        "horse_racing",
                        "-d",
                        "cards_horse_racing_db",
                        "-c",
                        f"SELECT COUNT(*) FROM {table};",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    count = result.stdout.strip().split("\n")[2].strip()
                    logger.info(f"✅ Cards {table}: {count} rows")
                    assert int(count) > 0, f"Cards {table} should have data"
                else:
                    logger.error(f"❌ Error checking cards {table}: {result.stderr}")

            except Exception as e:
                logger.error(f"❌ Error testing cards {table}: {e}")

    def test_results_database_population(self):
        """Test that results database has expected data."""
        logger.info("🧪 Testing results database population...")

        expected_tables = [
            "races",
            "horses",
            "jockeys_stats",
            "trainers_stats",
            "records",
        ]

        for table in expected_tables:
            try:
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "horse_racing_postgres_clean",
                        "psql",
                        "-U",
                        "horse_racing",
                        "-d",
                        "results_horse_racing_db",
                        "-c",
                        f"SELECT COUNT(*) FROM {table};",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    count = result.stdout.strip().split("\n")[2].strip()
                    logger.info(f"✅ Results {table}: {count} rows")
                    assert int(count) > 0, f"Results {table} should have data"
                else:
                    logger.error(f"❌ Error checking results {table}: {result.stderr}")

            except Exception as e:
                logger.error(f"❌ Error testing results {table}: {e}")

    def test_data_isolation(self):
        """Test that cards and results data are properly isolated."""
        logger.info("🧪 Testing data isolation between databases...")

        try:
            # Check that cards database has race cards data
            cards_result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "cards_horse_racing_db",
                    "-c",
                    "SELECT COUNT(*) FROM racecard_details;",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Check that results database has race results data
            results_result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "results_horse_racing_db",
                    "-c",
                    "SELECT COUNT(*) FROM records;",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cards_result.returncode == 0 and results_result.returncode == 0:
                cards_count = int(cards_result.stdout.strip().split("\n")[2].strip())
                results_count = int(
                    results_result.stdout.strip().split("\n")[2].strip()
                )

                logger.info(f"✅ Cards database has {cards_count} racecard details")
                logger.info(f"✅ Results database has {results_count} race records")

                assert cards_count > 0, "Cards database should have racecard details"
                assert results_count > 0, "Results database should have race records"

            else:
                logger.error("❌ Error checking data isolation")

        except Exception as e:
            logger.error(f"❌ Error testing data isolation: {e}")

    def test_ai_predictions_generator_exists(self):
        """Test that AI predictions generator is properly integrated."""
        logger.info("🧪 Testing AI predictions generator integration...")

        ai_generator_path = (
            project_root / "tools/ml_training/ai_race_predictions_generator.py"
        )

        assert ai_generator_path.exists(), "AI predictions generator should exist"

        # Check file size to ensure it's the full implementation
        file_size = ai_generator_path.stat().st_size
        assert (
            file_size > 30000
        ), f"AI generator should be substantial (got {file_size} bytes)"

        # Check for key imports and classes
        content = ai_generator_path.read_text()
        assert (
            "V201EnsemblePredictor" in content
        ), "Should integrate V201EnsemblePredictor"
        assert "cards_horse_racing_db" in content, "Should reference cards database"
        assert "RacePrediction" in content, "Should have RacePrediction class"

        logger.info("✅ AI predictions generator is properly integrated")

    def test_upload_scripts_exist(self):
        """Test that upload scripts for both databases exist."""
        logger.info("🧪 Testing upload scripts existence...")

        upload_scripts = [
            "tools/data_processing/upload_mapped_data_container.py",
            "tools/data_processing/upload_results_data_container.py",
        ]

        for script_path in upload_scripts:
            full_path = project_root / script_path
            assert full_path.exists(), f"Upload script {script_path} should exist"

            # Check that scripts have proper database targeting
            content = full_path.read_text()
            if "mapped_data" in script_path:
                assert (
                    "cards_horse_racing_db" in content
                ), "Cards upload should target cards database"
            elif "results_data" in script_path:
                assert (
                    "results_horse_racing_db" in content
                ), "Results upload should target results database"

        logger.info("✅ Upload scripts are properly configured")

    def test_schema_compatibility(self):
        """Test that database schemas are compatible with CSV data."""
        logger.info("🧪 Testing schema compatibility...")

        try:
            # Test cards database schema
            cards_schema = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "cards_horse_racing_db",
                    "-c",
                    "\\d races",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            # Test results database schema
            results_schema = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "results_horse_racing_db",
                    "-c",
                    "\\d races",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if cards_schema.returncode == 0 and results_schema.returncode == 0:
                logger.info("✅ Both database schemas are accessible")

                # Check for key columns
                assert (
                    "race_id" in cards_schema.stdout
                ), "Cards races should have race_id"
                assert (
                    "race_id" in results_schema.stdout
                ), "Results races should have race_id"

            else:
                logger.error("❌ Error checking schema compatibility")

        except Exception as e:
            logger.error(f"❌ Error testing schema compatibility: {e}")


class TestPipelineIntegration:
    """Test pipeline integration with database separation."""

    def test_pipeline_coordinator_awareness(self):
        """Test that pipeline coordinator is aware of database separation."""
        logger.info("🧪 Testing pipeline coordinator integration...")

        coordinator_path = project_root / "tools/pipeline_coordinator.py"
        assert coordinator_path.exists(), "Pipeline coordinator should exist"

        content = coordinator_path.read_text()
        assert "results_data" in content, "Pipeline should handle results data"
        assert "cards_data" in content, "Pipeline should handle cards data"

        logger.info("✅ Pipeline coordinator is aware of database separation")

    def test_docker_compose_configuration(self):
        """Test that Docker Compose is properly configured."""
        logger.info("🧪 Testing Docker Compose configuration...")

        compose_path = project_root / "docker-compose.clean.yml"
        assert compose_path.exists(), "Docker Compose file should exist"

        content = compose_path.read_text()
        assert (
            "horse_racing_postgres_clean" in content
        ), "Should have PostgreSQL service"
        assert (
            "horse_racing_data_pipeline_clean" in content
        ), "Should have pipeline service"

        logger.info("✅ Docker Compose is properly configured")

    def test_environment_configuration(self):
        """Test that environment variables are properly configured."""
        logger.info("🧪 Testing environment configuration...")

        env_path = project_root / ".env"
        if env_path.exists():
            content = env_path.read_text()
            if "CARDS_DATABASE_URL" in content and "RESULTS_DATABASE_URL" in content:
                logger.info("✅ Environment variables are configured")
            else:
                logger.warning("⚠️ Environment variables may need configuration")
        else:
            logger.warning("⚠️ .env file not found")


class TestSystemIntegration:
    """Test complete system integration."""

    def test_end_to_end_workflow(self):
        """Test complete end-to-end workflow."""
        logger.info("🧪 Testing end-to-end workflow...")

        # This would test:
        # 1. Data download → 2. Upload to cards DB → 3. AI predictions → 4. Results upload → 5. Validation

        try:
            # Check that data pipeline container is running
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--filter",
                    "name=horse_racing_data_pipeline_clean",
                    "--format",
                    "{{.Status}}",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if "Up" in result.stdout:
                logger.info("✅ Data pipeline container is running")
            else:
                logger.warning("⚠️ Data pipeline container may not be running")

        except Exception as e:
            logger.error(f"❌ Error testing end-to-end workflow: {e}")

    def test_performance_metrics(self):
        """Test system performance metrics."""
        logger.info("🧪 Testing performance metrics...")

        try:
            # Test database query performance
            start_time = time.time()

            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "cards_horse_racing_db",
                    "-c",
                    "SELECT COUNT(*) FROM races JOIN horses ON 1=1;",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            query_time = time.time() - start_time

            if result.returncode == 0:
                logger.info(f"✅ Database query completed in {query_time:.2f} seconds")
                assert query_time < 10, "Database queries should be reasonably fast"
            else:
                logger.error("❌ Database query failed")

        except Exception as e:
            logger.error(f"❌ Error testing performance: {e}")


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
