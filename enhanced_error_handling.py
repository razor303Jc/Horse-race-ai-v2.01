#!/usr/bin/env python3
"""
🔧 Phase 2: Enhanced Error Handling & Circuit Breaker
Advanced retry mechanisms and circuit breaker pattern implementation

This implements:
1. Circuit breaker pattern for external dependencies
2. Enhanced retry mechanisms with exponential backoff
3. Graceful degradation when services are unavailable
4. Comprehensive error logging with context
5. Alert system for critical failures

Author: AI Assistant
Date: August 12, 2025
"""

import asyncio
import time
import logging
import functools
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from enum import Enum
import json
from pathlib import Path


class CircuitBreakerState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"       # Normal operation
    OPEN = "open"           # Failing, blocking requests
    HALF_OPEN = "half_open" # Testing if service recovered


class CircuitBreakerError(Exception):
    """Circuit breaker is open, blocking requests."""
    pass


class RetryExhaustedException(Exception):
    """All retry attempts have been exhausted."""
    pass


class CircuitBreaker:
    """Circuit breaker pattern implementation for external services."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: int = 300,  # 5 minutes
        expected_exception: type = Exception,
        name: str = "default"
    ):
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds to wait before trying again
            expected_exception: Exception type to count as failure
            name: Name for logging/monitoring
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.expected_exception = expected_exception
        self.name = name
        
        # State tracking
        self.state = CircuitBreakerState.CLOSED
        self.failure_count = 0
        self.last_failure_time = None
        self.success_count = 0
        
        # Logging
        self.logger = logging.getLogger(f"circuit_breaker.{name}")
        
        # Metrics
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "circuit_opened_count": 0,
            "last_opened": None,
            "state_changes": []
        }

    def _can_attempt(self) -> bool:
        """Check if we can attempt the operation."""
        if self.state == CircuitBreakerState.CLOSED:
            return True
        elif self.state == CircuitBreakerState.OPEN:
            # Check if timeout has passed
            if (time.time() - self.last_failure_time) >= self.timeout:
                self._change_state(CircuitBreakerState.HALF_OPEN)
                return True
            return False
        elif self.state == CircuitBreakerState.HALF_OPEN:
            return True
        return False

    def _change_state(self, new_state: CircuitBreakerState):
        """Change circuit breaker state."""
        old_state = self.state
        self.state = new_state
        
        # Log state change
        self.logger.info(f"Circuit breaker '{self.name}' state: {old_state.value} -> {new_state.value}")
        
        # Track metrics
        self.metrics["state_changes"].append({
            "timestamp": datetime.now().isoformat(),
            "from_state": old_state.value,
            "to_state": new_state.value,
            "failure_count": self.failure_count
        })
        
        if new_state == CircuitBreakerState.OPEN:
            self.metrics["circuit_opened_count"] += 1
            self.metrics["last_opened"] = datetime.now().isoformat()

    def _on_success(self):
        """Handle successful operation."""
        self.success_count += 1
        self.metrics["successful_requests"] += 1
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Service has recovered, close circuit
            self._change_state(CircuitBreakerState.CLOSED)
            self.failure_count = 0
            self.logger.info(f"Service '{self.name}' recovered, circuit closed")

    def _on_failure(self, exception: Exception):
        """Handle failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        self.metrics["failed_requests"] += 1
        
        self.logger.warning(f"Service '{self.name}' failure #{self.failure_count}: {exception}")
        
        if self.state == CircuitBreakerState.HALF_OPEN:
            # Still failing, open circuit again
            self._change_state(CircuitBreakerState.OPEN)
        elif self.state == CircuitBreakerState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                # Too many failures, open circuit
                self._change_state(CircuitBreakerState.OPEN)
                self.logger.error(f"Circuit breaker '{self.name}' opened after {self.failure_count} failures")

    def get_metrics(self) -> Dict:
        """Get circuit breaker metrics."""
        return {
            **self.metrics,
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_threshold": self.failure_threshold,
            "timeout": self.timeout
        }

    def __call__(self, func: Callable) -> Callable:
        """Decorator to wrap functions with circuit breaker."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            self.metrics["total_requests"] += 1
            
            if not self._can_attempt():
                raise CircuitBreakerError(f"Circuit breaker '{self.name}' is open")
            
            try:
                result = await func(*args, **kwargs)
                self._on_success()
                return result
            except self.expected_exception as e:
                self._on_failure(e)
                raise
        
        return wrapper


class EnhancedRetry:
    """Enhanced retry mechanism with exponential backoff and jitter."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 300.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        retry_exceptions: tuple = (Exception,),
        circuit_breaker: Optional[CircuitBreaker] = None,
        name: str = "default"
    ):
        """
        Initialize enhanced retry mechanism.
        
        Args:
            max_attempts: Maximum number of retry attempts
            base_delay: Initial delay in seconds
            max_delay: Maximum delay in seconds
            backoff_factor: Exponential backoff factor
            jitter: Add random jitter to delays
            retry_exceptions: Tuple of exceptions to retry on
            circuit_breaker: Optional circuit breaker to use
            name: Name for logging
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.retry_exceptions = retry_exceptions
        self.circuit_breaker = circuit_breaker
        self.name = name
        
        self.logger = logging.getLogger(f"retry.{name}")
        
        # Metrics
        self.metrics = {
            "total_attempts": 0,
            "successful_attempts": 0,
            "failed_attempts": 0,
            "retry_attempts": 0,
            "average_attempts": 0.0
        }

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt."""
        delay = self.base_delay * (self.backoff_factor ** (attempt - 1))
        delay = min(delay, self.max_delay)
        
        if self.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay

    def _should_retry(self, exception: Exception, attempt: int) -> bool:
        """Determine if we should retry based on exception and attempt count."""
        if attempt >= self.max_attempts:
            return False
        
        if not isinstance(exception, self.retry_exceptions):
            return False
        
        # Don't retry if circuit breaker is open
        if isinstance(exception, CircuitBreakerError):
            return False
        
        return True

    async def __call__(self, func: Callable) -> Callable:
        """Decorator to add retry functionality to async functions."""
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, self.max_attempts + 1):
                self.metrics["total_attempts"] += 1
                
                try:
                    # Apply circuit breaker if configured
                    if self.circuit_breaker:
                        if not self.circuit_breaker._can_attempt():
                            raise CircuitBreakerError(f"Circuit breaker '{self.circuit_breaker.name}' is open")
                    
                    result = await func(*args, **kwargs)
                    
                    # Success
                    self.metrics["successful_attempts"] += 1
                    if attempt > 1:
                        self.logger.info(f"Operation '{self.name}' succeeded on attempt {attempt}")
                    
                    return result
                    
                except Exception as e:
                    last_exception = e
                    self.metrics["failed_attempts"] += 1
                    
                    # Update circuit breaker
                    if self.circuit_breaker:
                        self.circuit_breaker._on_failure(e)
                    
                    if not self._should_retry(e, attempt):
                        break
                    
                    if attempt < self.max_attempts:
                        self.metrics["retry_attempts"] += 1
                        delay = self._calculate_delay(attempt)
                        
                        self.logger.warning(
                            f"Attempt {attempt}/{self.max_attempts} failed for '{self.name}': {e}. "
                            f"Retrying in {delay:.2f}s..."
                        )
                        
                        await asyncio.sleep(delay)
            
            # All attempts exhausted
            self.logger.error(f"All {self.max_attempts} attempts failed for '{self.name}': {last_exception}")
            raise RetryExhaustedException(f"Failed after {self.max_attempts} attempts: {last_exception}")
        
        return wrapper

    def get_metrics(self) -> Dict:
        """Get retry metrics."""
        if self.metrics["total_attempts"] > 0:
            self.metrics["average_attempts"] = self.metrics["successful_attempts"] / self.metrics["total_attempts"]
        
        return {
            **self.metrics,
            "name": self.name,
            "max_attempts": self.max_attempts,
            "base_delay": self.base_delay,
            "backoff_factor": self.backoff_factor
        }


