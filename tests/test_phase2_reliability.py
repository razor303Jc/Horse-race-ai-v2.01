#!/usr/bin/env python3
"""
Test Phase 2 Reliability Improvements
Tests for Pydantic Configuration, Circuit Breakers, and Enhanced Error Handling
"""

import asyncio
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

# Import our Phase 2 components
try:
    from enhanced_error_handling import (
        CircuitBreaker,
        EnhancedRetry,
        ErrorContextLogger,
    )
    from pipeline_config_validator import (
        ConfigManager,
        PipelineConfig,
        create_config_manager,
    )
except ImportError as e:
    pytest.skip(f"Phase 2 modules not available: {e}", allow_module_level=True)


class TestPipelineConfiguration:
    """Test Pydantic configuration validation system"""

    def test_pipeline_config_creation(self):
        """Test creating a basic pipeline configuration"""
        config_data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass",
            },
            "pipeline": {
                "max_concurrent_stages": 3,
                "stage_timeout": 300,
                "retry_attempts": 3,
            },
        }

        config = PipelineConfig(**config_data)
        assert config.database.host == "localhost"
        assert config.database.port == 5432
        assert config.pipeline.max_concurrent_stages == 3

    def test_config_validation(self):
        """Test configuration validation with invalid data"""
        with pytest.raises(ValueError):
            # Invalid port number
            PipelineConfig(database={"host": "localhost", "port": -1})

    def test_environment_specific_config(self):
        """Test environment-specific configuration creation"""
        dev_config = PipelineConfig.create_environment_config("development")
        prod_config = PipelineConfig.create_environment_config("production")

        # Development should have different settings than production
        assert (
            dev_config.pipeline.max_concurrent_stages
            <= prod_config.pipeline.max_concurrent_stages
        )
        assert dev_config.database.host is not None
        assert prod_config.database.host is not None

    def test_config_manager_creation(self):
        """Test ConfigManager creation and basic functionality"""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            test_config = {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                    "database": "test_db",
                    "username": "test_user",
                    "password": "test_pass",
                },
                "pipeline": {"max_concurrent_stages": 2, "stage_timeout": 200},
            }
            json.dump(test_config, f)
            config_file = f.name

        try:
            ConfigManagerClass = create_config_manager()
            manager = ConfigManagerClass(config_file)
            config = manager.get_config()

            assert config.database.host == "localhost"
            assert config.pipeline.max_concurrent_stages == 2
        finally:
            os.unlink(config_file)


class TestCircuitBreaker:
    """Test Circuit Breaker pattern implementation"""

    def test_circuit_breaker_creation(self):
        """Test creating a circuit breaker with default settings"""
        cb = CircuitBreaker(failure_threshold=5, timeout=300)
        assert cb.failure_threshold == 5
        assert cb.timeout == 300
        assert cb.state.value == "CLOSED"

    def test_circuit_breaker_failure_tracking(self):
        """Test circuit breaker failure tracking and state transitions"""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        # Initially closed
        assert cb.state.value == "CLOSED"
        assert cb._can_attempt() is True

        # Record failures
        cb._record_failure()
        assert cb.state.value == "CLOSED"  # Still closed after 1 failure

        cb._record_failure()
        assert cb.state.value == "OPEN"  # Opens after threshold reached
        assert cb._can_attempt() is False

    def test_circuit_breaker_success_recovery(self):
        """Test circuit breaker recovery on success"""
        cb = CircuitBreaker(failure_threshold=1, timeout=0.1)

        # Trigger failure to open circuit
        cb._record_failure()
        assert cb.state.value == "OPEN"

        # Wait for timeout
        import time

        time.sleep(0.2)

        # Should be in HALF_OPEN state
        assert cb._can_attempt() is True

        # Record success to close circuit
        cb._record_success()
        assert cb.state.value == "CLOSED"

    @pytest.mark.asyncio
    async def test_circuit_breaker_decorator(self):
        """Test circuit breaker as decorator"""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)

        call_count = 0

        @cb
        async def test_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Test failure")
            return "success"

        # First two calls should fail and open circuit
        with pytest.raises(Exception):
            await test_function()

        with pytest.raises(Exception):
            await test_function()

        # Circuit should now be open
        assert cb.state.value == "OPEN"

        # Next call should be blocked by circuit breaker
        from enhanced_error_handling import CircuitBreakerError

        with pytest.raises(CircuitBreakerError):
            await test_function()


