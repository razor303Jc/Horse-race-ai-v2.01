#!/usr/bin/env python3
"""
📊 Pipeline Logging & Configuration System
==========================================

Enhanced logging configuration with structured output,
log rotation, and integration with monitoring systems.
"""

import json
import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


class PipelineLogger:
    """Enhanced logging system for pipeline operations"""

    def __init__(self, project_root: str = None):
        self.project_root = Path(
            project_root or "/home/jc/Documents/Horse-race-ai-v2.04"
        )
        self.logs_dir = self.project_root / "logs"
        self.logs_dir.mkdir(exist_ok=True)

        # Create loggers for different components
        self.loggers = {}
        self.setup_loggers()

    def setup_loggers(self):
        """Setup different loggers for pipeline components"""

        # Main pipeline logger
        self.loggers["pipeline"] = self.create_logger(
            "pipeline", self.logs_dir / "pipeline.log", level=logging.INFO
        )

        # File watcher logger
        self.loggers["watcher"] = self.create_logger(
            "watcher", self.logs_dir / "daily_file_watcher.log", level=logging.INFO
        )

        # Database operations logger
        self.loggers["database"] = self.create_logger(
            "database", self.logs_dir / "database.log", level=logging.INFO
        )

        # ML operations logger
        self.loggers["ml"] = self.create_logger(
            "ml", self.logs_dir / "ml_operations.log", level=logging.INFO
        )

        # System monitor logger
        self.loggers["monitor"] = self.create_logger(
            "monitor", self.logs_dir / "system_monitor.log", level=logging.INFO
        )

        # Error logger (all errors from all components)
        self.loggers["error"] = self.create_logger(
            "error", self.logs_dir / "errors.log", level=logging.ERROR
        )

    def create_logger(self, name: str, log_file: Path, level: int = logging.INFO):
        """Create a configured logger with rotation"""

        logger = logging.getLogger(name)
        logger.setLevel(level)

        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # File handler with rotation
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10MB
        )

        # Console handler
        console_handler = logging.StreamHandler()

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def get_logger(self, component: str) -> logging.Logger:
        """Get logger for specific component"""
        return self.loggers.get(component, self.loggers["pipeline"])

    def log_pipeline_event(self, stage: str, event: str, data: Dict[str, Any] = None):
        """Log structured pipeline events"""
        logger = self.get_logger("pipeline")

        event_data = {
            "timestamp": datetime.now().isoformat(),
            "stage": stage,
            "event": event,
            "data": data or {},
        }

        logger.info(f"PIPELINE_EVENT: {json.dumps(event_data)}")

    def log_file_operation(
        self,
        operation: str,
        file_path: str,
        status: str,
        details: Dict[str, Any] = None,
    ):
        """Log file operations"""
        logger = self.get_logger("watcher")

        operation_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "file_path": file_path,
            "status": status,
            "details": details or {},
        }

        logger.info(f"FILE_OPERATION: {json.dumps(operation_data)}")

    def log_database_operation(
        self, operation: str, table: str, status: str, details: Dict[str, Any] = None
    ):
        """Log database operations"""
        logger = self.get_logger("database")

        db_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "table": table,
            "status": status,
            "details": details or {},
        }

        logger.info(f"DB_OPERATION: {json.dumps(db_data)}")

    def log_ml_operation(
        self, operation: str, model: str, status: str, metrics: Dict[str, Any] = None
    ):
        """Log ML operations"""
        logger = self.get_logger("ml")

        ml_data = {
            "timestamp": datetime.now().isoformat(),
            "operation": operation,
            "model": model,
            "status": status,
            "metrics": metrics or {},
        }

        logger.info(f"ML_OPERATION: {json.dumps(ml_data)}")

    def log_system_status(
        self, component: str, status: str, metrics: Dict[str, Any] = None
    ):
        """Log system status"""
        logger = self.get_logger("monitor")

        status_data = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "status": status,
            "metrics": metrics or {},
        }

        logger.info(f"SYSTEM_STATUS: {json.dumps(status_data)}")

    def log_error(self, component: str, error: str, details: Dict[str, Any] = None):
        """Log errors from any component"""
        logger = self.get_logger("error")

        error_data = {
            "timestamp": datetime.now().isoformat(),
            "component": component,
            "error": error,
            "details": details or {},
        }

        logger.error(f"ERROR: {json.dumps(error_data)}")


# Global logger instance
pipeline_logger = PipelineLogger()


def get_pipeline_logger(component: str = "pipeline") -> logging.Logger:
    """Get configured pipeline logger"""
    return pipeline_logger.get_logger(component)


def log_pipeline_event(stage: str, event: str, data: Dict[str, Any] = None):
    """Convenience function for logging pipeline events"""
    pipeline_logger.log_pipeline_event(stage, event, data)


def log_file_operation(
    operation: str, file_path: str, status: str, details: Dict[str, Any] = None
):
    """Convenience function for logging file operations"""
    pipeline_logger.log_file_operation(operation, file_path, status, details)


def log_database_operation(
    operation: str, table: str, status: str, details: Dict[str, Any] = None
):
    """Convenience function for logging database operations"""
    pipeline_logger.log_database_operation(operation, table, status, details)


def log_ml_operation(
    operation: str, model: str, status: str, metrics: Dict[str, Any] = None
):
    """Convenience function for logging ML operations"""
    pipeline_logger.log_ml_operation(operation, model, status, metrics)


def log_system_status(component: str, status: str, metrics: Dict[str, Any] = None):
    """Convenience function for logging system status"""
    pipeline_logger.log_system_status(component, status, metrics)


def log_error(component: str, error: str, details: Dict[str, Any] = None):
    """Convenience function for logging errors"""
    pipeline_logger.log_error(component, error, details)
