#!/usr/bin/env python3
"""
Automation API Test Suite
=========================

Comprehensive testing for all 5 Horse Racing AI automation API endpoints
"""

import pytest
import requests
import json
import time
from unittest.mock import patch, MagicMock
from datetime import datetime
import asyncio
import aiohttp
from concurrent.futures import ThreadPoolExecutor

# Test configuration
NODE_RED_URL = "http://c2.horse-racing.local"  # Through Traefik proxy
API_BASE = f"{NODE_RED_URL}/api/pipeline"
REQUEST_TIMEOUT = 30


class TestAutomationAPIEndpoints:
    """Test suite for automation API endpoints"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test"""
        self.base_url = API_BASE
        self.endpoints = [
            "trigger",
            "data_relationships",
            "performance_tracker",
            "ml_training",
            "ai_selections",
        ]

    def test_api_endpoint_availability(self):
        """Test that all API endpoints are accessible"""
        for endpoint in self.endpoints:
            url = f"{self.base_url}/{endpoint}"

            try:
                response = requests.post(url, timeout=5)
                assert response.status_code in [
                    200,
                    202,
                ], f"Endpoint {endpoint} returned {response.status_code}"

                # Verify JSON response structure
                if response.content:
                    json_data = response.json()
                    assert (
                        "success" in json_data
                    ), f"Endpoint {endpoint} missing 'success' field"
                    assert (
                        "message" in json_data
                    ), f"Endpoint {endpoint} missing 'message' field"

            except requests.exceptions.RequestException as e:
                pytest.fail(f"Endpoint {endpoint} not accessible: {e}")

    def test_api_response_times(self):
        """Test API response times are acceptable"""
        for endpoint in self.endpoints:
            url = f"{self.base_url}/{endpoint}"

            start_time = time.time()
            response = requests.post(url, timeout=REQUEST_TIMEOUT)
            end_time = time.time()

            response_time = end_time - start_time

            # Response time should be under 5 seconds
            assert (
                response_time < 5.0
            ), f"Endpoint {endpoint} too slow: {response_time:.3f}s"

            # Response time should be reasonable (under 2s for most)
            if endpoint not in ["ml_training"]:  # ML training might be slower
                assert (
                    response_time < 2.0
                ), f"Endpoint {endpoint} response time too high: {response_time:.3f}s"

    def test_api_response_format(self):
        """Test API response format consistency"""
        for endpoint in self.endpoints:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, timeout=REQUEST_TIMEOUT)

            assert (
                response.status_code == 200
            ), f"Endpoint {endpoint} failed: {response.status_code}"

            json_data = response.json()

            # Check required fields
            assert isinstance(
                json_data.get("success"), bool
            ), f"Endpoint {endpoint} 'success' not boolean"
            assert isinstance(
                json_data.get("message"), str
            ), f"Endpoint {endpoint} 'message' not string"

            # Check success response structure
            if json_data.get("success"):
                assert (
                    "request_id" in json_data or "description" in json_data
                ), f"Endpoint {endpoint} missing identifier"

    def test_concurrent_api_requests(self):
        """Test API endpoints handle concurrent requests"""

        def make_request(endpoint):
            url = f"{self.base_url}/{endpoint}"
            return requests.post(url, timeout=REQUEST_TIMEOUT)

        # Test concurrent requests to same endpoint
        endpoint = "trigger"  # Use fastest endpoint

        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, endpoint) for _ in range(3)]
            responses = [future.result() for future in futures]

        # All requests should succeed
        for i, response in enumerate(responses):
            assert (
                response.status_code == 200
            ), f"Concurrent request {i} failed: {response.status_code}"

    def test_invalid_endpoint_handling(self):
        """Test handling of invalid endpoints"""
        invalid_url = f"{self.base_url}/nonexistent_endpoint"

        response = requests.post(invalid_url, timeout=5)
        assert (
            response.status_code == 404
        ), f"Invalid endpoint should return 404, got {response.status_code}"

    def test_api_error_handling(self):
        """Test API error handling with various scenarios"""
        # Test with different HTTP methods
        for endpoint in self.endpoints[:2]:  # Test subset to avoid too many requests
            url = f"{self.base_url}/{endpoint}"

            # Test GET method (should work or give appropriate response)
            get_response = requests.get(url, timeout=5)
            assert get_response.status_code in [
                200,
                404,
                405,
            ], f"GET {endpoint} unexpected status: {get_response.status_code}"

            # Test PUT method (should be rejected)
            put_response = requests.put(url, timeout=5)
            assert put_response.status_code in [
                404,
                405,
            ], f"PUT {endpoint} should be rejected: {put_response.status_code}"


class TestAutomationAPIPerformance:
    """Performance testing for automation APIs"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for performance tests"""
        self.base_url = API_BASE
        self.fast_endpoints = ["trigger", "data_relationships", "performance_tracker"]
        self.slow_endpoints = ["ml_training", "ai_selections"]

    @pytest.mark.performance
    def test_fast_endpoint_performance(self):
        """Test that fast endpoints respond quickly"""
        for endpoint in self.fast_endpoints:
            url = f"{self.base_url}/{endpoint}"

            # Measure multiple requests
            times = []
            for _ in range(3):
                start = time.time()
                response = requests.post(url, timeout=REQUEST_TIMEOUT)
                end = time.time()

                assert response.status_code == 200
                times.append(end - start)
                time.sleep(0.5)  # Brief pause between requests

            avg_time = sum(times) / len(times)
            assert (
                avg_time < 1.0
            ), f"Fast endpoint {endpoint} average time too high: {avg_time:.3f}s"

    @pytest.mark.performance
    def test_endpoint_reliability(self):
        """Test endpoint reliability over multiple requests"""
        endpoint = "trigger"  # Most reliable endpoint
        url = f"{self.base_url}/{endpoint}"

        success_count = 0
        total_requests = 5

        for i in range(total_requests):
            try:
                response = requests.post(url, timeout=REQUEST_TIMEOUT)
                if response.status_code == 200:
                    success_count += 1
            except:
                pass
            time.sleep(0.5)

        reliability = success_count / total_requests
        assert reliability >= 0.8, f"Endpoint reliability too low: {reliability:.1%}"


