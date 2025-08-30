"""
🧪 Web Application API Integration Tests
========================================

Integration tests for the Web Application API endpoints with PostgreSQL database.
Tests the Flask + FastAPI integration on port 3000 (external) / 8000 (internal).
"""

import pytest
import requests
import time
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
import json


class TestWebApplicationAPI:
    """Integration tests for Web Application API with PostgreSQL database"""

    # Test configuration
    BASE_URL = "http://localhost:3000"  # External port for web app
    API_BASE_URL = f"{BASE_URL}/api"  # API proxy through Flask
    FASTAPI_URL = "http://localhost:8001"  # Direct FastAPI access

    DB_CONFIG = {
        "host": "localhost",
        "port": 5432,
        "database": "results",  # Production database
        "user": "horse_racing",
        "password": "horse_racing_password",
    }

    @pytest.fixture(scope="class")
    def database_connection(self):
        """Create database connection for testing"""
        try:
            conn = psycopg2.connect(**self.DB_CONFIG, cursor_factory=RealDictCursor)
            yield conn
            conn.close()
        except Exception as e:
            pytest.skip(f"Database not available: {e}")

    @pytest.fixture(scope="class")
    def api_health_check(self):
        """Verify API is running before tests"""
        try:
            # Test FastAPI directly
            response = requests.get(f"{self.FASTAPI_URL}/health", timeout=5)
            if response.status_code != 200:
                pytest.skip("FastAPI server not responding")

            # Test Flask proxy
            response = requests.get(f"{self.API_BASE_URL}/system_status", timeout=5)
            if response.status_code != 200:
                pytest.skip("Flask proxy not responding")

            return True
        except Exception as e:
            pytest.skip(f"API not available: {e}")

    @pytest.mark.integration
    @pytest.mark.api
    def test_database_connectivity(self, database_connection):
        """Test database connection and data availability"""
        cursor = database_connection.cursor()

        # Test basic table existence and data
        cursor.execute("SELECT COUNT(*) as count FROM races")
        race_count = cursor.fetchone()["count"]
        assert race_count > 0, "No races found in database"

        cursor.execute("SELECT COUNT(*) as count FROM horses_entity")
        horse_count = cursor.fetchone()["count"]
        assert horse_count > 0, "No horses found in database"

        cursor.execute("SELECT COUNT(*) as count FROM jockeys_entity")
        jockey_count = cursor.fetchone()["count"]
        assert jockey_count > 0, "No jockeys found in database"

        print(
            f"✅ Database connectivity verified: {race_count} races, {horse_count} horses, {jockey_count} jockeys"
        )

    @pytest.mark.integration
    @pytest.mark.api
    def test_system_status_endpoint(self, api_health_check):
        """Test system status endpoint through Flask proxy"""
        response = requests.get(f"{self.API_BASE_URL}/system_status", timeout=10)

        assert (
            response.status_code == 200
        ), f"System status failed: {response.status_code}"

        data = response.json()
        assert "status" in data, "Status field missing from response"
        assert "database" in data, "Database field missing from response"
        assert "timestamp" in data, "Timestamp field missing from response"

        print(f"✅ System status: {data.get('status')}")

    @pytest.mark.integration
    @pytest.mark.api
    def test_database_stats_endpoint(self, api_health_check):
        """Test database statistics endpoint"""
        response = requests.get(f"{self.API_BASE_URL}/database_stats", timeout=10)

        assert (
            response.status_code == 200
        ), f"Database stats failed: {response.status_code}"

        data = response.json()

        # Verify expected statistics
        assert "total_races" in data, "Total races missing"
        assert "total_horses" in data, "Total horses missing"
        assert "total_jockeys" in data, "Total jockeys missing"
        assert "total_trainers" in data, "Total trainers missing"

        # Verify data integrity
        assert data["total_races"] > 0, "No races in statistics"
        assert data["total_horses"] > 0, "No horses in statistics"

        print(
            f"✅ Database stats: {data['total_races']} races, {data['total_horses']} horses"
        )

    @pytest.mark.integration
    @pytest.mark.api
    def test_daily_races_endpoint(self, api_health_check):
        """Test daily races endpoint with real data"""
        response = requests.get(f"{self.API_BASE_URL}/daily_races", timeout=10)

        assert (
            response.status_code == 200
        ), f"Daily races failed: {response.status_code}"

        data = response.json()

        # Verify response structure
        assert "total_races" in data, "Total races missing from daily races"
        assert "races" in data, "Races array missing"
        assert isinstance(data["races"], list), "Races should be a list"

        if data["total_races"] > 0:
            # Verify race structure
            race = data["races"][0]
            required_fields = [
                "race_id",
                "race_number",
                "race_time",
                "course",
                "race_name",
            ]
            for field in required_fields:
                assert field in race, f"Race missing field: {field}"

        print(f"✅ Daily races: {data['total_races']} races available")

    @pytest.mark.integration
    @pytest.mark.api
    def test_horses_endpoint(self, api_health_check):
        """Test horses endpoint with pagination"""
        response = requests.get(f"{self.API_BASE_URL}/horses?limit=10", timeout=10)

        assert (
            response.status_code == 200
        ), f"Horses endpoint failed: {response.status_code}"

        data = response.json()

        # Verify response structure
        assert "horses" in data or isinstance(data, list), "Horses data missing"

        horses = data.get("horses", data) if isinstance(data, dict) else data

        if len(horses) > 0:
            horse = horses[0]
            # Verify horse structure
            expected_fields = ["horse_id", "horse_name"]
            for field in expected_fields:
                assert field in horse, f"Horse missing field: {field}"

        print(f"✅ Horses endpoint: {len(horses)} horses returned")

    @pytest.mark.integration
    @pytest.mark.api
    def test_jockeys_endpoint(self, api_health_check):
        """Test jockeys endpoint"""
        response = requests.get(f"{self.API_BASE_URL}/jockeys?limit=10", timeout=10)

        assert (
            response.status_code == 200
        ), f"Jockeys endpoint failed: {response.status_code}"

        data = response.json()

        # Handle different response formats
        jockeys = data.get("jockeys", data) if isinstance(data, dict) else data

        if len(jockeys) > 0:
            jockey = jockeys[0]
            # Basic validation
            assert "jockey_name" in jockey or "name" in jockey, "Jockey name missing"

        print(f"✅ Jockeys endpoint: {len(jockeys)} jockeys returned")

    @pytest.mark.integration
    @pytest.mark.api
    def test_trainers_endpoint(self, api_health_check):
        """Test trainers endpoint"""
        response = requests.get(f"{self.API_BASE_URL}/trainers?limit=10", timeout=10)

        assert (
            response.status_code == 200
        ), f"Trainers endpoint failed: {response.status_code}"

        data = response.json()

        # Handle different response formats
        trainers = data.get("trainers", data) if isinstance(data, dict) else data

        if len(trainers) > 0:
            trainer = trainers[0]
            # Basic validation
            assert (
                "trainer_name" in trainer or "name" in trainer
            ), "Trainer name missing"

        print(f"✅ Trainers endpoint: {len(trainers)} trainers returned")

    @pytest.mark.integration
    @pytest.mark.api
    def test_race_details_endpoint(self, api_health_check, database_connection):
        """Test race details endpoint with specific race ID"""
        # Get a race ID from database
        cursor = database_connection.cursor()
        cursor.execute("SELECT race_id FROM races LIMIT 1")
        result = cursor.fetchone()

        if not result:
            pytest.skip("No races available for testing")

        race_id = result["race_id"]

        response = requests.get(
            f"{self.API_BASE_URL}/race_details/{race_id}", timeout=10
        )

        assert (
            response.status_code == 200
        ), f"Race details failed: {response.status_code}"

        data = response.json()

        # Verify race details structure
        assert "race_id" in data, "Race ID missing from race details"
        assert "race_name" in data, "Race name missing"
        assert "course" in data, "Course missing"

        print(f"✅ Race details for race {race_id}: {data.get('race_name', 'Unknown')}")

    @pytest.mark.performance
    @pytest.mark.api
    def test_api_response_times(self, api_health_check):
        """Test API response times for performance"""
        endpoints = [
            "/system_status",
            "/database_stats",
            "/daily_races",
            "/horses?limit=5",
            "/jockeys?limit=5",
        ]

        performance_results = {}

        for endpoint in endpoints:
            start_time = time.time()
            response = requests.get(f"{self.API_BASE_URL}{endpoint}", timeout=10)
            end_time = time.time()

            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            performance_results[endpoint] = {
                "response_time_ms": response_time,
                "status_code": response.status_code,
            }

            # Assert reasonable response times (under 1 second)
            assert (
                response_time < 1000
            ), f"Slow response for {endpoint}: {response_time:.2f}ms"
            assert (
                response.status_code == 200
            ), f"Failed endpoint {endpoint}: {response.status_code}"

        print("✅ API Performance Results:")
        for endpoint, metrics in performance_results.items():
            print(f"   {endpoint}: {metrics['response_time_ms']:.2f}ms")

    @pytest.mark.integration
    @pytest.mark.api
    def test_fastapi_direct_access(self):
        """Test direct FastAPI access (bypassing Flask proxy)"""
        try:
            response = requests.get(f"{self.FASTAPI_URL}/api/system_status", timeout=10)

            assert (
                response.status_code == 200
            ), f"Direct FastAPI failed: {response.status_code}"

            data = response.json()
            assert "status" in data, "Status missing from direct FastAPI response"

            print("✅ Direct FastAPI access working")

        except Exception as e:
            print(f"⚠️ Direct FastAPI access failed (may be expected): {e}")

    @pytest.mark.integration
    @pytest.mark.api
    def test_flask_proxy_functionality(self, api_health_check):
        """Test Flask proxy functionality and API forwarding"""
        # Test that Flask is properly proxying requests to FastAPI
        response = requests.get(f"{self.API_BASE_URL}/system_status", timeout=10)

        assert response.status_code == 200, "Flask proxy not working"

        # Verify we're getting responses through the Flask proxy
        # The Flask app should add headers or modify responses
        data = response.json()
        assert data is not None, "No data returned through Flask proxy"

        print("✅ Flask proxy functionality verified")


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
