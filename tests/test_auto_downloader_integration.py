#!/usr/bin/env python3
"""
Comprehensive test suite for auto-downloader integration into main Docker compose.

This test suite verifies:
1. Auto-downloader service is properly configured in main docker-compose.yml
2. Service dependencies are correctly set up
3. Environment variables and volumes are properly configured
4. Integration with ML training pipeline is working
5. Docker compose validation passes

Created as part of Docker ecosystem consolidation.
"""

import logging
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, patch

import pytest
import yaml

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAutoDownloaderIntegration:
    """Test suite for auto-downloader integration into main docker-compose.yml"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup test environment"""
        self.project_root = Path(__file__).parent.parent
        self.compose_file = self.project_root / "docker-compose.yml"
        self.auto_downloader_config_file = (
            self.project_root
            / "configs"
            / "docker"
            / "docker-compose.auto-downloader.yml"
        )

        # Ensure files exist
        assert (
            self.compose_file.exists()
        ), f"Main docker-compose.yml not found at {self.compose_file}"
        assert (
            self.auto_downloader_config_file.exists()
        ), f"Auto-downloader config not found at {self.auto_downloader_config_file}"

        # Load compose configurations
        with open(self.compose_file, "r") as f:
            self.main_compose = yaml.safe_load(f)

        with open(self.auto_downloader_config_file, "r") as f:
            self.auto_downloader_compose = yaml.safe_load(f)

        logger.info(
            f"Test setup complete. Main compose has {len(self.main_compose.get('services', {}))} services"
        )

    def test_auto_downloader_service_exists(self):
        """Test that auto-downloader service is present in main docker-compose.yml"""
        services = self.main_compose.get("services", {})

        # Check main auto-downloader service
        assert (
            "auto-downloader" in services
        ), "auto-downloader service not found in main docker-compose.yml"

        # Check test service
        assert (
            "auto-downloader-test" in services
        ), "auto-downloader-test service not found in main docker-compose.yml"

        logger.info("✓ Auto-downloader services found in main docker-compose.yml")

    def test_auto_downloader_configuration(self):
        """Test that auto-downloader service is properly configured"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        # Test basic configuration
        assert "build" in auto_downloader, "Auto-downloader missing build configuration"
        assert (
            "environment" in auto_downloader
        ), "Auto-downloader missing environment configuration"
        assert (
            "volumes" in auto_downloader
        ), "Auto-downloader missing volumes configuration"
        assert (
            "networks" in auto_downloader
        ), "Auto-downloader missing networks configuration"

        # Test container name
        assert (
            auto_downloader["container_name"] == "horserace-auto-downloader"
        ), "Wrong container name"

        # Test critical environment variables
        env_vars = auto_downloader["environment"]
        required_env_vars = [
            "DOCKER_CONTAINER=true",
            "HEADLESS=true",
            "PLAYWRIGHT_BROWSERS_PATH=/app/.playwright",
            "TZ=Europe/London",
            "LOG_LEVEL=INFO",
            "PYTHONUNBUFFERED=1",
            "PYTHONDONTWRITEBYTECODE=1",
        ]

        for required_var in required_env_vars:
            assert (
                required_var in env_vars
            ), f"Missing required environment variable: {required_var}"

        # Test volumes
        volumes = auto_downloader["volumes"]
        required_volumes = [
            "./data:/app/data",
            "./logs:/app/logs",
            "./cache:/app/cache",
            "/tmp:/tmp",
            "/dev/shm:/dev/shm",
            "/etc/localtime:/etc/localtime:ro",
        ]

        for required_volume in required_volumes:
            assert (
                required_volume in volumes
            ), f"Missing required volume: {required_volume}"

        logger.info("✓ Auto-downloader configuration validated")

    def test_auto_downloader_profiles(self):
        """Test that auto-downloader is assigned to correct profiles"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]
        auto_downloader_test = self.main_compose["services"]["auto-downloader-test"]

        # Main service should be in data-processing profile
        assert "profiles" in auto_downloader, "Auto-downloader missing profiles"
        assert (
            "data-processing" in auto_downloader["profiles"]
        ), "Auto-downloader not in data-processing profile"

        # Test service should be in test profile
        assert (
            "profiles" in auto_downloader_test
        ), "Auto-downloader-test missing profiles"
        assert (
            "test" in auto_downloader_test["profiles"]
        ), "Auto-downloader-test not in test profile"

        logger.info("✓ Auto-downloader profiles correctly configured")

    def test_auto_downloader_dependencies(self):
        """Test that auto-downloader has correct service dependencies"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        # Should depend on postgres and redis
        assert "depends_on" in auto_downloader, "Auto-downloader missing dependencies"

        depends_on = auto_downloader["depends_on"]
        assert "postgres" in depends_on, "Auto-downloader missing postgres dependency"
        assert "redis" in depends_on, "Auto-downloader missing redis dependency"

        # Check health check conditions
        assert (
            depends_on["postgres"]["condition"] == "service_healthy"
        ), "Wrong postgres condition"
        assert (
            depends_on["redis"]["condition"] == "service_healthy"
        ), "Wrong redis condition"

        logger.info("✓ Auto-downloader dependencies correctly configured")

    def test_ml_models_depends_on_auto_downloader(self):
        """Test that ML models service depends on auto-downloader"""
        ml_models = self.main_compose["services"]["ml-models"]

        assert "depends_on" in ml_models, "ML models missing dependencies"

        depends_on = ml_models["depends_on"]
        assert (
            "auto-downloader" in depends_on
        ), "ML models missing auto-downloader dependency"
        assert (
            depends_on["auto-downloader"]["condition"] == "service_healthy"
        ), "Wrong auto-downloader condition"

        logger.info("✓ ML models correctly depends on auto-downloader")

    def test_auto_downloader_health_check(self):
        """Test that auto-downloader has proper health check configuration"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        assert "healthcheck" in auto_downloader, "Auto-downloader missing health check"

        healthcheck = auto_downloader["healthcheck"]
        assert "test" in healthcheck, "Health check missing test command"
        assert "interval" in healthcheck, "Health check missing interval"
        assert "timeout" in healthcheck, "Health check missing timeout"
        assert "retries" in healthcheck, "Health check missing retries"
        assert "start_period" in healthcheck, "Health check missing start_period"

        # Validate health check timings
        assert healthcheck["interval"] == "5m", "Wrong health check interval"
        assert healthcheck["timeout"] == "30s", "Wrong health check timeout"
        assert healthcheck["retries"] == 3, "Wrong health check retries"
        assert healthcheck["start_period"] == "2m", "Wrong health check start period"

        logger.info("✓ Auto-downloader health check properly configured")

    def test_auto_downloader_resource_limits(self):
        """Test that auto-downloader has appropriate resource limits"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        assert (
            "deploy" in auto_downloader
        ), "Auto-downloader missing deploy configuration"
        assert (
            "resources" in auto_downloader["deploy"]
        ), "Auto-downloader missing resources configuration"

        resources = auto_downloader["deploy"]["resources"]

        # Check limits
        assert "limits" in resources, "Auto-downloader missing resource limits"
        limits = resources["limits"]
        assert limits["memory"] == "3G", "Wrong memory limit"
        assert limits["cpus"] == "1.5", "Wrong CPU limit"

        # Check reservations
        assert (
            "reservations" in resources
        ), "Auto-downloader missing resource reservations"
        reservations = resources["reservations"]
        assert reservations["memory"] == "1G", "Wrong memory reservation"
        assert reservations["cpus"] == "0.5", "Wrong CPU reservation"

        logger.info("✓ Auto-downloader resource limits properly configured")

    def test_auto_downloader_browser_optimization(self):
        """Test that auto-downloader has browser-specific optimizations"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        # Check shared memory size for browser stability
        assert "shm_size" in auto_downloader, "Auto-downloader missing shm_size"
        assert (
            auto_downloader["shm_size"] == "2gb"
        ), "Wrong shm_size for browser operation"

        # Check security options for Chrome/Chromium
        assert "security_opt" in auto_downloader, "Auto-downloader missing security_opt"
        assert (
            "seccomp:unconfined" in auto_downloader["security_opt"]
        ), "Missing seccomp:unconfined for browser"

        # Check graceful shutdown
        assert (
            "stop_grace_period" in auto_downloader
        ), "Auto-downloader missing stop_grace_period"
        assert auto_downloader["stop_grace_period"] == "30s", "Wrong stop_grace_period"
        assert auto_downloader["stop_signal"] == "SIGTERM", "Wrong stop_signal"

        logger.info("✓ Auto-downloader browser optimizations properly configured")

    def test_docker_compose_validation(self):
        """Test that docker-compose.yml is valid"""
        try:
            # Use docker-compose config to validate the file
            result = subprocess.run(
                ["docker-compose", "config"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                logger.error(f"Docker compose validation failed: {result.stderr}")
                pytest.fail(f"Docker compose validation failed: {result.stderr}")

            logger.info("✓ Docker compose configuration is valid")

        except subprocess.TimeoutExpired:
            pytest.fail("Docker compose validation timed out")
        except FileNotFoundError:
            logger.warning(
                "Docker compose not available for validation (CI environment?)"
            )
            # In CI environments where docker-compose might not be available

    def test_integration_with_data_processing_profile(self):
        """Test that auto-downloader integrates properly with data-processing profile"""
        services = self.main_compose["services"]

        # Find all services in data-processing profile
        data_processing_services = []
        for service_name, service_config in services.items():
            if (
                "profiles" in service_config
                and "data-processing" in service_config["profiles"]
            ):
                data_processing_services.append(service_name)

        # Auto-downloader should be in this list
        assert (
            "auto-downloader" in data_processing_services
        ), "Auto-downloader not in data-processing profile services"

        # Should also include data-processor
        assert (
            "data-processor" in data_processing_services
        ), "data-processor not found in data-processing profile"

        logger.info(f"✓ Data-processing profile contains: {data_processing_services}")

    def test_environment_variable_integration(self):
        """Test that auto-downloader environment variables integrate with main system"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]
        env_vars = auto_downloader["environment"]

        # Should have database integration
        database_vars = [var for var in env_vars if "DATABASE_URL" in str(var)]
        redis_vars = [var for var in env_vars if "REDIS_URL" in str(var)]

        assert (
            len(database_vars) > 0
        ), "Auto-downloader missing DATABASE_URL integration"
        assert len(redis_vars) > 0, "Auto-downloader missing REDIS_URL integration"

        # Check that database URL uses the same pattern as other services
        db_url = next((var for var in env_vars if "DATABASE_URL" in str(var)), None)
        assert "postgresql://horse_racing:" in str(db_url), "Wrong database URL pattern"
        assert "@postgres:5432/horse_racing_db" in str(
            db_url
        ), "Wrong database URL endpoint"

        logger.info("✓ Auto-downloader environment variables properly integrated")

    def test_pipeline_timing_coordination(self):
        """Test that auto-downloader timing coordinates with ML training"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]
        ml_models = self.main_compose["services"]["ml-models"]

        # Auto-downloader should be in scheduled mode
        command = auto_downloader.get("command", [])
        assert "--mode" in command, "Auto-downloader missing mode specification"
        mode_index = command.index("--mode")
        assert mode_index + 1 < len(command), "Auto-downloader mode value missing"
        assert (
            command[mode_index + 1] == "scheduled"
        ), "Auto-downloader not in scheduled mode"

        # ML models should have early morning configuration
        ml_env = ml_models.get("environment", {})
        ml_start_time = None
        for var in ml_env:
            if "ML_TRAINING_START_TIME" in str(var):
                ml_start_time = str(var).split("=")[1] if "=" in str(var) else None
                break

        # Should start at 00:30 (after auto-downloader runs)
        assert ml_start_time, "ML training start time not found"
        assert (
            "00:30" in ml_start_time
        ), f"ML training start time should be 00:30, found: {ml_start_time}"

        logger.info("✓ Pipeline timing properly coordinated")

    def test_network_configuration(self):
        """Test that auto-downloader is on the correct network"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]

        assert "networks" in auto_downloader, "Auto-downloader missing networks"
        networks = auto_downloader["networks"]
        assert (
            "horse_racing_network" in networks
        ), "Auto-downloader not on horse_racing_network"

        # Check that the network exists in the main compose file
        compose_networks = self.main_compose.get("networks", {})
        assert (
            "horse_racing_network" in compose_networks
        ), "horse_racing_network not defined in main compose"

        logger.info("✓ Auto-downloader network configuration correct")

    def test_command_configuration(self):
        """Test that auto-downloader command is properly configured"""
        auto_downloader = self.main_compose["services"]["auto-downloader"]
        auto_downloader_test = self.main_compose["services"]["auto-downloader-test"]

        # Main service should run in scheduled mode
        main_command = auto_downloader.get("command", [])
        assert "python" in main_command[0], "Auto-downloader not using python"
        assert (
            "run_docker_auto_downloader.py" in main_command[1]
        ), "Auto-downloader not using correct script"
        assert "--mode" in main_command, "Auto-downloader missing mode parameter"
        assert "scheduled" in main_command, "Auto-downloader not in scheduled mode"

        # Test service should run in once mode
        test_command = auto_downloader_test.get("command", [])
        assert "python" in test_command[0], "Auto-downloader-test not using python"
        assert (
            "run_docker_auto_downloader.py" in test_command[1]
        ), "Auto-downloader-test not using correct script"
        assert "--mode" in test_command, "Auto-downloader-test missing mode parameter"
        assert "once" in test_command, "Auto-downloader-test not in once mode"

        logger.info("✓ Auto-downloader commands properly configured")


def test_integration_end_to_end():
    """End-to-end integration test"""
    logger.info("Running end-to-end integration test for auto-downloader")

    # This would be a comprehensive test that verifies the entire integration
    # In a real scenario, this might involve:
    # 1. Starting the services with docker-compose
    # 2. Verifying auto-downloader starts and runs
    # 3. Checking data is downloaded
    # 4. Verifying ML training can access the data
    # 5. Cleaning up

    # For now, we'll do a comprehensive configuration check
    test_instance = TestAutoDownloaderIntegration()
    test_instance.setup()

    # Run all validation checks
    test_methods = [
        test_instance.test_auto_downloader_service_exists,
        test_instance.test_auto_downloader_configuration,
        test_instance.test_auto_downloader_profiles,
        test_instance.test_auto_downloader_dependencies,
        test_instance.test_ml_models_depends_on_auto_downloader,
        test_instance.test_auto_downloader_health_check,
        test_instance.test_auto_downloader_resource_limits,
        test_instance.test_auto_downloader_browser_optimization,
        test_instance.test_integration_with_data_processing_profile,
        test_instance.test_environment_variable_integration,
        test_instance.test_pipeline_timing_coordination,
        test_instance.test_network_configuration,
        test_instance.test_command_configuration,
    ]

    for test_method in test_methods:
        try:
            test_method()
        except Exception as e:
            logger.error(f"Test failed: {test_method.__name__}: {str(e)}")
            raise

    logger.info("✓ All integration tests passed successfully!")


if __name__ == "__main__":
    # Run tests when executed directly
    pytest.main([__file__, "-v"])