class TestAutomationAPIIntegration:
    """Integration testing for automation APIs"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for integration tests"""
        self.base_url = API_BASE

    @pytest.mark.integration
    def test_trigger_endpoint_integration(self):
        """Test trigger endpoint integration"""
        url = f"{self.base_url}/trigger"
        response = requests.post(url, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        json_data = response.json()

        assert json_data.get("success") is True
        assert "Pipeline triggered" in json_data.get("message", "")
        assert "request_id" in json_data

    @pytest.mark.integration
    def test_data_relationships_integration(self):
        """Test data relationships endpoint integration"""
        url = f"{self.base_url}/data_relationships"
        response = requests.post(url, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        json_data = response.json()

        assert json_data.get("success") is True
        assert "Data Relationships" in json_data.get("message", "")
        assert (
            json_data.get("description")
            == "Process jockey/trainer statistics and relationships"
        )

    @pytest.mark.integration
    def test_performance_tracker_integration(self):
        """Test performance tracker endpoint integration"""
        url = f"{self.base_url}/performance_tracker"
        response = requests.post(url, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        json_data = response.json()

        assert json_data.get("success") is True
        assert "Performance Tracker" in json_data.get("message", "")

    @pytest.mark.integration
    def test_ml_training_integration(self):
        """Test ML training endpoint integration"""
        url = f"{self.base_url}/ml_training"
        response = requests.post(url, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        json_data = response.json()

        assert json_data.get("success") is True
        assert "ML Training" in json_data.get("message", "")

    @pytest.mark.integration
    def test_ai_selections_integration(self):
        """Test AI selections endpoint integration"""
        url = f"{self.base_url}/ai_selections"
        response = requests.post(url, timeout=REQUEST_TIMEOUT)

        assert response.status_code == 200
        json_data = response.json()

        assert json_data.get("success") is True
        assert "AI Selections" in json_data.get("message", "")


class TestAutomationAPIPayloads:
    """Test API endpoints with different payload scenarios"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for payload tests"""
        self.base_url = API_BASE

    def test_empty_payload(self):
        """Test endpoints with empty payload"""
        for endpoint in ["trigger", "data_relationships"]:
            url = f"{self.base_url}/{endpoint}"

            response = requests.post(url, json={}, timeout=REQUEST_TIMEOUT)
            assert (
                response.status_code == 200
            ), f"Endpoint {endpoint} failed with empty payload"

    def test_json_payload(self):
        """Test endpoints with JSON payload"""
        test_payload = {
            "test_mode": True,
            "timestamp": datetime.now().isoformat(),
            "source": "automation_test_suite",
        }

        for endpoint in ["trigger", "data_relationships"]:
            url = f"{self.base_url}/{endpoint}"

            response = requests.post(url, json=test_payload, timeout=REQUEST_TIMEOUT)
            assert (
                response.status_code == 200
            ), f"Endpoint {endpoint} failed with JSON payload"

    def test_invalid_json_payload(self):
        """Test endpoints handle invalid JSON gracefully"""
        for endpoint in ["trigger"]:  # Test subset
            url = f"{self.base_url}/{endpoint}"

            # Test with malformed JSON
            response = requests.post(
                url,
                data='{"invalid": json}',
                headers={"Content-Type": "application/json"},
                timeout=REQUEST_TIMEOUT,
            )

            # Should either process successfully or return appropriate error
            assert response.status_code in [
                200,
                400,
            ], f"Endpoint {endpoint} bad error handling"


class TestAutomationAPISequencing:
    """Test API endpoint sequencing and dependencies"""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for sequencing tests"""
        self.base_url = API_BASE

    @pytest.mark.integration
    def test_typical_workflow_sequence(self):
        """Test typical automation workflow sequence"""
        # Typical morning sequence: data_relationships -> performance_tracker -> ai_selections
        sequence = [
            ("data_relationships", "Data Relationships"),
            ("performance_tracker", "Performance Tracker"),
            ("ai_selections", "AI Selections"),
        ]

        for endpoint, expected_message in sequence:
            url = f"{self.base_url}/{endpoint}"
            response = requests.post(url, timeout=REQUEST_TIMEOUT)

            assert response.status_code == 200, f"Sequence failed at {endpoint}"
            json_data = response.json()
            assert json_data.get("success") is True
            assert expected_message in json_data.get("message", "")

            # Brief pause between sequence steps
            time.sleep(1)

    @pytest.mark.integration
    def test_rapid_sequential_requests(self):
        """Test rapid sequential requests to same endpoint"""
        endpoint = "trigger"
        url = f"{self.base_url}/{endpoint}"

        responses = []
        for i in range(3):
            response = requests.post(url, timeout=REQUEST_TIMEOUT)
            responses.append(response)
            time.sleep(0.1)  # Very brief pause

        # All should succeed
        for i, response in enumerate(responses):
            assert response.status_code == 200, f"Rapid request {i} failed"


if __name__ == "__main__":
    # Run the test suite
    pytest.main([__file__, "-v", "--tb=short", "-x"])  # Stop on first failure
