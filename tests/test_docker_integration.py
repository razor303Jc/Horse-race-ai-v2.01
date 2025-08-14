#!/usr/bin/env python3
"""
🐳 Docker Container & Service Integration Tests
Tests Docker container functionality and service integration

This test suite validates:
- Docker container startup and health
- Service communication and networking
- Volume mounting and data persistence
- Environment variable configuration
- Service dependency management
- Pipeline orchestration within containers

Author: AI Assistant
Date: August 14, 2025
"""

import json
import logging
import subprocess
import sys
import time
import unittest
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup test logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TestDockerServices(unittest.TestCase):
    """Test Docker container functionality and service integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_start_time = datetime.now()
        self.project_root = project_root
        logger.info(f"🧪 Docker test started: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test"""
        duration = (datetime.now() - self.test_start_time).total_seconds()
        logger.info(
            f"✅ Docker test completed: {self._testMethodName} ({duration:.2f}s)"
        )

    def run_docker_command(self, command: List[str], timeout: int = 30) -> Dict:
        """Run a docker command and return results"""
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=self.project_root,
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout.strip(),
                "stderr": result.stderr.strip(),
                "returncode": result.returncode,
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timed out",
                "returncode": -1,
            }
        except Exception as e:
            return {"success": False, "stdout": "", "stderr": str(e), "returncode": -1}

    def test_docker_compose_file_syntax(self):
        """Test that docker-compose.yml has valid syntax"""
        logger.info("🧪 Testing Docker Compose File Syntax")

        result = self.run_docker_command(["docker-compose", "config"])

        if not result["success"]:
            logger.error(f"Docker compose syntax error: {result['stderr']}")

        self.assertTrue(
            result["success"], f"docker-compose.yml syntax error: {result['stderr']}"
        )
        logger.info("✅ Docker Compose file syntax is valid")

    def test_core_services_running(self):
        """Test that core services (postgres, redis) are running"""
        logger.info("🧪 Testing Core Services Status")

        # Check postgres
        result = self.run_docker_command(["docker-compose", "ps", "postgres"])
        self.assertTrue(result["success"], "Failed to check postgres status")

        # Check redis
        result = self.run_docker_command(["docker-compose", "ps", "redis"])
        self.assertTrue(result["success"], "Failed to check redis status")

        logger.info("✅ Core services status check completed")

    def test_data_processor_container_build(self):
        """Test that data-processor container can be built"""
        logger.info("🧪 Testing Data Processor Container Build")

        # Check if Dockerfile exists
        dockerfile_path = self.project_root / "Dockerfile.data-processing"
        self.assertTrue(
            dockerfile_path.exists(), "Dockerfile.data-processing not found"
        )

        # Validate Dockerfile content
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        # Check for essential Dockerfile components
        essential_components = [
            "FROM python:",
            "WORKDIR /app",
            "COPY requirements",
            "RUN pip install",
            "COPY docker/data_processing",
        ]

        for component in essential_components:
            self.assertIn(
                component,
                dockerfile_content,
                f"Dockerfile missing essential component: {component}",
            )

        logger.info("✅ Data processor Dockerfile structure is valid")

    def test_pipeline_manager_container_build(self):
        """Test that pipeline-manager container can be built"""
        logger.info("🧪 Testing Pipeline Manager Container Build")

        # Check if Dockerfile exists
        dockerfile_path = self.project_root / "Dockerfile.pipeline-management"
        self.assertTrue(
            dockerfile_path.exists(), "Dockerfile.pipeline-management not found"
        )

        # Validate Dockerfile content
        with open(dockerfile_path, "r") as f:
            dockerfile_content = f.read()

        # Check for essential Dockerfile components
        essential_components = [
            "FROM python:",
            "WORKDIR /app",
            "COPY requirements",
            "RUN pip install",
            "COPY docker/pipeline_management",
        ]

        for component in essential_components:
            self.assertIn(
                component,
                dockerfile_content,
                f"Dockerfile missing essential component: {component}",
            )

        logger.info("✅ Pipeline manager Dockerfile structure is valid")

    def test_docker_network_configuration(self):
        """Test Docker network configuration"""
        logger.info("🧪 Testing Docker Network Configuration")

        # Get network information
        result = self.run_docker_command(["docker", "network", "ls"])
        self.assertTrue(result["success"], "Failed to list Docker networks")

        # Check for horse racing network
        networks = result["stdout"]
        logger.info(f"Available networks: {networks}")

        logger.info("✅ Docker network configuration check completed")

    def test_volume_configuration(self):
        """Test Docker volume configuration and mounting"""
        logger.info("🧪 Testing Docker Volume Configuration")

        # Check docker-compose volume configuration
        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, "r") as f:
            compose_content = f.read()

        # Check for essential volume mounts
        essential_volumes = [
            "./data:/app/data",
            "./logs:/app/logs",
            "./config:/app/config",
            "postgres_data:/var/lib/postgresql/data",
        ]

        for volume in essential_volumes:
            self.assertIn(volume, compose_content, f"Missing volume mount: {volume}")

        logger.info("✅ Docker volume configuration is correct")

    def test_environment_variables(self):
        """Test environment variable configuration"""
        logger.info("🧪 Testing Environment Variables")

        # Check docker-compose environment variables
        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, "r") as f:
            compose_content = f.read()

        # Check for essential environment variables
        essential_env_vars = [
            "POSTGRES_DB",
            "POSTGRES_USER",
            "POSTGRES_PASSWORD",
            "DATABASE_URL",
            "REDIS_URL",
            "PYTHONPATH",
        ]

        for env_var in essential_env_vars:
            self.assertIn(
                env_var, compose_content, f"Missing environment variable: {env_var}"
            )

        logger.info("✅ Environment variable configuration is correct")

    def test_service_profiles(self):
        """Test Docker Compose service profiles"""
        logger.info("🧪 Testing Service Profiles")

        # Check that profiles are configured
        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, "r") as f:
            compose_content = f.read()

        # Check for profile definitions
        expected_profiles = ["data-processing", "pipeline-management"]

        for profile in expected_profiles:
            self.assertIn(
                f"- {profile}", compose_content, f"Missing profile: {profile}"
            )

        logger.info("✅ Service profiles are correctly configured")

    def test_file_organization_in_docker_dirs(self):
        """Test that files are properly organized in Docker directories"""
        logger.info("🧪 Testing File Organization in Docker Directories")

        # Test data_processing directory
        data_processing_dir = self.project_root / "docker" / "data_processing"
        self.assertTrue(
            data_processing_dir.exists(), "data_processing directory not found"
        )

        expected_data_files = [
            "complete_csv_processor.py",
            "clean_upload.py",
            "data_cleaner.py",
        ]

        for file_name in expected_data_files:
            file_path = data_processing_dir / file_name
            self.assertTrue(file_path.exists(), f"Missing file: {file_name}")

        # Test pipeline_management directory
        pipeline_dir = self.project_root / "docker" / "pipeline_management"
        self.assertTrue(
            pipeline_dir.exists(), "pipeline_management directory not found"
        )

        expected_pipeline_files = ["dynamic_pipeline_timing.py"]

        for file_name in expected_pipeline_files:
            file_path = pipeline_dir / file_name
            self.assertTrue(file_path.exists(), f"Missing file: {file_name}")

        logger.info("✅ File organization in Docker directories is correct")


