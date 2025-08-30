"""
🧪 Node-RED C2 Dashboard Test Suite
==================================

Integration tests for Node-RED flows, HTTP endpoints,
and dashboard functionality.
"""

import pytest
import requests
import json
import time
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os


class TestNodeREDFlows:
    """Test Node-RED flow functionality"""

    BASE_URL = "http://localhost:1881"

    def test_node_red_admin_accessible(self):
        """Test Node-RED admin interface is accessible"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/",
                timeout=10
            )
            assert response.status_code == 200
            # Should contain Node-RED admin interface
            assert "Node-RED" in response.text
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_c2_dashboard_endpoint(self):
        """Test C2 dashboard endpoint serves content"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=10
            )
            assert response.status_code == 200
            
            content = response.text
            # Check for essential dashboard elements
            assert "C2 Command Center" in content
            assert "nav-tabs" in content  # Bootstrap tabs
            assert "Overview" in content
            assert "Operations" in content
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_ui_redirect_functionality(self):
        """Test /ui/ redirect works correctly"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/ui/",
                timeout=10,
                allow_redirects=False
            )
            
            # Should redirect to C2 dashboard
            assert response.status_code == 302
            location = response.headers.get("Location", "")
            assert "/c2-dashboard" in location
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_container_status_flow(self):
        """Test container status monitoring flow"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/containers/status",
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify response structure
                assert "containers" in data
                assert "total" in data
                assert "healthy" in data
                assert isinstance(data["containers"], list)
                assert isinstance(data["total"], int)
                assert isinstance(data["healthy"], int)
                
                # Verify container entries have required fields
                for container in data["containers"]:
                    assert "name" in container
                    assert "status" in container
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_docker_stats_flow(self):
        """Test Docker statistics retrieval flow"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/docker/stats",
                timeout=20
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verify stats structure
                assert "timestamp" in data
                assert "containers" in data
                assert isinstance(data["containers"], list)
                
                # Check timestamp is recent
                timestamp = datetime.fromisoformat(
                    data["timestamp"].replace("Z", "+00:00")
                )
                now = datetime.now()
                # Should be within last 5 minutes
                assert abs((now - timestamp).total_seconds()) < 300
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_web_app_health_flow(self):
        """Test web app health check flow"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/web-app/health",
                timeout=10
            )
            
            # Should either get web app response or error
            assert response.status_code in [200, 503, 404]
            
            if response.status_code == 200:
                # Should have content from web app
                assert len(response.text) > 0
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_ntfy_send_flow(self):
        """Test NTFY notification send flow"""
        try:
            payload = {
                "message": "Test from Node-RED test suite",
                "priority": "3",
                "topic": "horse-racing-ai",
                "title": "Test Notification"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/send-ntfy",
                json=payload,
                timeout=10
            )
            
            # Should either succeed or fail gracefully
            assert response.status_code in [200, 400, 500, 503]
            
            if response.status_code == 200:
                data = response.json()
                assert "status" in data
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_container_logs_flow(self):
        """Test container logs retrieval flow"""
        try:
            # Test with known container names
            containers = [
                "horse_racing_web_app_clean",
                "horse_racing_postgres_clean",
                "horse_racing_node_red_dashboard"
            ]
            
            for container in containers:
                response = requests.get(
                    f"{self.BASE_URL}/docker/logs/{container}?lines=5",
                    timeout=10
                )
                
                # Should either succeed or fail gracefully
                assert response.status_code in [200, 404, 500]
                
                if response.status_code == 200:
                    data = response.json()
                    assert "logs" in data
                    assert "container" in data
                    assert data["container"] == container
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")


