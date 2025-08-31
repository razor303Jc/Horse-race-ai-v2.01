#!/usr/bin/env python3
"""
Advanced Metrics Test Runner
============================
Comprehensive test runner for the advanced metrics system
"""

import sys
import subprocess
import time
import os
from pathlib import Path
import pytest
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Test configuration
TEST_ROOT = Path(__file__).parent
PROJECT_ROOT = TEST_ROOT.parent
REPORTS_DIR = TEST_ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)


def check_docker_containers():
    """Check if required Docker containers are running"""
    logger.info("🐳 Checking Docker containers...")

    required_containers = [
        "horse_racing_postgres_clean",
        "horse_racing_data_pipeline_clean",
    ]

    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "table {{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
        )

        running_containers = result.stdout.lower()

        for container in required_containers:
            if container in running_containers:
                logger.info(f"✅ {container} is running")
            else:
                logger.warning(f"⚠️  {container} is not running")
                return False

        return True

    except Exception as e:
        logger.error(f"❌ Failed to check Docker containers: {e}")
        return False


def check_database_connectivity():
    """Check database connectivity"""
    logger.info("🗄️ Checking database connectivity...")

    try:
        import psycopg2

        # Test results database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="horse_racing",
            password="horse_racing_password",
            database="results_horse_racing_db",
        )

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM result_records")
        results_count = cursor.fetchone()[0]
        conn.close()

        logger.info(f"✅ Results database: {results_count} records")

        # Test AI database
        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="horse_racing",
            password="horse_racing_password",
            database="ai_horse_racing_db",
        )

        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM horse_speed_ratings")
        speed_count = cursor.fetchone()[0]
        conn.close()

        logger.info(f"✅ AI database: {speed_count} speed ratings")

        return True

    except Exception as e:
        logger.error(f"❌ Database connectivity failed: {e}")
        return False


def run_unit_tests():
    """Run unit tests for advanced metrics"""
    logger.info("🧪 Running unit tests...")

    unit_test_file = TEST_ROOT / "unit" / "test_advanced_metrics.py"

    if not unit_test_file.exists():
        logger.error(f"❌ Unit test file not found: {unit_test_file}")
        return False

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(unit_test_file),
                "-v",
                "--tb=short",
                f"--html={REPORTS_DIR}/unit_test_report.html",
                "--self-contained-html",
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info("✅ Unit tests passed")
            return True
        else:
            logger.error(f"❌ Unit tests failed:\n{result.stdout}\n{result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Unit tests timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to run unit tests: {e}")
        return False


def run_integration_tests():
    """Run integration tests for advanced metrics"""
    logger.info("🔗 Running integration tests...")

    integration_test_file = (
        TEST_ROOT / "integration" / "test_advanced_metrics_integration.py"
    )

    if not integration_test_file.exists():
        logger.error(f"❌ Integration test file not found: {integration_test_file}")
        return False

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(integration_test_file),
                "-v",
                "--tb=short",
                f"--html={REPORTS_DIR}/integration_test_report.html",
                "--self-contained-html",
            ],
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode == 0:
            logger.info("✅ Integration tests passed")
            return True
        else:
            logger.error(
                f"❌ Integration tests failed:\n{result.stdout}\n{result.stderr}"
            )
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Integration tests timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to run integration tests: {e}")
        return False


def test_live_metrics_execution():
    """Test live execution of the advanced metrics script"""
    logger.info("🚀 Testing live metrics execution...")

    script_path = PROJECT_ROOT / "docker_advanced_metrics_populator.py"

    if not script_path.exists():
        logger.error(f"❌ Advanced metrics script not found: {script_path}")
        return False

    try:
        start_time = time.time()

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

        if result.returncode == 0:
            logger.info(f"✅ Live execution completed in {execution_time:.2f}s")

            # Check for success indicators
            if "SUCCESS" in result.stdout or "✅" in result.stdout:
                logger.info("✅ Success indicators found in output")
                return True
            else:
                logger.warning("⚠️  No clear success indicators in output")
                return False
        else:
            logger.error(f"❌ Live execution failed:\n{result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Live execution timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to test live execution: {e}")
        return False