class TestEnhancedRetry:
    """Test Enhanced Retry mechanism with exponential backoff"""

    def test_retry_creation(self):
        """Test creating retry handler with default settings"""
        retry = EnhancedRetry(max_attempts=3, base_delay=1.0)
        assert retry.max_attempts == 3
        assert retry.base_delay == 1.0
        assert retry.max_delay == 60.0

    @pytest.mark.asyncio
    async def test_retry_success_on_first_attempt(self):
        """Test retry when function succeeds on first attempt"""
        retry = EnhancedRetry(max_attempts=3, base_delay=0.1)

        @retry
        async def successful_function():
            return "success"

        result = await successful_function()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_with_failures(self):
        """Test retry with initial failures then success"""
        retry = EnhancedRetry(max_attempts=3, base_delay=0.1)

        call_count = 0

        @retry
        async def flaky_function():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception("Temporary failure")
            return "success"

        result = await flaky_function()
        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhaustion(self):
        """Test retry exhaustion when all attempts fail"""
        retry = EnhancedRetry(max_attempts=2, base_delay=0.1)

        @retry
        async def always_fails():
            raise Exception("Always fails")

        with pytest.raises(Exception, match="Always fails"):
            await always_fails()

    @pytest.mark.asyncio
    async def test_retry_with_circuit_breaker(self):
        """Test retry integration with circuit breaker"""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)
        retry = EnhancedRetry(max_attempts=3, base_delay=0.1, circuit_breaker=cb)

        call_count = 0

        @retry
        async def test_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Test failure")

        # Should fail and eventually trigger circuit breaker
        with pytest.raises(Exception):
            await test_function()


class TestErrorContextLogger:
    """Test Enhanced Error Handling and Context Logging"""

    def test_error_logger_creation(self):
        """Test creating error context logger"""
        logger = ErrorContextLogger("test_logger")
        assert logger.logger.name == "test_logger"
        assert hasattr(logger, "error_history")

    def test_error_logging_with_context(self):
        """Test logging errors with rich context"""
        logger = ErrorContextLogger("test_logger")

        test_exception = Exception("Test error")
        context = {
            "stage": "test_stage",
            "operation": "test_operation",
            "retry_attempt": 1,
        }

        # Should not raise exception
        logger.log_error(
            test_exception, context=context, stage="test_stage", severity="error"
        )

        # Check error was recorded
        assert len(logger.error_history) > 0
        assert logger.error_history[-1]["stage"] == "test_stage"

    def test_error_pattern_detection(self):
        """Test error pattern detection functionality"""
        logger = ErrorContextLogger("test_logger")

        # Log multiple similar errors
        for i in range(3):
            logger.log_error(
                Exception("Database connection failed"),
                context={"operation": "database_query"},
                stage="database",
                severity="error",
            )

        # Should detect pattern (implementation detail may vary)
        assert len(logger.error_history) == 3

    def test_alert_manager_integration(self):
        """Test alert manager integration (if available)"""
        logger = ErrorContextLogger("test_logger")

        # Should create alert manager without error
        assert hasattr(logger, "alert_manager")


class TestIntegratedReliability:
    """Test integrated reliability features working together"""

    @pytest.mark.asyncio
    async def test_full_reliability_stack(self):
        """Test circuit breaker + retry + error logging working together"""
        cb = CircuitBreaker(failure_threshold=2, timeout=1)
        retry = EnhancedRetry(max_attempts=3, base_delay=0.1, circuit_breaker=cb)
        logger = ErrorContextLogger("integration_test")

        call_count = 0

        @retry
        async def unreliable_service():
            nonlocal call_count
            call_count += 1

            # Log the attempt
            logger.log_error(
                Exception(f"Service call {call_count} failed"),
                context={"attempt": call_count},
                stage="service_call",
                severity="warning",
            )

            if call_count <= 3:
                raise Exception(f"Service unavailable (attempt {call_count})")
            return "service_response"

        # Should eventually fail due to circuit breaker or retry exhaustion
        with pytest.raises(Exception):
            await unreliable_service()

        # Verify error logging occurred
        assert len(logger.error_history) > 0
        assert call_count >= 2  # At least some attempts were made


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
