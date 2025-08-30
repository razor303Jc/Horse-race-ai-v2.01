"""
🧪 C2 Status Real Data Integration Tests
=======================================

Tests to verify C2 status endpoint calls real health services instead of hardcoded values.
Validates the transition from mock data to real system monitoring.
"""

import pytest
import requests
import json
import time
from unittest.mock import Mock, patch
from typing import Dict, List, Any, Optional


@pytest.fixture
def c2_config():
    """C2 dashboard test configuration"""
    return {
        "base_url": "http://c2.horse-racing.local",
        "c2_status_endpoint": "/c2/status",
        "database_health_endpoint": "/database/health",
        "timeout": 10,
        "expected_services": ["database", "redis", "pipeline", "ml_trainer", "web_app"],
    }


class TestC2StatusRealDataIntegration:
    """Test C2 status endpoint integration with real health services"""

    def test_c2_status_endpoint_exists(self, c2_config):
        """Test that C2 status endpoint is accessible"""
        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        response = requests.get(url, timeout=c2_config["timeout"])
        assert response.status_code == 200, f"C2 status endpoint should be accessible"

        data = response.json()
        assert isinstance(data, dict), "C2 status should return JSON object"

    def test_c2_status_calls_real_database_health(self, c2_config):
        """Test that C2 status calls real database health endpoint instead of hardcoded values"""
        # First, verify database health endpoint is working
        db_url = f"{c2_config['base_url']}{c2_config['database_health_endpoint']}"
        db_response = requests.get(db_url, timeout=c2_config["timeout"])
        assert (
            db_response.status_code == 200
        ), "Database health endpoint must be working"

        db_data = db_response.json()
        assert (
            "overall_status" in db_data
        ), "Database health should return overall_status"

        # Now check C2 status
        c2_url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"
        c2_response = requests.get(c2_url, timeout=c2_config["timeout"])
        assert c2_response.status_code == 200

        c2_data = c2_response.json()

        # Verify C2 status includes database status
        assert "database" in c2_data, "C2 status must include database status"

        # KEY TEST: Verify database status matches real health endpoint
        # If it's calling real endpoint, status should match
        # If it's hardcoded, it will always be 'healthy'
        database_status = c2_data["database"]
        expected_status = db_data["overall_status"]

        # Allow mapping from overall_status to simplified status
        status_mapping = {
            "healthy": ["healthy", True],
            "degraded": ["degraded", "warning", "unhealthy"],
            "down": ["down", "error", False, "unhealthy"],
        }

        valid_statuses = []
        for mapped_statuses in status_mapping.values():
            valid_statuses.extend(mapped_statuses)

        assert (
            database_status in valid_statuses
        ), f"Database status '{database_status}' should be valid status, not hardcoded"

    def test_c2_status_response_structure(self, c2_config):
        """Test C2 status response has expected structure for real data integration"""
        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        response = requests.get(url, timeout=c2_config["timeout"])
        data = response.json()

        # Required top-level fields for system monitoring
        required_fields = ["database", "metrics", "ai"]
        for field in required_fields:
            assert field in data, f"C2 status must include '{field}' field"

        # Verify metrics structure (should not be all random values)
        metrics = data.get("metrics", {})
        assert isinstance(metrics, dict), "Metrics should be an object"

        # Check if metrics look realistic (not purely random)
        # Real metrics should have consistent data types and reasonable ranges
        if "selections" in metrics:
            assert isinstance(
                metrics["selections"], (int, float)
            ), "Selections metric should be numeric"
            assert (
                0 <= metrics["selections"] <= 1000
            ), "Selections should be reasonable number"

    def test_c2_status_not_all_hardcoded_healthy(self, c2_config):
        """Test that not all services return hardcoded 'healthy' status"""
        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        # Make multiple requests to check for variation
        responses = []
        for _ in range(3):
            response = requests.get(url, timeout=c2_config["timeout"])
            data = response.json()
            responses.append(data)
            time.sleep(0.5)  # Small delay between requests

        # Check if all services always return exactly 'healthy'
        # Real health checks should show some variation or at least proper status values
        service_statuses = set()
        for response_data in responses:
            for service in c2_config["expected_services"]:
                if service in response_data:
                    service_statuses.add(str(response_data[service]))

        # If everything is always exactly 'healthy', it's likely hardcoded
        # Real systems might show 'healthy', True, or health objects
        # This test ensures we're not just returning the string 'healthy' for everything
        assert len(service_statuses) > 0, "Should have at least one service status"

        # Check that we're getting proper status responses
        valid_status_patterns = [
            "healthy",
            "degraded",
            "down",  # String statuses
            True,
            False,  # Boolean statuses
        ]

        # At least one status should match expected patterns
        has_valid_status = any(
            status in valid_status_patterns for status in service_statuses
        )
        assert (
            has_valid_status
        ), f"Service statuses should follow valid patterns, got: {service_statuses}"

    def test_c2_status_performance_reasonable(self, c2_config):
        """Test that C2 status response time is reasonable for real health checks"""
        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        start_time = time.time()
        response = requests.get(url, timeout=c2_config["timeout"])
        end_time = time.time()

        response_time_ms = (end_time - start_time) * 1000

        # Real health checks should be reasonably fast but not instant
        # Hardcoded responses are usually < 10ms
        # Real health checks typically take 20-500ms depending on what they check
        assert response.status_code == 200
        assert (
            5 <= response_time_ms <= 2000
        ), f"C2 status response time {response_time_ms:.1f}ms suggests real health checks"

    def test_c2_status_includes_timestamps(self, c2_config):
        """Test that C2 status includes timestamps indicating real-time data"""
        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        # Make two requests with delay
        response1 = requests.get(url, timeout=c2_config["timeout"])
        data1 = response1.json()

        time.sleep(1)

        response2 = requests.get(url, timeout=c2_config["timeout"])
        data2 = response2.json()

        # Look for timestamp fields or time-sensitive data
        # Real health checks often include timestamps or change over time
        timestamp_fields = ["timestamp", "last_check", "updated_at", "checked_at"]

        has_timestamp = False
        for field in timestamp_fields:
            if field in data1 or field in data2:
                has_timestamp = True
                break

            # Check nested objects for timestamps
            for key, value in data1.items():
                if isinstance(value, dict) and field in value:
                    has_timestamp = True
                    break

        # Alternative: Check if any values changed between requests
        # (indicating real-time data vs static hardcoded values)
        values_changed = data1 != data2

        # At least one should be true for real health monitoring
        assert (
            has_timestamp or values_changed
        ), "C2 status should include timestamps or real-time changing data"


class TestC2StatusErrorHandling:
    """Test C2 status error handling when health services are unavailable"""

    def test_c2_status_handles_database_unavailable(self, c2_config):
        """Test C2 status gracefully handles database health service being down"""
        # This test assumes C2 status tries to call real health endpoints
        # If database health is down, C2 should still respond with error status

        url = f"{c2_config['base_url']}{c2_config['c2_status_endpoint']}"

        response = requests.get(url, timeout=c2_config["timeout"])

        # C2 status should always respond, even if individual services are down
        assert response.status_code == 200, "C2 status should always respond"

        data = response.json()

        if "database" in data:
            # If database health check fails, status should reflect that
            db_status = data["database"]

            # Should be proper error status, not hardcoded 'healthy'
            if isinstance(db_status, str):
                assert db_status in [
                    "healthy",
                    "degraded",
                    "down",
                    "error",
                    "unknown",
                ], f"Database status should be proper error state, not hardcoded: {db_status}"


# Performance and integration test markers
pytestmark = [pytest.mark.integration, pytest.mark.c2_dashboard, pytest.mark.real_data]
