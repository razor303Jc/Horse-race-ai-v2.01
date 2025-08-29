#!/usr/bin/env python3
"""
Enhanced Error Handling and Logging System for Horse Racing AI V2.03
Provides comprehensive error handling, logging, and debugging capabilities
"""

import os
import sys
import json
import time
import traceback
import functools
import threading
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable, Union
from pathlib import Path
import logging
import logging.handlers
from dataclasses import dataclass
from enum import Enum
import pickle
import gzip
import hashlib
import inspect

# Advanced logging imports
import structlog
from concurrent.futures import ThreadPoolExecutor
import queue
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class LogLevel(Enum):
    """Enhanced log levels with criticality"""

    TRACE = 5
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    FATAL = 60


class ErrorSeverity(Enum):
    """Error severity classification"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    FATAL = "fatal"


@dataclass
class ErrorReport:
    """Comprehensive error report structure"""

    timestamp: datetime
    error_id: str
    error_type: str
    error_message: str
    severity: ErrorSeverity
    module: str
    function: str
    line_number: int
    stack_trace: str
    context: Dict[str, Any]
    user_impact: str
    suggested_fix: str
    occurrence_count: int = 1
    first_seen: Optional[datetime] = None
    last_seen: Optional[datetime] = None


@dataclass
class LogEntry:
    """Structured log entry"""

    timestamp: datetime
    level: LogLevel
    message: str
    module: str
    function: str
    line_number: int
    context: Dict[str, Any]
    correlation_id: str
    session_id: str
    user_id: Optional[str] = None


class PerformanceMetrics:
    """Performance monitoring and metrics"""

    def __init__(self):
        self.execution_times: Dict[str, List[float]] = {}
        self.memory_usage: Dict[str, List[float]] = {}
        self.error_counts: Dict[str, int] = {}
        self.success_counts: Dict[str, int] = {}

    def record_execution_time(self, function_name: str, duration: float):
        """Record function execution time"""
        if function_name not in self.execution_times:
            self.execution_times[function_name] = []
        self.execution_times[function_name].append(duration)

    def record_memory_usage(self, function_name: str, memory: float):
        """Record memory usage"""
        if function_name not in self.memory_usage:
            self.memory_usage[function_name] = []
        self.memory_usage[function_name].append(memory)

    def record_error(self, function_name: str):
        """Record error occurrence"""
        self.error_counts[function_name] = self.error_counts.get(function_name, 0) + 1

    def record_success(self, function_name: str):
        """Record successful execution"""
        self.success_counts[function_name] = (
            self.success_counts.get(function_name, 0) + 1
        )

    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get comprehensive metrics summary"""
        summary = {}

        for func_name in set(
            list(self.execution_times.keys()) + list(self.error_counts.keys())
        ):
            times = self.execution_times.get(func_name, [])
            errors = self.error_counts.get(func_name, 0)
            successes = self.success_counts.get(func_name, 0)
            memory = self.memory_usage.get(func_name, [])

            summary[func_name] = {
                "avg_execution_time": sum(times) / len(times) if times else 0,
                "max_execution_time": max(times) if times else 0,
                "min_execution_time": min(times) if times else 0,
                "total_executions": len(times),
                "error_count": errors,
                "success_count": successes,
                "error_rate": (
                    errors / (errors + successes) if (errors + successes) > 0 else 0
                ),
                "avg_memory_usage": sum(memory) / len(memory) if memory else 0,
                "max_memory_usage": max(memory) if memory else 0,
            }

        return summary


