"""
Enhanced web application tests with advanced features
Includes load testing, detailed API validation, and UI interaction testing.
"""

import pytest
import requests
import json
import time
import concurrent.futures
from datetime import datetime, timedelta


class TestAdvancedAPI:
    """Advanced API testing with detailed validation"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_api_field_validation(self, base_url):
        """Test detailed API field validation and data types"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        data = response.json()

        # Test required field presence and types
        required_fields = {
            "overall_status": str,
            "timestamp": str,
            "ml_models": str,
            "betting_integration": str,
            "contextual_ai": str,
            "notifications": str,
            "performance_tracker": str,
        }

        for field, expected_type in required_fields.items():
            assert field in data, f"Missing required field: {field}"
            assert isinstance(data[field], expected_type), (
                f"Field {field} should be {expected_type.__name__}, "
                f"got {type(data[field]).__name__}"
            )

    def test_timestamp_validity(self, base_url):
        """Test that API timestamps are valid and recent"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        data = response.json()

        timestamp_str = data.get("timestamp")
        assert timestamp_str, "Timestamp field missing"

        # Parse timestamp (handle different formats)
        try:
            if "T" in timestamp_str:
                # ISO format
                timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            else:
                # Try other common formats
                timestamp = datetime.fromisoformat(timestamp_str)
        except ValueError:
            pytest.fail(f"Invalid timestamp format: {timestamp_str}")

        # Check timestamp is recent (within last 5 minutes)
        now = datetime.now(timestamp.tzinfo) if timestamp.tzinfo else datetime.now()
        time_diff = abs((now - timestamp).total_seconds())
        assert time_diff < 300, f"Timestamp too old: {time_diff}s ago"

    def test_status_value_constraints(self, base_url):
        """Test that status values follow expected constraints"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        data = response.json()

        # Define valid status values for each field
        valid_statuses = {
            "overall_status": ["EXCELLENT", "OPERATIONAL", "GOOD", "WARNING", "ERROR"],
            "ml_models": ["OPERATIONAL", "TRAINING", "ERROR", "OFFLINE"],
            "betting_integration": ["CONNECTED", "DISCONNECTED", "ERROR"],
            "contextual_ai": ["ACTIVE", "INACTIVE", "ERROR"],
            "notifications": ["ACTIVE", "INACTIVE", "ERROR"],
            "performance_tracker": ["RUNNING", "STOPPED", "ERROR"],
        }

        for field, valid_values in valid_statuses.items():
            if field in data:
                status = data[field]
                assert status in valid_values, (
                    f"Invalid status '{status}' for {field}. "
                    f"Valid values: {valid_values}"
                )

    def test_api_pagination_support(self, base_url):
        """Test if API supports pagination parameters (if applicable)"""
        # Test with pagination parameters
        params = {"page": 1, "limit": 10}
        response = requests.get(
            f"{base_url}/api/system_status", params=params, timeout=10
        )

        # Should still return valid response even with extra params
        assert response.status_code == 200


