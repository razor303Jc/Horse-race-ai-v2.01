#!/usr/bin/env python3
"""
Stage 12 Race Trends Analysis - Integration Test
Comprehensive testing of race trends analysis system with Monte Carlo integration.
"""

import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.stages.stage12_race_trends import Stage12RaceTrendsEngine


class TestStage12Integration:
    """Comprehensive integration tests for Stage 12 Race Trends Analysis"""

    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing"""
        temp_dir = Path(tempfile.mkdtemp())

        # Create directory structure
        (temp_dir / "results" / "stage10_monte_carlo").mkdir(
            parents=True, exist_ok=True
        )
        (temp_dir / "results" / "stage12_race_trends").mkdir(
            parents=True, exist_ok=True
        )
        (temp_dir / "data").mkdir(parents=True, exist_ok=True)

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def sample_monte_carlo_data(self):
        """Generate sample Monte Carlo data for testing"""
        return {
            "analysis_date": "2025-08-18",
            "races": [
                {
                    "race_id": "race_001",
                    "race_number": 1,
                    "horses": [
                        {
                            "horse_name": "Lightning Bolt",
                            "jockey_name": "J. Smith",
                            "trainer_name": "T. Wilson",
                            "win_probability": 0.35,
                            "place_probability": 0.65,
                            "show_probability": 0.80,
                            "odds": 2.5,
                            "confidence": 0.85,
                        },
                        {
                            "horse_name": "Thunder Strike",
                            "jockey_name": "M. Jones",
                            "trainer_name": "R. Brown",
                            "win_probability": 0.25,
                            "place_probability": 0.55,
                            "show_probability": 0.75,
                            "odds": 4.0,
                            "confidence": 0.80,
                        },
                    ],
                },
                {
                    "race_id": "race_002",
                    "race_number": 2,
                    "horses": [
                        {
                            "horse_name": "Speed Demon",
                            "jockey_name": "A. Garcia",
                            "trainer_name": "P. Martinez",
                            "win_probability": 0.40,
                            "place_probability": 0.70,
                            "show_probability": 0.85,
                            "odds": 2.2,
                            "confidence": 0.90,
                        }
                    ],
                },
            ],
            "performance_summary": {
                "total_simulations": 5000,
                "execution_time_seconds": 5.89,
                "simulations_per_second": 2545,
            },
        }

    def test_01_standalone_execution(self, temp_workspace, sample_monte_carlo_data):
        """Test 1: Standalone Stage 12 execution"""
        print("\n" + "=" * 60)
        print("TEST 1: STANDALONE STAGE 12 EXECUTION")
        print("=" * 60)

        # Setup Monte Carlo data
        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        # Initialize Stage 12 engine
        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))

        # Run analysis
        summary = engine.analyze_race_trends(test_date)

        # Validate results
        assert summary is not None, "❌ Analysis summary is None"
        assert summary.race_date == test_date, "❌ Incorrect race date"
        assert (
            summary.total_races == 2
        ), f"❌ Expected 2 races, got {summary.total_races}"
        assert (
            summary.total_horses == 3
        ), f"❌ Expected 3 horses, got {summary.total_horses}"

        print(f"✅ Race Date: {summary.race_date}")
        print(f"✅ Total Races: {summary.total_races}")
        print(f"✅ Total Horses: {summary.total_horses}")
        print(f"✅ Patterns Identified: {summary.patterns_identified}")
        print(f"✅ Average Confidence: {summary.average_confidence:.3f}")

        print("✅ TEST 1 PASSED: Standalone execution successful")

    def test_02_trend_metrics_analysis(self, temp_workspace, sample_monte_carlo_data):
        """Test 2: Trend metrics analysis validation"""
        print("\n" + "=" * 60)
        print("TEST 2: TREND METRICS ANALYSIS")
        print("=" * 60)

        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))
        summary = engine.analyze_race_trends(test_date)

        # Validate trend metrics
        assert hasattr(summary, "trend_metrics"), "❌ Missing trend_metrics attribute"
        assert isinstance(
            summary.trend_metrics, list
        ), "❌ trend_metrics should be a list"

        print(f"✅ Trend Metrics Count: {len(summary.trend_metrics)}")

        # Check trend metric types
        trend_types = set()
        for trend in summary.trend_metrics:
            trend_types.add(trend.trend_type)
            assert hasattr(trend, "confidence_level"), "❌ Missing confidence_level"
            assert hasattr(trend, "sample_size"), "❌ Missing sample_size"
            assert hasattr(trend, "value"), "❌ Missing value"

        print(
            f"✅ Trend Types Found: {', '.join(trend_types) if trend_types else 'None'}"
        )

        print("✅ TEST 2 PASSED: Trend metrics analysis validated")

    def test_03_race_patterns_identification(
        self, temp_workspace, sample_monte_carlo_data
    ):
        """Test 3: Race patterns identification"""
        print("\n" + "=" * 60)
        print("TEST 3: RACE PATTERNS IDENTIFICATION")
        print("=" * 60)

        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))
        summary = engine.analyze_race_trends(test_date)

        # Validate race patterns
        assert hasattr(summary, "race_patterns"), "❌ Missing race_patterns attribute"
        assert isinstance(
            summary.race_patterns, list
        ), "❌ race_patterns should be a list"

        print(f"✅ Race Patterns Count: {len(summary.race_patterns)}")

        # Check pattern attributes
        pattern_types = set()
        for pattern in summary.race_patterns:
            pattern_types.add(pattern.pattern_type)
            assert hasattr(pattern, "confidence"), "❌ Missing confidence"
            assert hasattr(pattern, "win_rate"), "❌ Missing win_rate"
            assert hasattr(pattern, "sample_size"), "❌ Missing sample_size"
            assert (
                0 <= pattern.confidence <= 1
            ), f"❌ Invalid confidence: {pattern.confidence}"
            assert (
                0 <= pattern.win_rate <= 1
            ), f"❌ Invalid win_rate: {pattern.win_rate}"

        print(
            f"✅ Pattern Types Found: {', '.join(pattern_types) if pattern_types else 'None'}"
        )

        print("✅ TEST 3 PASSED: Race patterns identification validated")

    def test_04_performance_benchmarks(self, temp_workspace, sample_monte_carlo_data):
        """Test 4: Performance benchmarks validation"""
        print("\n" + "=" * 60)
        print("TEST 4: PERFORMANCE BENCHMARKS")
        print("=" * 60)

        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))

        start_time = datetime.now()
        summary = engine.analyze_race_trends(test_date)
        execution_time = (datetime.now() - start_time).total_seconds()

        # Performance validation
        assert (
            execution_time < 600
        ), f"❌ Execution too slow: {execution_time:.2f}s (limit: 600s)"

        perf_summary = summary.performance_summary
        assert (
            "execution_time_seconds" in perf_summary
        ), "❌ Missing execution_time_seconds"

        print(f"✅ Execution Time: {execution_time:.2f}s")
        print(
            f"✅ Internal Execution Time: {perf_summary.get('execution_time_seconds', 0):.2f}s"
        )
        print(f"✅ Trends Analyzed: {perf_summary.get('trends_analyzed', 0)}")
        print(f"✅ Patterns Identified: {perf_summary.get('patterns_identified', 0)}")

        print("✅ TEST 4 PASSED: Performance benchmarks met")

    def test_05_results_file_output(self, temp_workspace, sample_monte_carlo_data):
        """Test 5: Results file output validation"""
        print("\n" + "=" * 60)
        print("TEST 5: RESULTS FILE OUTPUT")
        print("=" * 60)

        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))
        summary = engine.analyze_race_trends(test_date)

        # Check output files
        results_dir = temp_workspace / "results" / "stage12_race_trends"

        expected_files = [
            f"race_trends_{test_date}.json",
            f"trend_metrics_{test_date}.json",
            f"race_patterns_{test_date}.json",
        ]

        for filename in expected_files:
            file_path = results_dir / filename
            assert file_path.exists(), f"❌ Missing output file: {filename}"

            # Validate JSON structure
            with open(file_path, "r") as f:
                data = json.load(f)
                assert isinstance(
                    data, (dict, list)
                ), f"❌ Invalid JSON structure in {filename}"

            print(f"✅ Output file created: {filename}")

        print("✅ TEST 5 PASSED: Results file output validated")

    def test_06_statistical_validation(self, temp_workspace, sample_monte_carlo_data):
        """Test 6: Statistical validation of results"""
        print("\n" + "=" * 60)
        print("TEST 6: STATISTICAL VALIDATION")
        print("=" * 60)

        test_date = "2025-08-18"
        monte_carlo_file = (
            temp_workspace
            / "results"
            / "stage10_monte_carlo"
            / f"monte_carlo_results_{test_date}.json"
        )

        with open(monte_carlo_file, "w") as f:
            json.dump(sample_monte_carlo_data, f, indent=2)

        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))
        summary = engine.analyze_race_trends(test_date)

        # Statistical validation
        for trend in summary.trend_metrics:
            assert (
                0 <= trend.confidence_level <= 1
            ), f"❌ Invalid confidence_level: {trend.confidence_level}"
            assert (
                trend.sample_size >= 0
            ), f"❌ Invalid sample_size: {trend.sample_size}"
            assert (
                0 <= trend.statistical_significance <= 1
            ), f"❌ Invalid statistical_significance: {trend.statistical_significance}"

        for pattern in summary.race_patterns:
            assert (
                0 <= pattern.confidence <= 1
            ), f"❌ Invalid pattern confidence: {pattern.confidence}"
            assert (
                0 <= pattern.win_rate <= 1
            ), f"❌ Invalid win_rate: {pattern.win_rate}"
            assert (
                0 <= pattern.place_rate <= 1
            ), f"❌ Invalid place_rate: {pattern.place_rate}"
            assert (
                pattern.sample_size >= 0
            ), f"❌ Invalid pattern sample_size: {pattern.sample_size}"

        print(
            f"✅ Trend Metrics Statistical Validation: {len(summary.trend_metrics)} items"
        )
        print(
            f"✅ Race Patterns Statistical Validation: {len(summary.race_patterns)} items"
        )
        print(f"✅ Average Confidence Validation: {summary.average_confidence:.3f}")

        print("✅ TEST 6 PASSED: Statistical validation successful")

    def test_07_empty_data_handling(self, temp_workspace):
        """Test 7: Empty data handling"""
        print("\n" + "=" * 60)
        print("TEST 7: EMPTY DATA HANDLING")
        print("=" * 60)

        test_date = "2025-08-18"

        # No Monte Carlo data file
        engine = Stage12RaceTrendsEngine(base_dir=str(temp_workspace))
        summary = engine.analyze_race_trends(test_date)

        # Should handle gracefully
        assert summary is not None, "❌ Should return valid summary even with no data"
        assert (
            summary.total_races == 0
        ), f"❌ Expected 0 races, got {summary.total_races}"
        assert (
            summary.total_horses == 0
        ), f"❌ Expected 0 horses, got {summary.total_horses}"
        assert (
            summary.patterns_identified == 0
        ), f"❌ Expected 0 patterns, got {summary.patterns_identified}"

        print(
            f"✅ Empty Data Handling: {summary.total_races} races, {summary.total_horses} horses"
        )
        print(
            f"✅ Error Handling: {len(summary.performance_summary.get('errors', []))} errors logged"
        )

        print("✅ TEST 7 PASSED: Empty data handling successful")


def run_integration_tests():
    """Run all Stage 12 integration tests"""
    print("\n" + "=" * 80)
    print("STAGE 12 RACE TRENDS ANALYSIS - INTEGRATION TEST SUITE")
    print("=" * 80)
    print(f"Test Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Version: {sys.version}")
    print("=" * 80)

    # Create test instance
    test_suite = TestStage12Integration()

    # Run tests
    tests = [
        ("test_01_standalone_execution", "Standalone Stage 12 Execution"),
        ("test_02_trend_metrics_analysis", "Trend Metrics Analysis"),
        ("test_03_race_patterns_identification", "Race Patterns Identification"),
        ("test_04_performance_benchmarks", "Performance Benchmarks"),
        ("test_05_results_file_output", "Results File Output"),
        ("test_06_statistical_validation", "Statistical Validation"),
        ("test_07_empty_data_handling", "Empty Data Handling"),
    ]

    passed_tests = 0
    total_tests = len(tests)

    # Setup shared fixtures
    temp_workspace = Path(tempfile.mkdtemp())

    try:
        # Create directory structure
        (temp_workspace / "results" / "stage10_monte_carlo").mkdir(
            parents=True, exist_ok=True
        )
        (temp_workspace / "results" / "stage12_race_trends").mkdir(
            parents=True, exist_ok=True
        )

        sample_monte_carlo_data = {
            "analysis_date": "2025-08-18",
            "races": [
                {
                    "race_id": "race_001",
                    "race_number": 1,
                    "horses": [
                        {
                            "horse_name": "Lightning Bolt",
                            "jockey_name": "J. Smith",
                            "trainer_name": "T. Wilson",
                            "win_probability": 0.35,
                            "place_probability": 0.65,
                            "show_probability": 0.80,
                            "odds": 2.5,
                            "confidence": 0.85,
                        }
                    ],
                }
            ],
        }

        for test_method, test_name in tests:
            try:
                print(f"\n⏳ Running: {test_name}")

                if test_method == "test_07_empty_data_handling":
                    getattr(test_suite, test_method)(temp_workspace)
                else:
                    getattr(test_suite, test_method)(
                        temp_workspace, sample_monte_carlo_data
                    )

                passed_tests += 1

            except Exception as e:
                print(f"❌ FAILED: {test_name}")
                print(f"   Error: {str(e)}")

        # Final summary
        print("\n" + "=" * 80)
        print("STAGE 12 INTEGRATION TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")

        if passed_tests == total_tests:
            print("🎉 ALL TESTS PASSED - Stage 12 Race Trends Analysis Ready!")
        else:
            print(f"⚠️  {total_tests - passed_tests} TESTS FAILED - Review Required")

        print("=" * 80)

    finally:
        # Cleanup
        shutil.rmtree(temp_workspace)

    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_integration_tests()
    sys.exit(0 if passed == total else 1)
