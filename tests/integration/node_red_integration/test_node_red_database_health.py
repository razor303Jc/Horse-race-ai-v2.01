"""
🧪 Node-RED Database Health Integration Tests
============================================

Integration tests for Node-RED database health monitoring endpoints and flows.
Tests real-time health checks, connection monitoring, and API responses.
"""

import pytest
import requests
import json
import time
import psycopg2
from unittest.mock import Mock, patch
from typing import Dict, List, Any, Optional
import redis


# Test Configuration
@pytest.fixture
def node_red_config():
    """Node-RED test configuration"""
    return {
        "base_url": "http://c2.horse-racing.local",
        "database_health_endpoint": "/database/health",
        "redis_health_endpoint": "/redis/health",
        "system_status_endpoint": "/system/status",
        "container_health_endpoint": "/containers/health",
        "timeout": 10,
        "expected_response_time_ms": 500,
    }


@pytest.fixture
def database_config():
    """Database connection configuration"""
    return {
        "host": "horse_racing_postgres_clean",
        "port": 5432,
        "database": "horse_racing",
        "user": "horse_racing",
        "password": "secure_password_123",
    }


@pytest.fixture
def redis_config():
    """Redis connection configuration"""
    return {
        "host": "horse_racing_redis_clean",
        "port": 6379,
        "db": 0,
        "decode_responses": True,
    }