def verify_data_quality():
    """Verify the quality of generated metrics data"""
    logger.info("📊 Verifying data quality...")

    try:
        import psycopg2

        conn = psycopg2.connect(
            host="localhost",
            port=5432,
            user="horse_racing",
            password="horse_racing_password",
            database="ai_horse_racing_db",
        )

        cursor = conn.cursor()

        # Check speed ratings
        cursor.execute(
            """
            SELECT COUNT(*), AVG(speed_figure), MIN(speed_figure), MAX(speed_figure)
            FROM horse_speed_ratings 
            WHERE created_at >= CURRENT_DATE
        """
        )

        speed_stats = cursor.fetchone()
        if speed_stats and speed_stats[0] > 0:
            count, avg, min_val, max_val = speed_stats
            logger.info(
                f"Speed Ratings: {count} records, avg={avg:.2f}, range=[{min_val:.2f}, {max_val:.2f}]"
            )

            if not (20 <= min_val <= 120 and 20 <= max_val <= 120):
                logger.warning("⚠️  Speed figures outside expected range")

        # Check power ratings
        cursor.execute(
            """
            SELECT COUNT(*), AVG(power_rating), MIN(power_rating), MAX(power_rating)
            FROM horse_power_ratings 
            WHERE created_at >= CURRENT_DATE
        """
        )

        power_stats = cursor.fetchone()
        if power_stats and power_stats[0] > 0:
            count, avg, min_val, max_val = power_stats
            logger.info(
                f"Power Ratings: {count} records, avg={avg:.2f}, range=[{min_val:.2f}, {max_val:.2f}]"
            )

            if not (40 <= min_val <= 140 and 40 <= max_val <= 140):
                logger.warning("⚠️  Power ratings outside expected range")

        # Check Monte Carlo
        cursor.execute(
            """
            SELECT COUNT(*), AVG(win_probability), MIN(win_probability), MAX(win_probability)
            FROM monte_carlo_simulations 
            WHERE created_at >= CURRENT_DATE
        """
        )

        mc_stats = cursor.fetchone()
        if mc_stats and mc_stats[0] > 0:
            count, avg, min_val, max_val = mc_stats
            logger.info(
                f"Monte Carlo: {count} records, avg_win_prob={avg:.4f}, range=[{min_val:.4f}, {max_val:.4f}]"
            )

            if not (0 <= min_val <= 1 and 0 <= max_val <= 1):
                logger.warning("⚠️  Probabilities outside valid range")

        conn.close()
        logger.info("✅ Data quality verification completed")
        return True

    except Exception as e:
        logger.error(f"❌ Data quality verification failed: {e}")
        return False


def generate_test_report():
    """Generate comprehensive test report"""
    logger.info("📋 Generating test report...")

    report_content = f"""
# Advanced Metrics Test Report
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}

## Test Summary
- Unit Tests: {unit_tests_passed}
- Integration Tests: {integration_tests_passed}  
- Live Execution: {live_execution_passed}
- Data Quality: {data_quality_passed}

## Environment
- Docker Containers: {containers_status}
- Database Connectivity: {database_status}

## Results
- Overall Status: {"✅ PASSED" if all_tests_passed else "❌ FAILED"}

## Files Generated
- Unit Test Report: reports/unit_test_report.html
- Integration Test Report: reports/integration_test_report.html

## Next Steps
{"Ready for production use!" if all_tests_passed else "Review failed tests and fix issues before deployment."}
"""

    report_file = REPORTS_DIR / "advanced_metrics_test_summary.md"
    with open(report_file, "w") as f:
        f.write(report_content)

    logger.info(f"📋 Test report saved to: {report_file}")


def main():
    """Run comprehensive advanced metrics tests"""
    logger.info("🧪 Advanced Metrics Test Suite Starting...")
    logger.info("=" * 60)

    global containers_status, database_status, unit_tests_passed
    global integration_tests_passed, live_execution_passed, data_quality_passed, all_tests_passed

    # Pre-flight checks
    containers_status = check_docker_containers()
    database_status = check_database_connectivity()

    if not containers_status:
        logger.error("❌ Docker containers not ready - aborting tests")
        return False

    if not database_status:
        logger.error("❌ Database not ready - aborting tests")
        return False

    # Run test suites
    unit_tests_passed = run_unit_tests()
    integration_tests_passed = run_integration_tests()
    live_execution_passed = test_live_metrics_execution()
    data_quality_passed = verify_data_quality()

    # Overall result
    all_tests_passed = all(
        [
            unit_tests_passed,
            integration_tests_passed,
            live_execution_passed,
            data_quality_passed,
        ]
    )

    # Generate report
    generate_test_report()

    # Summary
    logger.info("=" * 60)
    if all_tests_passed:
        logger.info("🎉 ALL TESTS PASSED - Advanced Metrics Ready!")
    else:
        logger.error("❌ SOME TESTS FAILED - Review and fix issues")

    logger.info("=" * 60)

    return all_tests_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
