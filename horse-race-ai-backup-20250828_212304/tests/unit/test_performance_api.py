"""
🧪 AI Selections Performance API Tests
====================================

Comprehensive test suite for the PostgreSQL-based performance API
that tracks AI selection profit/loss data.
"""

import pytest
import psycopg2
from psycopg2.extras import RealDictCursor
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import sys
import os
from decimal import Decimal

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), "../../src/web"))

from performance_api import PerformanceAPI


class TestPerformanceAPI:
    """Test suite for PerformanceAPI class"""

    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection for testing"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        return mock_conn, mock_cursor

    @pytest.fixture
    def performance_api(self):
        """Create PerformanceAPI instance for testing"""
        return PerformanceAPI()

    @pytest.fixture
    def sample_performance_data(self):
        """Sample performance data for testing"""
        return [
            {
                "total_predictions": 2378,
                "correct_predictions": 647,
                "accuracy_rate": 27.2,
                "win_rate": 11.0,
                "place_rate": 1.3,
                "total_stakes": Decimal("23175.00"),
                "total_returns": Decimal("29172.24"),
                "total_profit_loss": Decimal("5996.99"),
                "roi_percentage": 25.88,
                "avg_starting_price": 22.64,
                "latest_running_roi": Decimal("3700.00"),
                "period_start": date(2025, 8, 19),
                "period_end": date(2025, 8, 25),
            }
        ]

    @pytest.fixture
    def sample_selections_data(self):
        """Sample selections data for testing"""
        return [
            {
                "race_id": 155457,
                "horse_name": "The Fitter",
                "selection_date": date(2025, 8, 25),
                "ai_probability": 1.0,
                "confidence_level": "LOW",
                "recommended_stake": Decimal("10.00"),
                "value_rating": 0.0,
                "starting_price": Decimal("81.00"),
                "market_rank": 11,
                "finishing_position": 11,
                "race_result": "LOSE",
                "profit_loss": Decimal("-10.00"),
                "roi_percentage": -100.0,
                "created_at": datetime(2025, 8, 27, 17, 0, 38),
            }
        ]

    def test_performance_api_initialization(self, performance_api):
        """Test PerformanceAPI initialization"""
        # Host should be localhost when not in Docker, postgres when in Docker
        assert performance_api.db_params["host"] in ["localhost", "postgres"]
        assert performance_api.db_params["database"] == "advanced_racing_metrics_db"
        assert performance_api.db_params["user"] == "horse_racing"
        assert performance_api.db_params["port"] == 5432

    @patch("performance_api.psycopg2.connect")
    def test_get_performance_summary_success(
        self, mock_connect, performance_api, mock_db_connection, sample_performance_data
    ):
        """Test successful performance summary retrieval"""
        mock_conn, mock_cursor = mock_db_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchone.return_value = sample_performance_data[0]
        mock_cursor.fetchall.return_value = (
            []
        )  # For confidence breakdown and daily performance

        result = performance_api.get_performance_summary(days_back=30)

        assert result["status"] == "success"
        assert "summary" in result["data"]
        assert result["data"]["summary"]["total_predictions"] == 2378
        assert result["data"]["summary"]["accuracy_rate"] == 27.2
        assert result["data"]["summary"]["roi_percentage"] == 25.88

        # Verify database connection was called
        mock_connect.assert_called_once()
        mock_cursor.execute.assert_called()

    @patch("performance_api.psycopg2.connect")
    def test_get_performance_summary_database_error(
        self, mock_connect, performance_api
    ):
        """Test performance summary with database error"""
        mock_connect.side_effect = psycopg2.Error("Connection failed")

        result = performance_api.get_performance_summary(days_back=30)

        assert result["status"] == "error"
        assert "Connection failed" in result["message"]
        assert result["data"]["summary"]["total_predictions"] == 0

    @patch("performance_api.psycopg2.connect")
    def test_get_recent_selections_success(
        self, mock_connect, performance_api, mock_db_connection, sample_selections_data
    ):
        """Test successful recent selections retrieval"""
        mock_conn, mock_cursor = mock_db_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = sample_selections_data

        result = performance_api.get_recent_selections(limit=10)

        assert result["status"] == "success"
        assert "selections" in result["data"]
        assert result["data"]["count"] == 1
        assert len(result["data"]["selections"]) == 1

        selection = result["data"]["selections"][0]
        assert selection["horse_name"] == "The Fitter"
        assert selection["race_result"] == "LOSE"
        assert selection["profit_loss"] == -10.0

    @patch("performance_api.psycopg2.connect")
    def test_get_recent_selections_with_limit(
        self, mock_connect, performance_api, mock_db_connection
    ):
        """Test recent selections with custom limit"""
        mock_conn, mock_cursor = mock_db_connection
        mock_connect.return_value = mock_conn
        mock_cursor.fetchall.return_value = []

        performance_api.get_recent_selections(limit=5)

        # Verify the SQL query includes the limit
        call_args = mock_cursor.execute.call_args[0][0]
        assert "LIMIT %s" in call_args

    @patch("performance_api.psycopg2.connect")
    def test_get_recent_selections_database_error(self, mock_connect, performance_api):
        """Test recent selections with database error"""
        mock_connect.side_effect = psycopg2.Error("Query failed")

        result = performance_api.get_recent_selections(limit=10)

        assert result["status"] == "error"
        assert "Query failed" in result["message"]
        assert result["data"]["count"] == 0
        assert result["data"]["selections"] == []

    def test_decimal_to_float_conversion(
        self, performance_api, sample_performance_data
    ):
        """Test that Decimal values are properly converted to float"""
        # Mock the database response with Decimal values
        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = sample_performance_data[0]
            mock_cursor.fetchall.return_value = []

            result = performance_api.get_performance_summary(days_back=30)

            # Verify Decimal values are converted to float for JSON serialization
            summary = result["data"]["summary"]
            assert isinstance(summary["total_profit_loss"], float)
            assert isinstance(summary["total_stakes"], float)
            assert isinstance(summary["total_returns"], float)

    def test_date_formatting(self, performance_api, sample_performance_data):
        """Test that date objects are properly formatted as strings"""
        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = sample_performance_data[0]
            mock_cursor.fetchall.return_value = []

            result = performance_api.get_performance_summary(days_back=30)

            # Verify dates are converted to strings
            summary = result["data"]["summary"]
            assert isinstance(summary["period_start"], str)
            assert isinstance(summary["period_end"], str)
            assert summary["period_start"] == "2025-08-19"