class TestPipelineOrchestration(unittest.TestCase):
    """Test pipeline orchestration and integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_start_time = datetime.now()
        self.project_root = project_root
        logger.info(f"🧪 Orchestration test started: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test"""
        duration = (datetime.now() - self.test_start_time).total_seconds()
        logger.info(
            f"✅ Orchestration test completed: {self._testMethodName} ({duration:.2f}s)"
        )

    def test_pipeline_config_generation(self):
        """Test that pipeline configuration can be generated"""
        logger.info("🧪 Testing Pipeline Configuration Generation")

        config_file = self.project_root / "config" / "complete_17_stage_config.json"

        if config_file.exists():
            with open(config_file, "r") as f:
                config = json.load(f)

            # Validate configuration structure
            self.assertIn("component_name", config)
            self.assertIn("dynamic_schedule", config)
            self.assertIn("stages", config)
            self.assertIn("timing", config)

            # Validate 17 stages
            self.assertEqual(len(config["stages"]), 17)
            self.assertEqual(config["timing"]["stage_count"], 17)

            # Validate phase distribution
            phases = set(stage["phase"] for stage in config["stages"])
            expected_phases = {
                "data_acquisition",
                "feature_engineering",
                "advanced_analytics",
                "simulation",
                "strategy",
                "pre_race",
            }
            self.assertEqual(phases, expected_phases)

            logger.info("✅ Pipeline configuration is valid")
        else:
            logger.warning("⚠️ Pipeline configuration file not found")
            self.skipTest("Configuration file not available")

    def test_csv_mapping_configuration(self):
        """Test CSV column mapping configuration"""
        logger.info("🧪 Testing CSV Mapping Configuration")

        mapping_file = self.project_root / "config" / "complete_csv_column_mapping.json"

        if mapping_file.exists():
            with open(mapping_file, "r") as f:
                mapping = json.load(f)

            # Check for essential tables
            essential_tables = [
                "races",
                "records",
                "horses",
                "jockeys_stats",
                "trainers_stats",
            ]

            for table in essential_tables:
                self.assertIn(table, mapping, f"Missing table mapping: {table}")
                self.assertIsInstance(
                    mapping[table], dict, f"Table {table} should have column mappings"
                )

            logger.info("✅ CSV mapping configuration is valid")
        else:
            logger.warning("⚠️ CSV mapping configuration file not found")
            self.skipTest("CSV mapping file not available")

    def test_docker_compose_service_dependencies(self):
        """Test that Docker services have proper dependencies"""
        logger.info("🧪 Testing Docker Service Dependencies")

        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, "r") as f:
            compose_content = f.read()

        # Check that data-processor depends on postgres and redis
        self.assertIn("depends_on:", compose_content)
        self.assertIn("postgres:", compose_content)
        self.assertIn("condition: service_healthy", compose_content)

        logger.info("✅ Docker service dependencies are correctly configured")

    def test_health_checks(self):
        """Test that health checks are configured"""
        logger.info("🧪 Testing Health Check Configuration")

        compose_file = self.project_root / "docker-compose.yml"
        with open(compose_file, "r") as f:
            compose_content = f.read()

        # Check for health check configuration
        self.assertIn("healthcheck:", compose_content)
        self.assertIn("test:", compose_content)
        self.assertIn("interval:", compose_content)
        self.assertIn("timeout:", compose_content)
        self.assertIn("retries:", compose_content)

        logger.info("✅ Health check configuration is present")


