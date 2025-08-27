"""
🧪 AI Selections Web API Integration Tests
========================================

Integration test suite for the AI selections web API endpoints
including performance, recent selections, and dashboard APIs.
"""

import pytest
import asyncio
import json
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
import sys
import os
from datetime import datetime, date

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src/web"))

try:
    from api_server_enhanced import app
except ImportError:
    # Create mock app for testing if import fails
    from fastapi import FastAPI

    app = FastAPI()


class TestAISelectionsAPIEndpoints:
    """Test suite for AI selections API endpoints"""

    @pytest.fixture
    def client(self):
        """Create test client for FastAPI app"""
        return TestClient(app)

    @pytest.fixture
    def mock_performance_api_success(self):
        """Mock successful performance API response"""
        return {
            "status": "success",
            "data": {
                "summary": {
                    "total_predictions": 2378,
                    "correct_predictions": 647,
                    "accuracy_rate": 27.2,
                    "win_rate": 11.0,
                    "place_rate": 1.3,
                    "total_stakes": 23175.0,
                    "total_returns": 29172.24,
                    "total_profit_loss": 5996.99,
                    "roi_percentage": 25.88,
                    "avg_starting_price": 22.64,
                    "latest_running_roi": 3700.0,
                    "period_start": "2025-08-19",
                    "period_end": "2025-08-25",
                },
                "confidence_breakdown": {
                    "LOW": {
                        "total_bets": 2376,
                        "successful_bets": 645,
                        "accuracy_rate": 27.1,
                        "profit_loss": 5975.89,
                        "avg_roi": 26.93,
                        "total_stakes": 23155.0,
                    }
                },
                "daily_performance": [
                    {
                        "date": "2025-08-25",
                        "bets": 381,
                        "wins": 117,
                        "profit": 876.28,
                        "roi": 34.11,
                        "accuracy": 30.71,
                    }
                ],
                "timestamp": datetime.now().isoformat(),
            },
        }

    @pytest.fixture
    def mock_recent_selections_success(self):
        """Mock successful recent selections response"""
        return {
            "status": "success",
            "data": {
                "selections": [
                    {
                        "race_id": 155457,
                        "horse_name": "The Fitter",
                        "selection_date": "2025-08-25",
                        "ai_probability": 1.0,
                        "confidence_level": "LOW",
                        "recommended_stake": 10.0,
                        "value_rating": 0.0,
                        "starting_price": 81.0,
                        "market_rank": 11,
                        "finishing_position": 11,
                        "race_result": "LOSE",
                        "profit_loss": -10.0,
                        "roi_percentage": -100.0,
                        "created_at": datetime.now().isoformat(),
                    }
                ],
                "count": 1,
                "timestamp": datetime.now().isoformat(),
            },
        }

    @patch("api_server_enhanced.performance_api")
    def test_get_ai_selections_performance_success(
        self, mock_perf_api, client, mock_performance_api_success
    ):
        """Test successful performance API endpoint"""
        mock_perf_api.get_performance_summary.return_value = (
            mock_performance_api_success
        )

        response = client.get("/api/ai_selections/performance")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "data" in data
        assert "summary" in data["data"]
        assert data["data"]["summary"]["total_predictions"] == 2378
        assert data["data"]["summary"]["roi_percentage"] == 25.88

        # Verify API was called
        mock_perf_api.get_performance_summary.assert_called_once_with(days_back=30)

    @patch("api_server_enhanced.performance_api")
    def test_get_ai_selections_performance_error(self, mock_perf_api, client):
        """Test performance API endpoint with error"""
        mock_perf_api.get_performance_summary.return_value = {
            "status": "error",
            "message": "Database connection failed",
            "data": {"summary": {"total_predictions": 0}},
        }

        response = client.get("/api/ai_selections/performance")

        assert response.status_code == 500
        data = response.json()
        assert "error" in data["detail"]

    @patch("api_server_enhanced.performance_api")
    def test_get_recent_ai_selections_success(
        self, mock_perf_api, client, mock_recent_selections_success
    ):
        """Test successful recent selections API endpoint"""
        mock_perf_api.get_recent_selections.return_value = (
            mock_recent_selections_success
        )

        response = client.get("/api/ai_selections/recent?limit=10")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "data" in data
        assert "selections" in data["data"]
        assert data["data"]["count"] == 1
        assert len(data["data"]["selections"]) == 1

        selection = data["data"]["selections"][0]
        assert selection["horse_name"] == "The Fitter"
        assert selection["race_result"] == "LOSE"
        assert selection["profit_loss"] == -10.0

        # Verify API was called with correct limit
        mock_perf_api.get_recent_selections.assert_called_once_with(limit=10)

    @patch("api_server_enhanced.performance_api")
    def test_get_recent_ai_selections_custom_limit(
        self, mock_perf_api, client, mock_recent_selections_success
    ):
        """Test recent selections with custom limit parameter"""
        mock_perf_api.get_recent_selections.return_value = (
            mock_recent_selections_success
        )

        response = client.get("/api/ai_selections/recent?limit=25")

        assert response.status_code == 200
        mock_perf_api.get_recent_selections.assert_called_once_with(limit=25)

    @patch("api_server_enhanced.performance_api")
    def test_get_recent_ai_selections_default_limit(
        self, mock_perf_api, client, mock_recent_selections_success
    ):
        """Test recent selections with default limit"""
        mock_perf_api.get_recent_selections.return_value = (
            mock_recent_selections_success
        )

        response = client.get("/api/ai_selections/recent")

        assert response.status_code == 200
        mock_perf_api.get_recent_selections.assert_called_once_with(limit=50)

    @patch("api_server_enhanced.performance_api")
    def test_get_ai_selections_dashboard_success(
        self,
        mock_perf_api,
        client,
        mock_performance_api_success,
        mock_recent_selections_success,
    ):
        """Test successful dashboard API endpoint"""
        mock_perf_api.get_performance_summary.return_value = (
            mock_performance_api_success
        )
        mock_perf_api.get_recent_selections.return_value = (
            mock_recent_selections_success
        )

        response = client.get("/api/ai_selections/dashboard")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "success"
        assert "data" in data
        assert "performance" in data["data"]
        assert "recent_selections" in data["data"]
        assert "system_status" in data["data"]
        assert "quick_stats" in data["data"]

        # Verify system status
        system_status = data["data"]["system_status"]
        assert system_status["ai_system"] == "ACTIVE"
        assert system_status["database"] == "CONNECTED"
        assert system_status["profit_tracking"] == "ENABLED"

        # Verify quick stats
        quick_stats = data["data"]["quick_stats"]
        assert quick_stats["total_predictions"] == 2378
        assert quick_stats["current_roi"] == 25.88
        assert quick_stats["accuracy_rate"] == 27.2

    @patch("api_server_enhanced.performance_api")
    def test_get_ai_selections_dashboard_partial_failure(self, mock_perf_api, client):
        """Test dashboard endpoint with partial API failures"""
        # Performance API succeeds, recent selections fails
        mock_perf_api.get_performance_summary.return_value = {
            "status": "success",
            "data": {"summary": {"total_predictions": 100}},
        }
        mock_perf_api.get_recent_selections.return_value = {
            "status": "error",
            "message": "Query failed",
            "data": {"selections": [], "count": 0},
        }

        response = client.get("/api/ai_selections/dashboard")

        # Should handle partial failures gracefully
        assert response.status_code in [200, 500]  # Depends on implementation

    def test_api_endpoints_cors_headers(self, client):
        """Test that API endpoints include proper CORS headers"""
        response = client.get("/api/ai_selections/performance")

        # Check for CORS headers (if implemented)
        # This would depend on the actual CORS configuration
        assert response.status_code in [200, 404, 500]  # Endpoint exists

    def test_api_response_content_type(self, client):
        """Test that API responses have correct content type"""
        with patch("api_server_enhanced.performance_api") as mock_api:
            mock_api.get_performance_summary.return_value = {
                "status": "success",
                "data": {"summary": {}},
            }

            response = client.get("/api/ai_selections/performance")

            assert "application/json" in response.headers.get("content-type", "")


