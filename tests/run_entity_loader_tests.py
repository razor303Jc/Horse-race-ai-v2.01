#!/usr/bin/env python3
"""
🧪 Entity Loader Test Suite Runner - v2.05
==========================================

Comprehensive test runner for entity loader functionality including:
- Place code mapping tests
- Database integration tests
- Index table maintenance tests
- Performance tests
"""

import pytest
import sys
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.append(str(PROJECT_ROOT))


def run_entity_loader_tests():
    """Run all entity loader related tests"""
    logger.info("🚀 Starting Entity Loader Test Suite v2.05")

    # Test configuration
    test_args = [
        "-v",  # Verbose output
        "--tb=short",  # Short traceback format
        "--disable-warnings",  # Disable warnings
        "--color=yes",  # Colored output
        "-m",
        "not slow",  # Skip slow tests by default
        "--durations=10",  # Show 10 slowest tests
    ]

    # Test paths
    test_paths = [
        "tests/unit/test_entity_loader.py",
        "tests/unit/test_index_updater.py",
        "tests/integration/test_entity_loader_integration.py",
    ]

    # Add test paths to arguments
    test_args.extend(test_paths)

    logger.info(f"Running tests with args: {test_args}")

    # Run tests
    exit_code = pytest.main(test_args)

    if exit_code == 0:
        logger.info("✅ All entity loader tests passed!")
    else:
        logger.error(f"❌ Tests failed with exit code: {exit_code}")

    return exit_code


def run_integration_tests():
    """Run only integration tests"""
    logger.info("🔗 Running Integration Tests")

    test_args = ["-v", "--tb=short", "-m", "integration", "tests/integration/"]

    exit_code = pytest.main(test_args)
    return exit_code


def run_performance_tests():
    """Run performance tests"""
    logger.info("⚡ Running Performance Tests")

    test_args = ["-v", "--tb=short", "-m", "slow", "tests/"]

    exit_code = pytest.main(test_args)
    return exit_code


def run_unit_tests_only():
    """Run only unit tests"""
    logger.info("🔬 Running Unit Tests Only")

    test_args = [
        "-v",
        "--tb=short",
        "-m",
        "not integration and not slow",
        "tests/unit/",
    ]

    exit_code = pytest.main(test_args)
    return exit_code


def generate_test_report():
    """Generate comprehensive test report"""
    logger.info("📊 Generating Test Report")

    test_args = [
        "-v",
        "--tb=short",
        "--html=tests/reports/entity_loader_test_report.html",
        "--self-contained-html",
        "--junit-xml=tests/reports/entity_loader_junit.xml",
        "-m",
        "not slow",
        "tests/unit/test_entity_loader.py",
        "tests/unit/test_index_updater.py",
        "tests/integration/test_entity_loader_integration.py",
    ]

    # Ensure reports directory exists
    reports_dir = Path("tests/reports")
    reports_dir.mkdir(exist_ok=True)

    exit_code = pytest.main(test_args)

    if exit_code == 0:
        logger.info("📈 Test report generated successfully!")
        logger.info(f"HTML Report: {reports_dir}/entity_loader_test_report.html")
        logger.info(f"JUnit XML: {reports_dir}/entity_loader_junit.xml")

    return exit_code


def validate_test_environment():
    """Validate that test environment is properly set up"""
    logger.info("🔍 Validating Test Environment")

    # Check required files exist
    required_files = [
        "scripts/fixed_entity_loader_v2_05.py",
        "scripts/update_index_tables.py",
        "tests/unit/test_entity_loader.py",
        "tests/unit/test_index_updater.py",
        "tests/integration/test_entity_loader_integration.py",
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"❌ Missing required files: {missing_files}")
        return False

    # Check test dependencies
    try:
        import pytest
        import pandas
        import psycopg2

        logger.info("✅ All test dependencies available")
    except ImportError as e:
        logger.error(f"❌ Missing test dependency: {e}")
        return False

    logger.info("✅ Test environment validation passed")
    return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Entity Loader Test Suite Runner")
    parser.add_argument(
        "--mode",
        choices=["all", "unit", "integration", "performance", "report"],
        default="all",
        help="Test mode to run",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validate test environment first"
    )

    args = parser.parse_args()

    # Validate environment if requested
    if args.validate:
        if not validate_test_environment():
            sys.exit(1)

    # Run tests based on mode
    if args.mode == "all":
        exit_code = run_entity_loader_tests()
    elif args.mode == "unit":
        exit_code = run_unit_tests_only()
    elif args.mode == "integration":
        exit_code = run_integration_tests()
    elif args.mode == "performance":
        exit_code = run_performance_tests()
    elif args.mode == "report":
        exit_code = generate_test_report()
    else:
        logger.error(f"Unknown mode: {args.mode}")
        exit_code = 1

    sys.exit(exit_code)
