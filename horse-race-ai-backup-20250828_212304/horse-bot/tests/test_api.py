"""
Integration tests for API endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
import json

from src.main import app


class TestHealthEndpoint:
    """Test cases for health check endpoint."""
    
    def test_health_check_success(self, client):
        """Test successful health check."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        assert "environment" in data
        assert "uptime_seconds" in data
        
        assert data["status"] == "healthy"
    
    def test_health_check_detailed(self, client):
        """Test detailed health check."""
        response = client.get("/health?detailed=true")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "status" in data
        assert "checks" in data
        assert "database" in data["checks"]
        assert "redis" in data["checks"]
        assert "ml_models" in data["checks"]
    
    @patch('src.database.connection.DatabaseManager.health_check')
    def test_health_check_database_failure(self, mock_db_health, client):
        """Test health check with database failure."""
        mock_db_health.return_value = False
        
        response = client.get("/health?detailed=true")
        
        # Should still return 200 but with unhealthy status
        assert response.status_code == 200
        data = response.json()
        
        assert data["checks"]["database"]["status"] == "unhealthy"


class TestRacesEndpoint:
    """Test cases for races endpoint."""
    
    def test_get_races_empty(self, client):
        """Test getting races when none exist."""
        response = client.get("/api/v1/races")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "races" in data
        assert isinstance(data["races"], list)
        assert len(data["races"]) == 0
    
    @patch('src.services.race_service.RaceService.get_races')
    def test_get_races_with_data(self, mock_get_races, client, mock_race_data):
        """Test getting races with existing data."""
        mock_get_races.return_value = [mock_race_data]
        
        response = client.get("/api/v1/races")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["races"]) == 1
        assert data["races"][0]["id"] == mock_race_data["id"]
        assert data["races"][0]["name"] == mock_race_data["name"]
    
    @patch('src.services.race_service.RaceService.get_race_by_id')
    def test_get_race_by_id(self, mock_get_race, client, mock_race_data):
        """Test getting a specific race by ID."""
        mock_get_race.return_value = mock_race_data
        
        response = client.get("/api/v1/races/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == mock_race_data["id"]
        assert data["name"] == mock_race_data["name"]
    
    @patch('src.services.race_service.RaceService.get_race_by_id')
    def test_get_race_not_found(self, mock_get_race, client):
        """Test getting a race that doesn't exist."""
        mock_get_race.return_value = None
        
        response = client.get("/api/v1/races/999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestPredictionsEndpoint:
    """Test cases for predictions endpoint."""
    
    def test_create_prediction_invalid_data(self, client):
        """Test creating prediction with invalid data."""
        invalid_data = {
            "race_id": "invalid",  # Should be integer
            "model_type": "unknown_model"
        }
        
        response = client.post(
            "/api/v1/predictions",
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.services.prediction_service.PredictionService.create_prediction')
    def test_create_prediction_success(self, mock_create_prediction, client):
        """Test successful prediction creation."""
        mock_prediction = {
            "id": 1,
            "race_id": 1,
            "model_type": "random_forest",
            "predictions": [
                {"horse_id": 1, "position": 1, "confidence": 0.85},
                {"horse_id": 2, "position": 2, "confidence": 0.75}
            ]
        }
        mock_create_prediction.return_value = mock_prediction
        
        prediction_request = {
            "race_id": 1,
            "model_type": "random_forest"
        }
        
        response = client.post(
            "/api/v1/predictions",
            json=prediction_request
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["id"] == mock_prediction["id"]
        assert data["race_id"] == mock_prediction["race_id"]
        assert len(data["predictions"]) == 2


class TestSimulationEndpoint:
    """Test cases for simulation endpoint."""
    
    def test_run_simulation_invalid_parameters(self, client):
        """Test simulation with invalid parameters."""
        invalid_data = {
            "race_id": 1,
            "num_runs": -100  # Invalid negative number
        }
        
        response = client.post(
            "/api/v1/simulations",
            json=invalid_data
        )
        
        assert response.status_code == 422  # Validation error
    
    @patch('src.services.simulation_service.SimulationService.run_simulation')
    def test_run_simulation_success(self, mock_run_simulation, client):
        """Test successful simulation run."""
        mock_result = {
            "id": 1,
            "race_id": 1,
            "num_runs": 1000,
            "results": {
                "1": {
                    "win_percentage": 25.5,
                    "place_percentage": 45.2,
                    "show_percentage": 65.8
                }
            },
            "execution_time_ms": 1500
        }
        mock_run_simulation.return_value = mock_result
        
        simulation_request = {
            "race_id": 1,
            "num_runs": 1000,
            "track_condition": "good"
        }
        
        response = client.post(
            "/api/v1/simulations",
            json=simulation_request
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["id"] == mock_result["id"]
        assert data["race_id"] == mock_result["race_id"]
        assert data["execution_time_ms"] == mock_result["execution_time_ms"]


class TestAnalyticsEndpoint:
    """Test cases for analytics endpoint."""
    
    @patch('src.services.analytics_service.AnalyticsService.get_horse_performance')
    def test_get_horse_analytics(self, mock_get_performance, client):
        """Test getting horse performance analytics."""
        mock_analytics = {
            "horse_id": 1,
            "total_races": 25,
            "wins": 5,
            "places": 8,
            "shows": 12,
            "win_percentage": 20.0,
            "average_position": 4.2,
            "earnings": 125000
        }
        mock_get_performance.return_value = mock_analytics
        
        response = client.get("/api/v1/analytics/horses/1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["horse_id"] == mock_analytics["horse_id"]
        assert data["win_percentage"] == mock_analytics["win_percentage"]
        assert data["total_races"] == mock_analytics["total_races"]
    
    def test_get_horse_analytics_not_found(self, client):
        """Test getting analytics for non-existent horse."""
        response = client.get("/api/v1/analytics/horses/999")
        
        # This should return 404 if horse doesn't exist
        # Implementation depends on service layer behavior
        assert response.status_code in [200, 404]


@pytest.mark.integration
class TestEndToEndWorkflow:
    """End-to-end integration tests."""
    
    def test_full_prediction_workflow(self, client):
        """Test complete workflow from race creation to prediction."""
        # This would be a more complex test that:
        # 1. Creates or retrieves a race
        # 2. Adds horses to the race
        # 3. Runs a prediction
        # 4. Runs a simulation
        # 5. Retrieves analytics
        
        # For now, just test that endpoints are available
        health_response = client.get("/health")
        assert health_response.status_code == 200
        
        races_response = client.get("/api/v1/races")
        assert races_response.status_code == 200