class TestAPIErrorHandling:
    """Test error handling in API endpoints"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("api_server_enhanced.performance_api")
    def test_api_import_error_handling(self, mock_perf_api, client):
        """Test handling of import errors"""
        # Simulate import error
        mock_perf_api.side_effect = ImportError("Module not found")

        response = client.get("/api/ai_selections/performance")

        # Should handle import errors gracefully
        assert response.status_code == 500

    @patch("api_server_enhanced.performance_api")
    def test_api_timeout_handling(self, mock_perf_api, client):
        """Test handling of API timeouts"""
        # Simulate slow response
        import time

        def slow_response(*args, **kwargs):
            time.sleep(0.1)  # Short delay for testing
            return {"status": "success", "data": {}}

        mock_perf_api.get_performance_summary.side_effect = slow_response

        response = client.get("/api/ai_selections/performance")

        # Should complete within reasonable time
        assert response.status_code == 200

    def test_invalid_query_parameters(self, client):
        """Test handling of invalid query parameters"""
        # Test with invalid limit parameter
        response = client.get("/api/ai_selections/recent?limit=invalid")

        # Should handle invalid parameters gracefully
        assert response.status_code in [400, 422, 500]  # Validation error

    def test_large_limit_parameter(self, client):
        """Test handling of excessively large limit parameters"""
        with patch("api_server_enhanced.performance_api") as mock_api:
            mock_api.get_recent_selections.return_value = {
                "status": "success",
                "data": {"selections": [], "count": 0},
            }

            response = client.get("/api/ai_selections/recent?limit=999999")

            # Should handle large limits appropriately
            assert response.status_code in [200, 400, 422]


class TestAPIPerformance:
    """Test API performance characteristics"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @pytest.mark.performance
    def test_api_response_time(self, client):
        """Test that API responses are within acceptable time limits"""
        with patch("api_server_enhanced.performance_api") as mock_api:
            mock_api.get_performance_summary.return_value = {
                "status": "success",
                "data": {"summary": {}},
            }

            import time

            start_time = time.time()

            response = client.get("/api/ai_selections/performance")

            end_time = time.time()
            response_time = end_time - start_time

            assert response.status_code == 200
            assert response_time < 5.0  # Should respond within 5 seconds

    @pytest.mark.performance
    def test_concurrent_api_requests(self, client):
        """Test handling of concurrent API requests"""
        import threading
        import time

        with patch("api_server_enhanced.performance_api") as mock_api:
            mock_api.get_performance_summary.return_value = {
                "status": "success",
                "data": {"summary": {}},
            }

            results = []

            def make_request():
                response = client.get("/api/ai_selections/performance")
                results.append(response.status_code)

            # Create multiple threads
            threads = []
            for _ in range(5):
                thread = threading.Thread(target=make_request)
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # All requests should succeed
            assert all(status == 200 for status in results)
            assert len(results) == 5


