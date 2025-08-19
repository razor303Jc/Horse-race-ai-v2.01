#!/usr/bin/env python3
"""
Simple Test Runner for Horse Racing AI V2.03
Runs tests using pytest without complex dependencies
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def run_pytest_tests(test_path, test_name, verbose=True):
    """Run pytest tests for a specific path"""
    print(f"\n🧪 Running {test_name}...")
    print("=" * 50)

    if not os.path.exists(test_path):
        print(f"⏭️ Test file not found: {test_path}")
        return {
            "status": "skipped",
            "tests": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0,
        }

    start_time = time.time()

    # Build pytest command
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        str(test_path),
        "-v" if verbose else "-q",
        "--tb=short",
        "--no-header",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=PROJECT_ROOT)
        duration = time.time() - start_time

        # Parse pytest output
        output_lines = result.stdout.split("\n")

        # Count test results
        passed = len([line for line in output_lines if " PASSED" in line])
        failed = len([line for line in output_lines if " FAILED" in line])
        skipped = len([line for line in output_lines if " SKIPPED" in line])
        total = passed + failed + skipped

        if result.returncode == 0:
            print(f"✅ {test_name} completed successfully")
            print(
                f"   Tests: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}"
            )
            print(f"   Duration: {duration:.2f}s")
            status = "passed"
        else:
            print(f"❌ {test_name} completed with issues")
            print(
                f"   Tests: {total} | Passed: {passed} | Failed: {failed} | Skipped: {skipped}"
            )
            print(f"   Duration: {duration:.2f}s")
            if verbose and result.stderr:
                print(f"   Errors: {result.stderr}")
            status = "failed"

        return {
            "status": status,
            "tests": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration": duration,
            "output": result.stdout,
        }

    except Exception as e:
        duration = time.time() - start_time
        print(f"❌ Error running {test_name}: {e}")
        return {
            "status": "error",
            "tests": 0,
            "passed": 0,
            "failed": 1,
            "duration": duration,
        }


def run_integration_tests():
    """Run integration tests directly"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)

    try:
        from tests.test_complete_system_integration import SystemIntegrationTestSuite

        start_time = time.time()
        suite = SystemIntegrationTestSuite()
        suite.setup_test_framework()
        suite.run_all_tests()
        duration = time.time() - start_time

        # Calculate results
        total_tests = len(suite.results)
        passed_tests = len(
            [r for r in suite.results if r["failures"] == 0 and r["errors"] == 0]
        )
        failed_tests = total_tests - passed_tests

        print(f"✅ Integration tests completed")
        print(
            f"   Test Suites: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}"
        )
        print(f"   Duration: {duration:.2f}s")

        return {
            "status": "passed" if failed_tests == 0 else "failed",
            "tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "skipped": 0,
            "duration": duration,
        }

    except ImportError as e:
        print(f"⏭️ Integration tests not available: {e}")
        return {
            "status": "skipped",
            "tests": 0,
            "passed": 0,
            "failed": 0,
            "duration": 0,
        }
    except Exception as e:
        print(f"❌ Error running integration tests: {e}")
        return {"status": "error", "tests": 0, "passed": 0, "failed": 1, "duration": 0}


def validate_test_framework():
    """Validate that our test framework components are working"""
    print("\n🔍 Validating Test Framework...")
    print("=" * 50)

    validations = [
        ("Test runner", "tests.run_comprehensive_tests"),
        ("System integration tests", "tests.test_complete_system_integration"),
        ("Unit test data processing", "tests.unit.test_data_processing"),
        ("Unit test ML components", "tests.unit.test_ml_components"),
        ("Unit test security", "tests.unit.test_security_components"),
        ("Performance tests", "tests.performance.test_performance_load"),
    ]

    results = []
    for name, module_name in validations:
        try:
            __import__(module_name)
            print(f"✅ {name}: Import successful")
            results.append(True)
        except ImportError as e:
            print(f"⚠️ {name}: Import failed - {e}")
            results.append(False)
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            results.append(False)

    success_rate = sum(results) / len(results) * 100
    print(
        f"\n📊 Validation Summary: {sum(results)}/{len(results)} components working ({success_rate:.1f}%)"
    )

    return success_rate >= 50  # At least 50% should work


