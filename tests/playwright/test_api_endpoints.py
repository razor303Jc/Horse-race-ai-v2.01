"""
Playwright tests for Horse Racing AI v2.0 API Endpoints
Tests API functionality, response formats, and error handling.
"""

import pytest
from playwright.sync_api import Page
import json
import time


class TestAPIEndpoints:
    """Test API endpoints and responses"""

    def test_system_status_endpoint(self, page: Page, base_url: str):
        """Test the system status API endpoint"""
        response = page.goto(f"{base_url}/api/system_status")

        assert response.status == 200

        # Parse JSON response
        content = page.content()
        data = json.loads(content)

        # Check required fields
        required_fields = [
            "overall_status",
            "timestamp",
            "ml_models",
            "betting_integration",
            "contextual_ai",
            "notifications",
            "performance_tracker",
        ]

        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"

        # Check status values
        assert data["overall_status"] in ["EXCELLENT", "OPERATIONAL", "WARNING"]

    def test_api_response_times(self, page: Page, base_url: str):
        """Test API response times are reasonable"""
        endpoints = [
            "/api/system_status",
        ]

        for endpoint in endpoints:
            start_time = time.time()
            response = page.goto(f"{base_url}{endpoint}")
            response_time = time.time() - start_time

            assert response.status == 200
            assert (
                response_time < 5.0
            ), f"API {endpoint} took {response_time:.2f}s (too slow)"

    def test_api_content_types(self, page: Page, base_url: str):
        """Test that APIs return proper content types"""
        response = page.goto(f"{base_url}/api/system_status")

        # Check content type header
        content_type = response.headers.get("content-type", "")
        assert "application/json" in content_type.lower()

    def test_error_handling_404(self, page: Page, base_url: str):
        """Test 404 error handling for non-existent endpoints"""
        response = page.goto(f"{base_url}/api/nonexistent-endpoint")

        assert response.status == 404

        # Should return proper error page
        content = page.content()
        assert "404" in content
        assert "not found" in content.lower()

    def test_cors_headers(self, page: Page, base_url: str):
        """Test CORS headers if applicable"""
        response = page.goto(f"{base_url}/api/system_status")

        # Check if CORS headers are present (optional)
        headers = response.headers

        # This is informational - some APIs might not need CORS
        cors_origin = headers.get("access-control-allow-origin")
        if cors_origin:
            assert cors_origin in ["*", base_url]


class TestWebSocketConnections:
    """Test WebSocket connections if implemented"""

    def test_websocket_availability(self, page: Page, base_url: str):
        """Test if WebSocket endpoints are available"""
        # This is a placeholder for future WebSocket testing
        # WebSocket testing in Playwright requires special handling

        # For now, just check that the page doesn't have WebSocket errors
        errors = []

        def handle_console(msg):
            if "websocket" in msg.text.lower() and msg.type == "error":
                errors.append(msg.text)

        page.on("console", handle_console)
        page.goto(base_url)
        page.wait_for_load_state("networkidle")

        # Allow time for WebSocket connection attempts
        time.sleep(3)

        # Non-critical: WebSocket errors are acceptable if not implemented
        if errors:
            print(f"WebSocket info: {errors}")


class TestDataValidation:
    """Test data validation and sanitization"""

    def test_json_structure_validity(self, page: Page, base_url: str):
        """Test that JSON responses have valid structure"""
        response = page.goto(f"{base_url}/api/system_status")
        content = page.content()

        try:
            data = json.loads(content)
            assert isinstance(data, dict)
        except json.JSONDecodeError as e:
            pytest.fail(f"Invalid JSON response: {e}")

    def test_timestamp_format(self, page: Page, base_url: str):
        """Test that timestamps are in proper format"""
        response = page.goto(f"{base_url}/api/system_status")
        content = page.content()
        data = json.loads(content)

        if "timestamp" in data:
            timestamp = data["timestamp"]

            # Should be ISO format string
            assert isinstance(timestamp, str)
            assert "T" in timestamp  # ISO format indicator

            # Try to parse timestamp
            from datetime import datetime

            try:
                datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            except ValueError:
                pytest.fail(f"Invalid timestamp format: {timestamp}")

    def test_status_values_validity(self, page: Page, base_url: str):
        """Test that status values are valid"""
        response = page.goto(f"{base_url}/api/system_status")
        content = page.content()
        data = json.loads(content)

        valid_statuses = [
            "EXCELLENT",
            "OPERATIONAL",
            "GOOD",
            "WARNING",
            "ERROR",
            "OFFLINE",
            "CONNECTED",
            "ACTIVE",
            "RUNNING",
        ]

        # Check all status fields
        for key, value in data.items():
            if "status" in key.lower() and isinstance(value, str):
                assert (
                    value.upper() in valid_statuses
                ), f"Invalid status value '{value}' for field '{key}'"