class ErrorContextLogger:
    """Enhanced error logging with context information."""

    def __init__(self, logger_name: str = "pipeline_errors"):
        self.logger = logging.getLogger(logger_name)
        self.error_history = []
        self.error_patterns = {}

    def log_error(
        self,
        error: Exception,
        context: Dict[str, Any],
        stage: str = "unknown",
        severity: str = "error"
    ):
        """Log error with comprehensive context."""
        
        error_info = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "severity": severity,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "error_traceback": traceback.format_exc(),
            "context": context
        }
        
        # Add to history
        self.error_history.append(error_info)
        
        # Track error patterns
        error_key = f"{stage}:{type(error).__name__}"
        if error_key not in self.error_patterns:
            self.error_patterns[error_key] = {"count": 0, "last_seen": None}
        
        self.error_patterns[error_key]["count"] += 1
        self.error_patterns[error_key]["last_seen"] = datetime.now().isoformat()
        
        # Log based on severity
        log_message = f"[{stage}] {type(error).__name__}: {error}"
        
        if severity == "critical":
            self.logger.critical(log_message, extra={"context": context})
        elif severity == "error":
            self.logger.error(log_message, extra={"context": context})
        elif severity == "warning":
            self.logger.warning(log_message, extra={"context": context})
        else:
            self.logger.info(log_message, extra={"context": context})

    def get_error_summary(self, hours: int = 24) -> Dict:
        """Get error summary for the last N hours."""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_errors = [
            error for error in self.error_history
            if datetime.fromisoformat(error["timestamp"]) > cutoff_time
        ]
        
        # Count by stage and type
        stage_counts = {}
        type_counts = {}
        
        for error in recent_errors:
            stage = error["stage"]
            error_type = error["error_type"]
            
            stage_counts[stage] = stage_counts.get(stage, 0) + 1
            type_counts[error_type] = type_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(recent_errors),
            "time_period_hours": hours,
            "errors_by_stage": stage_counts,
            "errors_by_type": type_counts,
            "error_patterns": self.error_patterns,
            "recent_errors": recent_errors[-10:]  # Last 10 errors
        }