def main():
    """Main test execution"""
    print("🧪 Horse Racing AI V2.03 - Simple Test Runner")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Validate test framework first
    if not validate_test_framework():
        print("\n❌ Test framework validation failed. Cannot proceed with tests.")
        return 1

    # Run tests
    test_results = {}
    total_start_time = time.time()

    # Unit Tests
    print("\n📋 UNIT TESTS")
    print("-" * 30)

    unit_tests = [
        ("tests/unit/test_data_processing.py", "Data Processing Tests"),
        ("tests/unit/test_ml_components.py", "ML Component Tests"),
        ("tests/unit/test_security_components.py", "Security Component Tests"),
    ]

    for test_path, test_name in unit_tests:
        result = run_pytest_tests(test_path, test_name)
        test_results[test_name] = result

    # Integration Tests
    print("\n📋 INTEGRATION TESTS")
    print("-" * 30)

    integration_result = run_integration_tests()
    test_results["Integration Tests"] = integration_result

    # Performance Tests (optional)
    print("\n📋 PERFORMANCE TESTS")
    print("-" * 30)

    perf_result = run_pytest_tests(
        "tests/performance/test_performance_load.py", "Performance Tests"
    )
    test_results["Performance Tests"] = perf_result

    # Calculate overall results
    total_duration = time.time() - total_start_time
    total_tests = sum(r["tests"] for r in test_results.values())
    total_passed = sum(r["passed"] for r in test_results.values())
    total_failed = sum(r["failed"] for r in test_results.values())
    total_skipped = sum(r["skipped"] for r in test_results.values())

    success_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    # Generate summary report
    print("\n" + "=" * 60)
    print("🎯 TEST EXECUTION SUMMARY")
    print("=" * 60)
    print(f"Total Duration: {total_duration:.2f}s")
    print(f"Total Tests: {total_tests}")
    print(
        f"✅ Passed: {total_passed} ({total_passed/total_tests*100:.1f}%)"
        if total_tests > 0
        else "✅ Passed: 0"
    )
    print(
        f"❌ Failed: {total_failed} ({total_failed/total_tests*100:.1f}%)"
        if total_tests > 0
        else "❌ Failed: 0"
    )
    print(
        f"⏭️ Skipped: {total_skipped} ({total_skipped/total_tests*100:.1f}%)"
        if total_tests > 0
        else "⏭️ Skipped: 0"
    )
    print(f"🎯 Success Rate: {success_rate:.1f}%")

    print("\n📋 Test Suite Breakdown:")
    for test_name, result in test_results.items():
        status_icon = (
            "✅"
            if result["status"] == "passed"
            else "❌" if result["status"] == "failed" else "⏭️"
        )
        print(
            f"  {status_icon} {test_name}: {result['passed']}/{result['tests']} passed ({result['duration']:.2f}s)"
        )

    # Final assessment
    if total_failed == 0 and total_tests > 0:
        print(f"\n🎉 ALL TESTS PASSED! System is ready for production.")
    elif success_rate >= 80:
        print(f"\n✅ Most tests passed ({success_rate:.1f}%). System is mostly ready.")
    elif success_rate >= 50:
        print(
            f"\n⚠️ Some tests failed ({success_rate:.1f}%). Review required before production."
        )
    else:
        print(
            f"\n❌ Many tests failed ({success_rate:.1f}%). Significant issues need resolution."
        )

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Create simple report file
    report_dir = PROJECT_ROOT / "tests" / "reports"
    report_dir.mkdir(exist_ok=True)

    report_file = report_dir / f"simple_test_report_{int(time.time())}.txt"
    with open(report_file, "w") as f:
        f.write(f"Horse Racing AI V2.03 - Simple Test Report\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"Passed: {total_passed}\n")
        f.write(f"Failed: {total_failed}\n")
        f.write(f"Skipped: {total_skipped}\n")
        f.write(f"Success Rate: {success_rate:.1f}%\n\n")

        for test_name, result in test_results.items():
            f.write(
                f"{test_name}: {result['status']} ({result['passed']}/{result['tests']})\n"
            )

    print(f"\n📄 Report saved to: {report_file}")

    return 0 if total_failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
