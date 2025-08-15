#!/usr/bin/env python3
"""
🚨 Pipeline Error Handler - Phase 2A Enhanced Error Handling

Comprehensive error handling and recovery system for the horse racing AI pipeline:
- Intelligent retry strategies with exponential backoff
- Context-aware error classification and handling
- Automatic recovery mechanisms
- Structured error logging with severity levels
- Integration with alerting systems (NTFY)

Author: AI Assistant
Date: August 15, 2025
Part of: Phase 2A - Enhanced Error Handling & Recovery
"""

import logging
import time
import json
import traceback
import requests
import sys
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from enum import Enum
from dataclasses import dataclass, asdict
from contextlib import contextmanager
from functools import wraps
import psycopg2
import redis
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels for prioritized handling."""
    LOW = "low"           # Minor issues, continue processing
    MEDIUM = "medium"     # Significant issues, retry with backoff
    HIGH = "high"         # Major issues, attempt recovery
    CRITICAL = "critical" # Pipeline-stopping issues, immediate alert


class ErrorCategory(Enum):
    """Categories of errors for specialized handling."""
    NETWORK = "network"           # Connection timeouts, HTTP errors
    DATABASE = "database"         # SQL errors, connection failures
    FILE_SYSTEM = "filesystem"    # File I/O, permission errors
    ML_TRAINING = "ml_training"   # Model training failures
    DATA_VALIDATION = "data_validation"  # Data quality issues
    EXTERNAL_API = "external_api" # Third-party service failures
    SYSTEM = "system"            # Memory, CPU, system-level errors
    UNKNOWN = "unknown"          # Unclassified errors


@dataclass
class ErrorContext:
    """Comprehensive error context information."""
    error_id: str
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    error_type: str
    error_message: str
    stack_trace: str
    function_name: str
    file_path: str
    line_number: int
    context_data: Dict[str, Any]
    retry_count: int = 0
    max_retries: int = 3
    last_retry: Optional[datetime] = None
    resolved: bool = False
    resolution_method: Optional[str] = None


@dataclass
class RetryConfig:
    """Configuration for retry strategies."""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True


class PipelineErrorHandler:
    """
    Comprehensive error handling and recovery system.
    
    Features:
    - Intelligent error classification
    - Context-aware retry strategies
    - Automatic recovery mechanisms
    - Structured logging and alerting
    - Performance monitoring integration
    """
    
    def __init__(
        self,
        log_file: Optional[str] = None,
        ntfy_url: Optional[str] = None,
        alert_threshold: ErrorSeverity = ErrorSeverity.HIGH
    ):
        """Initialize the error handler."""
        self.log_file = log_file or "logs/pipeline_errors.log"
        self.ntfy_url = ntfy_url or os.getenv("NTFY_URL")
        self.alert_threshold = alert_threshold
        
        # Error tracking
        self.error_history: List[ErrorContext] = []
        self.active_errors: Dict[str, ErrorContext] = {}
        
        # Retry configurations by category
        self.retry_configs = {
            ErrorCategory.NETWORK: RetryConfig(max_retries=5, base_delay=2.0),
            ErrorCategory.DATABASE: RetryConfig(max_retries=3, base_delay=5.0),
            ErrorCategory.EXTERNAL_API: RetryConfig(max_retries=4, base_delay=3.0),
            ErrorCategory.ML_TRAINING: RetryConfig(max_retries=2, base_delay=10.0),
            ErrorCategory.FILE_SYSTEM: RetryConfig(max_retries=3, base_delay=1.0),
            ErrorCategory.DATA_VALIDATION: RetryConfig(max_retries=1, base_delay=0.5),
            ErrorCategory.SYSTEM: RetryConfig(max_retries=2, base_delay=5.0),
            ErrorCategory.UNKNOWN: RetryConfig(max_retries=2, base_delay=2.0),
        }
        
        # Ensure log directory exists
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logger.info("🚨 Pipeline Error Handler initialized")
        logger.info(f"📁 Error log: {self.log_file}")
        logger.info(f"🔔 Alert threshold: {alert_threshold.value}")
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> Tuple[ErrorCategory, ErrorSeverity]:
        """
        Classify error by category and severity.
        
        Args:
            error: The exception to classify
            context: Additional context information
            
        Returns:
            Tuple of (category, severity)
        """
        error_type = type(error).__name__
        error_message = str(error).lower()
        
        # Network-related errors
        if any(keyword in error_message for keyword in [
            'connection', 'timeout', 'network', 'http', 'ssl', 'socket'
        ]) or error_type in ['ConnectionError', 'Timeout', 'HTTPError']:
            return ErrorCategory.NETWORK, ErrorSeverity.MEDIUM
        
        # Database-related errors
        if any(keyword in error_message for keyword in [
            'database', 'sql', 'postgres', 'cursor', 'transaction'
        ]) or error_type in ['DatabaseError', 'OperationalError', 'IntegrityError']:
            severity = ErrorSeverity.HIGH if 'connection' in error_message else ErrorSeverity.MEDIUM
            return ErrorCategory.DATABASE, severity
        
        # File system errors
        if any(keyword in error_message for keyword in [
            'file', 'directory', 'permission', 'disk', 'no such file'
        ]) or error_type in ['FileNotFoundError', 'PermissionError', 'IOError']:
            return ErrorCategory.FILE_SYSTEM, ErrorSeverity.MEDIUM
        
        # ML training errors
        if any(keyword in error_message for keyword in [
            'model', 'training', 'feature', 'sklearn', 'numpy', 'pandas'
        ]) or error_type in ['ValueError', 'RuntimeError'] and context and 'ml' in str(context):
            return ErrorCategory.ML_TRAINING, ErrorSeverity.HIGH
        
        # Data validation errors
        if any(keyword in error_message for keyword in [
            'validation', 'invalid', 'missing', 'null', 'empty'
        ]) or error_type in ['ValidationError', 'KeyError', 'IndexError']:
            return ErrorCategory.DATA_VALIDATION, ErrorSeverity.MEDIUM
        
        # External API errors
        if any(keyword in error_message for keyword in [
            'api', 'request', 'response', 'status', '404', '500'
        ]):
            return ErrorCategory.EXTERNAL_API, ErrorSeverity.MEDIUM
        
        # System-level errors
        if any(keyword in error_message for keyword in [
            'memory', 'cpu', 'resource', 'system', 'process'
        ]) or error_type in ['MemoryError', 'SystemError', 'OSError']:
            return ErrorCategory.SYSTEM, ErrorSeverity.HIGH
        
        # Default classification
        return ErrorCategory.UNKNOWN, ErrorSeverity.MEDIUM
    
    def create_error_context(
        self,
        error: Exception,
        context_data: Dict[str, Any] = None,
        function_name: str = None
    ) -> ErrorContext:
        """Create comprehensive error context."""
        # Get caller information
        frame = sys._getframe(2)  # Go back 2 frames to get actual caller
        file_path = frame.f_code.co_filename
        line_number = frame.f_lineno
        func_name = function_name or frame.f_code.co_name
        
        # Classify error
        category, severity = self.classify_error(error, context_data)
        
        # Generate unique error ID
        error_id = f"{category.value}_{int(time.time())}_{line_number}"
        
        return ErrorContext(
            error_id=error_id,
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            error_type=type(error).__name__,
            error_message=str(error),
            stack_trace=traceback.format_exc(),
            function_name=func_name,
            file_path=file_path,
            line_number=line_number,
            context_data=context_data or {},
            max_retries=self.retry_configs[category].max_retries
        )
    
    def calculate_retry_delay(self, error_context: ErrorContext) -> float:
        """Calculate delay for next retry using exponential backoff."""
        config = self.retry_configs[error_context.category]
        
        # Exponential backoff
        delay = min(
            config.base_delay * (config.exponential_base ** error_context.retry_count),
            config.max_delay
        )
        
        # Add jitter to prevent thundering herd
        if config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)
        
        return delay
    
    def should_retry(self, error_context: ErrorContext) -> bool:
        """Determine if an error should be retried."""
        if error_context.retry_count >= error_context.max_retries:
            return False
        
        if error_context.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Category-specific retry logic
        if error_context.category == ErrorCategory.DATA_VALIDATION:
            # Don't retry validation errors unless they're timeout-related
            return 'timeout' in error_context.error_message.lower()
        
        if error_context.category == ErrorCategory.FILE_SYSTEM:
            # Retry permission errors but not file not found
            return 'permission' in error_context.error_message.lower()
        
        return True
    
    def log_error(self, error_context: ErrorContext) -> None:
        """Log error with structured format."""
        log_entry = {
            "error_id": error_context.error_id,
            "timestamp": error_context.timestamp.isoformat(),
            "category": error_context.category.value,
            "severity": error_context.severity.value,
            "error_type": error_context.error_type,
            "error_message": error_context.error_message,
            "function": error_context.function_name,
            "file": error_context.file_path,
            "line": error_context.line_number,
            "retry_count": error_context.retry_count,
            "context": error_context.context_data
        }
        
        # Log to file
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logger.error(f"Failed to write error log: {e}")
        
        # Log to console with appropriate level
        if error_context.severity == ErrorSeverity.CRITICAL:
            logger.critical(f"🚨 CRITICAL ERROR: {error_context.error_message}")
        elif error_context.severity == ErrorSeverity.HIGH:
            logger.error(f"❌ HIGH SEVERITY: {error_context.error_message}")
        elif error_context.severity == ErrorSeverity.MEDIUM:
            logger.warning(f"⚠️ MEDIUM SEVERITY: {error_context.error_message}")
        else:
            logger.info(f"ℹ️ LOW SEVERITY: {error_context.error_message}")
    
    def send_alert(self, error_context: ErrorContext) -> bool:
        """Send alert notification if severity meets threshold."""
        if error_context.severity.value < self.alert_threshold.value:
            return False
        
        if not self.ntfy_url:
            logger.warning("⚠️ NTFY URL not configured - alert not sent")
            return False
        
        try:
            alert_message = (
                f"🚨 Pipeline Error Alert\n"
                f"Severity: {error_context.severity.value.upper()}\n"
                f"Category: {error_context.category.value}\n"
                f"Error: {error_context.error_message}\n"
                f"Function: {error_context.function_name}\n"
                f"Time: {error_context.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
            )
            
            response = requests.post(
                self.ntfy_url,
                data=alert_message.encode('utf-8'),
                headers={
                    'Title': f'Pipeline Error - {error_context.severity.value.upper()}',
                    'Priority': '5' if error_context.severity == ErrorSeverity.CRITICAL else '4',
                    'Tags': 'warning,pipeline,error'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"📱 Alert sent for error {error_context.error_id}")
                return True
            else:
                logger.error(f"Failed to send alert: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    @contextmanager
    def handle_errors(
        self,
        context_data: Dict[str, Any] = None,
        suppress_exceptions: bool = False,
        fallback_value: Any = None
    ):
        """
        Context manager for comprehensive error handling.
        
        Args:
            context_data: Additional context for error classification
            suppress_exceptions: Whether to suppress exceptions after handling
            fallback_value: Value to return if suppressing exceptions
        """
        try:
            yield self
        except Exception as error:
            # Create error context
            error_context = self.create_error_context(error, context_data)
            
            # Log error
            self.log_error(error_context)
            
            # Send alert if needed
            self.send_alert(error_context)
            
            # Track error
            self.error_history.append(error_context)
            self.active_errors[error_context.error_id] = error_context
            
            if suppress_exceptions:
                logger.info(f"🔄 Error suppressed, returning fallback value")
                return fallback_value
            else:
                # Re-raise the original exception
                raise
    
    def retry_with_backoff(
        self,
        func: Callable,
        *args,
        context_data: Dict[str, Any] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with intelligent retry and backoff.
        
        Args:
            func: Function to execute
            *args: Positional arguments for function
            context_data: Additional context for error handling
            **kwargs: Keyword arguments for function
            
        Returns:
            Function result if successful
            
        Raises:
            Exception if all retries exhausted
        """
        last_error = None
        error_context = None
        
        for attempt in range(max(config.max_retries for config in self.retry_configs.values()) + 1):
            try:
                result = func(*args, **kwargs)
                
                # If we had previous errors but succeeded, mark as resolved
                if error_context:
                    error_context.resolved = True
                    error_context.resolution_method = f"retry_success_attempt_{attempt + 1}"
                    logger.info(f"✅ Error {error_context.error_id} resolved after {attempt} retries")
                
                return result
                
            except Exception as error:
                last_error = error
                
                # Create or update error context
                if not error_context:
                    error_context = self.create_error_context(error, context_data)
                else:
                    error_context.retry_count = attempt
                    error_context.last_retry = datetime.now()
                
                # Check if we should retry
                if not self.should_retry(error_context) or attempt >= error_context.max_retries:
                    # Log final failure
                    self.log_error(error_context)
                    self.send_alert(error_context)
                    self.error_history.append(error_context)
                    self.active_errors[error_context.error_id] = error_context
                    raise error
                
                # Calculate delay and wait
                delay = self.calculate_retry_delay(error_context)
                logger.warning(
                    f"⏳ Retry {attempt + 1}/{error_context.max_retries} "
                    f"for {error_context.category.value} error in {delay:.2f}s"
                )
                time.sleep(delay)
        
        # This should never be reached, but just in case
        if last_error:
            raise last_error
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics."""
        if not self.error_history:
            return {"total_errors": 0, "categories": {}, "severities": {}}
        
        # Count by category
        category_counts = {}
        for category in ErrorCategory:
            category_counts[category.value] = sum(
                1 for error in self.error_history if error.category == category
            )
        
        # Count by severity
        severity_counts = {}
        for severity in ErrorSeverity:
            severity_counts[severity.value] = sum(
                1 for error in self.error_history if error.severity == severity
            )
        
        # Calculate resolution rate
        resolved_count = sum(1 for error in self.error_history if error.resolved)
        resolution_rate = (resolved_count / len(self.error_history)) * 100
        
        return {
            "total_errors": len(self.error_history),
            "active_errors": len(self.active_errors),
            "categories": category_counts,
            "severities": severity_counts,
            "resolution_rate": round(resolution_rate, 2),
            "recent_errors": len([
                error for error in self.error_history
                if error.timestamp > datetime.now() - timedelta(hours=24)
            ])
        }


# Decorator for automatic error handling
def handle_pipeline_errors(
    context_data: Dict[str, Any] = None,
    retry: bool = True,
    suppress: bool = False,
    fallback: Any = None
):
    """
    Decorator for automatic error handling in pipeline functions.
    
    Args:
        context_data: Additional context for error classification
        retry: Whether to retry on failures
        suppress: Whether to suppress exceptions
        fallback: Fallback value if suppressing exceptions
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create error handler
            error_handler = getattr(wrapper, '_error_handler', None)
            if not error_handler:
                error_handler = PipelineErrorHandler()
                wrapper._error_handler = error_handler
            
            # Prepare context
            func_context = context_data or {}
            func_context.update({
                "function": func.__name__,
                "args_count": len(args),
                "kwargs_keys": list(kwargs.keys())
            })
            
            if retry:
                return error_handler.retry_with_backoff(
                    func, *args, context_data=func_context, **kwargs
                )
            else:
                with error_handler.handle_errors(
                    context_data=func_context,
                    suppress_exceptions=suppress,
                    fallback_value=fallback
                ):
                    return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Global error handler instance
_global_error_handler = None


def get_error_handler() -> PipelineErrorHandler:
    """Get the global error handler instance."""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = PipelineErrorHandler()
    return _global_error_handler


if __name__ == "__main__":
    # Test the error handling system
    print("🚨 Testing Pipeline Error Handler...")
    
    handler = PipelineErrorHandler()
    
    # Test error classification
    try:
        raise ConnectionError("Database connection timeout")
    except Exception as e:
        context = handler.create_error_context(e, {"test": "classification"})
        print(f"📊 Error classified as: {context.category.value} / {context.severity.value}")
    
    # Test retry mechanism
    @handle_pipeline_errors(retry=True, context_data={"test": "retry"})
    def flaky_function(attempt_count: int = 0):
        if attempt_count < 2:
            raise ConnectionError("Temporary network issue")
        return "Success after retries!"
    
    try:
        result = flaky_function()
        print(f"✅ Retry test result: {result}")
    except Exception as e:
        print(f"❌ Retry test failed: {e}")
    
    # Print statistics
    stats = handler.get_error_statistics()
    print(f"📈 Error statistics: {stats}")
    
    print("🎉 Error handler testing complete!")
