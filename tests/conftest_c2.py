"""
🎯 C2 Test Configuration and Utilities
=====================================

Test configuration, fixtures, and utilities for C2 Command Center testing.
Provides common test data, mocks, and helper functions.
"""

import pytest
import json
import time
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, MagicMock
from typing import Dict, List, Any, Optional


# Test Configuration
class C2TestConfig:
    """Configuration for C2 Command Center tests"""
    
    # URLs
    NODE_RED_URL = "http://localhost:1881"
    WEB_APP_URL = "http://localhost:3000"
    
    # Authentication
    VALID_API_KEY = "horse-racing-c2-secure-key-2025"
    VALID_BEARER_TOKEN = "demo-token"
    INVALID_API_KEY = "invalid-key-12345"
    
    # Database Configuration
    DB_HOST = "localhost"
    DB_PORT = 5432
    DB_USER = "postgres"
    DB_PASSWORD = "password123"
    DB_NAMES = {
        "cards": "cards_db",
        "results": "results_db", 
        "advanced": "advanced_db"
    }
    
    # Container Names
    CONTAINER_NAMES = {
        "web_app": "horse_racing_web_app_clean",
        "postgres": "horse_racing_postgres_clean",
        "node_red": "horse_racing_node_red_dashboard",
        "redis": "horse_racing_redis_clean"
    }
    
    # Test Timeouts
    TIMEOUT_SHORT = 5
    TIMEOUT_MEDIUM = 10
    TIMEOUT_LONG = 30
    
    # Performance Thresholds
    PERFORMANCE = {
        "dashboard_load_time": 5.0,
        "api_response_time": 3.0,
        "api_p95_response_time": 10.0,
        "concurrent_success_rate": 0.8,
        "memory_increase_limit": 100  # MB
    }
    
    # Test Data
    SAMPLE_NTFY_PAYLOAD = {
        "message": "Test notification from test suite",
        "priority": "3",
        "topic": "horse-racing-ai",
        "title": "Test Message"
    }
    
    SAMPLE_PROCESSING_TRIGGER = {
        "data_type": "cards",
        "start_date": "2025-08-30",
        "end_date": "2025-08-30",
        "source": "test_suite"
    }


# Test Fixtures
@pytest.fixture
def c2_config():
    """Provide C2 test configuration"""
    return C2TestConfig()


