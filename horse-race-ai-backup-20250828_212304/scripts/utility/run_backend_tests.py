#!/usr/bin/env python3
"""
Comprehensive Test Runner for Horse Racing AI Backend
Runs all API tests and generates detailed reports
"""

import subprocess
import sys
import os
import time
import requests
import json
from datetime import datetime
from pathlib import Path


class TestRunner:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.test_results = {
            "start_time": datetime.now().isoformat(),
            "api_tests": {},
            "performance_tests": {},
            "security_tests": {},
            "integration_tests": {},
            "summary": {},
        }

    def check_api_server(self):
        """Check if API server is running"""
        print("🔍 Checking API server status...")

        max_attempts = 30
        for attempt in range(max_attempts):
            try:
                response = requests.get(f"{self.base_url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ API server is running at {self.base_url}")
                    return True
            except requests.RequestException:
                pass

            print(
                f"⏳ Waiting for API server... (attempt {attempt + 1}/{max_attempts})"
            )
            time.sleep(2)

        print(f"❌ API server not available at {self.base_url}")
        return False

    def run_pytest_tests(self):
        """Run pytest API tests"""
        print("\n🧪 Running pytest API tests...")

        try:
            # Run comprehensive API tests
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "tests/test_api_comprehensive.py",
                    "-v",
                    "--tb=short",
                    "--json-report",
                    "--json-report-file=test-results/api-tests.json",
                ],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )

            self.test_results["api_tests"] = {
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "success": result.returncode == 0,
            }

            if result.returncode == 0:
                print("✅ API tests passed")
            else:
                print("❌ API tests failed")
                print(f"Error output: {result.stderr}")

            return result.returncode == 0

        except Exception as e:
            print(f"❌ Error running API tests: {e}")
            self.test_results["api_tests"] = {"error": str(e), "success": False}
            return False

    def run_performance_tests(self):
        """Run basic performance tests"""
        print("\n⚡ Running performance tests...")

        performance_results = {
            "response_times": {},
            "concurrent_requests": {},
            "large_payload": {},
        }

        try:
            # Test response times
            endpoints = ["/health", "/api/daily_races", "/api/real_race_cards"]

            for endpoint in endpoints:
                start_time = time.time()
                try:
                    response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                    end_time = time.time()
                    response_time = end_time - start_time

                    performance_results["response_times"][endpoint] = {
                        "response_time_ms": round(response_time * 1000, 2),
                        "status_code": response.status_code,
                        "success": response.status_code in [200, 404, 503],
                    }

                except Exception as e:
                    performance_results["response_times"][endpoint] = {
                        "error": str(e),
                        "success": False,
                    }

            # Test concurrent requests
            print("Testing concurrent requests...")
            import concurrent.futures
            import threading

            def make_request():
                try:
                    response = requests.get(f"{self.base_url}/health", timeout=5)
                    return response.status_code == 200
                except:
                    return False

            start_time = time.time()
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_request) for _ in range(10)]
                results = [
                    future.result()
                    for future in concurrent.futures.as_completed(futures)
                ]
            end_time = time.time()

            performance_results["concurrent_requests"] = {
                "total_requests": 10,
                "successful_requests": sum(results),
                "total_time_ms": round((end_time - start_time) * 1000, 2),
                "success_rate": sum(results) / len(results),
            }

            self.test_results["performance_tests"] = performance_results
            print("✅ Performance tests completed")
            return True

        except Exception as e:
            print(f"❌ Error running performance tests: {e}")
            self.test_results["performance_tests"] = {"error": str(e)}
            return False

    def run_security_tests(self):
        """Run basic security tests"""
        print("\n🔒 Running security tests...")

        security_results = {
            "cors_headers": {},
            "security_headers": {},
            "error_handling": {},
        }

        try:
            # Test CORS headers
            response = requests.get(f"{self.base_url}/health")
            headers = {k.lower(): v for k, v in response.headers.items()}

            security_results["cors_headers"] = {
                "has_cors": "access-control-allow-origin" in headers,
                "cors_origin": headers.get("access-control-allow-origin", "not-set"),
            }

            # Test security headers
            security_headers = [
                "x-content-type-options",
                "x-frame-options",
                "x-xss-protection",
                "strict-transport-security",
            ]

            security_results["security_headers"] = {
                header: header in headers for header in security_headers
            }

            # Test error handling
            response = requests.get(f"{self.base_url}/api/nonexistent")
            security_results["error_handling"] = {
                "returns_404": response.status_code == 404,
                "has_error_message": len(response.text) > 0,
            }

            self.test_results["security_tests"] = security_results
            print("✅ Security tests completed")
            return True

        except Exception as e:
            print(f"❌ Error running security tests: {e}")
            self.test_results["security_tests"] = {"error": str(e)}
            return False

    def generate_report(self):
        """Generate comprehensive test report"""
        print("\n📊 Generating test report...")

        # Calculate summary
        total_tests = 0
        passed_tests = 0

        for test_category in ["api_tests", "performance_tests", "security_tests"]:
            if test_category in self.test_results:
                total_tests += 1
                if self.test_results[test_category].get("success", False):
                    passed_tests += 1

        self.test_results["summary"] = {
            "total_test_categories": total_tests,
            "passed_categories": passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "end_time": datetime.now().isoformat(),
        }

        # Create test results directory
        os.makedirs("test-results", exist_ok=True)

        # Save detailed results
        with open("test-results/backend-test-results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)

        # Generate HTML report
        self.generate_html_report()

        print(f"✅ Test report saved to test-results/")

    def generate_html_report(self):
        """Generate HTML test report"""
        html_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Horse Racing AI - Backend Test Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background: #f0f8ff; padding: 20px; border-radius: 8px; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }
        .success { background: #f0fff0; border-color: #90ee90; }
        .failure { background: #fff0f0; border-color: #ffcccb; }
        .warning { background: #fffacd; border-color: #ffd700; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: #f9f9f9; border-radius: 4px; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🏇 Horse Racing AI - Backend Test Report</h1>
        <p><strong>Generated:</strong> {timestamp}</p>
        <p><strong>API URL:</strong> {api_url}</p>
    </div>
    
    <div class="section {summary_class}">
        <h2>📊 Test Summary</h2>
        <div class="metric">
            <strong>Total Categories:</strong> {total_categories}
        </div>
        <div class="metric">
            <strong>Passed:</strong> {passed_categories}
        </div>
        <div class="metric">
            <strong>Success Rate:</strong> {success_rate:.1%}
        </div>
    </div>
    
    <div class="section {api_class}">
        <h2>🧪 API Tests</h2>
        <p><strong>Status:</strong> {api_status}</p>
        {api_details}
    </div>
    
    <div class="section {perf_class}">
        <h2>⚡ Performance Tests</h2>
        <p><strong>Status:</strong> {perf_status}</p>
        {perf_details}
    </div>
    
    <div class="section {sec_class}">
        <h2>🔒 Security Tests</h2>
        <p><strong>Status:</strong> {sec_status}</p>
        {sec_details}
    </div>
</body>
</html>
"""

        # Prepare template variables
        summary = self.test_results.get("summary", {})
        api_tests = self.test_results.get("api_tests", {})
        perf_tests = self.test_results.get("performance_tests", {})
        sec_tests = self.test_results.get("security_tests", {})

        # Generate content
        html_content = html_template.format(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            api_url=self.base_url,
            total_categories=summary.get("total_test_categories", 0),
            passed_categories=summary.get("passed_categories", 0),
            success_rate=summary.get("success_rate", 0),
            summary_class=(
                "success" if summary.get("success_rate", 0) > 0.8 else "warning"
            ),
            api_status="PASSED" if api_tests.get("success") else "FAILED",
            api_class="success" if api_tests.get("success") else "failure",
            api_details=f"<pre>{api_tests.get('stdout', 'No details available')}</pre>",
            perf_status="COMPLETED" if "error" not in perf_tests else "FAILED",
            perf_class="success" if "error" not in perf_tests else "failure",
            perf_details=self.format_performance_details(perf_tests),
            sec_status="COMPLETED" if "error" not in sec_tests else "FAILED",
            sec_class="success" if "error" not in sec_tests else "failure",
            sec_details=self.format_security_details(sec_tests),
        )

        # Save HTML report
        with open("test-results/backend-test-report.html", "w") as f:
            f.write(html_content)

    def format_performance_details(self, perf_tests):
        """Format performance test details for HTML"""
        if "error" in perf_tests:
            return f"<p>Error: {perf_tests['error']}</p>"

        details = "<h3>Response Times</h3><table><tr><th>Endpoint</th><th>Response Time (ms)</th><th>Status</th></tr>"

        for endpoint, data in perf_tests.get("response_times", {}).items():
            status = "✅" if data.get("success") else "❌"
            response_time = data.get("response_time_ms", "N/A")
            details += (
                f"<tr><td>{endpoint}</td><td>{response_time}</td><td>{status}</td></tr>"
            )

        details += "</table>"

        concurrent = perf_tests.get("concurrent_requests", {})
        if concurrent:
            details += f"<h3>Concurrent Requests</h3>"
            details += f"<p>Success Rate: {concurrent.get('success_rate', 0):.1%}</p>"
            details += f"<p>Total Time: {concurrent.get('total_time_ms', 0)}ms</p>"

        return details

    def format_security_details(self, sec_tests):
        """Format security test details for HTML"""
        if "error" in sec_tests:
            return f"<p>Error: {sec_tests['error']}</p>"

        details = (
            "<h3>Security Headers</h3><table><tr><th>Header</th><th>Present</th></tr>"
        )

        for header, present in sec_tests.get("security_headers", {}).items():
            status = "✅" if present else "❌"
            details += f"<tr><td>{header}</td><td>{status}</td></tr>"

        details += "</table>"

        cors = sec_tests.get("cors_headers", {})
        if cors:
            details += f"<h3>CORS</h3>"
            details += f"<p>CORS Enabled: {'✅' if cors.get('has_cors') else '❌'}</p>"

        return details

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive backend testing...")

        # Check if API server is running
        if not self.check_api_server():
            print("❌ Cannot run tests without API server")
            return False

        # Run all test categories
        results = []
        results.append(self.run_pytest_tests())
        results.append(self.run_performance_tests())
        results.append(self.run_security_tests())

        # Generate report
        self.generate_report()

        # Print summary
        print(f"\n📋 Test Summary:")
        print(
            f"   API Tests: {'✅' if self.test_results['api_tests'].get('success') else '❌'}"
        )
        print(
            f"   Performance Tests: {'✅' if 'error' not in self.test_results['performance_tests'] else '❌'}"
        )
        print(
            f"   Security Tests: {'✅' if 'error' not in self.test_results['security_tests'] else '❌'}"
        )

        overall_success = all(results)
        print(f"   Overall: {'✅ PASSED' if overall_success else '❌ FAILED'}")

        return overall_success


if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
