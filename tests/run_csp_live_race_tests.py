"""
Comprehensive test runner for CSP configuration and live race tracking features
Runs both test suites and generates a comprehensive report
"""

import subprocess
import sys
import time
import json
from pathlib import Path


def run_test_suite(test_file: str, test_name: str) -> dict:
    """Run a specific test suite and capture results"""
    print(f"\n🧪 Running {test_name} tests...")
    print("=" * 60)

    start_time = time.time()

    try:
        # Run pytest with verbose output and JSON report
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                test_file,
                "-v",
                "--tb=short",
                "--no-header",
                "--json-report",
                f"--json-report-file=tests/playwright/reports/{test_name.lower().replace(' ', '_')}_report.json",
            ],
            capture_output=True,
            text=True,
            cwd="/home/jc/Documents/Horse-race-ai-v2.03",
        )

        end_time = time.time()
        duration = end_time - start_time

        print(result.stdout)
        if result.stderr:
            print("⚠️  Warnings/Errors:")
            print(result.stderr)

        return {
            "name": test_name,
            "success": result.returncode == 0,
            "duration": duration,
            "return_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }

    except Exception as e:
        print(f"❌ Failed to run {test_name} tests: {e}")
        return {"name": test_name, "success": False, "duration": 0, "error": str(e)}


def generate_comprehensive_report(results: list):
    """Generate a comprehensive test report"""
    print("\n📊 Comprehensive Test Report")
    print("=" * 60)

    total_tests = len(results)
    passed_tests = sum(1 for r in results if r["success"])
    failed_tests = total_tests - passed_tests
    total_duration = sum(r.get("duration", 0) for r in results)

    print(f"📈 Overall Results:")
    print(f"  Total Test Suites: {total_tests}")
    print(f"  ✅ Passed: {passed_tests}")
    print(f"  ❌ Failed: {failed_tests}")
    print(f"  ⏱️  Total Duration: {total_duration:.2f} seconds")
    print(f"  📊 Success Rate: {(passed_tests/total_tests*100):.1f}%")

    print(f"\n📋 Detailed Results:")
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        duration = result.get("duration", 0)
        print(f"  {status} {result['name']} ({duration:.2f}s)")

        if not result["success"] and "error" in result:
            print(f"    Error: {result['error']}")

    # Create summary report file
    report_data = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total_suites": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "duration": total_duration,
            "success_rate": passed_tests / total_tests * 100,
        },
        "results": results,
    }

    report_path = Path("tests/playwright/reports/comprehensive_test_summary.json")
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with open(report_path, "w") as f:
        json.dump(report_data, f, indent=2)

    print(f"\n📄 Detailed report saved to: {report_path}")

    return report_data


def main():
    """Main test runner function"""
    print("🏇 Horse Racing AI v2.03 - CSP & Live Race Tracking Test Suite")
    print("=" * 70)
    print("🔧 Testing CSP configuration and live race tracking features")
    print("📅 " + time.strftime("%Y-%m-%d %H:%M:%S"))

    # Ensure reports directory exists
    Path("tests/playwright/reports").mkdir(parents=True, exist_ok=True)

    # Test suites to run
    test_suites = [
        {
            "file": "tests/playwright/test_csp_configuration.py",
            "name": "CSP Configuration",
        },
        {
            "file": "tests/playwright/test_live_race_tracking.py",
            "name": "Live Race Tracking",
        },
    ]

    results = []

    # Run each test suite
    for suite in test_suites:
        result = run_test_suite(suite["file"], suite["name"])
        results.append(result)

    # Generate comprehensive report
    report = generate_comprehensive_report(results)

    # Final summary
    print(f"\n🎯 Test Execution Complete!")
    success_rate = report["summary"]["success_rate"]

    if success_rate == 100:
        print("🎉 All tests passed successfully!")
        return 0
    elif success_rate >= 80:
        print("✅ Most tests passed with some issues to review")
        return 1
    else:
        print("⚠️  Significant test failures detected - review required")
        return 2


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