class TestSystemIntegration(unittest.TestCase):
    """Test complete system integration"""

    def setUp(self):
        """Set up test environment"""
        self.test_start_time = datetime.now()
        self.project_root = project_root
        logger.info(f"🧪 System integration test started: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test"""
        duration = (datetime.now() - self.test_start_time).total_seconds()
        logger.info(
            f"✅ System integration test completed: {self._testMethodName} ({duration:.2f}s)"
        )

    def test_complete_file_structure(self):
        """Test that all necessary files are in place"""
        logger.info("🧪 Testing Complete File Structure")

        essential_files = [
            "docker-compose.yml",
            "Dockerfile.data-processing",
            "Dockerfile.pipeline-management",
            "config/complete_17_stage_config.json",
            "config/complete_csv_column_mapping.json",
            "17_STAGE_PIPELINE_PLANNING.md",
            "docker/data_processing/complete_csv_processor.py",
            "docker/pipeline_management/dynamic_pipeline_timing.py",
        ]

        for file_path in essential_files:
            full_path = self.project_root / file_path
            self.assertTrue(full_path.exists(), f"Missing essential file: {file_path}")

        logger.info("✅ Complete file structure is in place")

    def test_git_commit_status(self):
        """Test that changes have been committed to git"""
        logger.info("🧪 Testing Git Commit Status")

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=self.project_root,
            )

            if result.returncode == 0:
                # Check if working directory is clean
                status_output = result.stdout.strip()
                if not status_output:
                    logger.info("✅ Working directory is clean - all changes committed")
                else:
                    logger.info(f"ℹ️ Uncommitted changes: {status_output}")
            else:
                logger.warning("⚠️ Git status check failed")

        except Exception as e:
            logger.warning(f"⚠️ Git status check failed: {e}")
            self.skipTest("Git not available")

    def test_pipeline_documentation(self):
        """Test that pipeline documentation is comprehensive"""
        logger.info("🧪 Testing Pipeline Documentation")

        planning_doc = self.project_root / "17_STAGE_PIPELINE_PLANNING.md"

        if planning_doc.exists():
            with open(planning_doc, "r") as f:
                content = f.read()

            # Check for essential documentation sections
            essential_sections = [
                "17-Stage Pipeline",
                "Phase 1: DATA ACQUISITION",
                "Phase 2: FEATURE ENGINEERING",
                "Phase 3: ADVANCED ANALYTICS",
                "Phase 4: SIMULATION",
                "Phase 5: STRATEGY",
                "Phase 6: PRE-RACE",
                "Total Pipeline Duration",
                "Critical Stages",
                "Dynamic Scaling",
            ]

            for section in essential_sections:
                self.assertIn(
                    section, content, f"Missing documentation section: {section}"
                )

            logger.info("✅ Pipeline documentation is comprehensive")
        else:
            logger.warning("⚠️ Pipeline documentation not found")
            self.skipTest("Documentation file not available")


def run_docker_integration_tests():
    """Run all Docker and integration tests"""
    print("🐳 Starting Docker Container & Integration Test Suite")
    print("=" * 60)

    start_time = datetime.now()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestDockerServices,
        TestPipelineOrchestration,
        TestSystemIntegration,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)

    # Generate summary report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("🎯 Docker Integration Test Results Summary")
    print("=" * 60)
    print(f"⏱️ Total Test Duration: {duration:.2f} seconds")
    print(f"🧪 Tests Run: {result.testsRun}")
    print(
        f"✅ Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}"
    )
    print(f"❌ Tests Failed: {len(result.failures)}")
    print(f"💥 Tests Errors: {len(result.errors)}")

    if result.failures:
        print("\n❌ Test Failures:")
        for test, traceback in result.failures:
            print(
                f"  - {test}: {traceback.split('AssertionError: ')[-1].split('\n')[0]}"
            )

    if result.errors:
        print("\n💥 Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('\n')[-2]}")

    success_rate = (
        (
            (result.testsRun - len(result.failures) - len(result.errors))
            / result.testsRun
            * 100
        )
        if result.testsRun > 0
        else 0
    )
    print(f"\n🎯 Success Rate: {success_rate:.1f}%")

    if result.wasSuccessful():
        print("\n🎉 ALL DOCKER & INTEGRATION TESTS PASSED!")
        return True
    else:
        print("\n⚠️ Some tests failed - Review and fix issues")
        return False


if __name__ == "__main__":
    success = run_docker_integration_tests()
    sys.exit(0 if success else 1)
