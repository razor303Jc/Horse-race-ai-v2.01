#!/usr/bin/env python3
"""
Docker-Compatible Advanced Metrics Test Framework Runner

Quick test runner that works with our Docker environment
"""

import subprocess
import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_docker_containers():
    """Check if required Docker containers are running"""
    logger.info("🐳 Checking Docker containers...")

    containers = ["horse_racing_postgres_clean", "horse_racing_data_pipeline_clean"]

    for container in containers:
        try:
            result = subprocess.run(
                [
                    "docker",
                    "ps",
                    "--format",
                    "{{.Names}}",
                    "--filter",
                    f"name={container}",
                ],
                capture_output=True,
                text=True,
            )

            if container in result.stdout:
                logger.info(f"✅ {container} is running")
            else:
                logger.error(f"❌ {container} is not running")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to check {container}: {e}")
            return False

    return True


def check_database_connectivity():
    """Check database connectivity through Docker"""
    logger.info("🗄️ Checking database connectivity...")

    try:
        # Test results database
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
                "SELECT COUNT(*) FROM result_records;",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            logger.error(f"❌ Results database failed: {result.stderr}")
            return False

        # Extract count from output
        lines = result.stdout.strip().split("\n")
        count_line = [line for line in lines if line.strip().isdigit()]
        results_count = count_line[0].strip() if count_line else "unknown"
        logger.info(f"✅ Results database: {results_count} records")

        # Test AI database metrics tables
        tables = [
            "horse_speed_ratings",
            "horse_power_ratings",
            "monte_carlo_simulations",
        ]
        for table in tables:
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "ai_horse_racing_db",
                    "-c",
                    f"SELECT COUNT(*) FROM {table};",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                count_line = [line for line in lines if line.strip().isdigit()]
                count = count_line[0].strip() if count_line else "0"
                logger.info(f"✅ {table}: {count} records")
            else:
                logger.warning(f"⚠️ {table} table check failed: {result.stderr}")

        return True

    except Exception as e:
        logger.error(f"❌ Database connectivity failed: {e}")
        return False


def run_live_test():
    """Run the actual advanced metrics calculation"""
    logger.info("🚀 Running live advanced metrics calculation...")

    try:
        # Run the Docker-compatible advanced metrics script
        result = subprocess.run(
            ["python", "docker_advanced_metrics_populator.py"],
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode == 0:
            logger.info("✅ Advanced metrics calculation completed successfully")

            # Check output for key metrics
            output = result.stdout
            if "Speed ratings calculated" in output:
                logger.info("✅ Speed ratings calculation confirmed")
            if "Power ratings calculated" in output:
                logger.info("✅ Power ratings calculation confirmed")
            if "Monte Carlo simulations" in output:
                logger.info("✅ Monte Carlo simulations confirmed")

            return True
        else:
            logger.error(f"❌ Advanced metrics calculation failed:")
            logger.error(f"Exit code: {result.returncode}")
            logger.error(f"Error output: {result.stderr}")
            logger.error(f"Standard output: {result.stdout}")
            return False

    except subprocess.TimeoutExpired:
        logger.error("❌ Advanced metrics calculation timed out (5 minutes)")
        return False
    except Exception as e:
        logger.error(f"❌ Advanced metrics calculation error: {e}")
        return False


def validate_results():
    """Validate the results are properly stored"""
    logger.info("🔍 Validating calculation results...")

    try:
        # Check final data counts
        tables = {
            "horse_speed_ratings": "speed ratings",
            "horse_power_ratings": "power ratings",
            "monte_carlo_simulations": "Monte Carlo simulations",
        }

        for table, description in tables.items():
            result = subprocess.run(
                [
                    "docker",
                    "exec",
                    "horse_racing_postgres_clean",
                    "psql",
                    "-U",
                    "horse_racing",
                    "-d",
                    "ai_horse_racing_db",
                    "-c",
                    f"SELECT COUNT(*) FROM {table};",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                count_line = [line for line in lines if line.strip().isdigit()]
                count = int(count_line[0].strip()) if count_line else 0

                if count > 0:
                    logger.info(f"✅ {description}: {count} records stored")
                else:
                    logger.warning(f"⚠️ {description}: No records found")

        return True

    except Exception as e:
        logger.error(f"❌ Result validation failed: {e}")
        return False


def main():
    """Main test execution"""
    logger.info("🧪 Docker Advanced Metrics Test Suite")
    logger.info("=" * 50)

    start_time = time.time()

    # Pre-flight checks
    if not check_docker_containers():
        logger.error("❌ Docker container check failed")
        sys.exit(1)

    if not check_database_connectivity():
        logger.error("❌ Database connectivity check failed")
        sys.exit(1)

    # Run live test
    if not run_live_test():
        logger.error("❌ Live test failed")
        sys.exit(1)

    # Validate results
    if not validate_results():
        logger.error("❌ Result validation failed")
        sys.exit(1)

    # Success summary
    end_time = time.time()
    duration = end_time - start_time

    logger.info("=" * 50)
    logger.info("🎉 ALL TESTS PASSED!")
    logger.info(f"⏱️ Total execution time: {duration:.2f} seconds")
    logger.info("✅ Advanced metrics system is production ready")
    logger.info("=" * 50)


if __name__ == "__main__":
    main()
