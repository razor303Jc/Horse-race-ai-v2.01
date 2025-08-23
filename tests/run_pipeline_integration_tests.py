"""
Comprehensive test runner for pipeline integration components.
Runs all tests related to the pipeline integration work.
"""

import pytest
import sys
import os
import logging
from pathlib import Path
import subprocess
import time

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def check_test_environment():
    """Check if test environment is properly set up."""
    logger.info("🔍 Checking test environment...")
    
    # Check Python packages
    required_packages = ['pytest', 'pandas', 'psycopg2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✅ {package} available")
        except ImportError:
            missing_packages.append(package)
            logger.warning(f"❌ {package} not available")
    
    if missing_packages:
        logger.warning(f"Missing packages: {missing_packages}")
        logger.info("Install with: pip install pytest pandas psycopg2-binary")
    
    # Check Docker availability
    try:
        result = subprocess.run(
            ["docker", "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("✅ Docker available")
        else:
            logger.warning("❌ Docker not available")
    except (FileNotFoundError, subprocess.TimeoutExpired):
        logger.warning("❌ Docker not available")
    
    # Check project structure
    test_files = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py", 
        "tests/test_database_uploader.py"
    ]
    
    for test_file in test_files:
        test_path = project_root / test_file
        if test_path.exists():
            logger.info(f"✅ {test_file} found")
        else:
            logger.warning(f"❌ {test_file} not found")
    
    return len(missing_packages) == 0


def run_unit_tests():
    """Run unit tests for pipeline components."""
    logger.info("🧪 Running unit tests...")
    
    test_args = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py",
        "tests/test_database_uploader.py",
        "-v",
        "--tb=short",
        "-m", "not slow and not integration"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        logger.info("✅ Unit tests passed")
    else:
        logger.error("❌ Unit tests failed")
    
    return result == 0


def run_integration_tests():
    """Run integration tests for pipeline components."""
    logger.info("🔗 Running integration tests...")
    
    test_args = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py",
        "tests/test_database_uploader.py",
        "-v",
        "--tb=short",
        "-m", "integration"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        logger.info("✅ Integration tests passed")
    else:
        logger.error("❌ Integration tests failed")
    
    return result == 0


def run_slow_tests():
    """Run slow tests that require external resources."""
    logger.info("🐌 Running slow tests...")
    
    test_args = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py",
        "tests/test_database_uploader.py",
        "-v",
        "--tb=short",
        "-m", "slow"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        logger.info("✅ Slow tests passed")
    else:
        logger.error("❌ Slow tests failed")
    
    return result == 0


def run_all_pipeline_tests():
    """Run all pipeline integration tests."""
    logger.info("🚀 Running all pipeline integration tests...")
    
    test_args = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py",
        "tests/test_database_uploader.py",
        "-v",
        "--tb=short",
        "--color=yes"
    ]
    
    result = pytest.main(test_args)
    
    if result == 0:
        logger.info("✅ All pipeline tests passed")
    else:
        logger.error("❌ Some pipeline tests failed")
    
    return result == 0


def generate_test_report():
    """Generate a comprehensive test report."""
    logger.info("📊 Generating test report...")
    
    report_file = project_root / "tests" / "pipeline_integration_test_report.txt"
    
    test_args = [
        "tests/test_pipeline_integration.py",
        "tests/test_csv_column_mapping.py",
        "tests/test_database_uploader.py",
        "-v",
        "--tb=short",
        f"--junitxml={project_root}/tests/pipeline_test_results.xml"
    ]
    
    # Run tests and capture output
    result = pytest.main(test_args)
    
    # Create summary report
    with open(report_file, 'w') as f:
        f.write("Pipeline Integration Test Report\n")
        f.write("================================\n\n")
        f.write(f"Test run date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Test result: {'PASSED' if result == 0 else 'FAILED'}\n\n")
        
        f.write("Test Coverage:\n")
        f.write("- File Watcher Integration\n")
        f.write("- Pipeline Automation\n")
        f.write("- CSV Column Mapping\n")
        f.write("- Database Uploader\n")
        f.write("- Separated Data Architecture\n")
        f.write("- Docker Integration\n")
        f.write("- Error Handling\n\n")
        
        f.write("Test Categories:\n")
        f.write("- Unit Tests: Component-level testing\n")
        f.write("- Integration Tests: Cross-component testing\n")
        f.write("- System Tests: End-to-end testing\n")
        f.write("- Performance Tests: Resource usage testing\n\n")
    
    logger.info(f"✅ Test report generated: {report_file}")
    return result == 0


def main():
    """Main test execution function."""
    logger.info("""
╭─────────────────────────────────────────╮
│     Pipeline Integration Test Suite     │
│                                         │
│  Testing all pipeline components and   │
│  integration functionality             │
╰─────────────────────────────────────────╯
    """)
    
    # Check environment
    if not check_test_environment():
        logger.error("❌ Test environment check failed")
        return 1
    
    # Run test suites
    results = []
    
    logger.info("\n" + "="*50)
    logger.info("UNIT TESTS")
    logger.info("="*50)
    results.append(run_unit_tests())
    
    logger.info("\n" + "="*50)
    logger.info("INTEGRATION TESTS")
    logger.info("="*50)
    results.append(run_integration_tests())
    
    logger.info("\n" + "="*50)
    logger.info("SLOW TESTS")
    logger.info("="*50)
    results.append(run_slow_tests())
    
    logger.info("\n" + "="*50)
    logger.info("COMPREHENSIVE TEST REPORT")
    logger.info("="*50)
    generate_test_report()
    
    # Summary
    passed_tests = sum(results)
    total_tests = len(results)
    
    logger.info(f"\n📊 Test Summary: {passed_tests}/{total_tests} test suites passed")
    
    if all(results):
        logger.info("🎉 All pipeline integration tests completed successfully!")
        return 0
    else:
        logger.error("❌ Some tests failed. Check logs for details.")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
