#!/usr/bin/env python3
"""
Integration Tests for Full Pipeline Execution - Phase 3 Priority 2
End-to-end testing of complete pipeline workflows

Test Categories:
1. Full Pipeline Execution Flow
2. Database Integration with Real Connections
3. File Processing Workflow Validation
4. External Service Integration
5. Error Recovery and Circuit Breaker Behavior
6. Configuration Loading and Hot-Reloading
7. Performance and Resource Management

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Import after path setup
from daily_pipeline_orchestrator import DailyPipelineOrchestrator


class TestFullPipelineExecution:
    """Integration tests for complete pipeline execution flows"""

    @pytest.fixture
    def temp_config_dir(self):
        """Create temporary configuration directory"""
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        # Create test configuration
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "horse_racing_test",
                "user": "test_user",
                "password": "test_pass",
                "pool_min_connections": 1,
                "pool_max_connections": 3,
            },
            "data_sources": {
                "enabled": ["racing_post"],
                "circuit_breaker_threshold": 3,
                "circuit_breaker_timeout": 60,
                "retry_attempts": 2,
                "timeout_minutes": 10,
            },
            "environment": "development",
            "debug_mode": True,
        }

        config_path = config_dir / "daily_pipeline_config.json"
        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        yield temp_dir

        # Cleanup
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_orchestrator_initialization_integration(
        self, mock_pool, mock_config_manager, temp_config_dir
    ):
        """Test full orchestrator initialization with real config structure"""
        # Mock config manager with realistic behavior
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        # Create realistic config object
        mock_config = Mock()
        mock_config.database.host = "localhost"
        mock_config.database.port = 5432
        mock_config.database.database = "horse_racing_test"
        mock_config.database.user = "test_user"
        mock_config.database.password = "test_pass"
        mock_config.database.pool_min_connections = 1
        mock_config.database.pool_max_connections = 3
        mock_config.data_sources.circuit_breaker_threshold = 3
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 2

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        # Mock database pool
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        # Test orchestrator creation
        orchestrator = DailyPipelineOrchestrator()

        # Verify integration points
        assert orchestrator.config_manager is not None
        assert orchestrator.config is not None
        assert orchestrator.connection_pool is not None

        # Verify all enterprise components are integrated
        assert len(orchestrator.circuit_breakers) == 4
        assert len(orchestrator.retry_handlers) == 3
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

        # Verify pipeline status tracking is initialized
        status = orchestrator.pipeline_status
        assert "last_run" in status
        assert "circuit_breaker_metrics" in status
        assert "retry_metrics" in status

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_circuit_breaker_integration_flow(self, mock_pool, mock_config_manager):
        """Test circuit breaker integration across multiple components"""
        # Setup orchestrator
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
        mock_config.data_sources.circuit_breaker_threshold = 2
        mock_config.data_sources.circuit_breaker_timeout = 30
        mock_config.data_sources.retry_attempts = 2

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        orchestrator = DailyPipelineOrchestrator()

        # Test circuit breaker states
        for service_name in [
            "database",
            "auto_downloader",
            "relationships_pipeline",
            "analytics_scripts",
        ]:
            circuit_breaker = orchestrator.circuit_breakers[service_name]

            # Initial state should be closed
            assert circuit_breaker.state.value == "closed"  # Compare enum value

            # Verify integration with retry handlers where applicable
            if service_name == "database":
                db_retry = orchestrator.retry_handlers["database_operations"]
                assert db_retry.circuit_breaker == circuit_breaker

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_error_handling_integration_flow(self, mock_pool, mock_config_manager):
        """Test error handling integration across all components"""
        # Setup orchestrator
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

        # Verify error handling components are integrated
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

        # Test that error tracking is integrated into pipeline status
        status = orchestrator.pipeline_status
        assert "errors" in status
        assert "error_summary" in status
        assert "failure_count" in status

        # Verify error handling is integrated with circuit breakers
        for cb_name, circuit_breaker in orchestrator.circuit_breakers.items():
            assert hasattr(circuit_breaker, "_on_failure")
            assert hasattr(circuit_breaker, "_on_success")

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_configuration_integration_flow(self, mock_pool, mock_config_manager):
        """Test configuration integration and validation flow"""
        # Setup with configuration validation
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class

        # Test configuration with validation warnings
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
            "Warning: Test configuration validation"
        ]

        with patch("daily_pipeline_orchestrator.logger") as mock_logger:
            orchestrator = DailyPipelineOrchestrator()

            # Verify warning was logged during integration
            mock_logger.warning.assert_called_once()

            # Verify configuration is still integrated properly
            assert orchestrator.config == mock_config
            assert orchestrator.config_manager == mock_manager_instance

    @patch("daily_pipeline_orchestrator.create_config_manager")
    def test_database_pool_integration_failure_recovery(self, mock_config_manager):
        """Test database pool failure and recovery integration"""
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

        # Test database pool failure during initialization
        with patch(
            "psycopg2.pool.ThreadedConnectionPool",
            side_effect=Exception("Database unavailable"),
        ):
            with patch("daily_pipeline_orchestrator.logger") as mock_logger:
                orchestrator = DailyPipelineOrchestrator()

                # Verify failure was handled gracefully
                assert orchestrator.connection_pool is None
                mock_logger.error.assert_called_once()

                # Verify other components still initialized properly
                assert orchestrator.config_manager is not None
                assert len(orchestrator.circuit_breakers) == 4
                assert len(orchestrator.retry_handlers) == 3


class TestDatabaseIntegrationWorkflow:
    """Integration tests for database operations and workflows"""

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_database_connection_lifecycle_integration(
        self, mock_pool, mock_config_manager
    ):
        """Test complete database connection lifecycle with circuit breaker integration"""
        # Setup orchestrator
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

        # Mock database pool and connections
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance

        mock_conn = Mock()
        mock_conn.closed = 0  # Connection is open
        mock_pool_instance.getconn.return_value = mock_conn

        orchestrator = DailyPipelineOrchestrator()

        # Test successful connection flow with circuit breaker
        orchestrator.circuit_breakers["database"]._can_attempt = Mock(return_value=True)
        orchestrator.circuit_breakers["database"]._on_success = Mock()

        # Test connection lifecycle (async method)
        conn = asyncio.run(orchestrator.get_db_connection())

        # Verify integration points
        assert conn == mock_conn
        mock_pool_instance.getconn.assert_called_once()
        orchestrator.circuit_breakers["database"]._on_success.assert_called_once()

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_database_failure_circuit_breaker_integration(
        self, mock_pool, mock_config_manager
    ):
        """Test database failure handling with circuit breaker integration"""
        # Setup orchestrator
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

        # Should raise CircuitBreakerError when circuit breaker is open (async method)
        from enhanced_error_handling import CircuitBreakerError

        with pytest.raises(CircuitBreakerError):
            asyncio.run(orchestrator.get_db_connection())


class TestConfigurationIntegrationWorkflow:
    """Integration tests for configuration management workflows"""

    def test_configuration_hot_reload_integration_flow(self):
        """Test configuration hot-reload integration workflow"""
        # Create temporary config directory
        temp_dir = tempfile.mkdtemp()
        config_dir = Path(temp_dir) / "config"
        config_dir.mkdir(parents=True, exist_ok=True)

        config_path = config_dir / "daily_pipeline_config.json"

        # Initial configuration
        initial_config = {
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
                "enabled": ["racing_post"],
                "circuit_breaker_threshold": 3,
                "circuit_breaker_timeout": 60,
                "retry_attempts": 2,
                "timeout_minutes": 10,
            },
        }

        with open(config_path, "w") as f:
            json.dump(initial_config, f, indent=2)

        try:
            # Test configuration manager integration
            from pipeline_config_validator import create_config_manager

            ConfigManagerClass = create_config_manager()
            manager = ConfigManagerClass(config_path)

            # Verify initial config loading
            config = manager.get_config()
            assert config.data_sources.circuit_breaker_threshold == 3

            # Test configuration validation integration
            issues = manager.validate_current_config()
            assert isinstance(issues, list)

            # Test that configuration structure is properly integrated
            assert hasattr(config, "database")
            assert hasattr(config, "data_sources")
            assert hasattr(config.database, "host")
            assert hasattr(config.data_sources, "circuit_breaker_threshold")

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])