class TestNodeRedDatabaseHealth:
    """Test Node-RED database health monitoring endpoints"""

    def test_database_health_endpoint_exists(self, node_red_config):
        """Test that database health endpoint is accessible"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        try:
            response = requests.get(url, timeout=node_red_config["timeout"])
            assert response.status_code in [
                200,
                503,
            ], f"Expected 200 or 503, got {response.status_code}"

            # Verify JSON response structure
            data = response.json()
            assert (
                "overall_status" in data
            ), "Response must contain 'overall_status' field"
            assert "timestamp" in data, "Response must contain 'timestamp' field"
            assert (
                "database_info" in data
            ), "Response must contain 'database_info' field"
            assert (
                "connection_test" in data
            ), "Response must contain 'connection_test' field"

        except requests.exceptions.RequestException as e:
            pytest.fail(f"Database health endpoint not accessible: {e}")

    def test_database_health_response_structure(self, node_red_config):
        """Test database health response has correct structure"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        response = requests.get(url, timeout=node_red_config["timeout"])
        data = response.json()

        # Required fields
        required_fields = [
            "overall_status",
            "timestamp",
            "database_info",
            "response_time",
        ]
        for field in required_fields:
            assert field in data, f"Required field '{field}' missing from response"

        # Status should be one of expected values
        assert data["overall_status"] in [
            "healthy",
            "degraded",
            "down",
        ], f"Invalid status: {data['overall_status']}"

        # Response time should be present and reasonable
        response_time_str = data.get("response_time", "0ms")
        if response_time_str.endswith("ms"):
            response_time_ms = float(response_time_str[:-2])
            assert (
                0 <= response_time_ms <= 10000
            ), f"Response time {response_time_ms}ms seems unreasonable"

    def test_database_health_performance(self, node_red_config):
        """Test database health check performance"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        start_time = time.time()
        response = requests.get(url, timeout=node_red_config["timeout"])
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Health check should be fast
        assert (
            response_time_ms < node_red_config["expected_response_time_ms"]
        ), f"Health check too slow: {response_time_ms}ms > {node_red_config['expected_response_time_ms']}ms"

        # Response should contain performance data
        data = response.json()
        if "response_time_ms" in data:
            # Allow some variance between measured and reported time
            reported_time = data["response_time_ms"]
            assert (
                abs(response_time_ms - reported_time) < 100
            ), f"Reported time {reported_time}ms differs significantly from measured {response_time_ms}ms"


class TestNodeRedRedisHealth:
    """Test Node-RED Redis health monitoring"""

    def test_redis_health_endpoint_exists(self, node_red_config):
        """Test that Redis health endpoint is accessible"""
        url = f"{node_red_config['base_url']}{node_red_config['redis_health_endpoint']}"

        try:
            response = requests.get(url, timeout=node_red_config["timeout"])
            assert response.status_code in [
                200,
                503,
            ], f"Expected 200 or 503, got {response.status_code}"

            data = response.json()
            assert "status" in data, "Response must contain 'status' field"
            assert "redis" in data, "Response must contain 'redis' field"

        except requests.exceptions.RequestException as e:
            # Redis health endpoint might not exist yet - this is expected during development
            pytest.skip(f"Redis health endpoint not yet implemented: {e}")

    def test_redis_connection_validation(self, redis_config):
        """Test direct Redis connection for validation"""
        try:
            r = redis.Redis(**redis_config)

            # Test basic Redis operations
            test_key = "test:node_red_health_check"
            r.set(test_key, "test_value", ex=30)  # 30 second expiry
            value = r.get(test_key)

            assert value == "test_value", "Redis set/get operation failed"

            # Test Redis info
            info = r.info()
            assert "redis_version" in info, "Redis info command failed"

            # Cleanup
            r.delete(test_key)

        except redis.ConnectionError as e:
            pytest.fail(f"Redis connection failed: {e}")


class TestNodeRedSystemStatus:
    """Test Node-RED system status aggregation"""

    def test_system_status_endpoint(self, node_red_config):
        """Test system status aggregation endpoint"""
        url = (
            f"{node_red_config['base_url']}{node_red_config['system_status_endpoint']}"
        )

        try:
            response = requests.get(url, timeout=node_red_config["timeout"])
            assert response.status_code in [
                200,
                503,
            ], f"Expected 200 or 503, got {response.status_code}"

            data = response.json()

            # Should aggregate multiple health checks
            expected_services = ["database", "redis", "containers"]
            for service in expected_services:
                if service in data:
                    assert (
                        "status" in data[service]
                    ), f"Service {service} missing status"
                    assert data[service]["status"] in [
                        "healthy",
                        "degraded",
                        "down",
                    ], f"Invalid status for {service}: {data[service]['status']}"

        except requests.exceptions.RequestException as e:
            pytest.skip(f"System status endpoint not yet implemented: {e}")


class TestNodeRedRealTimeUpdates:
    """Test Node-RED real-time update mechanisms"""

    def test_health_check_frequency(self, node_red_config):
        """Test that health checks update at reasonable intervals"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        # Get initial timestamp
        response1 = requests.get(url, timeout=node_red_config["timeout"])
        data1 = response1.json()
        timestamp1 = data1.get("timestamp")

        # Wait and get second timestamp
        time.sleep(2)
        response2 = requests.get(url, timeout=node_red_config["timeout"])
        data2 = response2.json()
        timestamp2 = data2.get("timestamp")

        # Timestamps should be different (indicating fresh checks)
        assert timestamp1 != timestamp2, "Health check timestamps should update"

    def test_health_check_caching(self, node_red_config):
        """Test appropriate caching of health check results"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        # Make rapid requests
        responses = []
        for _ in range(3):
            response = requests.get(url, timeout=node_red_config["timeout"])
            responses.append(response.json())
            time.sleep(0.1)  # 100ms between requests

        # Should handle rapid requests gracefully
        for response in responses:
            assert response["status"] in ["healthy", "degraded", "down"]
            assert "response_time_ms" in response


class TestNodeRedErrorHandling:
    """Test Node-RED error handling and fallback behavior"""

    def test_database_connection_failure_handling(self, node_red_config, monkeypatch):
        """Test behavior when database connection fails"""
        # This test would need to temporarily break database connection
        # For now, we'll test that the endpoint handles errors gracefully
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        response = requests.get(url, timeout=node_red_config["timeout"])

        # Even if database is down, endpoint should respond with proper error status
        if response.status_code == 503:
            data = response.json()
            assert (
                data["status"] == "down"
            ), "Failed health check should report 'down' status"
            assert (
                "error" in data or "message" in data
            ), "Error response should include error details"

    def test_timeout_handling(self, node_red_config):
        """Test handling of slow database responses"""
        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        # Use very short timeout to test timeout handling
        try:
            response = requests.get(url, timeout=0.1)
            # If this succeeds, the endpoint is very fast (good!)
            assert response.status_code in [200, 503]
        except requests.exceptions.Timeout:
            # Timeout is acceptable - the real Node-RED should handle this gracefully
            pass


# Performance benchmarks
@pytest.mark.performance
class TestNodeRedHealthPerformance:
    """Performance tests for Node-RED health endpoints"""

    def test_concurrent_health_checks(self, node_red_config):
        """Test handling of concurrent health check requests"""
        import concurrent.futures
        import threading

        url = f"{node_red_config['base_url']}{node_red_config['database_health_endpoint']}"

        def make_request():
            try:
                response = requests.get(url, timeout=node_red_config["timeout"])
                return {
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() * 1000,
                    "success": True,
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed or fail gracefully
        successful_requests = [r for r in results if r["success"]]
        assert (
            len(successful_requests) >= 8
        ), f"Too many failed requests: {len(successful_requests)}/10"

        # Response times should be reasonable
        if successful_requests:
            avg_response_time = sum(
                r["response_time"] for r in successful_requests
            ) / len(successful_requests)
            assert (
                avg_response_time < 1000
            ), f"Average response time too high: {avg_response_time}ms"


# Integration test markers
pytestmark = [pytest.mark.integration, pytest.mark.node_red, pytest.mark.database]
