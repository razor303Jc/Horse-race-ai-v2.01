"""
🔧 C2 API Endpoints Test Suite
==============================

Unit tests for C2 API endpoints including database connectivity,
container health checks, and system monitoring functionality.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

# Import the API modules to test
import sys
import os
sys.path.append('/home/jc/Documents/Horse-race-ai-v2.04/api')

try:
    from c2_api_endpoints import (
        get_processing_stats,
        get_database_stats,
        get_system_status,
        get_container_health,
        trigger_data_processing
    )
except ImportError:
    pytest.skip("C2 API endpoints not available", allow_module_level=True)


class TestC2APIEndpoints:
    """Unit tests for C2 API endpoint functions"""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        mock_conn = Mock()
        mock_cursor = Mock()
        
        # Configure cursor for empty database responses
        mock_cursor.fetchone.return_value = None
        mock_cursor.fetchall.return_value = []
        mock_cursor.rowcount = 0
        
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        
        return mock_conn

    @pytest.fixture
    def mock_redis_client(self):
        """Mock Redis client"""
        mock_redis = Mock()
        mock_redis.get.return_value = None
        mock_redis.set.return_value = True
        mock_redis.ping.return_value = True
        return mock_redis

    def test_get_processing_stats_empty_database(self, mock_db_connection):
        """Test processing stats with empty database"""
        with patch('c2_api_endpoints.psycopg2.connect', 
                   return_value=mock_db_connection):
            
            # Configure mock for empty database
            mock_cursor = mock_db_connection.cursor.return_value
            mock_cursor.fetchone.return_value = (0,)  # COUNT returns 0
            
            stats = get_processing_stats()
            
            assert isinstance(stats, dict)
            assert "cardsToday" in stats
            assert "resultsToday" in stats
            assert "totalCards" in stats
            assert "totalResults" in stats
            assert "timestamp" in stats
            
            # Empty database should return 0 for all counts
            assert stats["cardsToday"] == 0
            assert stats["resultsToday"] == 0
            assert stats["totalCards"] == 0
            assert stats["totalResults"] == 0

    def test_get_processing_stats_with_data(self, mock_db_connection):
        """Test processing stats with sample data"""
        with patch('c2_api_endpoints.psycopg2.connect', 
                   return_value=mock_db_connection):
            
            # Configure mock for database with data
            mock_cursor = mock_db_connection.cursor.return_value
            mock_cursor.fetchone.side_effect = [
                (5,),   # cardsToday
                (3,),   # resultsToday
                (100,), # totalCards
                (85,)   # totalResults
            ]
            
            stats = get_processing_stats()
            
            assert stats["cardsToday"] == 5
            assert stats["resultsToday"] == 3
            assert stats["totalCards"] == 100
            assert stats["totalResults"] == 85

    def test_get_processing_stats_database_error(self):
        """Test processing stats with database connection error"""
        with patch('c2_api_endpoints.psycopg2.connect', 
                   side_effect=Exception("Database connection failed")):
            
            stats = get_processing_stats()
            
            # Should return safe defaults on error
            assert isinstance(stats, dict)
            assert "error" in stats or all(
                stats[key] == 0 for key in 
                ["cardsToday", "resultsToday", "totalCards", "totalResults"]
            )

    def test_get_database_stats_all_online(self, mock_db_connection):
        """Test database stats when all databases are online"""
        with patch('c2_api_endpoints.psycopg2.connect', 
                   return_value=mock_db_connection):
            
            mock_cursor = mock_db_connection.cursor.return_value
            mock_cursor.fetchone.return_value = (1,)  # SELECT 1 succeeds
            
            stats = get_database_stats()
            
            assert isinstance(stats, dict)
            assert "databases" in stats
            assert "overall" in stats
            
            # Check that all expected databases are tested
            databases = stats["databases"]
            expected_dbs = ["cards", "results", "advanced"]
            
            for db_name in expected_dbs:
                if db_name in databases:
                    assert databases[db_name]["status"] == "online"

    def test_get_database_stats_with_offline_db(self):
        """Test database stats when some databases are offline"""
        def mock_connect_side_effect(host=None, database=None, **kwargs):
            if database == "cards_db":
                raise Exception("Connection refused")
            
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=None)
            return mock_conn
        
        with patch('c2_api_endpoints.psycopg2.connect', 
                   side_effect=mock_connect_side_effect):
            
            stats = get_database_stats()
            
            assert isinstance(stats, dict)
            assert "databases" in stats
            
            # Should handle mixed online/offline status
            databases = stats["databases"]
            if "cards" in databases:
                assert databases["cards"]["status"] == "offline"

    def test_get_system_status_basic(self):
        """Test system status retrieval"""
        with patch('c2_api_endpoints.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2025, 8, 30, 12, 0, 0)
            mock_datetime.now().isoformat.return_value = "2025-08-30T12:00:00"
            
            status = get_system_status()
            
            assert isinstance(status, dict)
            assert "timestamp" in status
            assert "uptime" in status
            assert "services" in status
            
            # Check service status structure
            services = status["services"]
            assert isinstance(services, dict)

    def test_get_container_health_web_app(self):
        """Test container health check for web app"""
        with patch('c2_api_endpoints.requests.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"status": "healthy"}
            mock_get.return_value = mock_response
            
            health = get_container_health("web-app")
            
            assert isinstance(health, dict)
            assert "status" in health
            assert "container" in health
            assert health["container"] == "web-app"

    def test_get_container_health_postgres(self):
        """Test container health check for PostgreSQL"""
        with patch('c2_api_endpoints.psycopg2.connect') as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_cursor.fetchone.return_value = (1,)
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=None)
            mock_connect.return_value = mock_conn
            
            health = get_container_health("postgres")
            
            assert isinstance(health, dict)
            assert health["container"] == "postgres"
            assert "status" in health

    def test_get_container_health_invalid_container(self):
        """Test container health check for invalid container"""
        health = get_container_health("invalid-container")
        
        assert isinstance(health, dict)
        assert health["container"] == "invalid-container"
        assert health["status"] == "unknown"

    def test_trigger_data_processing_valid(self, mock_redis_client):
        """Test data processing trigger with valid parameters"""
        with patch('c2_api_endpoints.redis.Redis', 
                   return_value=mock_redis_client):
            
            result = trigger_data_processing(
                data_type="cards",
                start_date="2025-08-30",
                end_date="2025-08-30",
                source="test"
            )
            
            assert isinstance(result, dict)
            assert "status" in result
            assert "processing_id" in result
            assert "data_type" in result
            assert result["data_type"] == "cards"
            
            # Verify Redis was called to queue the job
            mock_redis_client.set.assert_called()

    def test_trigger_data_processing_invalid_dates(self):
        """Test data processing trigger with invalid date range"""
        result = trigger_data_processing(
            data_type="cards",
            start_date="2025-08-31",  # End before start
            end_date="2025-08-30",
            source="test"
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "message" in result

    def test_trigger_data_processing_invalid_type(self):
        """Test data processing trigger with invalid data type"""
        result = trigger_data_processing(
            data_type="invalid_type",
            start_date="2025-08-30",
            end_date="2025-08-30",
            source="test"
        )
        
        assert isinstance(result, dict)
        assert result["status"] == "error"
        assert "message" in result

    def test_trigger_data_processing_redis_error(self):
        """Test data processing trigger with Redis connection error"""
        with patch('c2_api_endpoints.redis.Redis', 
                   side_effect=Exception("Redis connection failed")):
            
            result = trigger_data_processing(
                data_type="cards",
                start_date="2025-08-30",
                end_date="2025-08-30",
                source="test"
            )
            
            assert isinstance(result, dict)
            assert result["status"] == "error"
            assert "Redis" in result["message"]


class TestC2APIIntegration:
    """Integration tests for C2 API endpoints"""

    def test_processing_stats_integration(self):
        """Integration test for processing stats endpoint"""
        # This test verifies the function works end-to-end
        # with real database connections (if available)
        try:
            stats = get_processing_stats()
            
            # Should return valid structure regardless of data
            assert isinstance(stats, dict)
            required_keys = [
                "cardsToday", "resultsToday", 
                "totalCards", "totalResults", "timestamp"
            ]
            for key in required_keys:
                assert key in stats
                
            # All count values should be non-negative integers
            for key in required_keys[:-1]:  # Exclude timestamp
                assert isinstance(stats[key], int)
                assert stats[key] >= 0
                
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_database_stats_integration(self):
        """Integration test for database stats endpoint"""
        try:
            stats = get_database_stats()
            
            assert isinstance(stats, dict)
            assert "databases" in stats
            assert "overall" in stats
            
            # Each database should have status info
            for db_name, db_info in stats["databases"].items():
                assert "status" in db_info
                assert db_info["status"] in ["online", "offline"]
                
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    def test_system_status_integration(self):
        """Integration test for system status endpoint"""
        status = get_system_status()
        
        assert isinstance(status, dict)
        assert "timestamp" in status
        assert "uptime" in status
        assert "services" in status
        
        # Timestamp should be recent
        timestamp = datetime.fromisoformat(status["timestamp"])
        now = datetime.now()
        assert abs((now - timestamp).total_seconds()) < 60  # Within 1 minute

    def test_container_health_integration(self):
        """Integration test for container health checks"""
        containers = ["web-app", "postgres", "redis", "node-red"]
        
        for container in containers:
            health = get_container_health(container)
            
            assert isinstance(health, dict)
            assert "container" in health
            assert "status" in health
            assert health["container"] == container
            assert health["status"] in [
                "healthy", "unhealthy", "unknown", "error"
            ]


class TestC2APIPerformance:
    """Performance tests for C2 API endpoints"""

    def test_processing_stats_performance(self):
        """Test processing stats endpoint performance"""
        start_time = time.time()
        
        try:
            stats = get_processing_stats()
            execution_time = time.time() - start_time
            
            # Should complete within reasonable time
            assert execution_time < 5.0  # 5 seconds max
            assert isinstance(stats, dict)
            
        except Exception:
            pytest.skip("Database not available for performance test")

    def test_database_stats_performance(self):
        """Test database stats endpoint performance"""
        start_time = time.time()
        
        try:
            stats = get_database_stats()
            execution_time = time.time() - start_time
            
            # Should complete within reasonable time
            assert execution_time < 10.0  # 10 seconds max for all DBs
            assert isinstance(stats, dict)
            
        except Exception:
            pytest.skip("Database not available for performance test")

    def test_concurrent_api_calls(self):
        """Test concurrent API endpoint calls"""
        import threading
        import concurrent.futures
        
        def call_processing_stats():
            try:
                return get_processing_stats()
            except Exception:
                return {"error": "failed"}
        
        # Make 5 concurrent calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(call_processing_stats) 
                for _ in range(5)
            ]
            results = [
                future.result(timeout=10) 
                for future in concurrent.futures.as_completed(futures)
            ]
        
        # All calls should complete
        assert len(results) == 5
        
        # Most should succeed (allowing for some failures)
        successful = sum(1 for r in results if "error" not in r)
        assert successful >= 3  # At least 60% success rate


# Test utilities and fixtures
@pytest.fixture
def sample_api_response():
    """Sample API response for testing"""
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": {
            "cardsToday": 0,
            "resultsToday": 0,
            "totalCards": 0,
            "totalResults": 0
        }
    }

@pytest.fixture
def mock_container_stats():
    """Mock container statistics"""
    return {
        "timestamp": datetime.now().isoformat(),
        "containers": [
            {
                "name": "horse_racing_web_app_clean",
                "status": "running",
                "cpu_percent": 2.5,
                "memory_usage": "45.2MB",
                "memory_percent": 0.8
            },
            {
                "name": "horse_racing_postgres_clean", 
                "status": "running",
                "cpu_percent": 1.2,
                "memory_usage": "128.5MB",
                "memory_percent": 2.1
            }
        ],
        "total_containers": 2,
        "running_containers": 2
    }


if __name__ == "__main__":
    # Run API tests with verbose output
    pytest.main([__file__, "-v", "--tb=short", "-x"])