class AlertManager:
    """Advanced alerting and notification system"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.alert_history: List[Dict[str, Any]] = []
        self.alert_queue = queue.Queue()
        self.email_enabled = config.get("email_alerts", {}).get("enabled", False)
        self.slack_enabled = config.get("slack_alerts", {}).get("enabled", False)

        # Start alert processor
        self.alert_thread = threading.Thread(target=self._process_alerts, daemon=True)
        self.alert_thread.start()

    def send_alert(
        self,
        severity: ErrorSeverity,
        title: str,
        message: str,
        context: Optional[Dict[str, Any]] = None,
    ):
        """Send alert through configured channels"""
        alert = {
            "timestamp": datetime.now(),
            "severity": severity,
            "title": title,
            "message": message,
            "context": context or {},
        }

        self.alert_queue.put(alert)
        self.alert_history.append(alert)

        # Keep only last 1000 alerts
        if len(self.alert_history) > 1000:
            self.alert_history = self.alert_history[-1000:]

    def _process_alerts(self):
        """Process alerts from queue"""
        while True:
            try:
                alert = self.alert_queue.get(timeout=1.0)

                # Send email alerts
                if self.email_enabled and alert["severity"] in [
                    ErrorSeverity.HIGH,
                    ErrorSeverity.CRITICAL,
                    ErrorSeverity.FATAL,
                ]:
                    self._send_email_alert(alert)

                # Send Slack alerts
                if self.slack_enabled:
                    self._send_slack_alert(alert)

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Error processing alert: {e}")

    def _send_email_alert(self, alert: Dict[str, Any]):
        """Send email alert"""
        try:
            email_config = self.config.get("email_alerts", {})

            msg = MIMEMultipart()
            msg["From"] = email_config.get("from_email")
            msg["To"] = ", ".join(email_config.get("to_emails", []))
            msg["Subject"] = f"[{alert['severity'].value.upper()}] {alert['title']}"

            body = f"""
Alert Details:
- Severity: {alert['severity'].value.upper()}
- Time: {alert['timestamp']}
- Title: {alert['title']}
- Message: {alert['message']}

Context:
{json.dumps(alert['context'], indent=2)}
            """

            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(
                email_config.get("smtp_server"), email_config.get("smtp_port", 587)
            )
            server.starttls()
            server.login(email_config.get("username"), email_config.get("password"))
            server.send_message(msg)
            server.quit()

        except Exception as e:
            print(f"Failed to send email alert: {e}")

    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Send Slack alert"""
        try:
            import requests

            slack_config = self.config.get("slack_alerts", {})
            webhook_url = slack_config.get("webhook_url")

            if not webhook_url:
                return

            color_map = {
                ErrorSeverity.LOW: "good",
                ErrorSeverity.MEDIUM: "warning",
                ErrorSeverity.HIGH: "danger",
                ErrorSeverity.CRITICAL: "danger",
                ErrorSeverity.FATAL: "danger",
            }

            payload = {
                "attachments": [
                    {
                        "color": color_map.get(alert["severity"], "warning"),
                        "title": alert["title"],
                        "text": alert["message"],
                        "fields": [
                            {
                                "title": "Severity",
                                "value": alert["severity"].value.upper(),
                                "short": True,
                            },
                            {
                                "title": "Time",
                                "value": alert["timestamp"].strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                ),
                                "short": True,
                            },
                        ],
                    }
                ]
            }

            requests.post(webhook_url, json=payload, timeout=10)

        except Exception as e:
            print(f"Failed to send Slack alert: {e}")


