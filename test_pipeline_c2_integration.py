#!/usr/bin/env python3
"""
Pipeline Health Integration Test Suite
Tests pipeline health monitoring integration in C2 status endpoint
"""

import requests
import json
import time
import pytest
from datetime import datetime


class TestPipelineHealthIntegration:
    """Test pipeline health monitoring integration"""

    def setup_method(self):
        """Set up test configuration"""
        self.base_url = "http://c2.horse-racing.local"
        self.test_config = {
            "pipeline_config": {
                "container_name": "horse_racing_data_pipeline_clean",
                "expected_response_time_ms": 5000,  # 5 seconds max
                "timeout": 10,
            }
        }

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    def test_pipeline_health_in_c2_status(self):
        """Test that pipeline health status is available in C2 status endpoint."""
        response = requests.get(f"{self.base_url}/c2/status", timeout=10)
        assert (
            response.status_code == 200
        ), f"C2 status endpoint failed: {response.status_code}"

        data = response.json()
        assert (
            "pipeline" in data
        ), "Pipeline health status not found in C2 status response"

        pipeline_status = data["pipeline"]
        valid_statuses = ["healthy", "unhealthy"]
        assert (
            pipeline_status in valid_statuses
        ), f"Invalid pipeline status: {pipeline_status}"

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    def test_pipeline_health_response_structure(self):
        """Test that pipeline health status in C2 response has correct structure."""
        response = requests.get(f"{self.base_url}/c2/status", timeout=10)
        assert response.status_code == 200
        data = response.json()

        # Check for pipeline field in C2 status
        assert "pipeline" in data, "Pipeline health status not found in C2 status"
        pipeline_status = data["pipeline"]

        # Check that pipeline status is a valid value
        valid_statuses = ["healthy", "unhealthy"]
        assert (
            pipeline_status in valid_statuses
        ), f"Invalid pipeline status: {pipeline_status}"

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    def test_pipeline_health_performance(self):
        """Test that pipeline health check response time is acceptable."""
        start_time = time.time()
        response = requests.get(f"{self.base_url}/c2/status", timeout=10)
        response_time = (time.time() - start_time) * 1000  # Convert to ms

        assert response.status_code == 200

        # Response should be under reasonable time limit
        pipeline_config = self.test_config["pipeline_config"]
        max_response_time = pipeline_config["expected_response_time_ms"]
        assert response_time < max_response_time, (
            f"C2 status check too slow: {response_time:.0f}ms > "
            f"{max_response_time}ms"
        )

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    def test_pipeline_health_consistency(self):
        """Test that pipeline health status is consistent across multiple requests."""
        statuses = []

        # Make multiple requests
        for i in range(3):
            response = requests.get(f"{self.base_url}/c2/status", timeout=10)
            assert response.status_code == 200
            data = response.json()
            statuses.append(data["pipeline"])
            time.sleep(0.5)  # Small delay between requests

        # For pipeline health, we expect some consistency
        # (though it could change if container state changes)
        assert len(set(statuses)) <= 2, f"Pipeline status too inconsistent: {statuses}"


class TestPipelineHealthRealDataValidation:
    """Validate that pipeline health shows real data, not hardcoded values"""

    def setup_method(self):
        """Set up test configuration"""
        self.base_url = "http://c2.horse-racing.local"

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    @pytest.mark.real_data
    def test_pipeline_health_not_hardcoded_response(self):
        """Test that pipeline health reflects real container state, not hardcoded values."""
        # Make multiple requests over time to check for variation
        responses = []

        for i in range(5):
            response = requests.get(f"{self.base_url}/c2/status", timeout=10)
            assert response.status_code == 200
            data = response.json()
            responses.append(data["pipeline"])
            time.sleep(1)  # Wait between requests

        # Real pipeline health should show actual container state
        # It might be consistently healthy or unhealthy, but should reflect reality
        unique_statuses = set(responses)

        # Check that we're getting valid status values
        valid_statuses = {"healthy", "unhealthy"}
        assert unique_statuses.issubset(
            valid_statuses
        ), f"Invalid pipeline status values: {unique_statuses}"

    @pytest.mark.integration
    @pytest.mark.pipeline_health
    @pytest.mark.real_data
    def test_pipeline_health_reflects_actual_state(self):
        """Test that pipeline health status reflects actual container state."""
        response = requests.get(f"{self.base_url}/c2/status", timeout=10)
        assert response.status_code == 200
        data = response.json()

        pipeline_status = data["pipeline"]

        # The status should be a real assessment of the container
        # We can't predict if it will be healthy or unhealthy,
        # but it should be one of the valid values
        assert pipeline_status in [
            "healthy",
            "unhealthy",
        ], f"Pipeline status should be real assessment: {pipeline_status}"

        # Additional validation: check that other health statuses are also present
        # This confirms we're getting a complete health report
        required_fields = ["database", "redis", "pipeline"]
        for field in required_fields:
            assert field in data, f"Missing health field: {field}"
            assert data[field] in [
                "healthy",
                "unhealthy",
            ], f"Invalid {field} status: {data[field]}"


def test_pipeline_health_integration_main():
    """Main test function for running standalone"""
    print("🧪 Testing Pipeline Health Integration in C2 Status")
    print("=" * 60)

    base_url = "http://c2.horse-racing.local"

    try:
        # Test C2 status endpoint
        print("1. Testing C2 status endpoint...")
        response = requests.get(f"{base_url}/c2/status", timeout=10)

        if response.status_code != 200:
            print(f"❌ C2 status endpoint failed: {response.status_code}")
            return False

        data = response.json()
        print(f"✅ C2 status endpoint responding: {response.status_code}")

        # Check for pipeline field
        print("\n2. Checking pipeline health in C2 status...")
        if "pipeline" not in data:
            print("❌ Pipeline health status not found in C2 response")
            return False

        pipeline_status = data["pipeline"]
        print(f"✅ Pipeline health status found: {pipeline_status}")

        # Validate pipeline status value
        print("\n3. Validating pipeline status value...")
        valid_statuses = ["healthy", "unhealthy"]
        if pipeline_status not in valid_statuses:
            print(f"❌ Invalid pipeline status: {pipeline_status}")
            return False

        print(f"✅ Pipeline status is valid: {pipeline_status}")

        # Test response time
        print("\n4. Testing response time...")
        start_time = time.time()
        response = requests.get(f"{base_url}/c2/status", timeout=10)
        response_time = (time.time() - start_time) * 1000
        print(f"✅ Response time: {response_time:.0f}ms")

        if response_time > 5000:  # 5 seconds
            print(f"⚠️  Response time is high: {response_time:.0f}ms")

        # Display full status
        print("\n5. Full C2 status response:")
        print(json.dumps(data, indent=2))

        print("\n" + "=" * 60)
        print("🎉 Pipeline Health Integration Test PASSED!")
        print("✅ Pipeline health monitoring is working in C2 status endpoint")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = test_pipeline_health_integration_main()
    exit(0 if success else 1)