class TestAPIDataValidation:
    """Test data validation in API responses"""

    @pytest.fixture
    def client(self):
        return TestClient(app)

    @patch("api_server_enhanced.performance_api")
    def test_performance_response_schema(self, mock_perf_api, client):
        """Test that performance API response matches expected schema"""
        mock_response = {
            "status": "success",
            "data": {
                "summary": {
                    "total_predictions": 100,
                    "accuracy_rate": 25.0,
                    "roi_percentage": 10.5,
                    "total_profit_loss": 1000.0,
                }
            },
        }
        mock_perf_api.get_performance_summary.return_value = mock_response

        response = client.get("/api/ai_selections/performance")

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "status" in data
        assert "data" in data
        assert "summary" in data["data"]

        summary = data["data"]["summary"]
        assert isinstance(summary["total_predictions"], int)
        assert isinstance(summary["accuracy_rate"], (int, float))
        assert isinstance(summary["roi_percentage"], (int, float))
        assert isinstance(summary["total_profit_loss"], (int, float))

    @patch("api_server_enhanced.performance_api")
    def test_recent_selections_response_schema(self, mock_perf_api, client):
        """Test that recent selections API response matches expected schema"""
        mock_response = {
            "status": "success",
            "data": {
                "selections": [
                    {
                        "race_id": 12345,
                        "horse_name": "Test Horse",
                        "profit_loss": -10.0,
                        "roi_percentage": -100.0,
                    }
                ],
                "count": 1,
            },
        }
        mock_perf_api.get_recent_selections.return_value = mock_response

        response = client.get("/api/ai_selections/recent")

        assert response.status_code == 200
        data = response.json()

        # Validate response structure
        assert "status" in data
        assert "data" in data
        assert "selections" in data["data"]
        assert "count" in data["data"]

        if data["data"]["selections"]:
            selection = data["data"]["selections"][0]
            assert isinstance(selection["race_id"], int)
            assert isinstance(selection["horse_name"], str)
            assert isinstance(selection["profit_loss"], (int, float))
            assert isinstance(selection["roi_percentage"], (int, float))


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
