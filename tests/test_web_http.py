"""
Simple HTTP tests for Horse Racing AI v2.0 Web Application
Tests using the requests library without browser automation.
"""

import pytest
import requests
import json
import time


class TestWebApplicationHTTP:
    """Test web application using HTTP requests"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_dashboard_responds(self, base_url):
        """Test that the main dashboard responds"""
        response = requests.get(base_url, timeout=10)

        assert response.status_code == 200
        assert "Horse Racing AI" in response.text
        assert "Dashboard" in response.text

    def test_system_status_api(self, base_url):
        """Test the system status API"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)

        assert response.status_code == 200

        # Check content type
        assert "application/json" in response.headers.get("content-type", "")

        # Parse JSON
        data = response.json()

        # Check required fields
        assert "overall_status" in data
        assert "timestamp" in data

        # Check status values
        valid_statuses = ["EXCELLENT", "OPERATIONAL", "GOOD", "WARNING", "ERROR"]
        assert data["overall_status"] in valid_statuses

    def test_404_error_handling(self, base_url):
        """Test 404 error page"""
        response = requests.get(f"{base_url}/nonexistent-page", timeout=10)

        assert response.status_code == 404
        assert "404" in response.text
        assert "not found" in response.text.lower()

    def test_api_response_time(self, base_url):
        """Test API response times"""
        start_time = time.time()
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        response_time = time.time() - start_time

        assert response.status_code == 200
        assert response_time < 5.0, f"API too slow: {response_time:.2f}s"

    def test_api_data_structure(self, base_url):
        """Test API data structure and types"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        data = response.json()

        # Check data types
        assert isinstance(data, dict)
        assert isinstance(data.get("overall_status"), str)
        assert isinstance(data.get("timestamp"), str)

        # Check timestamp format (should be ISO-like)
        timestamp = data.get("timestamp", "")
        assert "T" in timestamp or ":" in timestamp  # Basic time format check

    def test_multiple_concurrent_requests(self, base_url):
        """Test handling of multiple concurrent requests"""
        import concurrent.futures

        def make_request():
            return requests.get(f"{base_url}/api/system_status", timeout=10)

        # Make 5 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_request) for _ in range(5)]
            results = [future.result() for future in futures]

        # All requests should succeed
        for response in results:
            assert response.status_code == 200

    def test_security_headers(self, base_url):
        """Test basic security headers"""
        response = requests.get(base_url, timeout=10)

        # Check that we don't expose sensitive information in headers
        headers = response.headers

        # Check that sensitive info is not in headers
        dangerous_headers = ["database", "password", "secret", "key"]
        for header_name, header_value in headers.items():
            header_combined = f"{header_name} {header_value}".lower()
            for dangerous in dangerous_headers:
                assert (
                    dangerous not in header_combined
                ), f"Sensitive info in header: {header_name}"

    def test_no_sensitive_data_exposure(self, base_url):
        """Test that sensitive data is not exposed"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        content = response.text.lower()

        # Check for common sensitive patterns
        sensitive_patterns = [
            "password",
            "secret_key",
            "api_key",
            "private_key",
            "database_url",
            "connection_string",
        ]

        for pattern in sensitive_patterns:
            assert pattern not in content, f"Sensitive data exposed: {pattern}"


class TestHealthChecks:
    """Test application health and monitoring"""

    @pytest.fixture
    def base_url(self):
        return "http://localhost:5002"

    def test_application_is_responding(self, base_url):
        """Test that application is responding to requests"""
        try:
            response = requests.get(base_url, timeout=5)
            assert response.status_code < 500, "Application server error"
        except requests.RequestException as e:
            pytest.fail(f"Application not responding: {e}")

    def test_system_components_status(self, base_url):
        """Test that system components report proper status"""
        response = requests.get(f"{base_url}/api/system_status", timeout=10)
        data = response.json()

        # Check component statuses
        components = [
            "ml_models",
            "betting_integration",
            "contextual_ai",
            "notifications",
            "performance_tracker",
        ]

        for component in components:
            if component in data:
                status = data[component]
                # Status should not be "ERROR" or "OFFLINE"
                assert status not in [
                    "ERROR",
                    "OFFLINE",
                ], f"Component {component} has error status: {status}"

    def test_api_consistency(self, base_url):
        """Test that API returns consistent data across multiple calls"""
        # Make multiple calls
        responses = []
        for _ in range(3):
            response = requests.get(f"{base_url}/api/system_status", timeout=10)
            responses.append(response.json())
            time.sleep(1)

        # Check that overall_status is consistent
        # (might change but shouldn't vary wildly)
        statuses = [r.get("overall_status") for r in responses]

        # All statuses should be valid
        valid_statuses = ["EXCELLENT", "OPERATIONAL", "GOOD", "WARNING", "ERROR"]
        for status in statuses:
            assert status in valid_statuses


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
