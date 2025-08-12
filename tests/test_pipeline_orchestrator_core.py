#!/usr/bin/env python3
"""
Unit Tests for Daily Pipeline Orchestrator - Phase 3 Priority 1
Comprehensive testing of individual components and methods

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
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import after path setup
from daily_pipeline_orchestrator import DailyPipelineOrchestrator
from enhanced_error_handling import CircuitBreakerError


class TestPipelineOrchestratorCore:
    """Core unit tests for pipeline orchestrator"""

    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_orchestrator_initialization(self, mock_pool, mock_config_manager):
        """Test basic orchestrator initialization"""
        # Mock config manager
        mock_manager_instance = Mock()
        mock_manager_class = Mock(return_value=mock_manager_instance)
        mock_config_manager.return_value = mock_manager_class
        
        # Mock config object with all required attributes
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
        
        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()
        
        # Basic assertions
        assert orchestrator is not None
        assert orchestrator.config_manager is not None
        assert orchestrator.config is not None
        assert hasattr(orchestrator, 'circuit_breakers')
        assert hasattr(orchestrator, 'retry_handlers')
        assert hasattr(orchestrator, 'pipeline_status')

    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_circuit_breakers_created(self, mock_pool, mock_config_manager):
        """Test that all required circuit breakers are created"""
        # Setup mocks
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
        
        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()
        
        # Check circuit breakers exist
        expected_breakers = [
            "database",
            "auto_downloader",
            "relationships_pipeline",
            "analytics_scripts"
        ]
        
        for breaker_name in expected_breakers:
            assert breaker_name in orchestrator.circuit_breakers
            assert orchestrator.circuit_breakers[breaker_name] is not None

    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_retry_handlers_created(self, mock_pool, mock_config_manager):
        """Test that all required retry handlers are created"""
        # Setup mocks
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
        
        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()
        
        # Check retry handlers exist
        expected_handlers = [
            "database_operations",
            "external_scripts",
            "file_operations"
        ]
        
        for handler_name in expected_handlers:
            assert handler_name in orchestrator.retry_handlers
            assert orchestrator.retry_handlers[handler_name] is not None

    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_pipeline_status_initialization(self, mock_pool, mock_config_manager):
        """Test pipeline status is properly initialized"""
        # Setup mocks
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
        
        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()
        
        # Check pipeline status structure
        status = orchestrator.pipeline_status
        required_fields = [
            "last_run", "current_stage", "errors", "success_count",
            "failure_count", "stages_completed", "analytics_results",
            "circuit_breaker_metrics", "retry_metrics", "error_summary"
        ]
        
        for field in required_fields:
            assert field in status
        
        # Check initial values
        assert status["success_count"] == 0
        assert status["failure_count"] == 0
        assert isinstance(status["errors"], list)
        assert isinstance(status["stages_completed"], dict)

    @patch('daily_pipeline_orchestrator.create_config_manager')
    @patch('psycopg2.pool.ThreadedConnectionPool')
    def test_database_pool_initialization(self, mock_pool, mock_config_manager):
        """Test database connection pool initialization"""
        # Setup mocks
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
        
        # Mock pool instance
        mock_pool_instance = Mock()
        mock_pool.return_value = mock_pool_instance
        
        # Create orchestrator
        orchestrator = DailyPipelineOrchestrator()
        
        # Verify pool was called with correct parameters
        mock_pool.assert_called_once_with(
            1, 5,  # min, max connections
            host="localhost",
            port=5432,
            database="test_db",
            user="test_user",
            password="test_pass"
        )
        
        # Verify orchestrator has pool
        assert orchestrator.connection_pool == mock_pool_instance

    @patch('daily_pipeline_orchestrator.create_config_manager')
    def test_database_pool_failure_handling(self, mock_config_manager):
        """Test handling of database pool initialization failure"""
        # Setup mocks
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
        
        # Mock pool failure
        with patch('psycopg2.pool.ThreadedConnectionPool', 
                   side_effect=Exception("Connection failed")):
            with patch('daily_pipeline_orchestrator.logger') as mock_logger:
                orchestrator = DailyPipelineOrchestrator()
                
                # Pool should be None after failure
                assert orchestrator.connection_pool is None
                
                # Error should be logged
                mock_logger.error.assert_called_once()


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v", "--tb=short"])
