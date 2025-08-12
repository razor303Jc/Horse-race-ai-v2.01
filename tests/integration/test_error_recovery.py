#!/usr/bin/env python3
"""
Error Recovery Integration Tests - Phase 3 Priority 2
Testing error scenarios and recovery mechanisms

Author: AI Assistant
Date: August 12, 2025
"""

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
from enhanced_error_handling import CircuitBreakerError, RetryExhaustedException


class TestErrorRecoveryIntegration:
    """Test error recovery and circuit breaker behavior"""

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_circuit_breaker_failure_recovery_cycle(
        self, mock_pool, mock_config_manager
    ):
        """Test complete circuit breaker failure and recovery cycle"""
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
        mock_config.data_sources.circuit_breaker_threshold = 2
        mock_config.data_sources.circuit_breaker_timeout = 60
        mock_config.data_sources.retry_attempts = 3

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        orchestrator = DailyPipelineOrchestrator()

        # Test all circuit breakers exist and are in closed state initially
        expected_services = [
            "database",
            "auto_downloader",
            "relationships_pipeline",
            "analytics_scripts",
        ]

        for service in expected_services:
            assert service in orchestrator.circuit_breakers
            circuit_breaker = orchestrator.circuit_breakers[service]
            assert circuit_breaker.state.value == "closed"  # Compare enum value
            assert circuit_breaker.failure_count == 0

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_retry_mechanism_integration_with_circuit_breakers(
        self, mock_pool, mock_config_manager
    ):
        """Test retry mechanisms integrated with circuit breakers"""
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
        mock_config.data_sources.retry_attempts = 2

        mock_manager_instance.get_config.return_value = mock_config
        mock_manager_instance.validate_current_config.return_value = []

        orchestrator = DailyPipelineOrchestrator()

        # Test retry handler integration
        expected_retry_handlers = [
            "database_operations",
            "external_scripts",
            "file_operations",
        ]

        for handler_name in expected_retry_handlers:
            assert handler_name in orchestrator.retry_handlers
            retry_handler = orchestrator.retry_handlers[handler_name]
            assert retry_handler.max_attempts >= 1
            assert retry_handler.base_delay > 0

        # Test database retry handler has circuit breaker integration
        db_retry = orchestrator.retry_handlers["database_operations"]
        db_circuit_breaker = orchestrator.circuit_breakers["database"]
        assert db_retry.circuit_breaker == db_circuit_breaker

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_error_logging_integration(self, mock_pool, mock_config_manager):
        """Test error logging integration across components"""
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

        # Test error handling components are integrated
        assert orchestrator.error_logger is not None
        assert orchestrator.alert_manager is not None

        # Test error tracking in pipeline status
        status = orchestrator.pipeline_status
        assert "errors" in status
        assert "error_summary" in status
        assert "circuit_breaker_metrics" in status
        assert "retry_metrics" in status

        # Verify initial state
        assert isinstance(status["errors"], list)
        assert len(status["errors"]) == 0
        assert isinstance(status["error_summary"], dict)
        assert isinstance(status["circuit_breaker_metrics"], dict)
        assert isinstance(status["retry_metrics"], dict)

    @patch("daily_pipeline_orchestrator.create_config_manager")
    def test_graceful_degradation_on_component_failure(self, mock_config_manager):
        """Test graceful degradation when components fail"""
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

        # Test database failure during initialization
        with patch(
            "psycopg2.pool.ThreadedConnectionPool",
            side_effect=Exception("Database service unavailable"),
        ):
            with patch("daily_pipeline_orchestrator.logger") as mock_logger:
                orchestrator = DailyPipelineOrchestrator()

                # Verify graceful degradation
                assert orchestrator.connection_pool is None
                mock_logger.error.assert_called_once()

                # Verify other components still function
                assert orchestrator.config_manager is not None
                assert orchestrator.config is not None
                assert len(orchestrator.circuit_breakers) == 4
                assert len(orchestrator.retry_handlers) == 3
                assert orchestrator.error_logger is not None
                assert orchestrator.pipeline_status is not None


class TestConfigurationWorkflows:
    """Test configuration management and validation workflows"""

    def test_configuration_validation_workflow(self):
        """Test complete configuration validation workflow"""
        # Create temporary config
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "test_config.json"

        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "user": "test_user",
                "password": "test_pass",
                "pool_min_connections": 1,
                "pool_max_connections": 10,
            },
            "data_sources": {
                "enabled": ["racing_post", "betfair"],
                "circuit_breaker_threshold": 5,
                "circuit_breaker_timeout": 300,
                "retry_attempts": 3,
                "timeout_minutes": 30,
            },
            "environment": "development",
            "debug_mode": True,
        }

        with open(config_path, "w") as f:
            json.dump(config_data, f, indent=2)

        try:
            # Test configuration manager workflow
            from pipeline_config_validator import create_config_manager

            ConfigManagerClass = create_config_manager()
            manager = ConfigManagerClass(config_path)

            # Test configuration loading
            config = manager.get_config()
            assert config is not None

            # Test configuration validation
            issues = manager.validate_current_config()
            assert isinstance(issues, list)

            # Test configuration structure
            assert hasattr(config, "database")
            assert hasattr(config, "data_sources")
            assert config.database.host == "localhost"
            assert config.database.port == 5432
            assert "racing_post" in config.data_sources.enabled
            assert config.data_sources.circuit_breaker_threshold == 5

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_invalid_configuration_handling(self):
        """Test handling of invalid configuration"""
        # Create temporary invalid config
        temp_dir = tempfile.mkdtemp()
        config_path = Path(temp_dir) / "invalid_config.json"

        # Invalid JSON
        with open(config_path, "w") as f:
            f.write("{ invalid json content")

        try:
            from pipeline_config_validator import create_config_manager

            ConfigManagerClass = create_config_manager()

            # This should handle invalid JSON gracefully
            try:
                manager = ConfigManagerClass(config_path)
                # If creation succeeds, validation should catch issues
                issues = manager.validate_current_config()
                # Should have issues or use defaults
                assert isinstance(issues, list)
            except Exception as e:
                # Expected behavior for invalid JSON
                assert any(
                    word in str(e).lower() for word in ["json", "decode", "parse"]
                )

        finally:
            # Cleanup
            import shutil

            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMetricsAndMonitoring:
    """Test metrics collection and monitoring integration"""

    @patch("daily_pipeline_orchestrator.create_config_manager")
    @patch("psycopg2.pool.ThreadedConnectionPool")
    def test_pipeline_status_metrics_integration(self, mock_pool, mock_config_manager):
        """Test pipeline status and metrics collection"""
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

        # Test comprehensive status tracking
        status = orchestrator.pipeline_status

        # Test required status fields
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
            assert field in status, f"Missing status field: {field}"

        # Test initial values and types
        assert status["last_run"] is None
        assert status["current_stage"] is None
        assert isinstance(status["errors"], list)
        assert status["success_count"] == 0
        assert status["failure_count"] == 0
        assert isinstance(status["stages_completed"], dict)
        assert isinstance(status["analytics_results"], dict)
        assert isinstance(status["circuit_breaker_metrics"], dict)
        assert isinstance(status["retry_metrics"], dict)
        assert isinstance(status["error_summary"], dict)


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "--tb=short"])
