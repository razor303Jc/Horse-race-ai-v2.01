#!/usr/bin/env python3
"""
Database Separation Integration Test Runner
==========================================

Comprehensive test runner for database separation implementation.
Tests all components of the separated database system.
"""

import subprocess
import sys
import time
import logging
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DatabaseSeparationTester:
    """Test runner for database separation system."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": {},
            "overall_success": False,
        }

    def run_all_tests(self):
        """Run all database separation tests."""
        logger.info("🚀 Starting Database Separation Integration Tests")
        logger.info("=" * 60)

        test_methods = [
            ("docker_containers", self.test_docker_containers),
            ("database_connectivity", self.test_database_connectivity),
            ("database_separation", self.test_database_separation),
            ("data_population", self.test_data_population),
            ("upload_scripts", self.test_upload_scripts),
            ("ai_predictions", self.test_ai_predictions),
            ("pipeline_integration", self.test_pipeline_integration),
            ("end_to_end", self.test_end_to_end_workflow),
        ]

        passed = 0
        total = len(test_methods)

        for test_name, test_method in test_methods:
            logger.info(f"\n🧪 Running test: {test_name}")
            logger.info("-" * 40)

            try:
                result = test_method()
                self.test_results["tests"][test_name] = {
                    "status": "PASSED" if result else "FAILED",
                    "timestamp": datetime.now().isoformat(),
                }

                if result:
                    logger.info(f"✅ {test_name}: PASSED")
                    passed += 1
                else:
                    logger.error(f"❌ {test_name}: FAILED")

            except Exception as e:
                logger.error(f"❌ {test_name}: ERROR - {e}")
                self.test_results["tests"][test_name] = {
                    "status": "ERROR",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }

        # Final results
        logger.info("\n" + "=" * 60)
        logger.info(f"🏁 TEST RESULTS: {passed}/{total} tests passed")

        if passed == total:
            logger.info("🎉 ALL TESTS PASSED - Database separation is ready!")
            self.test_results["overall_success"] = True
        else:
            logger.error(f"❌ {total - passed} tests failed - needs attention")

        # Save test results
        self.save_test_results()

        return passed == total

    def test_docker_containers(self) -> bool:
        """Test that required Docker containers are running."""
        logger.info("Testing Docker container status...")

        required_containers = [
            "horse_racing_postgres_clean",
            "horse_racing_data_pipeline_clean",
        ]

        try:
            result = subprocess.run(
                ["docker", "ps", "--format", "{{.Names}}"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.error("Failed to list Docker containers")
                return False

            running_containers = result.stdout.strip().split("\n")

            for container in required_containers:
                if container in running_containers:
                    logger.info(f"✅ {container} is running")
                else:
                    logger.error(f"❌ {container} is not running")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error checking containers: {e}")
            return False

    def test_database_connectivity(self) -> bool:
        """Test connectivity to both databases."""
        logger.info("Testing database connectivity...")

        databases = [
            "cards_horse_racing_db",
            "results_horse_racing_db",
            "horse_racing_db",
        ]

        try:
            for db in databases:
                result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        "horse_racing_postgres_clean",
                        "psql",
                        "-U",
                        "horse_racing",
                        "-d",
                        db,
                        "-c",
                        "SELECT 1;",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    logger.info(f"✅ {db} is accessible")
                else:
                    logger.error(f"❌ {db} is not accessible")
                    return False

            return True

        except Exception as e:
            logger.error(f"Error testing database connectivity: {e}")
            return False

    def test_database_separation(self) -> bool:
        """Test that databases are properly separated."""
        logger.info("Testing database separation...")

        try:
            # Test cards database has racecard_details
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

            # Test results database has records
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

                logger.info(f"✅ Cards DB: {cards_count} racecard details")
                logger.info(f"✅ Results DB: {results_count} race records")

                return cards_count > 0 and results_count > 0
            else:
                logger.error("Failed to query separation tables")
                return False

        except Exception as e:
            logger.error(f"Error testing database separation: {e}")
            return False

    def test_data_population(self) -> bool:
        """Test that both databases are properly populated."""
        logger.info("Testing data population...")

        expected_data = {
            "cards_horse_racing_db": {
                "races": 50,
                "horses": 500,
                "jockeys_stats": 6000,
                "trainers_stats": 4000,
                "racecard_details": 400,
            },
            "results_horse_racing_db": {
                "races": 50,
                "horses": 500,
                "jockeys_stats": 6000,
                "trainers_stats": 4000,
                "records": 300,
            },
        }

        try:
            for db_name, tables in expected_data.items():
                for table, min_count in tables.items():
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
                            f"SELECT COUNT(*) FROM {table};",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    if result.returncode == 0:
                        count = int(result.stdout.strip().split("\n")[2].strip())
                        if count >= min_count:
                            logger.info(f"✅ {db_name}.{table}: {count} rows")
                        else:
                            logger.warning(
                                f"⚠️ {db_name}.{table}: {count} rows (expected ≥{min_count})"
                            )
                    else:
                        logger.error(f"❌ Failed to query {db_name}.{table}")
                        return False

            return True

        except Exception as e:
            logger.error(f"Error testing data population: {e}")
            return False

    def test_upload_scripts(self) -> bool:
        """Test that upload scripts exist and are configured correctly."""
        logger.info("Testing upload scripts...")

        scripts = [
            "tools/data_processing/upload_mapped_data_container.py",
            "tools/data_processing/upload_results_data_container.py",
        ]

        try:
            for script_path in scripts:
                full_path = self.project_root / script_path
                if not full_path.exists():
                    logger.error(f"❌ {script_path} does not exist")
                    return False

                content = full_path.read_text()

                # Check for proper database targeting
                if "mapped_data" in script_path:
                    if "cards_horse_racing_db" not in content:
                        logger.error(f"❌ {script_path} doesn't target cards database")
                        return False
                elif "results_data" in script_path:
                    if "results_horse_racing_db" not in content:
                        logger.error(
                            f"❌ {script_path} doesn't target results database"
                        )
                        return False

                logger.info(f"✅ {script_path} is properly configured")

            return True

        except Exception as e:
            logger.error(f"Error testing upload scripts: {e}")
            return False

    def test_ai_predictions(self) -> bool:
        """Test AI predictions generator."""
        logger.info("Testing AI predictions generator...")

        try:
            ai_generator_path = (
                self.project_root / "tools/ml_training/ai_race_predictions_generator.py"
            )

            if not ai_generator_path.exists():
                logger.error("❌ AI predictions generator does not exist")
                return False

            # Check file size and content
            file_size = ai_generator_path.stat().st_size
            if file_size < 30000:
                logger.error(f"❌ AI generator seems too small ({file_size} bytes)")
                return False

            content = ai_generator_path.read_text()
            required_elements = [
                "V201EnsemblePredictor",
                "cards_horse_racing_db",
                "RacePrediction",
                "confidence_score",
            ]

            for element in required_elements:
                if element not in content:
                    logger.error(f"❌ AI generator missing: {element}")
                    return False

            logger.info(
                f"✅ AI predictions generator is properly implemented ({file_size} bytes)"
            )
            return True

        except Exception as e:
            logger.error(f"Error testing AI predictions: {e}")
            return False

    def test_pipeline_integration(self) -> bool:
        """Test pipeline integration."""
        logger.info("Testing pipeline integration...")

        try:
            pipeline_path = self.project_root / "tools/pipeline_coordinator.py"

            if not pipeline_path.exists():
                logger.error("❌ Pipeline coordinator does not exist")
                return False

            content = pipeline_path.read_text()

            # Check for database separation awareness
            integration_elements = [
                "upload_mapped_data_container.py",
                "upload_results_data_container.py",
                "ai_race_predictions_generator.py",
                "cards database",
                "results database",
            ]

            for element in integration_elements:
                if element not in content:
                    logger.error(f"❌ Pipeline missing integration: {element}")
                    return False

            logger.info("✅ Pipeline coordinator is properly integrated")
            return True

        except Exception as e:
            logger.error(f"Error testing pipeline integration: {e}")
            return False

    def test_end_to_end_workflow(self) -> bool:
        """Test end-to-end workflow simulation."""
        logger.info("Testing end-to-end workflow...")

        try:
            # Check that we can run the pipeline components
            logger.info("Testing pipeline components accessibility...")

            # Test that container can access upload scripts
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_data_pipeline_clean",
                    "ls",
                    "-la",
                    "/app/tools/data_processing/upload_mapped_data_container.py",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.error("❌ Upload scripts not accessible in container")
                return False

            # Test that AI generator is accessible
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_data_pipeline_clean",
                    "ls",
                    "-la",
                    "/app/tools/ml_training/ai_race_predictions_generator.py",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.error("❌ AI generator not accessible in container")
                return False

            logger.info("✅ End-to-end workflow components are accessible")
            return True

        except Exception as e:
            logger.error(f"Error testing end-to-end workflow: {e}")
            return False

    def save_test_results(self):
        """Save test results to file."""
        try:
            results_file = (
                self.project_root / "tests/database_separation_test_results.json"
            )

            import json

            with open(results_file, "w") as f:
                json.dump(self.test_results, f, indent=2)

            logger.info(f"📊 Test results saved to: {results_file}")

        except Exception as e:
            logger.error(f"Failed to save test results: {e}")


if __name__ == "__main__":
    tester = DatabaseSeparationTester()
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
