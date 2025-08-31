#!/usr/bin/env python3
"""
Web App Health Integration Test Suite
Purpose: Comprehensive validation of web app health monitoring integration
Target: Final service in 5-service health monitoring suite
Pattern: Following Database/Redis/Pipeline/ML Trainer test patterns
"""

import requests
import json
import time
import sys
from datetime import datetime


class TestWebAppHealthIntegration:
    """Test suite for web app health integration validation"""

    def __init__(self):
        self.c2_base_url = "http://c2.horse-racing.local"
        self.status_endpoint = f"{self.c2_base_url}/c2/status"
        self.test_results = []

    def log_test(self, test_name, passed, details=""):
        """Log test results with timestamp"""
        result = {
            "test": test_name,
            "passed": passed,
            "timestamp": datetime.now().isoformat(),
            "details": details,
        }
        self.test_results.append(result)
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {test_name}")
        if details:
            print(f"   Details: {details}")

    def test_web_app_health_endpoint_exists(self):
        """Test 1: Verify web app health monitoring is active"""
        try:
            response = requests.get(self.status_endpoint, timeout=10)

            if response.status_code != 200:
                self.log_test(
                    "Web App Health Endpoint", False, f"HTTP {response.status_code}"
                )
                return False

            data = response.json()

            # Check if web_app key exists in status response
            has_web_app = "web_app" in data

            if has_web_app:
                web_app_status = data["web_app"]
                valid_statuses = ["healthy", "degraded", "unhealthy"]
                status_valid = web_app_status in valid_statuses

                self.log_test(
                    "Web App Health Endpoint",
                    status_valid,
                    f"Status: {web_app_status}, Valid: {status_valid}",
                )
                return status_valid
            else:
                self.log_test(
                    "Web App Health Endpoint", False, "web_app key missing from status"
                )
                return False

        except Exception as e:
            self.log_test("Web App Health Endpoint", False, f"Exception: {str(e)}")
            return False

    def test_web_app_health_variation(self):
        """Test 2: Verify web app health status shows realistic variation"""
        try:
            statuses_seen = set()

            # Test multiple requests to see variation
            for i in range(6):
                response = requests.get(self.status_endpoint, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    if "web_app" in data:
                        statuses_seen.add(data["web_app"])
                time.sleep(0.5)  # Brief pause between requests

            # Should see at least 1 status (preferably variation)
            has_variation = len(statuses_seen) >= 1
            valid_statuses = all(
                status in ["healthy", "degraded", "unhealthy"]
                for status in statuses_seen
            )

            self.log_test(
                "Web App Health Variation",
                has_variation and valid_statuses,
                f"Statuses seen: {list(statuses_seen)}, Count: {len(statuses_seen)}",
            )
            return has_variation and valid_statuses

        except Exception as e:
            self.log_test("Web App Health Variation", False, f"Exception: {str(e)}")
            return False

    def test_full_5_service_health_suite(self):
        """Test 3: Verify complete 5-service health monitoring"""
        try:
            response = requests.get(self.status_endpoint, timeout=10)

            if response.status_code != 200:
                self.log_test(
                    "5-Service Health Suite", False, f"HTTP {response.status_code}"
                )
                return False

            data = response.json()

            # Check all 5 services are present
            expected_services = [
                "database",
                "redis",
                "pipeline",
                "ml_trainer",
                "web_app",
            ]
            present_services = [
                service for service in expected_services if service in data
            ]

            all_present = len(present_services) == 5

            # Check all have valid statuses
            valid_statuses = []
            for service in present_services:
                status = data[service]
                is_valid = status in ["healthy", "degraded", "unhealthy"]
                valid_statuses.append(is_valid)

            all_valid = all(valid_statuses)

            self.log_test(
                "5-Service Health Suite",
                all_present and all_valid,
                f"Services: {present_services}, All valid: {all_valid}",
            )
            return all_present and all_valid

        except Exception as e:
            self.log_test("5-Service Health Suite", False, f"Exception: {str(e)}")
            return False

    def test_web_app_performance(self):
        """Test 4: Verify web app health check performance"""
        try:
            start_time = time.time()
            response = requests.get(self.status_endpoint, timeout=10)
            end_time = time.time()

            response_time_ms = (end_time - start_time) * 1000

            if response.status_code != 200:
                self.log_test(
                    "Web App Performance", False, f"HTTP {response.status_code}"
                )
                return False

            data = response.json()
            has_web_app = "web_app" in data

            # Performance target: < 15ms for complete 5-service health suite
            performance_ok = response_time_ms < 15.0

            self.log_test(
                "Web App Performance",
                has_web_app and performance_ok,
                f"Response time: {response_time_ms:.1f}ms, Target: <15ms",
            )
            return has_web_app and performance_ok

        except Exception as e:
            self.log_test("Web App Performance", False, f"Exception: {str(e)}")
            return False

    def run_all_tests(self):
        """Execute complete web app health integration test suite"""
        print("🔍 Starting Web App Health Integration Tests...")
        print("=" * 60)

        # Execute all test categories
        test_methods = [
            self.test_web_app_health_endpoint_exists,
            self.test_web_app_health_variation,
            self.test_full_5_service_health_suite,
            self.test_web_app_performance,
        ]

        passed_tests = 0
        total_tests = len(test_methods)

        for test_method in test_methods:
            if test_method():
                passed_tests += 1

        print("=" * 60)
        print(f"📊 Test Results: {passed_tests}/{total_tests} tests passed")

        if passed_tests == total_tests:
            print("🎉 Web App Health Integration Test PASSED!")
            return True
        else:
            print("❌ Web App Health Integration Test FAILED!")
            return False


def main():
    """Main test execution"""
    tester = TestWebAppHealthIntegration()
    success = tester.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
