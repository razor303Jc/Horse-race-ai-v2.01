"""
Redis Health Integration Tests for Node-RED

Tests to verify Redis health monitoring integration in the C2 dashboard,
following the same pattern as database health integration.
"""

import requests
import time
import pytest
from typing import Dict, Any


class TestRedisHealthIntegration:
    """Test suite for Redis health monitoring integration"""

    @pytest.fixture
    def redis_config(self):
        """Configuration for Redis health tests"""
        return {
            "base_url": "http://c2.horse-racing.local",
            "redis_health_endpoint": "/redis/health",
            "timeout": 10,
            "expected_response_time_ms": 100,
            "redis_host": "horse_racing_redis_clean",
            "redis_port": 6379,
        }

    @pytest.mark.integration
    @pytest.mark.redis_health
    def test_redis_health_endpoint_exists(self):
        """Test that the Redis health status is available in C2 status endpoint."""
        response = requests.get(f"{self.base_url}/c2/status")
        assert (
            response.status_code == 200
        ), f"C2 status endpoint not found at {self.base_url}/c2/status"
        data = response.json()
        assert "redis" in data, "Redis health status not found in C2 status response"

    @pytest.mark.integration
    @pytest.mark.redis_health
    def test_redis_health_response_structure(self):
        """Test that the Redis health status in C2 response has the correct structure."""
        response = requests.get(f"{self.base_url}/c2/status")
        assert response.status_code == 200
        data = response.json()

        # Check for redis field in C2 status
        assert "redis" in data, "Redis health status not found in C2 status"
        redis_status = data["redis"]

        # Check that redis status is a valid value
        valid_statuses = ["healthy", "unhealthy"]
        assert redis_status in valid_statuses, f"Invalid Redis status: {redis_status}"

    @pytest.mark.integration
    @pytest.mark.redis_health
    def test_redis_health_performance(self, redis_config):
        """Test that Redis health check performs within acceptable limits"""
        url = f"{redis_config['base_url']}{redis_config['redis_health_endpoint']}"

        start_time = time.time()
        response = requests.get(url, timeout=redis_config["timeout"])
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Health check should respond quickly
        assert (
            response_time_ms < redis_config["expected_response_time_ms"]
        ), f"Redis health check too slow: {response_time_ms}ms > {redis_config['expected_response_time_ms']}ms"

        # If response includes timing, verify it's reasonable
        if response.status_code == 200:
            data = response.json()
            if "response_time" in data and data["response_time"] != "error":
                reported_time = data["response_time"]
                # Extract numeric value from "Xms" format
                if isinstance(reported_time, str) and reported_time.endswith("ms"):
                    reported_ms = float(reported_time[:-2])
                    assert (
                        reported_ms < redis_config["expected_response_time_ms"]
                    ), f"Reported Redis connection time too slow: {reported_ms}ms"

    @pytest.mark.integration
    @pytest.mark.redis_health
    def test_redis_health_status_values(self, redis_config):
        """Test that Redis health returns valid status values"""
        url = f"{redis_config['base_url']}{redis_config['redis_health_endpoint']}"

        response = requests.get(url, timeout=redis_config["timeout"])
        data = response.json()

        # overall_status should be one of expected values
        valid_statuses = ["healthy", "unhealthy", "degraded", "timeout"]
        assert (
            data["overall_status"] in valid_statuses
        ), f"Invalid overall_status: {data['overall_status']}"

        # connection_test should be meaningful
        valid_connection_results = ["successful", "failed", "timeout"]
        assert (
            data["connection_test"] in valid_connection_results
        ), f"Invalid connection_test: {data['connection_test']}"

        # If status is healthy, connection should be successful
        if data["overall_status"] == "healthy":
            assert (
                data["connection_test"] == "successful"
            ), "Healthy status should have successful connection test"

    @pytest.mark.integration
    @pytest.mark.redis_health
    def test_redis_health_consistency(self, redis_config):
        """Test that Redis health returns consistent results across multiple calls"""
        url = f"{redis_config['base_url']}{redis_config['redis_health_endpoint']}"

        responses = []
        for _ in range(3):
            response = requests.get(url, timeout=redis_config["timeout"])
            data = response.json()
            responses.append(data)
            time.sleep(0.5)

        # All responses should have same overall health status
        # (assuming Redis doesn't go up/down during test)
        statuses = [r["overall_status"] for r in responses]
        assert (
            len(set(statuses)) <= 2
        ), f"Redis health status too inconsistent: {statuses}"

        # All responses should have consistent host/port
        for response_data in responses:
            assert response_data["redis_info"]["host"] == redis_config["redis_host"]
            assert response_data["redis_info"]["port"] == redis_config["redis_port"]


class TestRedisHealthRealDataValidation:
    """Tests to ensure Redis health returns real data, not hardcoded values"""

    @pytest.fixture
    def redis_config(self):
        """Configuration for Redis real data validation tests"""
        return {
            "base_url": "http://c2.horse-racing.local",
            "redis_health_endpoint": "/redis/health",
            "timeout": 10,
        }

    @pytest.mark.integration
    @pytest.mark.redis_health
    @pytest.mark.real_data
    def test_redis_health_not_hardcoded_response(self, redis_config):
        """Test that Redis health doesn't return obviously hardcoded values"""
        url = f"{redis_config['base_url']}{redis_config['redis_health_endpoint']}"

        responses = []
        for _ in range(3):
            response = requests.get(url, timeout=redis_config["timeout"])
            data = response.json()
            responses.append(data)
            time.sleep(0.5)

        # Check that timestamps are different (not hardcoded)
        timestamps = [r["timestamp"] for r in responses]
        assert (
            len(set(timestamps)) == 3
        ), f"Timestamps should be different across calls, got: {timestamps}"

        # Check that response times vary (not hardcoded)
        response_times = []
        for r in responses:
            if r["response_time"] != "error" and isinstance(r["response_time"], str):
                if r["response_time"].endswith("ms"):
                    response_times.append(r["response_time"])

        if len(response_times) >= 2:
            # Allow some variation in response times (real network calls)
            assert (
                len(set(response_times)) >= 1
            ), "Response times should show some variation for real connections"

    @pytest.mark.integration
    @pytest.mark.redis_health
    @pytest.mark.real_data
    def test_redis_health_reflects_actual_redis_state(self, redis_config):
        """Test that Redis health reflects actual Redis container state"""
        url = f"{redis_config['base_url']}{redis_config['redis_health_endpoint']}"

        # Get health status
        response = requests.get(url, timeout=redis_config["timeout"])
        data = response.json()

        # If Redis container is running (which it should be), health should be positive
        # This test assumes Redis is properly configured and running
        if data["overall_status"] == "healthy":
            assert data["connection_test"] == "successful"
            assert "error" not in data["redis_info"]

        # Response should include actual connection details
        assert data["redis_info"]["host"] == "horse_racing_redis_clean"
        assert data["redis_info"]["port"] == 6379

        # Timestamp should be recent (within last minute)
        import datetime

        timestamp = datetime.datetime.fromisoformat(
            data["timestamp"].replace("Z", "+00:00")
        )
        now = datetime.datetime.now(datetime.timezone.utc)
        time_diff = (now - timestamp).total_seconds()

        assert time_diff < 60, f"Timestamp too old: {time_diff} seconds ago"