class EnhancedLogger:
    """Enhanced logging system with structured logging and context"""

    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.performance_metrics = PerformanceMetrics()
        self.alert_manager = AlertManager(config.get("alerts", {}))

        # Setup structured logging
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )

        # Create logger
        self.logger = structlog.get_logger(name)

        # Setup file handlers
        self._setup_file_handlers()

        # Session tracking
        self.session_id = self._generate_session_id()
        self.correlation_id = None

    def _setup_file_handlers(self):
        """Setup file handlers for different log levels"""
        logs_dir = Path(self.config.get("logs_directory", "logs"))
        logs_dir.mkdir(exist_ok=True)

        # Setup standard Python logger for file output
        self.py_logger = logging.getLogger(self.name)
        self.py_logger.setLevel(logging.DEBUG)

        # Error log handler
        error_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "error.log", maxBytes=10 * 1024 * 1024, backupCount=5  # 10MB
        )
        error_handler.setLevel(logging.ERROR)
        error_formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        error_handler.setFormatter(error_formatter)
        self.py_logger.addHandler(error_handler)

        # Debug log handler
        debug_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "debug.log", maxBytes=50 * 1024 * 1024, backupCount=3  # 50MB
        )
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(error_formatter)
        self.py_logger.addHandler(debug_handler)

        # Performance log handler
        perf_handler = logging.handlers.RotatingFileHandler(
            logs_dir / "performance.log",
            maxBytes=20 * 1024 * 1024,  # 20MB
            backupCount=3,
        )
        perf_handler.setLevel(logging.INFO)
        perf_handler.setFormatter(error_formatter)
        self.py_logger.addHandler(perf_handler)

    def _generate_session_id(self) -> str:
        """Generate unique session ID"""
        return f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(threading.current_thread().ident) % 10000}"

    def _generate_correlation_id(self) -> str:
        """Generate correlation ID for request tracking"""
        return f"{int(time.time() * 1000)}_{hash(threading.current_thread().ident) % 10000}"

    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for request tracking"""
        self.correlation_id = correlation_id

    def trace(self, message: str, **context):
        """Log trace level message"""
        self._log(LogLevel.TRACE, message, context)

    def debug(self, message: str, **context):
        """Log debug level message"""
        self._log(LogLevel.DEBUG, message, context)

    def info(self, message: str, **context):
        """Log info level message"""
        self._log(LogLevel.INFO, message, context)

    def warning(self, message: str, **context):
        """Log warning level message"""
        self._log(LogLevel.WARNING, message, context)

    def error(self, message: str, **context):
        """Log error level message"""
        self._log(LogLevel.ERROR, message, context)

        # Send alert for errors
        self.alert_manager.send_alert(
            ErrorSeverity.MEDIUM, "Application Error", message, context
        )

    def critical(self, message: str, **context):
        """Log critical level message"""
        self._log(LogLevel.CRITICAL, message, context)

        # Send critical alert
        self.alert_manager.send_alert(
            ErrorSeverity.CRITICAL, "Critical Error", message, context
        )

    def fatal(self, message: str, **context):
        """Log fatal level message"""
        self._log(LogLevel.FATAL, message, context)

        # Send fatal alert
        self.alert_manager.send_alert(
            ErrorSeverity.FATAL, "Fatal Error", message, context
        )

    def _log(self, level: LogLevel, message: str, context: Dict[str, Any]):
        """Internal logging method"""
        # Get caller information
        frame = inspect.currentframe()
        caller_frame = frame.f_back.f_back  # Go back 2 frames
        caller_info = {
            "module": caller_frame.f_globals.get("__name__", "unknown"),
            "function": caller_frame.f_code.co_name,
            "line_number": caller_frame.f_lineno,
        }

        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            module=caller_info["module"],
            function=caller_info["function"],
            line_number=caller_info["line_number"],
            context=context,
            correlation_id=self.correlation_id or self._generate_correlation_id(),
            session_id=self.session_id,
        )

        # Log to structured logger
        self.logger.info(
            message,
            level=level.name,
            module=caller_info["module"],
            function=caller_info["function"],
            line_number=caller_info["line_number"],
            session_id=self.session_id,
            correlation_id=log_entry.correlation_id,
            **context,
        )

        # Log to Python logger for file output
        py_level = getattr(logging, level.name, logging.INFO)
        self.py_logger.log(py_level, message, extra=context)


class ErrorHandler:
    """Comprehensive error handling and recovery system"""

    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.error_registry: Dict[str, ErrorReport] = {}
        self.recovery_strategies: Dict[str, Callable] = {}
        self.circuit_breakers: Dict[str, Dict[str, Any]] = {}

    def register_recovery_strategy(self, error_type: str, strategy: Callable):
        """Register recovery strategy for specific error type"""
        self.recovery_strategies[error_type] = strategy

    def handle_error(
        self,
        error: Exception,
        context: Optional[Dict[str, Any]] = None,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    ) -> bool:
        """Handle error with recovery strategies"""
        error_id = self._generate_error_id(error)
        error_type = type(error).__name__

        # Get caller information
        frame = inspect.currentframe()
        caller_frame = frame.f_back
        caller_info = {
            "module": caller_frame.f_globals.get("__name__", "unknown"),
            "function": caller_frame.f_code.co_name,
            "line_number": caller_frame.f_lineno,
        }

        # Create or update error report
        if error_id in self.error_registry:
            error_report = self.error_registry[error_id]
            error_report.occurrence_count += 1
            error_report.last_seen = datetime.now()
        else:
            error_report = ErrorReport(
                timestamp=datetime.now(),
                error_id=error_id,
                error_type=error_type,
                error_message=str(error),
                severity=severity,
                module=caller_info["module"],
                function=caller_info["function"],
                line_number=caller_info["line_number"],
                stack_trace=traceback.format_exc(),
                context=context or {},
                user_impact=self._assess_user_impact(error, severity),
                suggested_fix=self._suggest_fix(error_type),
                first_seen=datetime.now(),
            )
            self.error_registry[error_id] = error_report

        # Log error
        self.logger.error(
            f"{error_type}: {error}",
            error_id=error_id,
            severity=severity.value,
            module=caller_info["module"],
            function=caller_info["function"],
            line_number=caller_info["line_number"],
            stack_trace=error_report.stack_trace,
            context=context,
        )

        # Update performance metrics
        self.logger.performance_metrics.record_error(caller_info["function"])

        # Try recovery strategy
        if error_type in self.recovery_strategies:
            try:
                return self.recovery_strategies[error_type](error, context)
            except Exception as recovery_error:
                self.logger.error(
                    f"Recovery strategy failed for {error_type}",
                    recovery_error=str(recovery_error),
                    original_error=str(error),
                )

        return False

    def _generate_error_id(self, error: Exception) -> str:
        """Generate unique error ID"""
        error_signature = (
            f"{type(error).__name__}:{str(error)}:{traceback.format_exc()}"
        )
        return hashlib.md5(error_signature.encode()).hexdigest()[:16]

    def _assess_user_impact(self, error: Exception, severity: ErrorSeverity) -> str:
        """Assess user impact of error"""
        impact_map = {
            ErrorSeverity.LOW: "Minimal impact - logging/debugging features affected",
            ErrorSeverity.MEDIUM: "Moderate impact - some features may not work properly",
            ErrorSeverity.HIGH: "High impact - core functionality affected",
            ErrorSeverity.CRITICAL: "Critical impact - major features unavailable",
            ErrorSeverity.FATAL: "Fatal impact - application may not function",
        }
        return impact_map.get(severity, "Unknown impact")

    def _suggest_fix(self, error_type: str) -> str:
        """Suggest potential fixes for error types"""
        suggestions = {
            "FileNotFoundError": "Check file path and permissions",
            "ConnectionError": "Check network connectivity and service availability",
            "DatabaseError": "Verify database connection and schema",
            "ValueError": "Validate input data format and ranges",
            "KeyError": "Ensure required keys exist in data structures",
            "ImportError": "Install missing dependencies or check module paths",
            "PermissionError": "Check file/directory permissions",
            "TimeoutError": "Increase timeout values or check service responsiveness",
        }
        return suggestions.get(error_type, "Review error details and stack trace")

    def get_error_statistics(self) -> Dict[str, Any]:
        """Get comprehensive error statistics"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        last_week = now - timedelta(days=7)

        recent_errors = [
            e for e in self.error_registry.values() if e.last_seen >= last_24h
        ]
        weekly_errors = [
            e for e in self.error_registry.values() if e.last_seen >= last_week
        ]

        return {
            "total_unique_errors": len(self.error_registry),
            "errors_last_24h": len(recent_errors),
            "errors_last_week": len(weekly_errors),
            "most_common_errors": self._get_most_common_errors(),
            "error_trends": self._calculate_error_trends(),
            "severity_distribution": self._get_severity_distribution(),
        }

    def _get_most_common_errors(self) -> List[Dict[str, Any]]:
        """Get most common errors by occurrence count"""
        sorted_errors = sorted(
            self.error_registry.values(), key=lambda x: x.occurrence_count, reverse=True
        )

        return [
            {
                "error_type": error.error_type,
                "message": error.error_message,
                "count": error.occurrence_count,
                "severity": error.severity.value,
                "first_seen": error.first_seen.isoformat(),
                "last_seen": error.last_seen.isoformat(),
            }
            for error in sorted_errors[:10]
        ]

    def _calculate_error_trends(self) -> Dict[str, float]:
        """Calculate error trends over time"""
        now = datetime.now()
        last_24h = now - timedelta(hours=24)
        prev_24h = last_24h - timedelta(hours=24)

        recent_count = len(
            [e for e in self.error_registry.values() if e.last_seen >= last_24h]
        )
        previous_count = len(
            [
                e
                for e in self.error_registry.values()
                if prev_24h <= e.last_seen < last_24h
            ]
        )

        trend = 0.0
        if previous_count > 0:
            trend = ((recent_count - previous_count) / previous_count) * 100

        return {
            "errors_last_24h": recent_count,
            "errors_prev_24h": previous_count,
            "trend_percentage": trend,
        }

    def _get_severity_distribution(self) -> Dict[str, int]:
        """Get distribution of errors by severity"""
        distribution = {}
        for error in self.error_registry.values():
            severity = error.severity.value
            distribution[severity] = distribution.get(severity, 0) + 1
        return distribution