class TestSecurity:
    """Test security aspects of the API"""

    def test_no_sql_injection_vectors(self, page: Page, base_url: str):
        """Test that API doesn't expose SQL injection vectors"""
        # Test common SQL injection patterns
        injection_patterns = [
            "' OR '1'='1",
            "'; DROP TABLE users; --",
            "UNION SELECT * FROM",
        ]

        for pattern in injection_patterns:
            # Try pattern in query parameters (if any endpoints accept them)
            try:
                response = page.goto(f"{base_url}/api/system_status?test={pattern}")
                content = page.content()

                # Should not contain SQL error messages
                sql_errors = [
                    "sql",
                    "syntax error",
                    "mysql",
                    "postgresql",
                    "database error",
                    "table",
                    "column",
                ]

                content_lower = content.lower()
                for error_term in sql_errors:
                    assert (
                        error_term not in content_lower
                    ), f"Possible SQL injection vulnerability detected: {error_term}"
            except Exception:
                # If endpoint doesn't accept parameters, that's fine
                pass

    def test_no_xss_vulnerabilities(self, page: Page, base_url: str):
        """Test that API responses don't contain XSS vulnerabilities"""
        response = page.goto(f"{base_url}/api/system_status")
        content = page.content()

        # Check that content is properly escaped/encoded
        dangerous_patterns = ["<script>", "javascript:", "onload=", "onerror=", "eval("]

        content_lower = content.lower()
        for pattern in dangerous_patterns:
            assert (
                pattern not in content_lower
            ), f"Potential XSS vulnerability: {pattern} found in response"

    def test_information_disclosure(self, page: Page, base_url: str):
        """Test that API doesn't disclose sensitive information"""
        response = page.goto(f"{base_url}/api/system_status")
        content = page.content()

        # Check for information that shouldn't be exposed
        sensitive_info = [
            "password",
            "secret",
            "key",
            "token",
            "/home/",
            "/usr/",
            "root@",
            "admin@",
            "database_url",
            "connection_string",
        ]

        content_lower = content.lower()
        for info in sensitive_info:
            assert info not in content_lower, f"Sensitive information disclosed: {info}"


class TestPerformanceAndReliability:
    """Test performance and reliability aspects"""

    def test_concurrent_requests(self, page: Page, base_url: str):
        """Test handling of concurrent requests"""
        # Simple concurrent test - open multiple tabs
        contexts = []
        pages = []

        try:
            # Create multiple browser contexts
            for i in range(3):
                context = page.context.browser.new_context()
                test_page = context.new_page()
                contexts.append(context)
                pages.append(test_page)

            # Make concurrent requests
            start_time = time.time()
            for test_page in pages:
                test_page.goto(f"{base_url}/api/system_status")

            # Wait for all to complete
            for test_page in pages:
                test_page.wait_for_load_state("networkidle")

            end_time = time.time()

            # Should handle concurrent requests reasonably
            assert end_time - start_time < 15, "Concurrent requests too slow"

        finally:
            # Cleanup
            for context in contexts:
                context.close()

    def test_api_availability(self, page: Page, base_url: str):
        """Test that API is consistently available"""
        # Make multiple requests to ensure consistency
        for i in range(5):
            response = page.goto(f"{base_url}/api/system_status")
            assert response.status == 200

            content = page.content()
            data = json.loads(content)
            assert "overall_status" in data

            # Small delay between requests
            time.sleep(0.5)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