class AlertManager:
    """Simple alert manager for critical failures."""

    def __init__(self, config_file: Optional[Path] = None):
        self.config = self._load_config(config_file)
        self.logger = logging.getLogger("alert_manager")
        self.alert_history = []

    def _load_config(self, config_file: Optional[Path]) -> Dict:
        """Load alert configuration."""
        default_config = {
            "email_enabled": False,
            "slack_enabled": False,
            "webhook_enabled": False,
            "rate_limit_minutes": 60,  # Don't send same alert more than once per hour
            "severity_thresholds": {
                "critical": True,
                "error": False,
                "warning": False
            }
        }
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                self.logger.warning(f"Failed to load alert config: {e}")
        
        return default_config

    def should_send_alert(self, alert_type: str, severity: str) -> bool:
        """Check if alert should be sent based on rate limiting and config."""
        
        # Check if severity should trigger alert
        if not self.config["severity_thresholds"].get(severity, False):
            return False
        
        # Check rate limiting
        rate_limit = self.config["rate_limit_minutes"]
        cutoff_time = datetime.now() - timedelta(minutes=rate_limit)
        
        recent_alerts = [
            alert for alert in self.alert_history
            if (alert["type"] == alert_type and 
                datetime.fromisoformat(alert["timestamp"]) > cutoff_time)
        ]
        
        return len(recent_alerts) == 0

    async def send_alert(
        self,
        alert_type: str,
        message: str,
        severity: str = "error",
        context: Optional[Dict] = None
    ):
        """Send alert through configured channels."""
        
        if not self.should_send_alert(alert_type, severity):
            self.logger.debug(f"Alert rate limited: {alert_type}")
            return
        
        alert_info = {
            "timestamp": datetime.now().isoformat(),
            "type": alert_type,
            "severity": severity,
            "message": message,
            "context": context or {}
        }
        
        self.alert_history.append(alert_info)
        
        # Log the alert
        self.logger.warning(f"ALERT [{severity.upper()}] {alert_type}: {message}")
        
        # Here you would implement actual alert sending:
        # - Email notifications
        # - Slack webhooks  
        # - Discord notifications
        # - HTTP webhooks
        
        # For now, just log that alert would be sent
        if self.config["email_enabled"]:
            self.logger.info(f"Would send email alert: {alert_type}")
        
        if self.config["slack_enabled"]:
            self.logger.info(f"Would send Slack alert: {alert_type}")
        
        if self.config["webhook_enabled"]:
            self.logger.info(f"Would send webhook alert: {alert_type}")


