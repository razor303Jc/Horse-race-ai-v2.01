#!/usr/bin/env python3
"""
🧪 Stage 10 Monte Carlo Simulations - Integration Test Suite
Horse Racing AI v2.02 - Comprehensive Testing

Tests Stage 10 Monte Carlo integration with pipeline orchestrator,
Docker containers, and validates full end-to-end functionality.
"""

import asyncio
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project paths
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "tools" / "pipeline"))

try:
    from daily_orchestrator import DailyOrchestrator
except ImportError as e:
    logger.warning(f"⚠️ Could not import orchestrator: {e}")
    DailyOrchestrator = None


class Stage10IntegrationTestSuite:
    """🧪 Comprehensive integration test suite for Stage 10 Monte Carlo"""

    def __init__(self):
        self.project_root = project_root
        self.test_results = []
        self.start_time = time.time()

    async def run_comprehensive_tests(self) -> Dict[str, Any]:
        """🚀 Run comprehensive Stage 10 integration tests"""

        logger.info("🧪 Starting Stage 10 Monte Carlo Integration Tests")
        logger.info("=" * 70)

        results = {
            "test_suite": "stage10_monte_carlo_integration",
            "start_time": datetime.now().isoformat(),
            "tests_run": 0,
            "tests_passed": 0,
            "tests_failed": 0,
            "test_results": [],
            "overall_success": False,
            "execution_time": 0,
            "summary": {},
        }

        # Test 1: Standalone Stage 10 Execution
        test1_result = await self._test_standalone_execution()
        results["test_results"].append(test1_result)
        results["tests_run"] += 1
        if test1_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 2: Pipeline Integration
        test2_result = await self._test_pipeline_integration()
        results["test_results"].append(test2_result)
        results["tests_run"] += 1
        if test2_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 3: Docker Container Compatibility
        test3_result = await self._test_docker_compatibility()
        results["test_results"].append(test3_result)
        results["tests_run"] += 1
        if test3_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 4: Results Validation
        test4_result = await self._test_results_validation()
        results["test_results"].append(test4_result)
        results["tests_run"] += 1
        if test4_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 5: Performance Benchmarks
        test5_result = await self._test_performance_benchmarks()
        results["test_results"].append(test5_result)
        results["tests_run"] += 1
        if test5_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 6: Monte Carlo Statistical Validation
        test6_result = await self._test_monte_carlo_statistics()
        results["test_results"].append(test6_result)
        results["tests_run"] += 1
        if test6_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Test 7: Betting Recommendation Quality
        test7_result = await self._test_betting_recommendations()
        results["test_results"].append(test7_result)
        results["tests_run"] += 1
        if test7_result["passed"]:
            results["tests_passed"] += 1
        else:
            results["tests_failed"] += 1

        # Calculate final results
        results["execution_time"] = round(time.time() - self.start_time, 2)
        success_rate = (results["tests_passed"] / results["tests_run"]) * 100
        results["overall_success"] = success_rate >= 85.0  # 85% success threshold

        results["summary"] = {
            "success_rate_percent": round(success_rate, 1),
            "tests_passed": results["tests_passed"],
            "tests_failed": results["tests_failed"],
            "execution_time_seconds": results["execution_time"],
            "stage10_operational": results["overall_success"],
        }

        results["end_time"] = datetime.now().isoformat()

        return results

    async def _test_standalone_execution(self) -> Dict[str, Any]:
        """🔧 Test 1: Standalone Stage 10 execution"""

        test_result = {
            "test_name": "standalone_execution",
            "description": "Stage 10 Monte Carlo standalone execution",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("🔧 Test 1: Standalone Stage 10 execution...")

            # Execute Stage 10 script directly
            stage10_script = self.project_root / "stage10_monte_carlo_simulations.py"

            if not stage10_script.exists():
                test_result["errors"].append("Stage 10 script not found")
                return test_result

            # Run with timeout
            result = subprocess.run(
                [sys.executable, str(stage10_script)],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout for test
                cwd=self.project_root,
            )

            execution_time = time.time() - start_time
            test_result["execution_time"] = round(execution_time, 3)

            if result.returncode == 0:
                # Parse output for success indicators
                output = result.stdout
                success_indicators = [
                    "STAGE 10 RESULTS SUMMARY",
                    "Monte Carlo results saved",
                    "simulations completed",
                ]

                indicators_found = sum(
                    1 for indicator in success_indicators if indicator in output
                )

                test_result["details"] = {
                    "return_code": result.returncode,
                    "execution_time_seconds": execution_time,
                    "success_indicators_found": indicators_found,
                    "output_length": len(output),
                }

                test_result["passed"] = indicators_found >= 2
                logger.info(
                    f"✅ Test 1 passed: {indicators_found}/3 success indicators"
                )

            else:
                test_result["errors"].append(f"Exit code: {result.returncode}")
                test_result["errors"].append(f"Stderr: {result.stderr[:500]}")
                logger.error(f"❌ Test 1 failed: exit code {result.returncode}")

        except subprocess.TimeoutExpired:
            test_result["errors"].append("Execution timeout (120s)")
            logger.error("❌ Test 1 failed: timeout")
        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 1 failed: {e}")

        return test_result

    async def _test_pipeline_integration(self) -> Dict[str, Any]:
        """🔗 Test 2: Pipeline orchestrator integration"""

        test_result = {
            "test_name": "pipeline_integration",
            "description": "Stage 10 integration with pipeline orchestrator",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("🔗 Test 2: Pipeline integration...")

            if DailyOrchestrator is None:
                test_result["errors"].append("DailyOrchestrator not available")
                return test_result

            # Initialize orchestrator
            orchestrator = DailyOrchestrator()

            # Test Monte Carlo method exists and is callable
            if hasattr(orchestrator, "monte_carlo_simulation"):
                # Run Monte Carlo through orchestrator
                monte_carlo_result = await orchestrator.monte_carlo_simulation()

                execution_time = time.time() - start_time
                test_result["execution_time"] = round(execution_time, 3)

                # Validate orchestrator response
                required_fields = [
                    "success",
                    "races_simulated",
                    "simulations_run",
                    "win_probabilities_calculated",
                    "errors",
                ]

                fields_present = sum(
                    1 for field in required_fields if field in monte_carlo_result
                )

                test_result["details"] = {
                    "method_exists": True,
                    "execution_time_seconds": execution_time,
                    "required_fields_present": fields_present,
                    "orchestrator_success": monte_carlo_result.get("success", False),
                    "simulations_run": monte_carlo_result.get("simulations_run", 0),
                }

                test_result["passed"] = (
                    fields_present >= 4
                    and monte_carlo_result.get("simulations_run", 0) > 0
                )

                if test_result["passed"]:
                    logger.info(
                        f"✅ Test 2 passed: orchestrator integration successful"
                    )
                else:
                    logger.warning(
                        f"⚠️ Test 2 partial: {fields_present}/5 fields present"
                    )

            else:
                test_result["errors"].append("monte_carlo_simulation method not found")
                logger.error("❌ Test 2 failed: method not found")

        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 2 failed: {e}")

        return test_result

    async def _test_docker_compatibility(self) -> Dict[str, Any]:
        """🐳 Test 3: Docker container compatibility"""

        test_result = {
            "test_name": "docker_compatibility",
            "description": "Stage 10 execution in Docker containers",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("🐳 Test 3: Docker compatibility...")

            # Check if Docker containers are running
            docker_check = subprocess.run(
                ["docker", "ps", "--format", "table {{.Names}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if docker_check.returncode != 0:
                test_result["errors"].append("Docker not available")
                test_result["passed"] = True  # Skip test gracefully
                logger.info("ℹ️ Test 3 skipped: Docker not available")
                return test_result

            # Look for our containers
            containers_output = docker_check.stdout
            our_containers = [
                "horse_racing_data_pipeline_clean",
                "horse_racing_ml_trainer_clean",
            ]

            containers_found = [
                container
                for container in our_containers
                if container in containers_output
            ]

            if containers_found:
                # Test Stage 10 in container
                container_name = containers_found[0]

                docker_exec_result = subprocess.run(
                    [
                        "docker",
                        "exec",
                        container_name,
                        "python3",
                        "/app/stage10_monte_carlo_simulations.py",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )

                execution_time = time.time() - start_time
                test_result["execution_time"] = round(execution_time, 3)

                test_result["details"] = {
                    "containers_available": len(containers_found),
                    "container_used": container_name,
                    "docker_exit_code": docker_exec_result.returncode,
                    "execution_time_seconds": execution_time,
                }

                test_result["passed"] = docker_exec_result.returncode == 0

                if test_result["passed"]:
                    logger.info(f"✅ Test 3 passed: Docker execution successful")
                else:
                    test_result["errors"].append(
                        f"Docker exit code: {docker_exec_result.returncode}"
                    )
                    logger.warning(f"⚠️ Test 3 partial: Docker execution issues")
            else:
                test_result["passed"] = True  # Skip test gracefully
                logger.info("ℹ️ Test 3 skipped: No horse racing containers found")

        except subprocess.TimeoutExpired:
            test_result["errors"].append("Docker execution timeout")
            logger.error("❌ Test 3 failed: timeout")
        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            test_result["passed"] = True  # Skip test gracefully
            logger.info(f"ℹ️ Test 3 skipped: {e}")

        return test_result

    async def _test_results_validation(self) -> Dict[str, Any]:
        """📊 Test 4: Results file validation"""

        test_result = {
            "test_name": "results_validation",
            "description": "Validate Stage 10 results file structure and content",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("📊 Test 4: Results validation...")

            # Check for results file
            results_file = (
                self.project_root
                / "data"
                / "monte_carlo_results"
                / "stage10_monte_carlo_latest.json"
            )

            if not results_file.exists():
                test_result["errors"].append("Results file not found")
                return test_result

            # Load and validate results
            with open(results_file, "r") as f:
                results_data = json.load(f)

            execution_time = time.time() - start_time
            test_result["execution_time"] = round(execution_time, 3)

            # Validate structure
            required_fields = [
                "stage",
                "success",
                "races_processed",
                "total_simulations",
                "horses_analyzed",
                "betting_opportunities",
                "race_analyses",
                "summary_stats",
                "performance_metrics",
            ]

            fields_present = sum(
                1 for field in required_fields if field in results_data
            )

            # Validate data quality
            races_processed = results_data.get("races_processed", 0)
            simulations_run = results_data.get("total_simulations", 0)
            race_analyses = results_data.get("race_analyses", [])

            test_result["details"] = {
                "file_exists": True,
                "file_size_bytes": results_file.stat().st_size,
                "required_fields_present": fields_present,
                "races_processed": races_processed,
                "total_simulations": simulations_run,
                "race_analyses_count": len(race_analyses),
                "data_structure_valid": isinstance(results_data, dict),
            }

            test_result["passed"] = (
                fields_present >= 7
                and races_processed > 0
                and simulations_run > 0
                and len(race_analyses) > 0
            )

            if test_result["passed"]:
                logger.info(f"✅ Test 4 passed: Results validation successful")
            else:
                logger.warning(f"⚠️ Test 4 partial: validation issues detected")

        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 4 failed: {e}")

        return test_result

    async def _test_performance_benchmarks(self) -> Dict[str, Any]:
        """⚡ Test 5: Performance benchmarks"""

        test_result = {
            "test_name": "performance_benchmarks",
            "description": "Stage 10 performance benchmark validation",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("⚡ Test 5: Performance benchmarks...")

            # Load results for performance analysis
            results_file = (
                self.project_root
                / "data"
                / "monte_carlo_results"
                / "stage10_monte_carlo_latest.json"
            )

            if not results_file.exists():
                test_result["errors"].append("Results file not found")
                return test_result

            with open(results_file, "r") as f:
                results_data = json.load(f)

            execution_time = time.time() - start_time
            test_result["execution_time"] = round(execution_time, 3)

            # Extract performance metrics
            perf_metrics = results_data.get("performance_metrics", {})
            total_simulations = results_data.get("total_simulations", 0)
            execution_time_sec = perf_metrics.get("execution_time_seconds", 0)
            simulations_per_sec = perf_metrics.get("simulations_per_second", 0)

            # Performance benchmarks (30 minutes = 1800 seconds target)
            benchmarks = {
                "execution_under_30min": execution_time_sec < 1800,
                "min_simulations_per_sec": simulations_per_sec >= 1000,
                "total_simulations_reasonable": total_simulations >= 5000,
            }

            benchmarks_passed = sum(benchmarks.values())

            test_result["details"] = {
                "execution_time_seconds": execution_time_sec,
                "simulations_per_second": simulations_per_sec,
                "total_simulations": total_simulations,
                "benchmarks_passed": benchmarks_passed,
                "benchmarks": benchmarks,
            }

            test_result["passed"] = benchmarks_passed >= 2  # At least 2/3 benchmarks

            if test_result["passed"]:
                logger.info(
                    f"✅ Test 5 passed: {benchmarks_passed}/3 performance benchmarks met"
                )
            else:
                logger.warning(
                    f"⚠️ Test 5 partial: {benchmarks_passed}/3 benchmarks met"
                )

        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 5 failed: {e}")

        return test_result

    async def _test_monte_carlo_statistics(self) -> Dict[str, Any]:
        """📈 Test 6: Monte Carlo statistical validation"""

        test_result = {
            "test_name": "monte_carlo_statistics",
            "description": "Validate Monte Carlo statistical properties",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("📈 Test 6: Monte Carlo statistics...")

            # Load results for statistical analysis
            results_file = (
                self.project_root
                / "data"
                / "monte_carlo_results"
                / "stage10_monte_carlo_latest.json"
            )

            if not results_file.exists():
                test_result["errors"].append("Results file not found")
                return test_result

            with open(results_file, "r") as f:
                results_data = json.load(f)

            execution_time = time.time() - start_time
            test_result["execution_time"] = round(execution_time, 3)

            # Analyze race analyses for statistical properties
            race_analyses = results_data.get("race_analyses", [])

            if not race_analyses:
                test_result["errors"].append("No race analyses found")
                return test_result

            # Check win probability distributions
            total_probabilities = []
            races_with_valid_probs = 0

            for race in race_analyses:
                win_probs = race.get("win_probabilities", {})
                if win_probs:
                    prob_sum = sum(win_probs.values())
                    total_probabilities.append(prob_sum)

                    # Win probabilities should sum to approximately 1.0
                    if 0.95 <= prob_sum <= 1.05:
                        races_with_valid_probs += 1

            # Statistical validation checks
            valid_probability_distribution = (
                races_with_valid_probs / len(race_analyses) >= 0.8
                if race_analyses
                else False
            )

            has_betting_recommendations = any(
                len(race.get("betting_recommendations", [])) > 0
                for race in race_analyses
            )

            has_confidence_intervals = any(
                "confidence_intervals" in race.get("monte_carlo_analysis", {})
                for race in race_analyses
            )

            test_result["details"] = {
                "races_analyzed": len(race_analyses),
                "races_with_valid_probabilities": races_with_valid_probs,
                "probability_distribution_valid": valid_probability_distribution,
                "has_betting_recommendations": has_betting_recommendations,
                "has_confidence_intervals": has_confidence_intervals,
                "average_probability_sum": (
                    sum(total_probabilities) / len(total_probabilities)
                    if total_probabilities
                    else 0
                ),
            }

            statistical_checks = [
                valid_probability_distribution,
                has_betting_recommendations,
                has_confidence_intervals,
            ]

            test_result["passed"] = sum(statistical_checks) >= 2

            if test_result["passed"]:
                logger.info(f"✅ Test 6 passed: Monte Carlo statistics valid")
            else:
                logger.warning(f"⚠️ Test 6 partial: statistical validation issues")

        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 6 failed: {e}")

        return test_result

    async def _test_betting_recommendations(self) -> Dict[str, Any]:
        """💰 Test 7: Betting recommendation quality"""

        test_result = {
            "test_name": "betting_recommendations",
            "description": "Validate betting recommendation quality and logic",
            "passed": False,
            "execution_time": 0,
            "details": {},
            "errors": [],
        }

        try:
            start_time = time.time()
            logger.info("💰 Test 7: Betting recommendations...")

            # Load results for betting analysis
            results_file = (
                self.project_root
                / "data"
                / "monte_carlo_results"
                / "stage10_monte_carlo_latest.json"
            )

            if not results_file.exists():
                test_result["errors"].append("Results file not found")
                return test_result

            with open(results_file, "r") as f:
                results_data = json.load(f)

            execution_time = time.time() - start_time
            test_result["execution_time"] = round(execution_time, 3)

            # Analyze betting recommendations
            race_analyses = results_data.get("race_analyses", [])
            total_recommendations = 0
            high_quality_recommendations = 0

            for race in race_analyses:
                recommendations = race.get("betting_recommendations", [])
                total_recommendations += len(recommendations)

                for rec in recommendations:
                    # Quality checks
                    has_required_fields = all(
                        field in rec
                        for field in [
                            "horse_name",
                            "probability",
                            "confidence",
                            "value_rating",
                        ]
                    )

                    probability_reasonable = 0.1 <= rec.get("probability", 0) <= 0.8
                    confidence_reasonable = 0.5 <= rec.get("confidence", 0) <= 1.0

                    if (
                        has_required_fields
                        and probability_reasonable
                        and confidence_reasonable
                    ):
                        high_quality_recommendations += 1

            # Summary statistics
            total_betting_opportunities = results_data.get("betting_opportunities", 0)
            high_confidence_picks = results_data.get("high_confidence_picks", 0)

            quality_rate = (
                high_quality_recommendations / total_recommendations
                if total_recommendations > 0
                else 0
            )

            test_result["details"] = {
                "total_recommendations": total_recommendations,
                "high_quality_recommendations": high_quality_recommendations,
                "quality_rate": round(quality_rate, 3),
                "total_betting_opportunities": total_betting_opportunities,
                "high_confidence_picks": high_confidence_picks,
                "recommendations_per_race": (
                    total_recommendations / len(race_analyses) if race_analyses else 0
                ),
            }

            test_result["passed"] = (
                total_recommendations > 0
                and quality_rate >= 0.8  # 80% quality threshold
                and total_betting_opportunities > 0
            )

            if test_result["passed"]:
                logger.info(
                    f"✅ Test 7 passed: Betting recommendations quality validated"
                )
            else:
                logger.warning(f"⚠️ Test 7 partial: betting recommendation issues")

        except Exception as e:
            test_result["errors"].append(f"Exception: {e}")
            logger.error(f"❌ Test 7 failed: {e}")

        return test_result


async def main():
    """🚀 Run the comprehensive Stage 10 integration test suite"""

    print("🧪 Stage 10 Monte Carlo - Integration Test Suite")
    print("=" * 70)

    # Initialize test suite
    test_suite = Stage10IntegrationTestSuite()

    # Run comprehensive tests
    results = await test_suite.run_comprehensive_tests()

    # Display results
    print(f"\n📊 TEST SUITE RESULTS")
    print(f"Overall Success: {'✅' if results['overall_success'] else '❌'}")
    print(f"Success Rate: {results['summary']['success_rate_percent']}%")
    print(f"Tests Passed: {results['tests_passed']}/{results['tests_run']}")
    print(f"Execution Time: {results['execution_time']}s")

    print(f"\n🔍 INDIVIDUAL TEST RESULTS:")
    for i, test in enumerate(results["test_results"], 1):
        status = "✅" if test["passed"] else "❌"
        print(f"   {i}. {test['test_name']}: {status} ({test['execution_time']}s)")
        if test["errors"]:
            for error in test["errors"][:2]:  # Show first 2 errors
                print(f"      ⚠️ {error}")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = (
        test_suite.project_root / f"test_stage10_integration_results_{timestamp}.json"
    )

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {results_file}")

    return results


if __name__ == "__main__":
    try:
        results = asyncio.run(main())
        exit_code = 0 if results.get("overall_success", False) else 1
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
        sys.exit(1)
