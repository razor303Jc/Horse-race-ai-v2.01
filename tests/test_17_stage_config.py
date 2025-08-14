#!/usr/bin/env python3
"""
🏇 Complete 17-Stage Pipeline Configuration Test Suite
Tests the complete 17-stage pipeline using actual configuration

This test suite validates:
- 17-stage configuration completeness
- Stage timing and dependencies
- Phase distribution
- Critical vs optional stages
- Docker integration readiness

Author: AI Assistant
Date: August 14, 2025
"""

import json
import logging
import sys
import unittest
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup test logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class Test17StageConfiguration(unittest.TestCase):
    """Test suite for 17-stage pipeline configuration"""

    def setUp(self):
        """Set up test environment"""
        self.test_start_time = datetime.now()
        self.config_file = project_root / "config" / "complete_17_stage_config.json"
        logger.info(f"🧪 Configuration test started: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test"""
        duration = (datetime.now() - self.test_start_time).total_seconds()
        logger.info(
            f"✅ Configuration test completed: {self._testMethodName} ({duration:.2f}s)"
        )

    def load_config(self):
        """Load the 17-stage configuration"""
        if not self.config_file.exists():
            self.skipTest("17-stage configuration file not found")

        with open(self.config_file, "r") as f:
            return json.load(f)

    def test_configuration_exists(self):
        """Test that the 17-stage configuration file exists and is valid JSON"""
        logger.info("🧪 Testing configuration file existence and validity")

        self.assertTrue(
            self.config_file.exists(), "17-stage configuration file not found"
        )

        try:
            config = self.load_config()
            self.assertIsInstance(config, dict, "Configuration should be a dictionary")
            logger.info("✅ Configuration file exists and contains valid JSON")
        except json.JSONDecodeError as e:
            self.fail(f"Configuration file contains invalid JSON: {e}")

    def test_17_stages_present(self):
        """Test that exactly 17 stages are defined"""
        logger.info("🧪 Testing 17-stage completeness")

        config = self.load_config()

        self.assertIn("stages", config, "Configuration missing 'stages' key")
        stages = config["stages"]

        self.assertEqual(len(stages), 17, f"Expected 17 stages, found {len(stages)}")

        # Verify timing indicates 17 stages
        if "timing" in config:
            timing = config["timing"]
            if "stage_count" in timing:
                self.assertEqual(
                    timing["stage_count"], 17, "Timing indicates incorrect stage count"
                )

        logger.info("✅ All 17 stages are present in configuration")

    def test_stage_phase_distribution(self):
        """Test that stages are properly distributed across 6 phases"""
        logger.info("🧪 Testing stage phase distribution")

        config = self.load_config()
        stages = config["stages"]

        # Count stages by phase
        phase_counts = {}
        for stage in stages:
            phase = stage.get("phase", "unknown")
            phase_counts[phase] = phase_counts.get(phase, 0) + 1

        # Expected phase distribution
        expected_phases = {
            "data_acquisition": 4,
            "feature_engineering": 3,
            "advanced_analytics": 3,
            "simulation": 3,
            "strategy": 3,
            "pre_race": 1,
        }

        for phase, expected_count in expected_phases.items():
            self.assertIn(phase, phase_counts, f"Phase '{phase}' not found")
            self.assertEqual(
                phase_counts[phase],
                expected_count,
                f"Phase '{phase}' has {phase_counts[phase]} stages, expected {expected_count}",
            )

        logger.info("✅ Stage phase distribution is correct")

    def test_critical_stages_identification(self):
        """Test that critical stages are properly identified"""
        logger.info("🧪 Testing critical stage identification")

        config = self.load_config()
        stages = config["stages"]

        critical_stages = [stage for stage in stages if stage.get("critical", False)]
        optional_stages = [
            stage for stage in stages if not stage.get("critical", False)
        ]

        # Should have some critical and some optional stages
        self.assertGreater(len(critical_stages), 0, "No critical stages found")
        self.assertGreater(len(optional_stages), 0, "No optional stages found")

        # Critical stages should include essential data processing stages
        critical_stage_names = [stage["name"] for stage in critical_stages]
        essential_stages = [
            "data_validation",
            "data_preprocessing",
            "ml_model_training",
        ]

        for essential in essential_stages:
            self.assertIn(
                essential,
                critical_stage_names,
                f"Essential stage '{essential}' not marked as critical",
            )

        logger.info(
            f"✅ Critical stage identification correct: {len(critical_stages)} critical, {len(optional_stages)} optional"
        )

    def test_stage_dependencies(self):
        """Test that stage dependencies are properly defined"""
        logger.info("🧪 Testing stage dependencies")

        config = self.load_config()
        stages = config["stages"]

        stage_names = [stage["name"] for stage in stages]

        # Check that all prerequisite stages exist (if prerequisites field exists)
        for stage in stages:
            prerequisites = stage.get("prerequisites", [])
            for prereq in prerequisites:
                self.assertIn(
                    prereq,
                    stage_names,
                    f"Prerequisite '{prereq}' for stage '{stage['name']}' not found",
                )

        # Check that first stage can run independently
        first_stage = stages[0]
        prerequisites = first_stage.get("prerequisites", [])
        self.assertEqual(
            len(prerequisites), 0, "First stage should have no prerequisites"
        )

        logger.info("✅ Stage dependencies are properly defined")

    def test_timing_configuration(self):
        """Test that timing configuration is valid"""
        logger.info("🧪 Testing timing configuration")

        config = self.load_config()

        # Check for timing in dynamic_schedule
        if "dynamic_schedule" in config:
            timing = config["dynamic_schedule"]

            # Check for required timing fields
            required_fields = ["total_window_minutes", "buffer_minutes"]
            for field in required_fields:
                self.assertIn(field, timing, f"Timing missing required field: {field}")

            # Validate total duration is reasonable (should be several hours)
            total_duration = timing["total_window_minutes"]
            self.assertGreater(
                total_duration, 300, "Total duration too short (< 5 hours)"
            )
            self.assertLess(
                total_duration, 1440, "Total duration too long (> 24 hours)"
            )

            logger.info(
                f"✅ Timing configuration valid: {total_duration} minutes ({total_duration/60:.1f} hours)"
            )
        else:
            logger.warning(
                "⚠️ No dynamic_schedule section found - skipping timing validation"
            )

    def test_stage_completeness(self):
        """Test that each stage has all required fields"""
        logger.info("🧪 Testing stage field completeness")

        config = self.load_config()
        stages = config["stages"]

        required_fields = ["name", "phase", "duration_minutes"]

        for i, stage in enumerate(stages):
            stage_name = stage.get("name", f"Stage_{i+1}")

            # Check required fields
            for field in required_fields:
                self.assertIn(
                    field,
                    stage,
                    f"Stage '{stage_name}' missing required field: {field}",
                )

            # Validate duration is positive
            duration = stage["duration_minutes"]
            self.assertGreater(
                duration, 0, f"Stage '{stage_name}' has invalid duration: {duration}"
            )

        logger.info("✅ All stages have required fields")

    def test_docker_integration_readiness(self):
        """Test that configuration is ready for Docker deployment"""
        logger.info("🧪 Testing Docker integration readiness")

        config = self.load_config()

        # Check component name
        self.assertIn("component_name", config, "Configuration missing component name")
        component_name = config["component_name"]
        self.assertIn(
            "pipeline",
            component_name.lower(),
            "Component name should reference pipeline",
        )

        # Check for dynamic schedule flag
        if "dynamic_schedule" in config:
            self.assertTrue(
                config["dynamic_schedule"], "Dynamic schedule should be enabled"
            )

        # Validate configuration is JSON serializable (Docker-ready)
        try:
            json.dumps(config)
            logger.info("✅ Configuration is JSON serializable and Docker-ready")
        except TypeError as e:
            self.fail(f"Configuration is not JSON serializable: {e}")

    def test_performance_requirements(self):
        """Test that performance requirements are met"""
        logger.info("🧪 Testing performance requirements")

        config = self.load_config()
        stages = config["stages"]

        # Check that no single stage is excessively long
        max_stage_duration = max(stage["duration_minutes"] for stage in stages)
        self.assertLess(
            max_stage_duration,
            120,
            f"Stage duration too long: {max_stage_duration} minutes",
        )

        # Check reasonable minimum durations
        min_stage_duration = min(stage["duration_minutes"] for stage in stages)
        self.assertGreater(
            min_stage_duration, 0, "All stages must have positive duration"
        )

        # Check that critical path is reasonable
        if "timing" in config:
            timing = config["timing"]
            if "buffer_minutes" in timing:
                buffer = timing["buffer_minutes"]
                total = timing["total_duration_minutes"]
                buffer_ratio = buffer / total
                self.assertGreater(
                    buffer_ratio, 0.1, "Buffer should be at least 10% of total time"
                )
                self.assertLess(
                    buffer_ratio, 0.8, "Buffer should not exceed 80% of total time"
                )

        logger.info("✅ Performance requirements satisfied")


def run_17_stage_configuration_tests():
    """Run all 17-stage configuration tests"""
    print("🏇 Starting 17-Stage Pipeline Configuration Test Suite")
    print("=" * 60)

    start_time = datetime.now()

    # Create test suite
    test_suite = unittest.TestSuite()

    # Add all test methods
    test_class = Test17StageConfiguration
    tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
    test_suite.addTests(tests)

    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(test_suite)

    # Generate summary report
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 60)
    print("🎯 17-Stage Configuration Test Results Summary")
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
                f"  - {test}: {traceback.split('AssertionError: ')[-1].split(chr(10))[0]}"
            )

    if result.errors:
        print("\n💥 Test Errors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split(chr(10))[-2]}")

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
        print("\n🎉 ALL 17-STAGE CONFIGURATION TESTS PASSED!")
        return True
    else:
        print("\n⚠️ Some tests failed - Review configuration")
        return False


if __name__ == "__main__":
    success = run_17_stage_configuration_tests()
    sys.exit(0 if success else 1)
