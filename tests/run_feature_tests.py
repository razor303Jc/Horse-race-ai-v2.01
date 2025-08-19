#!/usr/bin/env python3
"""
Feature Test Suite Runner
Executes all feature-specific test suites for the Horse Racing AI platform
"""

import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path


class FeatureTestRunner:
    """Feature-specific test suite runner with reporting"""

    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0

        # Define test suites in execution order
        self.test_suites = [
            {
                "name": "ML Management Features",
                "file": "test_ml_management_features.py",
                "description": "Tests ML model management, A/B testing, and premium marketplace",
            },
            {
                "name": "Mobile Features",
                "file": "test_mobile_features.py",
                "description": "Tests PWA functionality, mobile interfaces, and cross-platform compatibility",
            },
            {
                "name": "Security Features",
                "file": "test_security_features.py",
                "description": "Tests 2FA, GDPR compliance, security monitoring, and fraud prevention",
            },
            {
                "name": "Analytics Features",
                "file": "test_analytics_features.py",
                "description": "Tests advanced analytics, performance monitoring, and reporting",
            },
            {
                "name": "Third-Party Integrations",
                "file": "test_third_party_integrations.py",
                "description": "Tests bookmaker APIs, payment systems, and external services",
            },
        ]

    def print_header(self):
        """Print test suite header"""
        print("🏇 Horse Racing AI - Feature Test Suite Runner")
        print("=" * 80)
        print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🧪 Test Suites: {len(self.test_suites)}")
        print("=" * 80)

    def run_test_suite(self, suite):
        """Run a single test suite"""
        print(f"\n🔄 Running: {suite['name']}")
        print(f"📝 Description: {suite['description']}")
        print("-" * 60)

        test_file = Path(__file__).parent / "unit" / suite["file"]

        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            return False

        # Run pytest with detailed output
        cmd = [
            sys.executable,
            "-m",
            "pytest",
            str(test_file),
            "-v",  # Verbose output
            "--tb=short",  # Short traceback format
            "--strict-markers",  # Strict marker validation
            "--capture=no",  # Don't capture output
            "--durations=10",  # Show 10 slowest tests
        ]

        start_time = time.time()

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per suite
            )

            duration = time.time() - start_time

            # Parse test results
            output_lines = result.stdout.split("\n")

            # Count tests
            test_count = 0
            passed_count = 0
            failed_count = 0

            for line in output_lines:
                if " PASSED " in line:
                    passed_count += 1
                    test_count += 1
                elif " FAILED " in line:
                    failed_count += 1
                    test_count += 1

            # Store results
            self.test_results[suite["name"]] = {
                "success": result.returncode == 0,
                "duration": duration,
                "test_count": test_count,
                "passed": passed_count,
                "failed": failed_count,
                "output": result.stdout,
                "errors": result.stderr,
            }

            # Update totals
            self.total_tests += test_count
            self.passed_tests += passed_count
            self.failed_tests += failed_count

            # Print results
            if result.returncode == 0:
                print(
                    f"✅ {suite['name']}: PASSED ({test_count} tests, {duration:.2f}s)"
                )
            else:
                print(
                    f"❌ {suite['name']}: FAILED ({passed_count} passed, {failed_count} failed, {duration:.2f}s)"
                )

                # Print error details (first few lines)
                if result.stderr:
                    print(f"🔧 Error Details:")
                    error_lines = result.stderr.strip().split("\n")[:5]
                    for line in error_lines:
                        print(f"   {line}")
                    if len(result.stderr.split("\n")) > 5:
                        print("   ...")

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            print(f"⏰ {suite['name']}: TIMEOUT (exceeded 5 minutes)")
            self.test_results[suite["name"]] = {
                "success": False,
                "duration": 300,
                "test_count": 0,
                "passed": 0,
                "failed": 0,
                "output": "",
                "errors": "Test suite timed out",
            }
            return False

        except Exception as e:
            print(f"💥 {suite['name']}: ERROR - {str(e)}")
            self.test_results[suite["name"]] = {
                "success": False,
                "duration": 0,
                "test_count": 0,
                "passed": 0,
                "failed": 0,
                "output": "",
                "errors": str(e),
            }
            return False

    def print_summary(self):
        """Print comprehensive test summary"""
        total_duration = time.time() - self.start_time

        print("\n" + "=" * 80)
        print("📊 FEATURE TEST SUITE SUMMARY")
        print("=" * 80)

        # Overall statistics
        successful_suites = sum(
            1 for result in self.test_results.values() if result["success"]
        )
        total_suites = len(self.test_results)

        print(f"⏱️  Total Duration: {total_duration:.2f} seconds")
        print(f"🧪 Test Suites: {successful_suites}/{total_suites} passed")
        print(f"🔬 Individual Tests: {self.passed_tests}/{self.total_tests} passed")

        if self.failed_tests > 0:
            print(f"❌ Failed Tests: {self.failed_tests}")

        print("\n📋 DETAILED RESULTS:")
        print("-" * 80)

        # Detailed results for each suite
        for suite_name, result in self.test_results.items():
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            duration = result["duration"]
            test_info = f"{result['passed']}/{result['test_count']} tests"

            print(f"{status:<8} {suite_name:<35} {test_info:<15} {duration:>6.2f}s")

        # Performance analysis
        print("\n⚡ PERFORMANCE ANALYSIS:")
        print("-" * 80)

        sorted_by_duration = sorted(
            self.test_results.items(), key=lambda x: x[1]["duration"], reverse=True
        )

        for suite_name, result in sorted_by_duration:
            duration = result["duration"]
            tests_per_second = result["test_count"] / duration if duration > 0 else 0
            print(
                f"{suite_name:<40} {duration:>6.2f}s ({tests_per_second:>4.1f} tests/sec)"
            )

        # Final verdict
        print("\n" + "=" * 80)
        if successful_suites == total_suites and self.failed_tests == 0:
            print(
                "🎉 ALL FEATURE TESTS PASSED! The Horse Racing AI platform features are working correctly."
            )
        elif successful_suites == total_suites:
            print(
                f"⚠️  Test suites passed but {self.failed_tests} individual tests failed."
            )
            print("🔧 Please review the failed tests above.")
        else:
            failed_suites = total_suites - successful_suites
            print(
                f"❌ {failed_suites} test suite(s) failed with {self.failed_tests} individual test failures."
            )
            print("🔧 Please fix the failing tests before deployment.")

        print("=" * 80)

    def generate_report(self):
        """Generate detailed test report"""
        report_file = Path(__file__).parent / "feature_test_report.md"

        with open(report_file, "w") as f:
            f.write("# Horse Racing AI - Feature Test Suite Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"**Total Duration:** {time.time() - self.start_time:.2f} seconds\n\n"
            )

            # Executive Summary
            successful_suites = sum(
                1 for result in self.test_results.values() if result["success"]
            )
            total_suites = len(self.test_results)

            f.write("## Executive Summary\n\n")
            f.write(f"- **Test Suites:** {successful_suites}/{total_suites} passed\n")
            f.write(
                f"- **Individual Tests:** {self.passed_tests}/{self.total_tests} passed\n"
            )
            f.write(
                f"- **Overall Status:** {'✅ PASSED' if successful_suites == total_suites and self.failed_tests == 0 else '❌ FAILED'}\n\n"
            )

            # Summary table
            f.write("## Test Suite Results\n\n")
            f.write("| Suite | Status | Tests | Duration |\n")
            f.write("|-------|--------|-------|----------|\n")

            for suite_name, result in self.test_results.items():
                status = "✅ PASS" if result["success"] else "❌ FAIL"
                test_info = f"{result['passed']}/{result['test_count']}"
                duration = f"{result['duration']:.2f}s"
                f.write(f"| {suite_name} | {status} | {test_info} | {duration} |\n")

            # Feature Coverage
            f.write("\n## Feature Coverage\n\n")
            f.write("### Tested Features\n\n")

            feature_descriptions = {
                "ML Management Features": [
                    "Machine Learning model management and versioning",
                    "A/B testing framework for model comparison",
                    "Premium model marketplace with licensing",
                    "Real-time model performance monitoring",
                ],
                "Mobile Features": [
                    "Progressive Web App (PWA) functionality",
                    "Mobile-responsive user interfaces",
                    "Touch gesture optimization",
                    "Cross-platform compatibility testing",
                ],
                "Security Features": [
                    "Two-Factor Authentication (2FA) with TOTP",
                    "GDPR compliance and privacy management",
                    "Security monitoring and audit logging",
                    "Fraud detection and prevention systems",
                ],
                "Analytics Features": [
                    "Advanced betting analytics and reporting",
                    "Real-time performance monitoring",
                    "ROI and risk analysis calculations",
                    "Data visualization and dashboard systems",
                ],
                "Third-Party Integrations": [
                    "Multi-bookmaker API integrations",
                    "Payment gateway processing (Stripe, PayPal, Open Banking)",
                    "External data feed synchronization",
                    "Notification services (Email, SMS, Push)",
                ],
            }

            for suite_name, features in feature_descriptions.items():
                result = self.test_results.get(suite_name)
                status = "✅" if result and result["success"] else "❌"
                f.write(f"#### {status} {suite_name}\n\n")
                for feature in features:
                    f.write(f"- {feature}\n")
                f.write("\n")

            # Detailed results
            f.write("## Detailed Test Results\n\n")

            for suite_name, result in self.test_results.items():
                f.write(f"### {suite_name}\n\n")
                f.write(
                    f"- **Status:** {'PASSED' if result['success'] else 'FAILED'}\n"
                )
                f.write(f"- **Duration:** {result['duration']:.2f} seconds\n")
                f.write(
                    f"- **Tests:** {result['test_count']} total, {result['passed']} passed, {result['failed']} failed\n\n"
                )

                if result["errors"] and result["errors"].strip():
                    f.write(
                        f"**Errors:**\n```\n{result['errors'][:1000]}{'...' if len(result['errors']) > 1000 else ''}\n```\n\n"
                    )

        print(f"📄 Detailed report saved to: {report_file}")

    def run_all_tests(self):
        """Run all test suites"""
        self.print_header()
        self.start_time = time.time()

        all_passed = True

        for suite in self.test_suites:
            suite_passed = self.run_test_suite(suite)
            if not suite_passed:
                all_passed = False

        self.print_summary()
        self.generate_report()

        return all_passed


def main():
    """Main entry point"""
    runner = FeatureTestRunner()

    try:
        success = runner.run_all_tests()
        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\n⚠️  Test execution interrupted by user")
        print("🔧 Partial results may be available in feature_test_report.md")
        sys.exit(2)

    except Exception as e:
        print(f"\n💥 Test runner error: {str(e)}")
        sys.exit(3)


if __name__ == "__main__":
    main()
