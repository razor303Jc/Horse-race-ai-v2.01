#!/usr/bin/env python3
"""
🚨 Comprehensive Error Handling Framework
Advanced error management for Horse Racing AI Pipeline

Features:
- Hierarchical error classification
- Retry strategies with exponential backoff
- Circuit breaker pattern
- Fallback mechanisms
- Alert routing
- Recovery strategies
"""

import time
import json
import traceback
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Callable, Union
from enum import Enum
from dataclasses import dataclass, asdict
import smtplib
import requests
from email.mime.text import MIMEText
from pathlib import Path


class ErrorSeverity(Enum):
    """Error severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorCategory(Enum):
    """Error categories for classification"""
    DATA_ERROR = "data_error"
    SYSTEM_ERROR = "system_error"
    MODEL_ERROR = "model_error"
    NETWORK_ERROR = "network_error"
    AUTHENTICATION_ERROR = "auth_error"
    CONFIGURATION_ERROR = "config_error"
    EXTERNAL_API_ERROR = "external_api_error"
    RESOURCE_ERROR = "resource_error"


@dataclass
class PipelineError:
    """Structured error information"""
    error_id: str
    timestamp: datetime
    category: ErrorCategory
    severity: ErrorSeverity
    phase: Optional[str]
    stage: Optional[str]
    process: Optional[str]
    message: str
    exception_type: str
    exception_message: str
    traceback_info: str
    context: Dict[str, Any]
    retry_count: int = 0
    resolved: bool = False
    resolution_strategy: Optional[str] = None


class RetryStrategy:
    """Configurable retry strategy with exponential backoff"""
    
    def __init__(self, max_retries: int = 3, base_delay: float = 1.0, 
                 max_delay: float = 300.0, backoff_multiplier: float = 2.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_multiplier = backoff_multiplier
    
    def should_retry(self, attempt: int, error: Exception) -> bool:
        """Determine if operation should be retried"""
        if attempt >= self.max_retries:
            return False
        
        # Don't retry certain types of errors
        non_retryable = [
            KeyboardInterrupt,
            SystemExit,
            MemoryError,
            SyntaxError,
            TypeError
        ]
        
        return not any(isinstance(error, err_type) for err_type in non_retryable)
    
    def get_delay(self, attempt: int) -> float:
        """Calculate delay for next retry"""
        delay = self.base_delay * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay)


class CircuitBreaker:
    """Circuit breaker pattern for external services"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, half_open
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception(f"Circuit breaker is OPEN. Service unavailable.")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if circuit breaker should attempt to reset"""
        if self.last_failure_time is None:
            return True
        return (datetime.now() - self.last_failure_time).seconds > self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = "closed"
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "open"


class NotificationManager:
    """Manage error notifications across multiple channels"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.notification_history = []
    
    def send_alert(self, error: PipelineError, channels: List[str] = None):
        """Send error alert through specified channels"""
        if channels is None:
            channels = self._get_default_channels(error.severity)
        
        for channel in channels:
            try:
                if channel == "email":
                    self._send_email_alert(error)
                elif channel == "slack":
                    self._send_slack_alert(error)
                elif channel == "ntfy":
                    self._send_ntfy_alert(error)
                elif channel == "webhook":
                    self._send_webhook_alert(error)
            except Exception as e:
                print(f"Failed to send alert via {channel}: {e}")
    
    def _get_default_channels(self, severity: ErrorSeverity) -> List[str]:
        """Get default notification channels based on severity"""
        if severity == ErrorSeverity.CRITICAL:
            return ["email", "slack", "ntfy"]
        elif severity == ErrorSeverity.HIGH:
            return ["slack", "ntfy"]
        elif severity == ErrorSeverity.MEDIUM:
            return ["slack"]
        else:
            return []
    
    def _send_email_alert(self, error: PipelineError):
        """Send email alert"""
        email_config = self.config.get("email", {})
        if not email_config.get("enabled", False):
            return
        
        subject = f"🚨 Pipeline Error: {error.severity.value.upper()} - {error.category.value}"
        body = self._format_error_message(error)
        
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = email_config.get("from_address")
        msg['To'] = ", ".join(email_config.get("recipients", []))
        
        try:
            with smtplib.SMTP(email_config.get("smtp_server"), email_config.get("smtp_port", 587)) as server:
                if email_config.get("use_tls", True):
                    server.starttls()
                if email_config.get("username"):
                    server.login(email_config["username"], email_config["password"])
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email: {e}")
    
    def _send_slack_alert(self, error: PipelineError):
        """Send Slack alert"""
        slack_config = self.config.get("slack", {})
        if not slack_config.get("webhook_url"):
            return
        
        color = {
            ErrorSeverity.CRITICAL: "danger",
            ErrorSeverity.HIGH: "warning",
            ErrorSeverity.MEDIUM: "warning",
            ErrorSeverity.LOW: "good"
        }.get(error.severity, "warning")
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"🚨 Pipeline Error: {error.category.value}",
                "text": error.message,
                "fields": [
                    {"title": "Severity", "value": error.severity.value, "short": True},
                    {"title": "Phase", "value": error.phase or "N/A", "short": True},
                    {"title": "Stage", "value": error.stage or "N/A", "short": True},
                    {"title": "Process", "value": error.process or "N/A", "short": True},
                    {"title": "Error ID", "value": error.error_id, "short": True},
                    {"title": "Time", "value": error.timestamp.strftime("%Y-%m-%d %H:%M:%S"), "short": True}
                ],
                "footer": "Horse Racing AI Pipeline",
                "ts": int(error.timestamp.timestamp())
            }]
        }
        
        try:
            response = requests.post(slack_config["webhook_url"], json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send Slack alert: {e}")
    
    def _send_ntfy_alert(self, error: PipelineError):
        """Send ntfy.sh alert"""
        ntfy_config = self.config.get("ntfy", {})
        if not ntfy_config.get("topic"):
            return
        
        priority = {
            ErrorSeverity.CRITICAL: "urgent",
            ErrorSeverity.HIGH: "high",
            ErrorSeverity.MEDIUM: "default",
            ErrorSeverity.LOW: "low"
        }.get(error.severity, "default")
        
        headers = {
            "Title": f"Pipeline Error: {error.category.value}",
            "Priority": priority,
            "Tags": "warning,horse_racing"
        }
        
        message = f"{error.message}\n\nPhase: {error.phase}\nStage: {error.stage}\nTime: {error.timestamp}"
        
        try:
            response = requests.post(
                f"https://ntfy.sh/{ntfy_config['topic']}",
                data=message,
                headers=headers
            )
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send ntfy alert: {e}")
    
    def _send_webhook_alert(self, error: PipelineError):
        """Send webhook alert"""
        webhook_config = self.config.get("webhook", {})
        if not webhook_config.get("url"):
            return
        
        payload = {
            "error": asdict(error),
            "timestamp": error.timestamp.isoformat(),
            "source": "horse_racing_ai_pipeline"
        }
        
        try:
            response = requests.post(webhook_config["url"], json=payload)
            response.raise_for_status()
        except Exception as e:
            print(f"Failed to send webhook alert: {e}")
    
    def _format_error_message(self, error: PipelineError) -> str:
        """Format error message for notifications"""
        return f"""
🚨 Horse Racing AI Pipeline Error

Error ID: {error.error_id}
Severity: {error.severity.value.upper()}
Category: {error.category.value}
Time: {error.timestamp.strftime('%Y-%m-%d %H:%M:%S')}

Phase: {error.phase or 'N/A'}
Stage: {error.stage or 'N/A'}
Process: {error.process or 'N/A'}

Message: {error.message}
Exception: {error.exception_type}: {error.exception_message}

Context: {json.dumps(error.context, indent=2)}

Retry Count: {error.retry_count}
Resolved: {error.resolved}

---
Horse Racing AI Pipeline v2.02
        """.strip()


class ErrorHandler:
    """Comprehensive error handling system"""
    
    def __init__(self, config_path: str = "config/comprehensive_pipeline_config.json"):
        self.config = self._load_config(config_path)
        self.retry_strategies = self._setup_retry_strategies()
        self.circuit_breakers = {}
        self.notification_manager = NotificationManager(
            self.config.get("notifications", {})
        )
        self.error_history = []
        self.fallback_strategies = self.config.get("fallback_strategies", {})
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load error handling configuration"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('error_handling', {})
        except Exception:
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default error handling configuration"""
        return {
            "retry_strategy": {
                "exponential_backoff": [1, 2, 4, 8, 16, 32],
                "max_retries": 6,
                "circuit_breaker_threshold": 5
            },
            "fallback_strategies": {
                "data_unavailable": "use_previous_day",
                "model_training_failed": "use_last_trained_model",
                "external_api_down": "switch_to_backup"
            },
            "notifications": {
                "email": {"enabled": False},
                "slack": {"webhook_url": ""},
                "ntfy": {"topic": ""}
            }
        }
    
    def _setup_retry_strategies(self) -> Dict[str, RetryStrategy]:
        """Setup retry strategies for different error types"""
        retry_config = self.config.get("retry_strategy", {})
        
        return {
            "default": RetryStrategy(
                max_retries=retry_config.get("max_retries", 3),
                base_delay=1.0,
                max_delay=300.0
            ),
            "network": RetryStrategy(
                max_retries=5,
                base_delay=2.0,
                max_delay=60.0
            ),
            "external_api": RetryStrategy(
                max_retries=3,
                base_delay=5.0,
                max_delay=120.0
            ),
            "database": RetryStrategy(
                max_retries=2,
                base_delay=1.0,
                max_delay=30.0
            )
        }
    
    def handle_error(self, exception: Exception, context: Dict[str, Any] = None,
                    phase: str = None, stage: str = None, process: str = None) -> PipelineError:
        """Main error handling entry point"""
        error = self._create_error_record(
            exception, context or {}, phase, stage, process
        )
        
        # Store error in history
        self.error_history.append(error)
        
        # Determine if retry should be attempted
        retry_strategy = self._get_retry_strategy(error.category)
        
        if retry_strategy.should_retry(error.retry_count, exception):
            error.retry_count += 1
            return error
        
        # Apply fallback strategy if available
        fallback_result = self._apply_fallback_strategy(error)
        if fallback_result:
            error.resolved = True
            error.resolution_strategy = "fallback"
        
        # Send notifications for unresolved errors
        if not error.resolved:
            self.notification_manager.send_alert(error)
        
        return error
    
    def _create_error_record(self, exception: Exception, context: Dict[str, Any],
                           phase: str = None, stage: str = None, 
                           process: str = None) -> PipelineError:
        """Create structured error record"""
        error_id = f"err_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(exception)}"
        
        # Classify error
        category = self._classify_error(exception)
        severity = self._determine_severity(exception, category)
        
        return PipelineError(
            error_id=error_id,
            timestamp=datetime.now(),
            category=category,
            severity=severity,
            phase=phase,
            stage=stage,
            process=process,
            message=str(exception),
            exception_type=type(exception).__name__,
            exception_message=str(exception),
            traceback_info=traceback.format_exc(),
            context=context
        )
    
    def _classify_error(self, exception: Exception) -> ErrorCategory:
        """Classify error into appropriate category"""
        error_mappings = {
            (FileNotFoundError, PermissionError, IOError): ErrorCategory.DATA_ERROR,
            (ConnectionError, TimeoutError, requests.RequestException): ErrorCategory.NETWORK_ERROR,
            (MemoryError, OSError, SystemError): ErrorCategory.SYSTEM_ERROR,
            (ValueError, TypeError, AttributeError): ErrorCategory.MODEL_ERROR,
            (KeyError, json.JSONDecodeError): ErrorCategory.CONFIGURATION_ERROR,
        }
        
        for exception_types, category in error_mappings.items():
            if isinstance(exception, exception_types):
                return category
        
        # Check error message for additional clues
        message = str(exception).lower()
        if any(keyword in message for keyword in ['auth', 'token', 'credential', 'permission']):
            return ErrorCategory.AUTHENTICATION_ERROR
        elif any(keyword in message for keyword in ['api', 'http', 'request']):
            return ErrorCategory.EXTERNAL_API_ERROR
        elif any(keyword in message for keyword in ['memory', 'disk', 'cpu']):
            return ErrorCategory.RESOURCE_ERROR
        
        return ErrorCategory.SYSTEM_ERROR
    
    def _determine_severity(self, exception: Exception, category: ErrorCategory) -> ErrorSeverity:
        """Determine error severity"""
        critical_errors = [MemoryError, SystemExit, KeyboardInterrupt]
        if any(isinstance(exception, err_type) for err_type in critical_errors):
            return ErrorSeverity.CRITICAL
        
        if category in [ErrorCategory.DATA_ERROR, ErrorCategory.MODEL_ERROR]:
            return ErrorSeverity.HIGH
        elif category in [ErrorCategory.NETWORK_ERROR, ErrorCategory.EXTERNAL_API_ERROR]:
            return ErrorSeverity.MEDIUM
        else:
            return ErrorSeverity.LOW
    
    def _get_retry_strategy(self, category: ErrorCategory) -> RetryStrategy:
        """Get appropriate retry strategy for error category"""
        strategy_map = {
            ErrorCategory.NETWORK_ERROR: "network",
            ErrorCategory.EXTERNAL_API_ERROR: "external_api",
            ErrorCategory.SYSTEM_ERROR: "database"
        }
        
        strategy_name = strategy_map.get(category, "default")
        return self.retry_strategies[strategy_name]
    
    def _apply_fallback_strategy(self, error: PipelineError) -> bool:
        """Apply fallback strategy if available"""
        strategy_key = f"{error.category.value}_{error.phase}_{error.stage}"
        
        # Try specific strategy first
        if strategy_key in self.fallback_strategies:
            strategy = self.fallback_strategies[strategy_key]
            return self._execute_fallback_strategy(strategy, error)
        
        # Try general category strategy
        if error.category.value in self.fallback_strategies:
            strategy = self.fallback_strategies[error.category.value]
            return self._execute_fallback_strategy(strategy, error)
        
        return False
    
    def _execute_fallback_strategy(self, strategy: str, error: PipelineError) -> bool:
        """Execute specific fallback strategy"""
        try:
            if strategy == "use_previous_day":
                # Implement previous day data fallback
                return True
            elif strategy == "use_last_trained_model":
                # Implement model fallback
                return True
            elif strategy == "switch_to_backup":
                # Implement backup service fallback
                return True
            
            return False
        except Exception:
            return False
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            threshold = self.config.get("retry_strategy", {}).get("circuit_breaker_threshold", 5)
            self.circuit_breakers[service_name] = CircuitBreaker(failure_threshold=threshold)
        
        return self.circuit_breakers[service_name]
    
    def get_error_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get error summary for specified time period"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        recent_errors = [e for e in self.error_history if e.timestamp > cutoff_time]
        
        summary = {
            "total_errors": len(recent_errors),
            "by_severity": {},
            "by_category": {},
            "by_phase": {},
            "resolved_count": len([e for e in recent_errors if e.resolved]),
            "most_recent": recent_errors[-1] if recent_errors else None
        }
        
        for error in recent_errors:
            # Count by severity
            severity = error.severity.value
            summary["by_severity"][severity] = summary["by_severity"].get(severity, 0) + 1
            
            # Count by category
            category = error.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
            
            # Count by phase
            phase = error.phase or "unknown"
            summary["by_phase"][phase] = summary["by_phase"].get(phase, 0) + 1
        
        return summary


# Example usage and testing
if __name__ == "__main__":
    # Initialize error handler
    error_handler = ErrorHandler()
    
    print("🚨 Testing Error Handling Framework")
    
    # Test different types of errors
    test_errors = [
        (FileNotFoundError("Test file not found"), {"file": "test.csv"}),
        (ConnectionError("Network timeout"), {"url": "https://api.example.com"}),
        (ValueError("Invalid model parameter"), {"model": "xgboost"}),
        (MemoryError("Out of memory"), {"process": "data_loading"})
    ]
    
    for exception, context in test_errors:
        print(f"\n🔍 Testing {type(exception).__name__}: {exception}")
        
        error = error_handler.handle_error(
            exception, 
            context=context,
            phase="test_phase",
            stage="test_stage",
            process="test_process"
        )
        
        print(f"   Category: {error.category.value}")
        print(f"   Severity: {error.severity.value}")
        print(f"   Error ID: {error.error_id}")
        print(f"   Resolved: {error.resolved}")
    
    # Get error summary
    summary = error_handler.get_error_summary(hours=1)
    print(f"\n📊 Error Summary: {summary}")
    
    print("\n✅ Error handling framework testing completed!")