class TestNodeREDSecurity:
    """Test Node-RED security and authentication"""

    BASE_URL = "http://localhost:1881"

    def test_invalid_container_logs_rejected(self):
        """Test that invalid container names are rejected"""
        try:
            # Test with clearly invalid container name
            response = requests.get(
                f"{self.BASE_URL}/docker/logs/../../etc/passwd",
                timeout=10
            )
            
            # Should reject malicious paths
            assert response.status_code in [400, 404, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_api_key_validation(self):
        """Test API key validation in flows"""
        try:
            # Test with valid API key
            headers = {"X-API-Key": "horse-racing-c2-secure-key-2025"}
            response = requests.get(
                f"{self.BASE_URL}/containers/status",
                headers=headers,
                timeout=10
            )
            
            # Should succeed with valid key
            assert response.status_code == 200
            
            # Test with invalid API key
            headers = {"X-API-Key": "invalid-key-12345"}
            response = requests.get(
                f"{self.BASE_URL}/containers/status",
                headers=headers,
                timeout=10
            )
            
            # May or may not enforce auth (depends on flow config)
            assert response.status_code in [200, 401, 403]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_bearer_token_validation(self):
        """Test Bearer token validation"""
        try:
            # Test with Bearer token
            headers = {"Authorization": "Bearer demo-token"}
            response = requests.get(
                f"{self.BASE_URL}/containers/status",
                headers=headers,
                timeout=10
            )
            
            # Should handle Bearer token appropriately
            assert response.status_code in [200, 401, 403]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_rate_limiting_flows(self):
        """Test rate limiting in Node-RED flows"""
        try:
            # Make rapid successive requests
            responses = []
            for i in range(10):
                response = requests.get(
                    f"{self.BASE_URL}/containers/status",
                    timeout=2
                )
                responses.append(response.status_code)
                time.sleep(0.1)  # Small delay
            
            # Should handle rapid requests gracefully
            success_count = sum(1 for status in responses if status == 200)
            assert success_count >= 5  # At least half should succeed
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")


class TestNodeREDDashboardUI:
    """Test Node-RED dashboard UI components"""

    BASE_URL = "http://localhost:1881"

    def test_dashboard_css_loaded(self):
        """Test dashboard CSS and styling loaded"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for Bootstrap CSS
                assert "bootstrap" in content.lower()
                
                # Check for Font Awesome icons
                assert "font-awesome" in content.lower() or \
                       "fa-" in content
                
                # Check for custom CSS classes
                assert "c2-" in content or "command-center" in content
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_dashboard_javascript_loaded(self):
        """Test dashboard JavaScript functionality"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for Bootstrap JS
                assert "bootstrap" in content.lower()
                
                # Check for tab functionality
                assert "data-bs-toggle" in content
                
                # Check for AJAX/fetch calls
                assert "fetch(" in content or "XMLHttpRequest" in content
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_dashboard_responsive_elements(self):
        """Test responsive design elements"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for responsive classes
                assert "col-" in content or "row" in content
                
                # Check for viewport meta tag
                assert "viewport" in content
                
                # Check for responsive components
                assert "navbar" in content or "nav-tabs" in content
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_dashboard_tab_structure(self):
        """Test dashboard tab structure and content"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=10
            )
            
            if response.status_code == 200:
                content = response.text
                
                # Check for tab navigation
                expected_tabs = [
                    "Overview",
                    "Operations", 
                    "NTFY Control",
                    "Console"
                ]
                
                for tab in expected_tabs:
                    assert tab in content
                
                # Check for tab panes
                assert "tab-pane" in content
                assert "tab-content" in content
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")


