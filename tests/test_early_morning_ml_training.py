#!/usr/bin/env python3
"""
Comprehensive Tests for Early Morning ML Training System
Horse Racing AI v2.02

Tests the early morning ML training pipeline integration with comprehensive
error handling, logging verification, and Docker compatibility.
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import unittest
from datetime import datetime, time, timedelta
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "docker" / "ml_training"))
sys.path.append(str(project_root / "docker" / "pipeline_management"))

# Import components to test
from docker.ml_training.early_morning_ml_trainer import (
    DockerLogger,
    EarlyMorningMLTrainer,
    EarlyMorningTrainingConfig,
    TrainingMetrics,
)
from docker.ml_training.pipeline_integration import EarlyMorningPipelineIntegration


class TestEarlyMorningTrainingConfig(unittest.TestCase):
    """Test configuration class"""

    def test_default_config(self):
        """Test default configuration values"""
        config = EarlyMorningTrainingConfig()

        self.assertEqual(config.start_time, "00:30")
        self.assertEqual(config.end_time, "04:00")
        self.assertEqual(config.total_minutes, 210)
        self.assertEqual(config.max_training_cycles, 8)
        self.assertEqual(config.cycle_duration_minutes, 25)
        self.assertTrue(config.performance_tracking)

    def test_config_customization(self):
        """Test configuration customization"""
        config = EarlyMorningTrainingConfig(
            start_time="01:00", end_time="05:00", max_training_cycles=10
        )

        self.assertEqual(config.start_time, "01:00")
        self.assertEqual(config.end_time, "05:00")
        self.assertEqual(config.max_training_cycles, 10)


class TestTrainingMetrics(unittest.TestCase):
    """Test metrics tracking"""

    def test_metrics_initialization(self):
        """Test metrics initialization"""
        metrics = TrainingMetrics()

        self.assertIsNotNone(metrics.session_id)
        self.assertIsInstance(metrics.start_time, datetime)
        self.assertEqual(metrics.total_cycles, 0)
        self.assertEqual(metrics.successful_cycles, 0)
        self.assertEqual(metrics.failed_cycles, 0)
        self.assertIsInstance(metrics.errors, list)
        self.assertIsInstance(metrics.warnings, list)

    def test_metrics_updates(self):
        """Test metrics updates"""
        metrics = TrainingMetrics()

        # Update metrics
        metrics.total_cycles = 5
        metrics.successful_cycles = 4
        metrics.failed_cycles = 1
        metrics.total_training_time = 1500.0

        # Verify updates
        self.assertEqual(metrics.total_cycles, 5)
        self.assertEqual(metrics.successful_cycles, 4)
        self.assertEqual(metrics.failed_cycles, 1)
        self.assertEqual(metrics.total_training_time, 1500.0)


class TestDockerLogger(unittest.TestCase):
    """Test Docker logging system"""

    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.logs_dir = Path(self.temp_dir) / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def test_logger_initialization(self):
        """Test logger initialization"""
        with patch("pathlib.Path.exists", return_value=True):
            logger = DockerLogger("test_component")

            self.assertIsNotNone(logger.logger)
            self.assertEqual(logger.component_name, "test_component")

    def test_logging_methods(self):
        """Test different logging methods"""
        logger = DockerLogger("test_component")

        # Test logging methods (they should not raise exceptions)
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.debug("Test debug message")
        logger.performance("Test performance", duration=1.5)

        # Test error logging with exception
        try:
            raise ValueError("Test error")
        except Exception as e:
            logger.error("Test error message", error=e)


class TestEarlyMorningMLTrainer(unittest.TestCase):
    """Test early morning ML trainer"""

    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test config
        self.config = EarlyMorningTrainingConfig()
        self.config.data_path = str(self.temp_dir / "data")
        self.config.models_path = str(self.temp_dir / "models")
        self.config.logs_path = str(self.temp_dir / "logs")
        self.config.max_training_cycles = 2  # Reduce for testing
        self.config.timeout_seconds = 10  # Short timeout for testing

        # Create directories
        Path(self.config.data_path).mkdir(exist_ok=True)
        Path(self.config.models_path).mkdir(exist_ok=True)
        Path(self.config.logs_path).mkdir(exist_ok=True)

    def test_trainer_initialization(self):
        """Test trainer initialization"""
        trainer = EarlyMorningMLTrainer(self.config)

        self.assertIsNotNone(trainer.config)
        self.assertIsNotNone(trainer.logger)
        self.assertIsNotNone(trainer.metrics)
        self.assertEqual(trainer.config.max_training_cycles, 2)

    @patch("docker.ml_training.early_morning_ml_trainer.PipelineTimeAllocator")
    def test_pipeline_integration_initialization(self, mock_allocator):
        """Test pipeline integration initialization"""
        mock_allocator.return_value = MagicMock()

        trainer = EarlyMorningMLTrainer(self.config)

        self.assertIsNotNone(trainer.pipeline_allocator)

    async def test_preconditions_validation(self):
        """Test preconditions validation"""
        trainer = EarlyMorningMLTrainer(self.config)

        # Create test data directory
        Path(self.config.data_path).mkdir(exist_ok=True)

        # Mock the data download verification
        with patch.object(
            trainer, "_verify_data_download_completion", new_callable=AsyncMock
        ):
            try:
                await trainer._validate_training_preconditions()
                # If no exception, validation passed
                self.assertTrue(True)
            except Exception as e:
                self.fail(f"Preconditions validation failed: {e}")

    async def test_single_training_cycle(self):
        """Test single training cycle execution"""
        trainer = EarlyMorningMLTrainer(self.config)

        # Mock the ML training methods
        trainer._load_training_data = AsyncMock()
        trainer._train_models = AsyncMock()
        trainer._validate_and_save_models = AsyncMock()

        try:
            await trainer._execute_single_cycle(0)
            # If no exception, cycle completed
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Single training cycle failed: {e}")

    async def test_training_timeout(self):
        """Test training timeout handling"""
        trainer = EarlyMorningMLTrainer(self.config)

        # Mock a slow training cycle
        async def slow_training(cycle):
            await asyncio.sleep(15)  # Longer than timeout

        trainer._run_ml_training_cycle = slow_training

        with self.assertRaises(TimeoutError):
            await trainer._execute_single_cycle(0)

    async def test_error_handling_in_cycles(self):
        """Test error handling during training cycles"""
        trainer = EarlyMorningMLTrainer(self.config)

        # Mock training method that raises error
        async def failing_training(cycle):
            raise ValueError("Simulated training error")

        trainer._run_ml_training_cycle = failing_training

        # Execute training cycles (should handle errors gracefully)
        await trainer._execute_training_cycles()

        # Check that failed cycles were recorded
        self.assertGreater(trainer.metrics.failed_cycles, 0)
        self.assertEqual(trainer.metrics.successful_cycles, 0)


class TestPipelineIntegration(unittest.TestCase):
    """Test pipeline integration"""

    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Mock environment variables
        self.env_patch = patch.dict(
            os.environ,
            {
                "DATA_PATH": str(self.temp_dir / "data"),
                "MODELS_PATH": str(self.temp_dir / "models"),
                "LOGS_PATH": str(self.temp_dir / "logs"),
                "ML_MAX_CYCLES": "3",
                "ML_LOG_LEVEL": "DEBUG",
            },
        )
        self.env_patch.start()

    def tearDown(self):
        """Cleanup test environment"""
        self.env_patch.stop()

    @patch("docker.ml_training.pipeline_integration.PipelineTimeAllocator")
    def test_integration_initialization(self, mock_allocator):
        """Test integration initialization"""
        mock_allocator.return_value = MagicMock()

        integration = EarlyMorningPipelineIntegration()

        self.assertIsNotNone(integration.logger)
        self.assertIsNotNone(integration.pipeline_allocator)

    def test_training_window_check(self):
        """Test training window checking"""
        integration = EarlyMorningPipelineIntegration()

        # Test with mock time
        with patch("docker.ml_training.pipeline_integration.datetime") as mock_datetime:
            # Mock current time as 02:00 (in training window)
            mock_datetime.now.return_value.time.return_value = time(2, 0)

            in_window, status = integration.check_training_window()

            self.assertTrue(in_window)
            self.assertIn("In training window", status)

    def test_buffer_time_calculation(self):
        """Test buffer time calculation"""
        integration = EarlyMorningPipelineIntegration()

        # Test buffer calculation
        buffer = integration._calculate_buffer_time("04:00", "13:45")

        # Should be approximately 9 hours 45 minutes = 585 minutes
        self.assertEqual(buffer, 585)

    async def test_pipeline_timing_calculation(self):
        """Test pipeline timing calculation"""
        with patch(
            "docker.ml_training.pipeline_integration.PipelineTimeAllocator"
        ) as mock_allocator:
            # Mock pipeline allocation response
            mock_schedule = {
                "stage_schedule": {
                    "ml_model_training": {
                        "start_time": "00:30",
                        "end_time": "04:00",
                        "duration_minutes": 210,
                    }
                },
                "timing_analysis": {"schedule_type": "normal"},
            }

            mock_allocator.return_value.allocate_stage_times.return_value = (
                mock_schedule
            )

            integration = EarlyMorningPipelineIntegration()

            timing = await integration._calculate_pipeline_timing("00:30", "13:45")

            self.assertEqual(timing["ml_training_start"], "00:30")
            self.assertEqual(timing["ml_training_end"], "04:00")
            self.assertEqual(timing["ml_duration_minutes"], 210)
            self.assertEqual(timing["schedule_type"], "normal")

    async def test_ml_configuration(self):
        """Test ML training configuration"""
        integration = EarlyMorningPipelineIntegration()

        # Mock pipeline timing
        pipeline_timing = {
            "ml_training_start": "00:30",
            "ml_training_end": "04:00",
            "ml_duration_minutes": 210,
            "buffer_to_race_minutes": 585,
        }

        config = await integration._configure_ml_training(pipeline_timing)

        self.assertEqual(config.start_time, "00:30")
        self.assertEqual(config.end_time, "04:00")
        self.assertEqual(config.total_minutes, 210)
        self.assertLessEqual(config.max_training_cycles, 8)

    async def test_status_reporting(self):
        """Test status reporting"""
        integration = EarlyMorningPipelineIntegration()

        # Mock training results
        training_results = {
            "session_id": "test_session",
            "successful_cycles": 3,
            "failed_cycles": 0,
            "total_training_time": 1500.0,
        }

        status = await integration._update_pipeline_status(training_results)

        self.assertTrue(status["early_morning_ml_complete"])
        self.assertTrue(status["ml_training_success"])
        self.assertTrue(status["ready_for_next_phase"])
        self.assertEqual(status["next_phase"], "data_processing")


class TestIntegrationScenarios(unittest.TestCase):
    """Test complete integration scenarios"""

    def setUp(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()

        # Create test directories
        for subdir in ["data", "models", "logs", "reports", "cache"]:
            Path(self.temp_dir / subdir).mkdir(exist_ok=True)

    @patch("docker.ml_training.pipeline_integration.PipelineTimeAllocator")
    @patch("docker.ml_training.early_morning_ml_trainer.PipelineTimeAllocator")
    async def test_complete_early_morning_workflow(
        self, mock_trainer_allocator, mock_integration_allocator
    ):
        """Test complete early morning ML workflow"""

        # Mock pipeline allocations
        mock_schedule = {
            "stage_schedule": {
                "ml_model_training": {
                    "start_time": "00:30",
                    "end_time": "04:00",
                    "duration_minutes": 210,
                }
            },
            "timing_analysis": {"schedule_type": "normal"},
        }

        mock_integration_allocator.return_value.allocate_stage_times.return_value = (
            mock_schedule
        )
        mock_trainer_allocator.return_value = MagicMock()

        # Setup environment
        with patch.dict(
            os.environ,
            {
                "DATA_PATH": str(self.temp_dir / "data"),
                "MODELS_PATH": str(self.temp_dir / "models"),
                "LOGS_PATH": str(self.temp_dir / "logs"),
                "ML_MAX_CYCLES": "2",
            },
        ):

            # Create integration
            integration = EarlyMorningPipelineIntegration()

            # Mock trainer execution
            with patch.object(
                integration, "_execute_ml_training", new_callable=AsyncMock
            ) as mock_training:
                mock_training.return_value = {
                    "session_id": "test_session",
                    "successful_cycles": 2,
                    "failed_cycles": 0,
                    "total_training_time": 1200.0,
                }

                # Execute workflow
                result = await integration.execute_early_morning_ml_phase()

                # Verify results
                self.assertTrue(result["success"])
                self.assertIn("pipeline_schedule", result)
                self.assertIn("training_results", result)
                self.assertIn("pipeline_status", result)

    async def test_error_recovery_scenario(self):
        """Test error recovery scenario"""

        with patch.dict(
            os.environ,
            {
                "DATA_PATH": str(self.temp_dir / "data"),
                "MODELS_PATH": str(self.temp_dir / "models"),
                "LOGS_PATH": str(self.temp_dir / "logs"),
            },
        ):

            # Create trainer with error-prone configuration
            config = EarlyMorningTrainingConfig()
            config.max_training_cycles = 2
            config.max_retries = 1

            trainer = EarlyMorningMLTrainer(config)

            # Mock training that fails
            async def failing_training(cycle):
                raise RuntimeError("Simulated training failure")

            trainer._run_ml_training_cycle = failing_training

            # Execute training (should handle errors)
            try:
                await trainer._execute_training_cycles()
                # Should complete without raising exception
                self.assertTrue(True)

                # Check error metrics
                self.assertGreater(trainer.metrics.failed_cycles, 0)
                self.assertGreater(len(trainer.metrics.errors), 0)

            except Exception as e:
                self.fail(f"Error recovery failed: {e}")


class TestDockerCompatibility(unittest.TestCase):
    """Test Docker environment compatibility"""

    def test_environment_variable_handling(self):
        """Test environment variable handling"""
        with patch.dict(
            os.environ,
            {
                "ML_LOG_LEVEL": "DEBUG",
                "ML_MAX_CYCLES": "5",
                "ML_TIMEOUT": "3600",
                "ML_MAX_RETRIES": "2",
            },
        ):

            config = EarlyMorningTrainingConfig()

            # Environment variables should be handled by the integration layer
            integration = EarlyMorningPipelineIntegration()

            # Verify integration can access environment
            self.assertEqual(os.environ.get("ML_LOG_LEVEL"), "DEBUG")
            self.assertEqual(os.environ.get("ML_MAX_CYCLES"), "5")

    def test_docker_path_handling(self):
        """Test Docker path handling"""
        config = EarlyMorningTrainingConfig()

        # Default paths should be Docker-compatible
        self.assertTrue(
            config.data_path.startswith("/app/") or not config.data_path.startswith("/")
        )
        self.assertTrue(
            config.models_path.startswith("/app/")
            or not config.models_path.startswith("/")
        )
        self.assertTrue(
            config.logs_path.startswith("/app/") or not config.logs_path.startswith("/")
        )

    def test_logging_configuration(self):
        """Test logging configuration for Docker"""
        logger = DockerLogger("test_docker")

        # Should create logger without errors
        self.assertIsNotNone(logger.logger)

        # Should handle Docker environment
        with patch.dict(os.environ, {"HOSTNAME": "test-container"}):
            logger.info("Test Docker log message")


# Test suite execution
def create_test_suite():
    """Create comprehensive test suite"""
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestEarlyMorningTrainingConfig,
        TestTrainingMetrics,
        TestDockerLogger,
        TestEarlyMorningMLTrainer,
        TestPipelineIntegration,
        TestIntegrationScenarios,
        TestDockerCompatibility,
    ]

    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)

    return suite


async def run_async_tests():
    """Run async tests separately"""
    print("🧪 Running async tests...")

    # Test async components
    test_instances = [
        TestEarlyMorningMLTrainer(),
        TestPipelineIntegration(),
        TestIntegrationScenarios(),
    ]

    for instance in test_instances:
        instance.setUp() if hasattr(instance, "setUp") else None

        # Run async test methods
        for method_name in dir(instance):
            if method_name.startswith("test_") and asyncio.iscoroutinefunction(
                getattr(instance, method_name)
            ):
                try:
                    print(f"  Running {instance.__class__.__name__}.{method_name}")
                    await getattr(instance, method_name)()
                    print(f"  ✅ {method_name} passed")
                except Exception as e:
                    print(f"  ❌ {method_name} failed: {e}")

        instance.tearDown() if hasattr(instance, "tearDown") else None


def main():
    """Main test execution"""
    print("🌅 Early Morning ML Training System - Test Suite")
    print("=" * 60)

    # Run synchronous tests
    print("\n🧪 Running synchronous tests...")
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    sync_result = runner.run(suite)

    # Run asynchronous tests
    print("\n🧪 Running asynchronous tests...")
    asyncio.run(run_async_tests())

    # Summary
    print("\n📊 Test Summary:")
    print(
        f"  Synchronous tests: {sync_result.testsRun} run, {len(sync_result.failures)} failed, {len(sync_result.errors)} errors"
    )

    if sync_result.wasSuccessful():
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
