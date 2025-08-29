#!/usr/bin/env python3
"""
🧪 Step 4: Complete Integration Testing for 17-Stage Dynamic Pipeline
Tests all scenarios from A (download) → B (first race) → scheduling

This comprehensive test suite validates:
1. Dynamic schedule generation for different race times
2. All 17 stages allocation across 6 phases
3. Compression scenarios for tight time windows
4. Integration with auto-downloader timing
5. Production deployment readiness

Author: AI Assistant
Date: August 13, 2025
"""

import json
import logging
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator
from dynamic_pipeline_timing import PipelineTimeAllocator

# Setup test logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - TEST - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PipelineIntegrationTester:
    """Comprehensive integration testing for 17-stage dynamic pipeline"""

    def __init__(self):
        self.orchestrator = DailyPipelineOrchestrator()
        self.time_allocator = PipelineTimeAllocator()
        self.test_results = {}

    def run_all_tests(self) -> Dict:
        """Run complete integration test suite"""
        logger.info("🧪 Starting Step 4: Complete Integration Testing")
        logger.info("=" * 60)

        tests = [
            ("Test 1: Morning Races (11:00)", self.test_morning_races),
            ("Test 2: Afternoon Races (14:00)", self.test_afternoon_races),
            ("Test 3: Evening Races (18:00)", self.test_evening_races),
            ("Test 4: Compressed Schedule (08:00)", self.test_compressed_schedule),
            ("Test 5: Optimal Schedule (16:00)", self.test_optimal_schedule),
            (
                "Test 6: Auto-downloader Integration",
                self.test_autodownloader_integration,
            ),
            ("Test 7: All 17 Stages Validation", self.test_17_stages_validation),
            ("Test 8: Phase Distribution", self.test_phase_distribution),
            ("Test 9: Production Readiness", self.test_production_readiness),
        ]

        for test_name, test_func in tests:
            logger.info(f"\n🔬 Running {test_name}...")
            try:
                result = test_func()
                self.test_results[test_name] = {"status": "PASS", "result": result}
                logger.info(f"✅ {test_name}: PASSED")
            except Exception as e:
                self.test_results[test_name] = {"status": "FAIL", "error": str(e)}
                logger.error(f"❌ {test_name}: FAILED - {e}")

        return self._generate_test_report()

    def test_morning_races(self) -> Dict:
        """Test scenario: Early morning races at 11:00"""
        first_race = datetime.now().replace(hour=11, minute=0, second=0, microsecond=0)

        schedule = self.time_allocator.calculate_17_stage_allocation(
            download_time="06:25", first_race_time=first_race
        )

        analysis = schedule["timing_analysis"]

        # Validations
        assert (
            analysis["total_stages"] == 17
        ), f"Expected 17 stages, got {analysis['total_stages']}"
        assert (
            analysis["phases_covered"] == 6
        ), f"Expected 6 phases, got {analysis['phases_covered']}"
        assert (
            analysis["schedule_type"] == "compressed"
        ), "Morning races should use compressed schedule"

        return {
            "first_race_time": "11:00",
            "schedule_type": analysis["schedule_type"],
            "stages": analysis["total_stages"],
            "buffer_minutes": analysis["buffer_minutes"],
            "window_minutes": analysis["total_window_minutes"],
        }

    def test_afternoon_races(self) -> Dict:
        """Test scenario: Standard afternoon races at 14:00"""
        first_race = datetime.now().replace(hour=14, minute=0, second=0, microsecond=0)

        schedule = self.time_allocator.calculate_17_stage_allocation(
            download_time="06:25", first_race_time=first_race
        )

        analysis = schedule["timing_analysis"]

        # Validations
        assert (
            analysis["total_stages"] == 17
        ), f"Expected 17 stages, got {analysis['total_stages']}"
        assert analysis["schedule_type"] in [
            "optimal",
            "tight",
        ], "Afternoon races should be optimal/tight"
        assert (
            analysis["buffer_minutes"] >= 30
        ), "Should have reasonable buffer for afternoon races"

        return {
            "first_race_time": "14:00",
            "schedule_type": analysis["schedule_type"],
            "stages": analysis["total_stages"],
            "buffer_minutes": analysis["buffer_minutes"],
            "window_minutes": analysis["total_window_minutes"],
        }

    def test_evening_races(self) -> Dict:
        """Test scenario: Evening races at 18:00"""
        first_race = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)

        schedule = self.time_allocator.calculate_17_stage_allocation(
            download_time="06:25", first_race_time=first_race
        )

        analysis = schedule["timing_analysis"]

        # Validations
        assert (
            analysis["total_stages"] == 17
        ), f"Expected 17 stages, got {analysis['total_stages']}"
        assert (
            analysis["schedule_type"] == "optimal"
        ), "Evening races should use optimal schedule"
        assert (
            analysis["buffer_minutes"] >= 100
        ), "Evening races should have large buffer"

        return {
            "first_race_time": "18:00",
            "schedule_type": analysis["schedule_type"],
            "stages": analysis["total_stages"],
            "buffer_minutes": analysis["buffer_minutes"],
            "window_minutes": analysis["total_window_minutes"],
        }

    def test_compressed_schedule(self) -> Dict:
        """Test compressed schedule with very tight timing"""
        first_race = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)

        schedule = self.time_allocator.calculate_17_stage_allocation(
            download_time="06:25", first_race_time=first_race
        )

        analysis = schedule["timing_analysis"]
        stages = schedule["schedule"]

        # Validations
        assert (
            analysis["schedule_type"] == "compressed"
        ), "Should use compressed schedule"

        # Check that scalable stages are compressed
        compressed_stages = [
            name for name, stage in stages.items() if stage.get("compressed", False)
        ]
        assert len(compressed_stages) > 0, "Should have compressed stages"

        return {
            "schedule_type": analysis["schedule_type"],
            "compressed_stages": len(compressed_stages),
            "compression_ratio": analysis.get("compression_ratio", 1.0),
            "window_minutes": analysis["total_window_minutes"],
        }

    def test_optimal_schedule(self) -> Dict:
        """Test optimal schedule with plenty of time"""
        first_race = datetime.now().replace(hour=16, minute=0, second=0, microsecond=0)

        schedule = self.time_allocator.calculate_17_stage_allocation(
            download_time="06:25", first_race_time=first_race
        )

        analysis = schedule["timing_analysis"]
        stages = schedule["schedule"]

        # Validations
        assert analysis["schedule_type"] == "optimal", "Should use optimal schedule"
        assert (
            analysis["buffer_minutes"] >= 200
        ), "Should have large buffer in optimal mode"

        # Check that no stages are compressed
        compressed_stages = [
            name for name, stage in stages.items() if stage.get("compressed", False)
        ]
        assert (
            len(compressed_stages) == 0
        ), "No stages should be compressed in optimal mode"

        return {
            "schedule_type": analysis["schedule_type"],
            "buffer_minutes": analysis["buffer_minutes"],
            "window_minutes": analysis["total_window_minutes"],
            "uncompressed_stages": len(stages),
        }

    def test_autodownloader_integration(self) -> Dict:
        """Test integration with auto-downloader at 06:25"""
        # Test with orchestrator's generate_dynamic_schedule
        schedule = self.orchestrator.generate_dynamic_schedule()

        # Validations
        assert schedule is not None, "Schedule generation should not fail"
        assert "schedule" in schedule, "Schedule should contain stages"
        assert "timing_analysis" in schedule, "Schedule should contain analysis"

        stages = schedule["schedule"]
        analysis = schedule["timing_analysis"]

        # Check that data_download starts at fixed time (05:00) and data_validation at 06:25
        assert "data_download" in stages, "Should include data_download stage"
        assert "data_validation" in stages, "Should include data_validation stage"

        # Verify auto-downloader timing integration
        download_stage = stages["data_download"]
        validation_stage = stages["data_validation"]

        assert download_stage["start_time"] == "05:00", "Download should start at 05:00"
        assert (
            validation_stage["start_time"] == "06:25"
        ), "Validation should start after auto-downloader"

        return {
            "download_time": download_stage["start_time"],
            "validation_time": validation_stage["start_time"],
            "total_stages": analysis["total_stages"],
            "integration_successful": True,
        }

    def test_17_stages_validation(self) -> Dict:
        """Validate that all 17 stages are properly included and ordered"""
        schedule = self.orchestrator.generate_dynamic_schedule()
        stages = schedule["schedule"]

        # Expected 17 stages
        expected_stages = [
            "data_download",
            "data_validation",
            "data_preprocessing",
            "data_relationships",
            "feature_engineering",
            "contextual_analysis",
            "form_scoring",
            "power_ratings",
            "speed_analysis",
            "ml_model_training",
            "monte_carlo_simulations",
            "race_trends",
            "composite_scoring",
            "betting_strategies",
            "ai_selections",
            "report_generation",
            "pre_race_updates",
        ]

        # Validations
        assert len(stages) == 17, f"Expected 17 stages, got {len(stages)}"

        for stage_name in expected_stages:
            assert stage_name in stages, f"Missing stage: {stage_name}"

        # Check stage ordering (start times should be chronological)
        stage_times = [
            (name, datetime.strptime(info["start_time"], "%H:%M"))
            for name, info in stages.items()
        ]
        stage_times.sort(key=lambda x: x[1])

        # Verify chronological order
        for i in range(1, len(stage_times)):
            assert (
                stage_times[i][1] >= stage_times[i - 1][1]
            ), f"Stage ordering error: {stage_times[i][0]} starts before {stage_times[i-1][0]}"

        return {
            "all_stages_present": True,
            "chronological_order": True,
            "stage_count": len(stages),
            "first_stage": stage_times[0][0],
            "last_stage": stage_times[-1][0],
        }

    def test_phase_distribution(self) -> Dict:
        """Test that all 6 phases are properly distributed"""
        schedule = self.orchestrator.generate_dynamic_schedule()
        stages = schedule["schedule"]

        # Count phases
        phases = {}
        for stage_name, stage_info in stages.items():
            phase = stage_info.get("phase", "unknown")
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(stage_name)

        expected_phases = [
            "data_acquisition",
            "feature_engineering",
            "advanced_analytics",
            "simulation",
            "strategy",
            "pre_race",
        ]

        # Validations
        assert len(phases) == 6, f"Expected 6 phases, got {len(phases)}"

        for phase in expected_phases:
            assert phase in phases, f"Missing phase: {phase}"
            assert len(phases[phase]) > 0, f"Phase {phase} has no stages"

        return {
            "phase_count": len(phases),
            "phase_distribution": {
                phase: len(stages) for phase, stages in phases.items()
            },
            "all_phases_present": True,
        }

    def test_production_readiness(self) -> Dict:
        """Test production deployment readiness"""
        # Test multiple scenarios rapidly
        test_times = ["08:00", "11:00", "14:00", "17:00", "20:00"]
        results = {}

        for time_str in test_times:
            hour, minute = map(int, time_str.split(":"))
            first_race = datetime.now().replace(
                hour=hour, minute=minute, second=0, microsecond=0
            )

            schedule = self.time_allocator.calculate_17_stage_allocation(
                download_time="06:25", first_race_time=first_race
            )

            analysis = schedule["timing_analysis"]
            results[time_str] = {
                "schedule_type": analysis["schedule_type"],
                "buffer_minutes": analysis["buffer_minutes"],
                "stages": analysis["total_stages"],
            }

        # Verify all scenarios work
        for time_str, result in results.items():
            assert (
                result["stages"] == 17
            ), f"Scenario {time_str} failed: wrong stage count"
            assert result["schedule_type"] in [
                "optimal",
                "tight",
                "compressed",
            ], f"Scenario {time_str} failed: invalid schedule type"

        return {
            "scenarios_tested": len(test_times),
            "all_scenarios_passed": True,
            "scenario_results": results,
            "production_ready": True,
        }

    def _generate_test_report(self) -> Dict:
        """Generate comprehensive test report"""
        passed = sum(
            1 for result in self.test_results.values() if result["status"] == "PASS"
        )
        total = len(self.test_results)

        logger.info(f"\n" + "=" * 60)
        logger.info(f"🧪 STEP 4 INTEGRATION TEST RESULTS")
        logger.info(f"=" * 60)
        logger.info(f"✅ Tests Passed: {passed}/{total}")
        logger.info(f"❌ Tests Failed: {total - passed}/{total}")
        logger.info(f"📊 Success Rate: {(passed/total)*100:.1f}%")

        if passed == total:
            logger.info(f"\n🎉 ALL TESTS PASSED - STEP 4 COMPLETE!")
            logger.info(f"🚀 17-Stage Dynamic Pipeline is PRODUCTION READY!")
        else:
            logger.warning(
                f"\n⚠️  Some tests failed - review before production deployment"
            )

        # Save detailed results
        report_file = Path("project_root / 'logs' / step4_integration_test_report.json")
        report_file.parent.mkdir(exist_ok=True)

        full_report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "success_rate": (passed / total) * 100,
            },
            "test_results": self.test_results,
            "production_ready": passed == total,
        }

        with open(report_file, "w") as f:
            json.dump(full_report, f, indent=2)

        logger.info(f"📋 Detailed report saved: {report_file}")

        return full_report


def main():
    """Run Step 4 integration testing"""
    print("🧪 Step 4: Complete Integration Testing for 17-Stage Dynamic Pipeline")
    print("=" * 70)

    tester = PipelineIntegrationTester()
    report = tester.run_all_tests()

    if report["production_ready"]:
        print("\n🎉 SUCCESS: 17-Stage Dynamic Pipeline is ready for production!")
        print("🚀 All integration tests passed - deploy with confidence!")
    else:
        print("\n⚠️  WARNING: Some tests failed - review before deployment")

    return report


if __name__ == "__main__":
    main()