def with_error_handling(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    retry_count: int = 0,
    retry_delay: float = 1.0,
):
    """Decorator for automatic error handling and recovery"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get or create logger for this module
            module_name = func.__module__
            if not hasattr(wrapper, "_logger"):
                wrapper._logger = EnhancedLogger(module_name, {})
                wrapper._error_handler = ErrorHandler(wrapper._logger)

            attempts = 0
            max_attempts = retry_count + 1

            while attempts < max_attempts:
                try:
                    start_time = time.time()

                    # Execute function
                    result = func(*args, **kwargs)

                    # Record performance metrics
                    execution_time = time.time() - start_time
                    wrapper._logger.performance_metrics.record_execution_time(
                        func.__name__, execution_time
                    )
                    wrapper._logger.performance_metrics.record_success(func.__name__)

                    # Log successful execution
                    wrapper._logger.debug(
                        f"Function {func.__name__} executed successfully",
                        execution_time=execution_time,
                        attempt=attempts + 1,
                    )

                    return result

                except Exception as e:
                    attempts += 1

                    # Handle error
                    context = {
                        "function": func.__name__,
                        "args": str(args)[:200],  # Limit size
                        "kwargs": str(kwargs)[:200],
                        "attempt": attempts,
                        "max_attempts": max_attempts,
                    }

                    recovered = wrapper._error_handler.handle_error(
                        e, context, severity
                    )

                    if attempts < max_attempts and not recovered:
                        wrapper._logger.warning(
                            f"Retrying {func.__name__} after error (attempt {attempts}/{max_attempts})",
                            error=str(e),
                            retry_delay=retry_delay,
                        )
                        time.sleep(retry_delay)
                        continue
                    else:
                        wrapper._logger.error(
                            f"Function {func.__name__} failed after {attempts} attempts",
                            error=str(e),
                            severity=severity.value,
                        )
                        if not recovered:
                            raise
                        return None

        return wrapper

    return decorator


async def with_async_error_handling(
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    retry_count: int = 0,
    retry_delay: float = 1.0,
):
    """Async decorator for automatic error handling and recovery"""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Get or create logger for this module
            module_name = func.__module__
            if not hasattr(wrapper, "_logger"):
                wrapper._logger = EnhancedLogger(module_name, {})
                wrapper._error_handler = ErrorHandler(wrapper._logger)

            attempts = 0
            max_attempts = retry_count + 1

            while attempts < max_attempts:
                try:
                    start_time = time.time()

                    # Execute async function
                    result = await func(*args, **kwargs)

                    # Record performance metrics
                    execution_time = time.time() - start_time
                    wrapper._logger.performance_metrics.record_execution_time(
                        func.__name__, execution_time
                    )
                    wrapper._logger.performance_metrics.record_success(func.__name__)

                    # Log successful execution
                    wrapper._logger.debug(
                        f"Async function {func.__name__} executed successfully",
                        execution_time=execution_time,
                        attempt=attempts + 1,
                    )

                    return result

                except Exception as e:
                    attempts += 1

                    # Handle error
                    context = {
                        "function": func.__name__,
                        "args": str(args)[:200],
                        "kwargs": str(kwargs)[:200],
                        "attempt": attempts,
                        "max_attempts": max_attempts,
                    }

                    recovered = wrapper._error_handler.handle_error(
                        e, context, severity
                    )

                    if attempts < max_attempts and not recovered:
                        wrapper._logger.warning(
                            f"Retrying async {func.__name__} after error (attempt {attempts}/{max_attempts})",
                            error=str(e),
                            retry_delay=retry_delay,
                        )
                        await asyncio.sleep(retry_delay)
                        continue
                    else:
                        wrapper._logger.error(
                            f"Async function {func.__name__} failed after {attempts} attempts",
                            error=str(e),
                            severity=severity.value,
                        )
                        if not recovered:
                            raise
                        return None

        return wrapper

    return decorator


class DebugProfiler:
    """Advanced debugging and profiling utilities"""

    def __init__(self, logger: EnhancedLogger):
        self.logger = logger
        self.active_profiles: Dict[str, Dict[str, Any]] = {}

    def start_profile(self, profile_name: str):
        """Start performance profiling"""
        import cProfile
        import pstats
        import io

        self.active_profiles[profile_name] = {
            "profiler": cProfile.Profile(),
            "start_time": time.time(),
            "memory_start": self._get_memory_usage(),
        }

        self.active_profiles[profile_name]["profiler"].enable()

        self.logger.debug(f"Started profiling: {profile_name}")

    def end_profile(self, profile_name: str) -> Dict[str, Any]:
        """End profiling and return results"""
        if profile_name not in self.active_profiles:
            self.logger.warning(f"Profile {profile_name} not found")
            return {}

        profile_data = self.active_profiles[profile_name]
        profile_data["profiler"].disable()

        # Calculate metrics
        end_time = time.time()
        memory_end = self._get_memory_usage()

        execution_time = end_time - profile_data["start_time"]
        memory_delta = memory_end - profile_data["memory_start"]

        # Generate profiling report
        import pstats
        import io

        s = io.StringIO()
        ps = pstats.Stats(profile_data["profiler"], stream=s)
        ps.sort_stats("cumulative")
        ps.print_stats(20)  # Top 20 functions

        results = {
            "profile_name": profile_name,
            "execution_time": execution_time,
            "memory_delta": memory_delta,
            "profiling_report": s.getvalue(),
            "timestamp": datetime.now().isoformat(),
        }

        # Cleanup
        del self.active_profiles[profile_name]

        self.logger.info(
            f"Completed profiling: {profile_name}",
            execution_time=execution_time,
            memory_delta=memory_delta,
        )

        return results

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB"""
        try:
            import psutil

            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # Convert to MB
        except ImportError:
            return 0.0


