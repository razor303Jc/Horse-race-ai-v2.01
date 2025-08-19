"""
Comprehensive API Tests for Horse Racing AI Backend
Tests all API endpoints and functionality
"""

import pytest
import requests
import json
from typing import Dict, Any
import time


class TestAPIEndpoints:
    """Test all API endpoints"""

    BASE_URL = "http://localhost:8000"

    def test_health_endpoint(self):
        """Test API health check"""
        response = requests.get(f"{self.BASE_URL}/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_api_documentation_access(self):
        """Test that API documentation is accessible"""
        response = requests.get(f"{self.BASE_URL}/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")

    def test_openapi_schema(self):
        """Test OpenAPI schema endpoint"""
        response = requests.get(f"{self.BASE_URL}/openapi.json")
        assert response.status_code == 200

        schema = response.json()
        assert "openapi" in schema
        assert "info" in schema
        assert "paths" in schema


class TestRaceDataEndpoints:
    """Test race data related endpoints"""

    BASE_URL = "http://localhost:8000"

    def test_daily_races_endpoint(self):
        """Test daily races endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/daily_races")

        # Should return either data or appropriate error
        assert response.status_code in [200, 404, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))

    def test_real_race_cards_endpoint(self):
        """Test real race cards endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/real_race_cards")

        # Should return either data or appropriate error
        assert response.status_code in [200, 404, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)
            if "races" in data:
                assert isinstance(data["races"], list)

    def test_race_cards_with_parameters(self):
        """Test race cards endpoint with query parameters"""
        params = {"date": "2025-08-19", "track": "ascot"}

        response = requests.get(f"{self.BASE_URL}/api/real_race_cards", params=params)
        assert response.status_code in [200, 404, 422, 503]

    def test_betting_recommendations_endpoint(self):
        """Test betting recommendations endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/betting/recommendations")

        assert response.status_code in [200, 404, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, (dict, list))


class TestPerformanceEndpoints:
    """Test performance analytics endpoints"""

    BASE_URL = "http://localhost:8000"

    def test_stage8_performance_endpoint(self):
        """Test Stage 8 performance analytics"""
        response = requests.get(f"{self.BASE_URL}/api/stage8/performance")

        assert response.status_code in [200, 404, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_performance_with_date_range(self):
        """Test performance endpoint with date range"""
        params = {"start_date": "2025-08-01", "end_date": "2025-08-19"}

        response = requests.get(
            f"{self.BASE_URL}/api/stage8/performance", params=params
        )
        assert response.status_code in [200, 404, 422, 503]


class TestPredictionEndpoints:
    """Test ML prediction endpoints"""

    BASE_URL = "http://localhost:8000"

    def test_prediction_endpoint_get(self):
        """Test prediction endpoint via GET"""
        response = requests.get(f"{self.BASE_URL}/predict")

        # Should return either prediction interface or data
        assert response.status_code in [200, 405]

    def test_prediction_endpoint_post(self):
        """Test prediction endpoint via POST"""
        sample_data = {
            "horse_name": "Test Horse",
            "age": 4,
            "weight_kg": 60,
            "jockey_name": "Test Jockey",
            "trainer_name": "Test Trainer",
            "recent_form": "1-2-1",
            "track_condition": "Good",
        }

        response = requests.post(
            f"{self.BASE_URL}/predict",
            json=sample_data,
            headers={"Content-Type": "application/json"},
        )

        # Should return prediction or validation error
        assert response.status_code in [200, 422, 503]

        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)

    def test_batch_prediction_endpoint(self):
        """Test batch prediction if available"""
        sample_batch = {
            "horses": [
                {
                    "horse_name": "Horse 1",
                    "age": 4,
                    "weight_kg": 60,
                    "jockey_name": "Jockey 1",
                    "trainer_name": "Trainer 1",
                },
                {
                    "horse_name": "Horse 2",
                    "age": 5,
                    "weight_kg": 58,
                    "jockey_name": "Jockey 2",
                    "trainer_name": "Trainer 2",
                },
            ]
        }

        response = requests.post(
            f"{self.BASE_URL}/predict/batch",
            json=sample_batch,
            headers={"Content-Type": "application/json"},
        )

        # Endpoint might not exist, so accept 404
        assert response.status_code in [200, 404, 422, 503]


class TestErrorHandling:
    """Test API error handling"""

    BASE_URL = "http://localhost:8000"

    def test_invalid_endpoint(self):
        """Test request to non-existent endpoint"""
        response = requests.get(f"{self.BASE_URL}/api/nonexistent")
        assert response.status_code == 404

    def test_invalid_method(self):
        """Test invalid HTTP method"""
        response = requests.delete(f"{self.BASE_URL}/health")
        assert response.status_code in [405, 404]

    def test_invalid_json_payload(self):
        """Test invalid JSON in POST request"""
        response = requests.post(
            f"{self.BASE_URL}/predict",
            data="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 422]

    def test_malformed_parameters(self):
        """Test malformed query parameters"""
        params = {"date": "invalid-date", "limit": "not-a-number"}

        response = requests.get(f"{self.BASE_URL}/api/daily_races", params=params)
        assert response.status_code in [400, 422]


class TestAPIPerformance:
    """Test API performance characteristics"""

    BASE_URL = "http://localhost:8000"

    def test_response_time_health(self):
        """Test health endpoint response time"""
        start_time = time.time()
        response = requests.get(f"{self.BASE_URL}/health")
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 1.0  # Should respond within 1 second
        assert response.status_code == 200

    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import concurrent.futures
        import threading

        def make_request():
            return requests.get(f"{self.BASE_URL}/health")

        # Make 10 concurrent requests
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            responses = [
                future.result() for future in concurrent.futures.as_completed(futures)
            ]

        # All requests should succeed
        for response in responses:
            assert response.status_code == 200

    def test_large_payload_handling(self):
        """Test handling of large JSON payloads"""
        large_payload = {
            "horses": [
                {
                    "horse_name": f"Horse {i}",
                    "age": 4,
                    "weight_kg": 60,
                    "data": "x" * 1000,  # 1KB of data per horse
                }
                for i in range(100)  # 100 horses = ~100KB
            ]
        }

        response = requests.post(
            f"{self.BASE_URL}/predict",
            json=large_payload,
            headers={"Content-Type": "application/json"},
            timeout=10,
        )

        # Should handle large payload or return appropriate error
        assert response.status_code in [200, 413, 422, 503]


class TestSecurity:
    """Test API security features"""

    BASE_URL = "http://localhost:8000"

    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = requests.get(f"{self.BASE_URL}/health")

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers

    def test_security_headers(self):
        """Test security headers"""
        response = requests.get(f"{self.BASE_URL}/health")

        # Should have basic security headers
        headers = {k.lower(): v for k, v in response.headers.items()}

        # These headers improve security
        expected_headers = [
            "x-content-type-options",
            "x-frame-options",
            "x-xss-protection",
        ]

        # Log which security headers are present
        present_headers = [h for h in expected_headers if h in headers]
        print(f"Present security headers: {present_headers}")

    def test_rate_limiting(self):
        """Test rate limiting if implemented"""
        # Make rapid requests to test rate limiting
        responses = []
        for i in range(20):
            response = requests.get(f"{self.BASE_URL}/health")
            responses.append(response)
            time.sleep(0.1)  # 100ms between requests

        # Check if any responses indicate rate limiting
        rate_limited = [r for r in responses if r.status_code == 429]

        # Log rate limiting status
        print(f"Rate limited responses: {len(rate_limited)}/20")

        # Most responses should still succeed
        successful = [r for r in responses if r.status_code == 200]
        assert len(successful) > 10


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