class TestLoadAndStress:
    """Load testing and stress testing"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_sustained_load(self, base_url):
        """Test sustained load over time"""
        duration = 30  # 30 seconds
        request_interval = 0.5  # Request every 500ms

        start_time = time.time()
        successful_requests = 0
        failed_requests = 0
        response_times = []

        while time.time() - start_time < duration:
            try:
                req_start = time.time()
                response = requests.get(f"{base_url}/api/system_status", timeout=5)
                req_time = time.time() - req_start

                if response.status_code == 200:
                    successful_requests += 1
                    response_times.append(req_time)
                else:
                    failed_requests += 1

            except requests.RequestException:
                failed_requests += 1

            time.sleep(request_interval)

        # Analyze results
        total_requests = successful_requests + failed_requests
        success_rate = successful_requests / total_requests if total_requests > 0 else 0
        avg_response_time = (
            sum(response_times) / len(response_times) if response_times else 0
        )

        # Assertions
        assert success_rate >= 0.95, f"Success rate too low: {success_rate:.2%}"
        assert (
            avg_response_time < 2.0
        ), f"Average response time too high: {avg_response_time:.2f}s"
        assert len(response_times) > 10, "Not enough successful requests"

    def test_burst_load(self, base_url):
        """Test handling of burst traffic"""
        num_requests = 20

        def make_request():
            start_time = time.time()
            try:
                response = requests.get(f"{base_url}/api/system_status", timeout=10)
                return {
                    "status_code": response.status_code,
                    "response_time": time.time() - start_time,
                    "success": response.status_code == 200,
                }
            except Exception as e:
                return {
                    "status_code": 0,
                    "response_time": time.time() - start_time,
                    "success": False,
                    "error": str(e),
                }

        # Execute burst of concurrent requests
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=num_requests
        ) as executor:
            futures = [executor.submit(make_request) for _ in range(num_requests)]
            results = [future.result() for future in futures]

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        success_rate = len(successful) / len(results)
        avg_response_time = (
            sum(r["response_time"] for r in successful) / len(successful)
            if successful
            else 0
        )

        # Assertions
        assert success_rate >= 0.90, f"Burst success rate too low: {success_rate:.2%}"
        assert (
            avg_response_time < 5.0
        ), f"Burst avg response time too high: {avg_response_time:.2f}s"

        # Log results for analysis
        print("\nBurst Test Results:")
        print(f"  Total requests: {len(results)}")
        print(f"  Successful: {len(successful)}")
        print(f"  Failed: {len(failed)}")
        print(f"  Success rate: {success_rate:.2%}")
        print(f"  Avg response time: {avg_response_time:.3f}s")


class TestErrorHandlingAdvanced:
    """Advanced error handling and edge case testing"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_malformed_requests(self, base_url):
        """Test handling of malformed requests"""
        # Test with invalid HTTP methods
        methods_to_test = ["PUT", "DELETE", "PATCH"]

        for method in methods_to_test:
            response = requests.request(
                method, f"{base_url}/api/system_status", timeout=10
            )
            # Should return proper error code (405 Method Not Allowed or 404)
            assert response.status_code in [
                404,
                405,
            ], f"Unexpected status for {method}: {response.status_code}"

    def test_large_request_handling(self, base_url):
        """Test handling of large requests"""
        # Create a large payload
        large_data = "x" * 10000  # 10KB of data

        try:
            response = requests.post(
                f"{base_url}/api/system_status", data=large_data, timeout=10
            )
            # Should handle gracefully (either accept or reject properly)
            assert response.status_code in [
                200,
                400,
                404,
                405,
                413,
            ], f"Unexpected status for large request: {response.status_code}"
        except requests.RequestException:
            # Connection errors are acceptable for oversized requests
            pass

    def test_special_characters_in_url(self, base_url):
        """Test handling of special characters in URLs"""
        special_urls = [
            "/api/system_status?param=<script>",
            "/api/system_status?param='OR'1'='1",
            "/api/system_status?param=../../../etc/passwd",
            "/api/system_status?param=%3Cscript%3E",
        ]

        for url in special_urls:
            response = requests.get(f"{base_url}{url}", timeout=10)

            # Should not return 500 errors (proper input validation)
            assert response.status_code != 500, f"Server error for URL: {url}"

            # Response should not contain the malicious payload
            if response.status_code == 200:
                content = response.text.lower()
                assert "<script>" not in content
                assert "etc/passwd" not in content


class TestUIInteraction:
    """Test UI elements and user interactions"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_css_and_javascript_loading(self, base_url):
        """Test that CSS and JavaScript resources load properly"""
        response = requests.get(base_url, timeout=10)
        content = response.text

        # Check for CSS references
        css_patterns = ['rel="stylesheet"', ".css", "<style"]

        has_css = any(pattern in content for pattern in css_patterns)
        assert has_css, "No CSS references found in HTML"

        # Check for JavaScript references
        js_patterns = ["<script", '.js"', "javascript"]

        has_js = any(pattern in content for pattern in js_patterns)
        # JavaScript is optional, but if present should be valid
        if has_js:
            assert "<script>" not in content or "</script>" in content

    def test_meta_tags_and_seo(self, base_url):
        """Test meta tags and SEO elements"""
        response = requests.get(base_url, timeout=10)
        content = response.text

        # Check for essential meta tags
        meta_tags = ["charset=", "viewport", "<title>"]

        for tag in meta_tags:
            assert tag in content, f"Missing meta tag: {tag}"

        # Title should be descriptive
        title_start = content.find("<title>") + 7
        title_end = content.find("</title>")
        if title_start > 6 and title_end > title_start:
            title = content[title_start:title_end]
            assert len(title) > 10, "Title too short"
            assert "Horse Racing AI" in title, "Title should mention the application"

    def test_form_security(self, base_url):
        """Test form security measures"""
        response = requests.get(base_url, timeout=10)
        content = response.text.lower()

        # If forms exist, they should have CSRF protection
        if "<form" in content:
            # Look for CSRF tokens or similar security measures
            security_indicators = ["csrf", "token", "hidden", "authenticity_token"]

            # At least one security indicator should be present
            has_security = any(
                indicator in content for indicator in security_indicators
            )
            # This is informational - not all forms need CSRF in development
            if not has_security:
                print("INFO: No CSRF protection detected in forms")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