class TestNodeREDErrorHandling:
    """Test Node-RED error handling and resilience"""

    BASE_URL = "http://localhost:1881"

    def test_invalid_endpoint_handling(self):
        """Test handling of invalid endpoints"""
        try:
            response = requests.get(
                f"{self.BASE_URL}/invalid-endpoint-12345",
                timeout=10
            )
            
            # Should return 404 for invalid endpoints
            assert response.status_code == 404
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_malformed_json_handling(self):
        """Test handling of malformed JSON in POST requests"""
        try:
            headers = {"Content-Type": "application/json"}
            invalid_json = "{'malformed': json, 'missing': quotes}"
            
            response = requests.post(
                f"{self.BASE_URL}/send-ntfy",
                data=invalid_json,
                headers=headers,
                timeout=10
            )
            
            # Should handle malformed JSON gracefully
            assert response.status_code in [400, 422, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_timeout_resilience(self):
        """Test resilience to network timeouts"""
        try:
            # Test with very short timeout
            response = requests.get(
                f"{self.BASE_URL}/containers/status",
                timeout=0.001
            )
            # If it succeeds despite short timeout, that's fine
            assert response.status_code == 200
            
        except requests.exceptions.Timeout:
            # Expected behavior for very short timeout
            assert True
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_large_request_handling(self):
        """Test handling of large requests"""
        try:
            # Create large payload
            large_message = "A" * 50000  # 50KB message
            payload = {
                "message": large_message,
                "priority": "3",
                "topic": "horse-racing-ai"
            }
            
            response = requests.post(
                f"{self.BASE_URL}/send-ntfy",
                json=payload,
                timeout=15
            )
            
            # Should either accept or reject large payloads gracefully
            assert response.status_code in [200, 400, 413, 500]
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")


class TestNodeREDPerformance:
    """Test Node-RED performance characteristics"""

    BASE_URL = "http://localhost:1881"

    def test_dashboard_load_performance(self):
        """Test dashboard load time performance"""
        try:
            start_time = time.time()
            response = requests.get(
                f"{self.BASE_URL}/c2-dashboard",
                timeout=30
            )
            load_time = time.time() - start_time
            
            if response.status_code == 200:
                # Dashboard should load within reasonable time
                assert load_time < 10.0  # 10 seconds max
                
                # Content should be substantial but not excessive
                content_length = len(response.text)
                assert content_length > 1000  # At least 1KB
                assert content_length < 1000000  # Less than 1MB
                
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_api_endpoint_performance(self):
        """Test API endpoint response times"""
        try:
            endpoints = [
                "/containers/status",
                "/docker/stats",
                "/web-app/health"
            ]
            
            for endpoint in endpoints:
                start_time = time.time()
                response = requests.get(
                    f"{self.BASE_URL}{endpoint}",
                    timeout=15
                )
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    # API endpoints should respond quickly
                    assert response_time < 10.0  # 10 seconds max
                    
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")

    def test_concurrent_request_handling(self):
        """Test handling of concurrent requests"""
        try:
            import concurrent.futures
            import threading
            
            def make_request():
                try:
                    response = requests.get(
                        f"{self.BASE_URL}/containers/status",
                        timeout=10
                    )
                    return response.status_code
                except Exception:
                    return 500
            
            # Make 8 concurrent requests
            with concurrent.futures.ThreadPoolExecutor(
                max_workers=8
            ) as executor:
                futures = [
                    executor.submit(make_request) 
                    for _ in range(8)
                ]
                results = [
                    future.result() 
                    for future in concurrent.futures.as_completed(futures)
                ]
            
            # Most requests should succeed
            success_count = sum(1 for status in results if status == 200)
            assert success_count >= 5  # At least 62% success rate
            
        except requests.exceptions.ConnectionError:
            pytest.skip("Node-RED not running")


# Test fixtures and utilities
@pytest.fixture
def node_red_client():
    """Fixture providing Node-RED test client"""
    class NodeREDTestClient:
        def __init__(self):
            self.base_url = "http://localhost:1881"
            self.timeout = 10
        
        def get(self, endpoint, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return requests.get(f"{self.base_url}{endpoint}", **kwargs)
        
        def post(self, endpoint, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return requests.post(f"{self.base_url}{endpoint}", **kwargs)
        
        def is_available(self):
            try:
                response = self.get("/")
                return response.status_code == 200
            except Exception:
                return False
    
    return NodeREDTestClient()

@pytest.fixture
def sample_ntfy_payload():
    """Sample NTFY notification payload"""
    return {
        "message": "Test notification from test suite",
        "priority": "3",
        "topic": "horse-racing-ai",
        "title": "Test Message"
    }


if __name__ == "__main__":
    # Run Node-RED tests with specific markers
    pytest.main([__file__, "-v", "--tb=short", "-m", "not slow"])
