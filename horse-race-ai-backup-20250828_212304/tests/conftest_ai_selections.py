"""
🧪 AI Selections Test Configuration
==================================

Pytest configuration specifically for AI selection P&L tracking tests.
"""

import pytest
import os
import sys
from pathlib import Path

# Test-specific configuration
pytest_plugins = ["pytest_html", "pytest_cov"]

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root / "src" / "web"))
sys.path.append(str(project_root / "scripts"))


# Test markers
def pytest_configure(config):
    """Configure pytest markers for AI selection tests"""
    config.addinivalue_line("markers", "unit: Unit tests for individual components")
    config.addinivalue_line(
        "markers", "integration: Integration tests for system components"
    )
    config.addinivalue_line("markers", "performance: Performance and load tests")
    config.addinivalue_line("markers", "database: Database-related tests")
    config.addinivalue_line("markers", "api: Web API endpoint tests")


# Test environment variables
@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Set up test environment variables"""
    os.environ["TEST_MODE"] = "true"
    os.environ["TEST_DB_HOST"] = os.getenv("TEST_DB_HOST", "localhost")
    os.environ["TEST_DB_PORT"] = os.getenv("TEST_DB_PORT", "5432")
    os.environ["TEST_DB_NAME"] = os.getenv(
        "TEST_DB_NAME", "test_advanced_racing_metrics_db"
    )
    os.environ["TEST_DB_USER"] = os.getenv("TEST_DB_USER", "horse_racing")
    os.environ["TEST_DB_PASSWORD"] = os.getenv(
        "TEST_DB_PASSWORD", "secure_password_123"
    )


@pytest.fixture
def test_data_dir():
    """Test data directory fixture"""
    return Path(__file__).parent / "fixtures" / "ai_selections"


@pytest.fixture
def mock_performance_data():
    """Mock performance data for testing"""
    return {
        "total_predictions": 2378,
        "accuracy_rate": 27.2,
        "roi_percentage": 25.88,
        "total_profit_loss": 5996.99,
    }


@pytest.fixture
def mock_selection_data():
    """Mock selection data for testing"""
    return {
        "race_id": 155457,
        "horse_name": "Test Horse",
        "profit_loss": -10.0,
        "roi_percentage": -100.0,
        "race_result": "LOSE",
    }


# Custom test collection
def pytest_collection_modifyitems(config, items):
    """Modify test collection for AI selection tests"""
    for item in items:
        # Add markers based on test file location
        if "test_performance_api" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.api)
        elif "test_ai_migration" in item.nodeid:
            item.add_marker(pytest.mark.unit)
            item.add_marker(pytest.mark.database)
        elif "test_ai_selections_api" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.api)
        elif "test_ai_selections_db" in item.nodeid:
            item.add_marker(pytest.mark.integration)
            item.add_marker(pytest.mark.database)


# Test reporting
def pytest_html_report_title(report):
    """Customize HTML report title"""
    report.title = "AI Selections P&L Tracking Test Report"


def pytest_html_results_summary(prefix, summary, postfix):
    """Customize HTML report summary"""
    prefix.extend(
        [
            "<h2>AI Selections P&L Tracking System Tests</h2>",
            "<p>Comprehensive test results for the AI selection profit/loss tracking implementation.</p>",
            "<p><strong>Test Coverage:</strong></p>",
            "<ul>",
            "<li>Performance API (PostgreSQL integration)</li>",
            "<li>Migration scripts (data integrity)</li>",
            "<li>Web API endpoints (FastAPI)</li>",
            "<li>Database operations (PostgreSQL)</li>",
            "</ul>",
        ]
    )
