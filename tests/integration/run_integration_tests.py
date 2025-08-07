"""
Integration test runner for containerized environment.

This script runs the complete integration test suite including:
- NTFY notifications
- Database connectivity
- Service health checks
- Cross-service communication
"""

import asyncio
import os
import sys
import time
from pathlib import Path

import pytest
import requests
import structlog

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

logger = structlog.get_logger(__name__)


class IntegrationTestRunner:
    """Manages integration test execution in containerized environment."""

    def __init__(self):
        """Initialize test runner with configuration."""
        self.services = {
            "postgres": {
                "host": os.getenv("POSTGRES_HOST", "postgres-test"),
                "port": int(os.getenv("POSTGRES_PORT", "5432")),
                "health_check": self._check_postgres_health,
            },
            "redis": {
                "host": os.getenv("REDIS_HOST", "redis-test"),
                "port": int(os.getenv("REDIS_PORT", "6379")),
                "health_check": self._check_redis_health,
            },
            "ntfy": {
                "host": os.getenv("NTFY_HOST", "ntfy-test"),
                "port": int(os.getenv("NTFY_PORT", "80")),
                "health_check": self._check_ntfy_health,
            },
        }

        self.max_wait_time = int(os.getenv("SERVICE_WAIT_TIME", "60"))
        self.check_interval = 2

    def _check_postgres_health(self, config: dict) -> bool:
        """Check PostgreSQL health."""
        try:
            import psycopg2

            conn = psycopg2.connect(
                host=config["host"],
                port=config["port"],
                database=os.getenv("POSTGRES_DB", "horse_racing_test"),
                user=os.getenv("POSTGRES_USER", "testuser"),
                password=os.getenv("POSTGRES_PASSWORD", "testpass"),
                connect_timeout=5,
            )
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    result = cur.fetchone()
                    return result[0] == 1
        except Exception as e:
            logger.debug(f"PostgreSQL health check failed: {e}")
            return False

    def _check_redis_health(self, config: dict) -> bool:
        """Check Redis health."""
        try:
            import redis

            client = redis.Redis(
                host=config["host"],
                port=config["port"],
                db=0,
                socket_connect_timeout=5,
                socket_timeout=5,
            )
            response = client.ping()
            client.close()
            return response is True
        except Exception as e:
            logger.debug(f"Redis health check failed: {e}")
            return False

    def _check_ntfy_health(self, config: dict) -> bool:
        """Check NTFY health."""
        try:
            url = f"http://{config['host']}:{config['port']}/v1/health"
            response = requests.get(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.debug(f"NTFY health check failed: {e}")
            return False

    async def wait_for_services(self) -> bool:
        """Wait for all services to be healthy."""
        logger.info("🔄 Waiting for services to be ready...")

        start_time = time.time()

        while time.time() - start_time < self.max_wait_time:
            all_healthy = True

            for service_name, config in self.services.items():
                is_healthy = config["health_check"](config)

                if is_healthy:
                    logger.info(f"✅ {service_name} is healthy")
                else:
                    logger.warning(f"⏳ {service_name} not ready yet...")
                    all_healthy = False

            if all_healthy:
                logger.info("🎉 All services are ready!")
                return True

            logger.info(f"⏱️  Waiting {self.check_interval}s before next check...")
            await asyncio.sleep(self.check_interval)

        logger.error(f"❌ Services not ready after {self.max_wait_time}s")
        return False

    def run_integration_tests(self) -> int:
        """Run the integration test suite."""
        logger.info("🧪 Starting integration test suite...")

        # Test configuration
        test_args = [
            "tests/integration/",
            "-v",
            "--tb=short",
            "--asyncio-mode=auto",
            "--junit-xml=test-results/integration-results.xml",
            "--cov=src",
            "--cov-report=xml:test-results/integration-coverage.xml",
            "--cov-report=html:test-results/htmlcov-integration",
            "--cov-report=term-missing",
        ]

        # Add markers for specific test types
        markers = os.getenv("PYTEST_MARKERS", "")
        if markers:
            test_args.extend(["-m", markers])

        # Run tests
        logger.info(f"Running: pytest {' '.join(test_args)}")
        exit_code = pytest.main(test_args)

        if exit_code == 0:
            logger.info("✅ All integration tests passed!")
        else:
            logger.error(f"❌ Integration tests failed with exit code: {exit_code}")

        return exit_code

    def generate_test_report(self):
        """Generate comprehensive test report."""
        logger.info("📊 Generating test report...")

        report_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "services": {},
            "environment": {
                "POSTGRES_HOST": os.getenv("POSTGRES_HOST"),
                "REDIS_HOST": os.getenv("REDIS_HOST"),
                "NTFY_HOST": os.getenv("NTFY_HOST"),
                "PYTEST_MARKERS": os.getenv("PYTEST_MARKERS", "all"),
            },
        }

        # Check final service status
        for service_name, config in self.services.items():
            is_healthy = config["health_check"](config)
            report_data["services"][service_name] = {
                "healthy": is_healthy,
                "host": config["host"],
                "port": config["port"],
            }

        # Write report
        import json

        report_path = Path("test-results/integration-report.json")
        report_path.parent.mkdir(exist_ok=True)

        with open(report_path, "w") as f:
            json.dump(report_data, f, indent=2)

        logger.info(f"📋 Test report saved to: {report_path}")


async def main():
    """Main entry point for integration test runner."""
    # Configure logging
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logger.info("🚀 Starting Horse Racing AI Integration Tests")

    runner = IntegrationTestRunner()

    # Wait for services
    if not await runner.wait_for_services():
        logger.error("❌ Service health checks failed - aborting tests")
        return 1

    # Run tests
    try:
        exit_code = runner.run_integration_tests()
    except Exception as e:
        logger.error(f"❌ Test execution failed: {e}")
        exit_code = 1
    finally:
        # Always generate report
        runner.generate_test_report()

    if exit_code == 0:
        logger.info("🎉 Integration test suite completed successfully!")
    else:
        logger.error("💥 Integration test suite failed!")

    return exit_code


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