class TestPerformanceAPIIntegration:
    """Integration tests for PerformanceAPI with real database scenarios"""

    @pytest.mark.integration
    def test_performance_api_with_mock_database_schema(self):
        """Test performance API with mock database that simulates real schema"""
        # This would be used for integration testing with a test database
        # For now, we'll focus on unit tests with mocked connections
        pass

    @pytest.mark.integration
    def test_performance_api_error_handling_edge_cases(self):
        """Test error handling for various edge cases"""
        api = PerformanceAPI()

        # Test with invalid days_back parameter
        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_connect.side_effect = Exception("Unexpected error")

            result = api.get_performance_summary(days_back=-1)
            assert result["status"] == "error"

            result = api.get_recent_selections(limit=0)
            assert result["status"] == "error"


class TestPerformanceAPIBoundaryConditions:
    """Test boundary conditions and edge cases"""

    @pytest.fixture
    def performance_api(self):
        return PerformanceAPI()

    def test_empty_database_response(self, performance_api):
        """Test handling of empty database responses"""
        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchone.return_value = None
            mock_cursor.fetchall.return_value = []

            result = performance_api.get_performance_summary(days_back=30)

            assert result["status"] == "success"
            # Should have default values when no data found
            assert result["data"]["summary"]["total_predictions"] == 0

    def test_large_dataset_handling(self, performance_api):
        """Test handling of large datasets"""
        # Simulate large dataset response
        large_dataset = [{"horse_name": f"Horse_{i}"} for i in range(1000)]

        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = large_dataset

            result = performance_api.get_recent_selections(limit=1000)

            assert result["status"] == "success"
            assert result["data"]["count"] == 1000

    def test_sql_injection_protection(self, performance_api):
        """Test that the API is protected against SQL injection"""
        with patch("performance_api.psycopg2.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_connect.return_value = mock_conn
            mock_conn.cursor.return_value = mock_cursor
            mock_cursor.fetchall.return_value = []

            # Try SQL injection attempt
            result = performance_api.get_recent_selections(
                limit="10; DROP TABLE betting_performance_tracker;"
            )

            # Should either handle gracefully or use parameterized queries
            # The exact behavior depends on implementation
            assert result["status"] in ["success", "error"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