def create_enhanced_retry_decorator(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    circuit_breaker_config: Optional[Dict] = None,
    name: str = "default"
):
    """Create an enhanced retry decorator with optional circuit breaker."""
    
    circuit_breaker = None
    if circuit_breaker_config:
        circuit_breaker = CircuitBreaker(
            failure_threshold=circuit_breaker_config.get("failure_threshold", 5),
            timeout=circuit_breaker_config.get("timeout", 300),
            name=circuit_breaker_config.get("name", name)
        )
    
    retry_handler = EnhancedRetry(
        max_attempts=max_attempts,
        base_delay=base_delay,
        circuit_breaker=circuit_breaker,
        name=name
    )
    
    return retry_handler


async def test_error_handling_system():
    """Test the enhanced error handling system."""
    
    print("🔧 Testing Enhanced Error Handling System")
    print("=" * 50)
    
    # Test circuit breaker
    print("\n1. Testing Circuit Breaker...")
    
    @CircuitBreaker(failure_threshold=3, timeout=2, name="test_service")
    async def failing_service():
        import random
        if random.random() < 0.8:  # 80% failure rate
            raise ConnectionError("Service unavailable")
        return "success"
    
    # Test failures
    for i in range(5):
        try:
            result = await failing_service()
            print(f"   Attempt {i+1}: {result}")
        except (ConnectionError, CircuitBreakerError) as e:
            print(f"   Attempt {i+1}: Failed - {type(e).__name__}: {e}")
    
    # Test retry mechanism
    print("\n2. Testing Enhanced Retry...")
    
    retry_handler = EnhancedRetry(
        max_attempts=3,
        base_delay=0.1,  # Fast for testing
        name="test_retry"
    )
    
    async def unreliable_function():
        import random
        if random.random() < 0.7:  # 70% failure rate
            raise ValueError("Random failure")
        return "success"
    
    # Apply retry to function
    retryable_function = await retry_handler(unreliable_function)
    
    try:
        result = await retryable_function()
        print(f"   Retry test result: {result}")
    except RetryExhaustedException as e:
        print(f"   Retry test failed: {e}")
    
    # Test error logging
    print("\n3. Testing Error Context Logger...")
    
    error_logger = ErrorContextLogger()
    
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        error_logger.log_error(
            e,
            context={"user_id": 123, "operation": "test"},
            stage="testing",
            severity="warning"
        )
    
    summary = error_logger.get_error_summary(hours=1)
    print(f"   Error summary: {summary['total_errors']} errors logged")
    
    # Test alert manager
    print("\n4. Testing Alert Manager...")
    
    alert_manager = AlertManager()
    
    await alert_manager.send_alert(
        "circuit_breaker_open",
        "Test service circuit breaker opened",
        severity="critical"
    )
    
    print("✅ Enhanced error handling system testing completed!")


def main():
    """Main function to test the error handling system."""
    return asyncio.run(test_error_handling_system())


if __name__ == "__main__":
    import sys
    sys.exit(main())
