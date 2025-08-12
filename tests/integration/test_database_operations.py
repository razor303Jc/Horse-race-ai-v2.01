#!/usr/bin/env python3
"""
Database Integration Tests - Phase 3 Priority 2
Testing database operations with real/simulated connections

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import after path setup
from daily_pipeline_orchestrator import DailyPipelineOrchestrator
from enhanced_error_handling import CircuitBreakerError


class TestDatabaseOperations:
    """Test database operations and connection management"""

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_database_connection_flow(self, mock_pool, mock_config_manager):
        """Test complete database connection workflow"""
        # Setup configuration
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 5
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        # Mock database components
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        mock_conn = Mock()
        mock_conn.closed = 0
        mock_pool_instance.getconn.return_value = mock_conn

        # Create orchestrator and test connection
        orchestrator = DailyPipelineOrchestrator()

        # Mock circuit breaker behavior
        orchestrator.circuit_breakers["database"]._can_attempt = Mock(return_value=True)
        orchestrator.circuit_breakers["database"]._on_success = Mock()

        # Test connection retrieval (async method)
        conn = asyncio.run(orchestrator.get_db_connection())

        # Verify results
        assert conn == mock_conn
        mock_pool_instance.getconn.assert_called_once()
        orchestrator.circuit_breakers["database"]._on_success.assert_called_once()

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_circuit_breaker_database_protection(self, mock_pool, mock_config_manager):
        """Test circuit breaker protection for database operations"""
        # Setup
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 5
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        orchestrator = DailyPipelineOrchestrator()

        # Test circuit breaker open state
        orchestrator.circuit_breakers["database"]._can_attempt = Mock(
            return_value=False
        )

        # Should raise CircuitBreakerError (async method)
        with pytest.raises(CircuitBreakerError):
            asyncio.run(orchestrator.get_db_connection())

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_connection_pool_configuration(self, mock_pool, mock_config_manager):
        """Test database connection pool configuration"""
        # Setup
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 2
        mock_config.database.pool_max_connections = 8
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()

        # Verify pool was created with correct parameters
        mock_pool.assert_called_once_with(
            2,
            8,  # min, max connections from config
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass",
        )

        assert orchestrator.connection_pool == mock_pool_instance

    @patch("daily_pipeline_orchestrator.create_config_manager")
    def test_database_pool_failure_handling(self, mock_config_manager):
        """Test handling of database pool initialization failure"""
        # Setup
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 5
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        # Mock database pool failure
        with patch(
            "psycopg2.pool.ThreadedConnectionPool",
            side_effect=Exception("Connection failed"),
        ):
            with patch("daily_pipeline_orchestrator.logger") as mock_logger:
                orchestrator = DailyPipelineOrchestrator()

                # Verify failure was handled
                assert orchestrator.connection_pool is None
                mock_logger.error.assert_called_once()

                # Verify other components still work
                assert orchestrator.config_manager is not None
                assert len(orchestrator.circuit_breakers) == 4


class TestIntegratedWorkflows:
    """Test integrated workflows combining multiple components"""

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_full_initialization_workflow(self, mock_pool, mock_config_manager):
        """Test complete orchestrator initialization workflow"""
        # Setup realistic configuration
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "horse_racing_prod"
        mock_config.database.user = "pipeline_user"
        mock_config.database.password = "secure_password"
        mock_config.database.pool_min_connections = 2
        mock_config.database.pool_max_connections = 10
        mock_config.data_sources.circuit_breaker_threshold = 5
        mock_config.data_sources.circuit_breaker_timeout = 300
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        # Test full initialization
        orchestrator = DailyPipelineOrchestrator()

        # Verify all components are integrated
        assert orchestrator.config_manager is not None
        assert orchestrator.config is not None
        assert orchestrator.connection_pool is not None

        # Verify enterprise reliability components
        assert len(orchestrator.circuit_breakers) == 4
        assert len(orchestrator.retry_handlers) == 3
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

        # Verify circuit breaker integration with retry handlers
        db_retry = orchestrator.retry_handlers["database_operations"]
        assert db_retry.circuit_breaker == orchestrator.circuit_breakers["database"]

        # Verify pipeline status tracking
        status = orchestrator.pipeline_status
        required_fields = [
            "last_run",
            "current_stage",
            "errors",
            "success_count",
            "failure_count",
            "stages_completed",
            "analytics_results",
            "circuit_breaker_metrics",
            "retry_metrics",
            "error_summary",
        ]

        for field in required_fields:
            assert field in status

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_error_recovery_integration(self, mock_pool, mock_config_manager):
        """Test error recovery across integrated components"""
        # Setup
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "test_db"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 5
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        orchestrator = DailyPipelineOrchestrator()

        # Test error handling integration
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

        # Test that pipeline status tracks errors
        status = orchestrator.pipeline_status
        assert "errors" in status
        assert "error_summary" in status
        assert "failure_count" in status
        assert isinstance(status["errors"], list)
        assert isinstance(status["error_summary"], dict)
        assert status["failure_count"] == 0


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])
