#!/usr/bin/env python3
"""
Unit Tests for Daily Pipeline Orchestrator - Phase 3
Comprehensive testing of individual components and methods

Test Categories:
1. Initialization and Configuration
2. Database Connection Management
3. Circuit Breaker Operations
4. Retry Mechanisms
5. Pipeline Stage Execution
6. Error Handling and Logging
7. Status Tracking and Metrics
8. Configuration Hot-Reloading

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import json
import logging
import os
import sys
import tempfile
import unittest.mock as mock
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import psycopg2
import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from daily_pipeline_orchestrator import DailyPipelineOrchestrator
from enhanced_error_handling import CircuitBreakerError, RetryExhaustedException


class TestPipelineOrchestratorInitialization:
    """Test orchestrator initialization and configuration"""

    def setup_method(self):
        """Setup for each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "config" / "daily_pipeline_config.json"
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Create minimal valid config
        self.test_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "pool_min_connections": 1,
                "pool_max_connections": 5,
            },
            "data_sources": {
                "circuit_breaker_threshold": 3,
                "circuit_breaker_timeout": 60,
                "retry_attempts": 3,
            },
        }

        with open(self.config_path, "w") as f:
            json.dump(self.test_config, f)

    def teardown_method(self):
        """Cleanup after each test"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_orchestrator_creation_success(self, mock_pool, mock_config_manager):
        """Test successful orchestrator creation with valid configuration"""
        # Mock config manager
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        # Mock config object
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

        # Mock connection pool
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()

        # Assertions
        assert orchestrator is not None
        assert orchestrator.config_manager is not None
        assert orchestrator.config is not None
        assert orchestrator.connection_pool is not None
        assert len(orchestrator.circuit_breakers) == 4
        assert len(orchestrator.retry_handlers) == 3
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

    @patch("daily_pipeline_orchestrator.create_config_manager")
    def test_orchestrator_config_validation_warnings(self, mock_config_manager):
        """Test orchestrator handles configuration validation warnings"""
        # Mock config manager with validation issues
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
        mock_manager_instance.validate_current_config.return_value = [
            "Warning: test issue"
        ]

        with patch("psycopg2.pool.ThreadedConnectionPool"):
            with patch("daily_pipeline_orchestrator.logger") as mock_logger:
                DailyPipelineOrchestrator()

                # Check that warning was logged
                mock_logger.warning.assert_called_once()

    @patch("daily_pipeline_orchestrator.create_config_manager")
    def test_orchestrator_database_pool_failure(self, mock_config_manager):
        """Test orchestrator handles database pool initialization failure"""
        # Mock config manager
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
            side_effect=Exception("DB connection failed"),
        ):
            with patch("daily_pipeline_orchestrator.logger") as mock_logger:
                orchestrator = DailyPipelineOrchestrator()

                # Check that error was logged and pool is None
                mock_logger.error.assert_called_once()
                assert orchestrator.connection_pool is None


class TestDatabaseConnectionManagement:
    """Test database connection management and pool operations"""

    def setup_method(self):
        """Setup for each test"""
        self.orchestrator = self._create_mock_orchestrator()

    def _create_mock_orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    @patch("daily_pipeline_orchestrator.logger")
    def test_get_db_connection_success(self, mock_logger):
        """Test successful database connection retrieval"""
        # Mock connection pool
        mock_conn = Mock()
        mock_conn.closed = 0  # Connection is open
        self.orchestrator.connection_pool = Mock()
        self.orchestrator.connection_pool.getconn.return_value = mock_conn

        # Mock circuit breaker
        self.orchestrator.circuit_breakers["database"]._can_attempt = Mock(
            return_value=True
        )
        self.orchestrator.circuit_breakers["database"]._on_success = Mock()

        # Test connection retrieval
        conn = self.orchestrator.get_db_connection()

        # Assertions
        assert conn == mock_conn
        self.orchestrator.circuit_breakers["database"]._on_success.assert_called_once()

    def test_get_db_connection_circuit_breaker_open(self):
        """Test database connection when circuit breaker is open"""
        # Mock circuit breaker as open
        self.orchestrator.circuit_breakers["database"]._can_attempt = Mock(
            return_value=False
        )

        # Test connection retrieval raises CircuitBreakerError
        with pytest.raises(CircuitBreakerError):
            self.orchestrator.get_db_connection()

    def test_get_db_connection_no_pool(self):
        """Test database connection when pool is not initialized"""
        self.orchestrator.connection_pool = None

        # Test connection retrieval raises exception
        with pytest.raises(Exception, match="Database connection pool not initialized"):
            self.orchestrator.get_db_connection()

    def test_get_db_connection_closed_connection_recovery(self):
        """Test recovery when getting a closed connection from pool"""
        # Mock closed connection, then open connection
        mock_closed_conn = Mock()
        mock_closed_conn.closed = 1  # Connection is closed
        mock_open_conn = Mock()
        mock_open_conn.closed = 0  # Connection is open

        self.orchestrator.connection_pool = Mock()
        self.orchestrator.connection_pool.getconn.side_effect = [
            mock_closed_conn,
            mock_open_conn,
        ]
        self.orchestrator.connection_pool.putconn = Mock()

        # Mock circuit breaker
        self.orchestrator.circuit_breakers["database"]._can_attempt = Mock(
            return_value=True
        )
        self.orchestrator.circuit_breakers["database"]._on_success = Mock()

        # Test connection retrieval
        conn = self.orchestrator.get_db_connection()

        # Assertions
        assert conn == mock_open_conn
        self.orchestrator.connection_pool.putconn.assert_called_once_with(
            mock_closed_conn
        )


class TestCircuitBreakerOperations:
    """Test circuit breaker functionality and integration"""

    def setup_method(self):
        """Setup for each test"""
        self.orchestrator = self._create_mock_orchestrator()

    def _create_mock_orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    def test_circuit_breakers_initialization(self):
        """Test that all circuit breakers are properly initialized"""
        expected_breakers = [
            "database",
            "auto_downloader",
            "relationships_pipeline",
            "analytics_scripts",
        ]

        for breaker_name in expected_breakers:
            assert breaker_name in self.orchestrator.circuit_breakers
            breaker = self.orchestrator.circuit_breakers[breaker_name]
            assert breaker is not None
            assert breaker.name == breaker_name

    def test_circuit_breaker_integration_with_retry(self):
        """Test circuit breaker integration with retry handlers"""
        # Database retry handler should have database circuit breaker
        db_retry = self.orchestrator.retry_handlers["database_operations"]
        assert (
            db_retry.circuit_breaker == self.orchestrator.circuit_breakers["database"]
        )

        # Other retry handlers may or may not have circuit breakers
        external_retry = self.orchestrator.retry_handlers["external_scripts"]
        file_retry = self.orchestrator.retry_handlers["file_operations"]

        # These should exist and be properly configured
        assert external_retry is not None
        assert file_retry is not None

    def test_circuit_breaker_metrics_tracking(self):
        """Test that circuit breaker metrics are tracked in pipeline status"""
        # Pipeline status should have circuit breaker metrics
        assert "circuit_breaker_metrics" in self.orchestrator.pipeline_status

        # Initially should be empty dict
        assert isinstance(
            self.orchestrator.pipeline_status["circuit_breaker_metrics"], dict
        )


class TestRetryMechanisms:
    """Test retry mechanism functionality and configuration"""

    def setup_method(self):
        """Setup for each test"""
        self.orchestrator = self._create_mock_orchestrator()

    def _create_mock_orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    def test_retry_handlers_initialization(self):
        """Test that all retry handlers are properly initialized"""
        expected_handlers = [
            "database_operations",
            "external_scripts",
            "file_operations",
        ]

        for handler_name in expected_handlers:
            assert handler_name in self.orchestrator.retry_handlers
            handler = self.orchestrator.retry_handlers[handler_name]
            assert handler is not None
            assert handler.name == handler_name

    def test_retry_configuration_parameters(self):
        """Test retry handler configuration parameters"""
        # Database operations retry
        db_retry = self.orchestrator.retry_handlers["database_operations"]
        assert db_retry.max_attempts >= 1
        assert db_retry.base_delay > 0

        # External scripts retry
        external_retry = self.orchestrator.retry_handlers["external_scripts"]
        assert external_retry.max_attempts >= 1
        assert external_retry.base_delay > 0

        # File operations retry
        file_retry = self.orchestrator.retry_handlers["file_operations"]
        assert file_retry.max_attempts >= 1
        assert file_retry.base_delay > 0

    def test_retry_metrics_tracking(self):
        """Test that retry metrics are tracked in pipeline status"""
        # Pipeline status should have retry metrics
        assert "retry_metrics" in self.orchestrator.pipeline_status

        # Initially should be empty dict
        assert isinstance(self.orchestrator.pipeline_status["retry_metrics"], dict)


class TestStatusTrackingAndMetrics:
    """Test pipeline status tracking and metrics collection"""

    def setup_method(self):
        """Setup for each test"""
        self.orchestrator = self._create_mock_orchestrator()

    def _create_mock_orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    def test_pipeline_status_initialization(self):
        """Test that pipeline status is properly initialized"""
        status = self.orchestrator.pipeline_status

        # Check all required fields exist
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

    def test_status_field_types(self):
        """Test that status fields have correct types"""
        status = self.orchestrator.pipeline_status

        # Check types
        assert status["last_run"] is None or isinstance(
            status["last_run"], (str, type(None))
        )
        assert status["current_stage"] is None or isinstance(
            status["current_stage"], str
        )
        assert isinstance(status["errors"], list)
        assert isinstance(status["success_count"], int)
        assert isinstance(status["failure_count"], int)
        assert isinstance(status["stages_completed"], dict)
        assert isinstance(status["analytics_results"], dict)
        assert isinstance(status["circuit_breaker_metrics"], dict)
        assert isinstance(status["retry_metrics"], dict)
        assert isinstance(status["error_summary"], dict)

    def test_status_initial_values(self):
        """Test initial values of status fields"""
        status = self.orchestrator.pipeline_status

        assert status["last_run"] is None
        assert status["current_stage"] is None
        assert status["errors"] == []
        assert status["success_count"] == 0
        assert status["failure_count"] == 0
        assert status["stages_completed"] == {}
        assert status["analytics_results"] == {}
        assert status["circuit_breaker_metrics"] == {}
        assert status["retry_metrics"] == {}
        assert status["error_summary"] == {}


class TestErrorHandlingAndLogging:
    """Test error handling and logging functionality"""

    def setup_method(self):
        """Setup for each test"""
        self.orchestrator = self._create_mock_orchestrator()

    def _create_mock_orchestrator(self):
        """Create orchestrator with mocked dependencies"""
        with patch("daily_pipeline_orchestrator.create_config_manager"):
            with patch("psycopg2.pool.ThreadedConnectionPool"):
                return DailyPipelineOrchestrator()

    def test_error_logger_initialization(self):
        """Test that error logger is properly initialized"""
        assert self.orchestrator.error_logger is not None
        # Error logger should have a name/category
        assert hasattr(self.orchestrator.error_logger, "_category")

    def test_alert_manager_initialization(self):
        """Test that alert manager is properly initialized"""
        assert self.orchestrator.alert_manager is not None

    def test_error_summary_tracking(self):
        """Test that error summary is tracked in pipeline status"""
        assert "error_summary" in self.orchestrator.pipeline_status
        assert isinstance(self.orchestrator.pipeline_status["error_summary"], dict)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