@pytest.fixture
def node_red_client(c2_config):
    """HTTP client for Node-RED endpoints"""
    import requests
    
    class NodeREDClient:
        def __init__(self, config):
            self.base_url = config.NODE_RED_URL
            self.timeout = config.TIMEOUT_MEDIUM
            self.session = requests.Session()
        
        def get(self, endpoint, headers=None, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return self.session.get(
                f"{self.base_url}{endpoint}", 
                headers=headers, 
                **kwargs
            )
        
        def post(self, endpoint, headers=None, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return self.session.post(
                f"{self.base_url}{endpoint}", 
                headers=headers, 
                **kwargs
            )
        
        def is_available(self):
            try:
                response = self.get("/", timeout=5)
                return response.status_code == 200
            except Exception:
                return False
        
        def authenticated_get(self, endpoint, api_key=None, **kwargs):
            """GET request with API key authentication"""
            headers = kwargs.pop('headers', {})
            if api_key:
                headers['X-API-Key'] = api_key
            return self.get(endpoint, headers=headers, **kwargs)
        
        def authenticated_post(self, endpoint, api_key=None, **kwargs):
            """POST request with API key authentication"""
            headers = kwargs.pop('headers', {})
            if api_key:
                headers['X-API-Key'] = api_key
            return self.post(endpoint, headers=headers, **kwargs)
    
    return NodeREDClient(c2_config)


@pytest.fixture
def web_app_client(c2_config):
    """HTTP client for Web App endpoints"""
    import requests
    
    class WebAppClient:
        def __init__(self, config):
            self.base_url = config.WEB_APP_URL
            self.timeout = config.TIMEOUT_MEDIUM
            self.session = requests.Session()
        
        def get(self, endpoint, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return self.session.get(f"{self.base_url}{endpoint}", **kwargs)
        
        def post(self, endpoint, **kwargs):
            kwargs.setdefault('timeout', self.timeout)
            return self.session.post(f"{self.base_url}{endpoint}", **kwargs)
        
        def is_available(self):
            try:
                response = self.get("/health", timeout=5)
                return response.status_code == 200
            except Exception:
                return False
    
    return WebAppClient(c2_config)


@pytest.fixture
def mock_database():
    """Mock database connection and cursor"""
    
    class MockCursor:
        def __init__(self):
            self.fetchone_return = None
            self.fetchall_return = []
            self.rowcount = 0
            self.executed_queries = []
        
        def execute(self, query, params=None):
            self.executed_queries.append((query, params))
        
        def fetchone(self):
            return self.fetchone_return
        
        def fetchall(self):
            return self.fetchall_return
        
        def close(self):
            pass
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            pass
    
    class MockConnection:
        def __init__(self):
            self.mock_cursor = MockCursor()
            self.closed = False
        
        def cursor(self):
            return self.mock_cursor
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def close(self):
            self.closed = True
        
        def __enter__(self):
            return self
        
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.close()
    
    return MockConnection()


@pytest.fixture
def mock_redis():
    """Mock Redis client"""
    
    class MockRedis:
        def __init__(self):
            self.data = {}
            self.connected = True
        
        def get(self, key):
            return self.data.get(key)
        
        def set(self, key, value, ex=None):
            self.data[key] = value
            return True
        
        def delete(self, key):
            return self.data.pop(key, None) is not None
        
        def ping(self):
            if not self.connected:
                raise Exception("Redis connection error")
            return True
        
        def keys(self, pattern="*"):
            return list(self.data.keys())
        
        def flushdb(self):
            self.data.clear()
            return True
    
    return MockRedis()


@pytest.fixture
def sample_processing_stats():
    """Sample processing statistics data"""
    return {
        "cardsToday": 0,
        "resultsToday": 0,
        "totalCards": 0,
        "totalResults": 0,
        "timestamp": datetime.now().isoformat(),
        "lastUpdate": datetime.now().isoformat(),
        "processingStatus": "idle"
    }


@pytest.fixture
def sample_database_stats():
    """Sample database statistics data"""
    return {
        "databases": {
            "cards": {
                "status": "online",
                "connection_count": 1,
                "last_check": datetime.now().isoformat()
            },
            "results": {
                "status": "online",
                "connection_count": 1,
                "last_check": datetime.now().isoformat()
            },
            "advanced": {
                "status": "online", 
                "connection_count": 1,
                "last_check": datetime.now().isoformat()
            }
        },
        "overall": {
            "status": "healthy",
            "total_databases": 3,
            "online_databases": 3,
            "timestamp": datetime.now().isoformat()
        }
    }


@pytest.fixture
def sample_container_status():
    """Sample container status data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "containers": [
            {
                "name": "web-app",
                "status": "running",
                "health": "healthy",
                "url": "http://horse_racing_web_app_clean:8000/health"
            },
            {
                "name": "postgres",
                "status": "running", 
                "health": "healthy",
                "url": "internal"
            },
            {
                "name": "redis",
                "status": "running",
                "health": "healthy", 
                "url": "internal"
            },
            {
                "name": "node-red",
                "status": "running",
                "health": "healthy",
                "url": "http://localhost:1881"
            }
        ],
        "total": 4,
        "healthy": 4,
        "running": 4
    }


@pytest.fixture
def sample_docker_stats():
    """Sample Docker statistics data"""
    return {
        "timestamp": datetime.now().isoformat(),
        "containers": [
            {
                "name": "horse_racing_web_app_clean",
                "status": "running",
                "cpu_percent": 2.5,
                "memory_usage": "45.2MB",
                "memory_percent": 0.8,
                "network_io": "1.2MB / 856KB",
                "block_io": "12.3MB / 4.1MB"
            },
            {
                "name": "horse_racing_postgres_clean",
                "status": "running", 
                "cpu_percent": 1.2,
                "memory_usage": "128.5MB",
                "memory_percent": 2.1,
                "network_io": "2.1MB / 1.8MB",
                "block_io": "45.2MB / 12.8MB"
            },
            {
                "name": "horse_racing_node_red_dashboard",
                "status": "running",
                "cpu_percent": 0.8,
                "memory_usage": "67.3MB", 
                "memory_percent": 1.1,
                "network_io": "892KB / 456KB",
                "block_io": "5.6MB / 2.1MB"
            }
        ],
        "total_containers": 3,
        "running_containers": 3,
        "system": {
            "cpu_count": 4,
            "memory_total": "8GB",
            "memory_available": "4.2GB"
        }
    }


# Test Utilities
class C2TestUtils:
    """Utility functions for C2 testing"""
    
    @staticmethod
    def wait_for_service(url, timeout=30, interval=1):
        """Wait for a service to become available"""
        import requests
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(interval)
        return False
    
    @staticmethod
    def measure_response_time(func, *args, **kwargs):
        """Measure function execution time"""
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            success = True
        except Exception as e:
            result = e
            success = False
        end_time = time.time()
        
        return {
            "result": result,
            "success": success,
            "response_time": end_time - start_time
        }
    
    @staticmethod
    def generate_test_data(size_kb=1):
        """Generate test data of specified size"""
        chars_per_kb = 1024
        return "A" * (size_kb * chars_per_kb)
    
    @staticmethod
    def validate_json_structure(data, required_keys):
        """Validate JSON data has required structure"""
        if not isinstance(data, dict):
            return False
        
        for key in required_keys:
            if key not in data:
                return False
        
        return True
    
    @staticmethod
    def create_temp_config(config_data):
        """Create temporary configuration file"""
        with tempfile.NamedTemporaryFile(
            mode='w', 
            suffix='.json', 
            delete=False
        ) as f:
            json.dump(config_data, f, indent=2)
            return f.name
    
    @staticmethod
    def cleanup_temp_file(file_path):
        """Clean up temporary file"""
        try:
            os.unlink(file_path)
        except FileNotFoundError:
            pass


@pytest.fixture
def test_utils():
    """Provide test utilities"""
    return C2TestUtils()


# Test Markers and Configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "system: marks tests as system/end-to-end tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add markers based on test file location
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
            item.add_marker(pytest.mark.slow)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "system" in str(item.fspath):
            item.add_marker(pytest.mark.system)
            item.add_marker(pytest.mark.slow)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)


# Pytest Fixtures for Session Management
@pytest.fixture(scope="session")
def c2_test_session():
    """Session-level fixture for C2 testing"""
    
    class C2TestSession:
        def __init__(self):
            self.start_time = time.time()
            self.test_results = []
            self.services_available = {}
        
        def check_service_availability(self):
            """Check which services are available for testing"""
            utils = C2TestUtils()
            
            services = {
                "node_red": "http://localhost:1881/",
                "web_app": "http://localhost:3000/health",
            }
            
            for service_name, url in services.items():
                self.services_available[service_name] = utils.wait_for_service(
                    url, timeout=10
                )
            
            return self.services_available
        
        def add_result(self, test_name, result):
            """Add test result to session tracking"""
            self.test_results.append({
                "test": test_name,
                "result": result,
                "timestamp": time.time()
            })
        
        def get_summary(self):
            """Get test session summary"""
            total_tests = len(self.test_results)
            passed_tests = sum(
                1 for r in self.test_results 
                if r["result"].get("passed", False)
            )
            duration = time.time() - self.start_time
            
            return {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "duration": duration,
                "services_available": self.services_available
            }
    
    session = C2TestSession()
    session.check_service_availability()
    
    yield session
    
    # Session teardown
    summary = session.get_summary()
    print(f"\nC2 Test Session Summary:")
    print(f"Tests: {summary['passed_tests']}/{summary['total_tests']} passed")
    print(f"Duration: {summary['duration']:.1f}s")
    print(f"Services: {summary['services_available']}")


if __name__ == "__main__":
    # Test the configuration
    config = C2TestConfig()
    print("C2 Test Configuration:")
    print(f"Node-RED URL: {config.NODE_RED_URL}")
    print(f"Web App URL: {config.WEB_APP_URL}")
    print(f"Database Host: {config.DB_HOST}:{config.DB_PORT}")
    print(f"Container Names: {config.CONTAINER_NAMES}")
    print(f"Performance Thresholds: {config.PERFORMANCE}")