def create_logger(name: str, config: Optional[Dict[str, Any]] = None) -> EnhancedLogger:
    """Factory function to create enhanced logger"""
    default_config = {
        "logs_directory": "logs",
        "alerts": {
            "email_alerts": {
                "enabled": False,
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "from_email": "",
                "to_emails": [],
                "username": "",
                "password": "",
            },
            "slack_alerts": {"enabled": False, "webhook_url": ""},
        },
    }

    if config:
        default_config.update(config)

    return EnhancedLogger(name, default_config)


# Global logger instance
_global_logger = None


def get_logger(name: Optional[str] = None) -> EnhancedLogger:
    """Get global logger instance"""
    global _global_logger

    if _global_logger is None:
        _global_logger = create_logger(name or __name__)

    return _global_logger


def main():
    """Demonstration of error handling and logging system"""
    # Create logger
    logger = create_logger("horse_racing_ai.error_handling")
    error_handler = ErrorHandler(logger)
    profiler = DebugProfiler(logger)

    print("🛡️ Enhanced Error Handling and Logging System")
    print("=" * 60)

    # Demonstrate logging
    logger.info("Error handling system initialized")
    logger.debug("Debug message with context", module="test", version="1.0")
    logger.warning("Warning message", category="test_warning")

    # Demonstrate error handling
    @with_error_handling(severity=ErrorSeverity.MEDIUM, retry_count=2)
    def test_function_with_errors():
        import random

        if random.random() < 0.7:  # 70% chance of error
            raise ValueError("Random test error")
        return "Success!"

    # Test function
    try:
        result = test_function_with_errors()
        print(f"Function result: {result}")
    except Exception as e:
        print(f"Function failed: {e}")

    # Demonstrate profiling
    profiler.start_profile("test_profile")
    time.sleep(0.1)  # Simulate work
    profile_results = profiler.end_profile("test_profile")
    print(f"Profile results: {profile_results['execution_time']:.3f}s")

    # Display error statistics
    stats = error_handler.get_error_statistics()
    print(f"Error statistics: {stats}")

    # Display performance metrics
    metrics = logger.performance_metrics.get_metrics_summary()
    print(f"Performance metrics: {json.dumps(metrics, indent=2)}")

    print("✅ Error handling and logging system demonstration completed")


if __name__ == "__main__":
    main()
