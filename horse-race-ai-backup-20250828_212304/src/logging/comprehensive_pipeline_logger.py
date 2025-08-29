#!/usr/bin/env python3
"""
🔧 Comprehensive Pipeline Logger
Advanced logging framework for Horse Racing AI Pipeline

Features:
- Structured JSON logging
- Multiple output destinations
- Log correlation tracking
- Performance metrics
- Error categorization
- Real-time monitoring integration
"""

import json
import logging
import logging.handlers
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid
import psutil
import os


class PipelineLogger:
    """
    Comprehensive logging system for pipeline operations
    """
    
    def __init__(self, config_path: str = "config/comprehensive_pipeline_config.json"):
        self.config = self._load_config(config_path)
        self.correlation_id = self._generate_correlation_id()
        self.logger = self._setup_logger()
        self.metrics = {}
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load logging configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                return config.get('logging_configuration', {})
        except Exception as e:
            # Fallback configuration
            return {
                "log_level": "INFO",
                "structured_logging": True,
                "log_destinations": {
                    "file": {"enabled": True, "path": "logs/pipeline_{date}.log"},
                    "console": {"enabled": True, "format": "detailed"}
                }
            }
    
    def _generate_correlation_id(self) -> str:
        """Generate unique correlation ID for this pipeline run"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return f"pipeline_{timestamp}_{uuid.uuid4().hex[:8]}"
    
    def _setup_logger(self) -> logging.Logger:
        """Setup comprehensive logger with multiple handlers"""
        logger = logging.getLogger(f"pipeline_{self.correlation_id}")
        logger.setLevel(getattr(logging, self.config.get('log_level', 'INFO')))
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # File handler with rotation
        if self.config.get('log_destinations', {}).get('file', {}).get('enabled', True):
            self._setup_file_handler(logger)
        
        # Console handler
        if self.config.get('log_destinations', {}).get('console', {}).get('enabled', True):
            self._setup_console_handler(logger)
        
        return logger
    
    def _setup_file_handler(self, logger: logging.Logger):
        """Setup rotating file handler"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"pipeline_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=100 * 1024 * 1024,  # 100MB
            backupCount=30
        )
        
        if self.config.get('structured_logging', True):
            file_handler.setFormatter(StructuredFormatter())
        else:
            file_handler.setFormatter(StandardFormatter())
        
        logger.addHandler(file_handler)
    
    def _setup_console_handler(self, logger: logging.Logger):
        """Setup console handler"""
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter())
        logger.addHandler(console_handler)
    
    def start_phase(self, phase_name: str, phase_id: str) -> Dict[str, Any]:
        """Log the start of a pipeline phase"""
        phase_context = {
            "phase_name": phase_name,
            "phase_id": phase_id,
            "start_time": datetime.now().isoformat(),
            "correlation_id": self.correlation_id
        }
        
        self.log_info(
            f"🚀 Starting Phase: {phase_name}",
            phase=phase_id,
            event_type="phase_start",
            metadata=phase_context
        )
        
        return phase_context
    
    def end_phase(self, phase_context: Dict[str, Any], success: bool = True, 
                  error: Optional[Exception] = None):
        """Log the end of a pipeline phase"""
        end_time = datetime.now()
        start_time = datetime.fromisoformat(phase_context["start_time"])
        duration = (end_time - start_time).total_seconds()
        
        phase_context.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "success": success
        })
        
        if success:
            self.log_info(
                f"✅ Completed Phase: {phase_context['phase_name']} ({duration:.2f}s)",
                phase=phase_context["phase_id"],
                event_type="phase_end",
                metadata=phase_context
            )
        else:
            self.log_error(
                f"❌ Failed Phase: {phase_context['phase_name']} ({duration:.2f}s)",
                phase=phase_context["phase_id"],
                event_type="phase_error",
                error=error,
                metadata=phase_context
            )
    
    def start_stage(self, stage_name: str, stage_id: str, phase_id: str) -> Dict[str, Any]:
        """Log the start of a pipeline stage"""
        stage_context = {
            "stage_name": stage_name,
            "stage_id": stage_id,
            "phase_id": phase_id,
            "start_time": datetime.now().isoformat(),
            "correlation_id": self.correlation_id
        }
        
        self.log_info(
            f"  🔧 Starting Stage: {stage_name}",
            phase=phase_id,
            stage=stage_id,
            event_type="stage_start",
            metadata=stage_context
        )
        
        return stage_context
    
    def end_stage(self, stage_context: Dict[str, Any], success: bool = True,
                  metrics: Optional[Dict[str, Any]] = None,
                  error: Optional[Exception] = None):
        """Log the end of a pipeline stage"""
        end_time = datetime.now()
        start_time = datetime.fromisoformat(stage_context["start_time"])
        duration = (end_time - start_time).total_seconds()
        
        stage_context.update({
            "end_time": end_time.isoformat(),
            "duration_seconds": duration,
            "success": success,
            "metrics": metrics or {}
        })
        
        if success:
            metrics_str = f" | {metrics}" if metrics else ""
            self.log_info(
                f"  ✅ Completed Stage: {stage_context['stage_name']} ({duration:.2f}s){metrics_str}",
                phase=stage_context["phase_id"],
                stage=stage_context["stage_id"],
                event_type="stage_end",
                metadata=stage_context
            )
        else:
            self.log_error(
                f"  ❌ Failed Stage: {stage_context['stage_name']} ({duration:.2f}s)",
                phase=stage_context["phase_id"],
                stage=stage_context["stage_id"],
                event_type="stage_error",
                error=error,
                metadata=stage_context
            )
    
    def log_process(self, process_name: str, message: str, 
                   phase: str = None, stage: str = None,
                   metrics: Optional[Dict[str, Any]] = None,
                   level: str = "INFO"):
        """Log process-level information"""
        log_func = getattr(self, f"log_{level.lower()}")
        log_func(
            f"    ⚙️  {process_name}: {message}",
            phase=phase,
            stage=stage,
            process=process_name,
            event_type="process_log",
            metadata={
                "process_name": process_name,
                "metrics": metrics or {},
                "system_metrics": self._get_system_metrics()
            }
        )
    
    def log_data_quality(self, validation_results: Dict[str, Any],
                        phase: str = None, stage: str = None):
        """Log data quality metrics"""
        quality_score = validation_results.get('quality_score', 0)
        
        if quality_score >= 95:
            level = "INFO"
            emoji = "✅"
        elif quality_score >= 90:
            level = "WARNING"
            emoji = "⚠️"
        else:
            level = "ERROR"
            emoji = "❌"
        
        log_func = getattr(self, f"log_{level.lower()}")
        log_func(
            f"    {emoji} Data Quality: {quality_score}% | {validation_results}",
            phase=phase,
            stage=stage,
            event_type="data_quality",
            metadata={
                "quality_score": quality_score,
                "validation_results": validation_results
            }
        )
    
    def log_ml_metrics(self, model_name: str, metrics: Dict[str, Any],
                      phase: str = None, stage: str = None):
        """Log machine learning model metrics"""
        accuracy = metrics.get('accuracy', 0)
        
        if accuracy >= 0.75:
            emoji = "🎯"
        elif accuracy >= 0.70:
            emoji = "📈"
        else:
            emoji = "📉"
        
        self.log_info(
            f"    {emoji} Model {model_name}: Accuracy={accuracy:.3f} | {metrics}",
            phase=phase,
            stage=stage,
            event_type="ml_metrics",
            metadata={
                "model_name": model_name,
                "metrics": metrics
            }
        )
    
    def log_betting_analysis(self, analysis_results: Dict[str, Any],
                           phase: str = None, stage: str = None):
        """Log betting analysis results"""
        roi = analysis_results.get('roi', 0)
        
        if roi > 0.10:
            emoji = "💰"
        elif roi > 0:
            emoji = "📊"
        else:
            emoji = "📉"
        
        self.log_info(
            f"    {emoji} Betting Analysis: ROI={roi:.2%} | {analysis_results}",
            phase=phase,
            stage=stage,
            event_type="betting_analysis",
            metadata={
                "analysis_results": analysis_results
            }
        )
    
    def _get_system_metrics(self) -> Dict[str, Any]:
        """Get current system performance metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else None
            }
        except Exception:
            return {}
    
    def log_critical(self, message: str, **kwargs):
        """Log critical level message"""
        self._log_structured("CRITICAL", message, **kwargs)
    
    def log_error(self, message: str, error: Optional[Exception] = None, **kwargs):
        """Log error level message"""
        if error:
            kwargs['error_details'] = {
                "type": type(error).__name__,
                "message": str(error),
                "traceback": traceback.format_exc()
            }
        self._log_structured("ERROR", message, **kwargs)
    
    def log_warning(self, message: str, **kwargs):
        """Log warning level message"""
        self._log_structured("WARNING", message, **kwargs)
    
    def log_info(self, message: str, **kwargs):
        """Log info level message"""
        self._log_structured("INFO", message, **kwargs)
    
    def log_debug(self, message: str, **kwargs):
        """Log debug level message"""
        self._log_structured("DEBUG", message, **kwargs)
    
    def _log_structured(self, level: str, message: str, **kwargs):
        """Log with structured format"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "correlation_id": self.correlation_id,
            **kwargs
        }
        
        # Use appropriate logging level
        log_func = getattr(self.logger, level.lower())
        
        if self.config.get('structured_logging', True):
            log_func(json.dumps(log_entry))
        else:
            log_func(message)


class StructuredFormatter(logging.Formatter):
    """Formatter for structured JSON logging"""
    
    def format(self, record):
        try:
            # Try to parse as JSON for structured logs
            log_data = json.loads(record.getMessage())
            return json.dumps(log_data, indent=None, separators=(',', ':'))
        except (json.JSONDecodeError, ValueError):
            # Fallback to standard formatting
            return super().format(record)


class StandardFormatter(logging.Formatter):
    """Standard text formatter"""
    
    def __init__(self):
        super().__init__(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )


class ColoredFormatter(logging.Formatter):
    """Colored console formatter"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        try:
            # Try to parse structured logs and format nicely
            log_data = json.loads(record.getMessage())
            message = log_data.get('message', '')
            level = log_data.get('level', record.levelname)
            timestamp = log_data.get('timestamp', '').split('T')[1][:8]  # Just time
            
            color = self.COLORS.get(level, '')
            reset = self.COLORS['RESET']
            
            # Format: [TIME] LEVEL: MESSAGE
            return f"{color}[{timestamp}] {level}: {message}{reset}"
        except (json.JSONDecodeError, ValueError, KeyError):
            # Fallback for non-structured logs
            color = self.COLORS.get(record.levelname, '')
            reset = self.COLORS['RESET']
            return f"{color}[{record.asctime}] {record.levelname}: {record.getMessage()}{reset}"


# Example usage and testing
if __name__ == "__main__":
    # Initialize logger
    logger = PipelineLogger()
    
    # Test different log levels
    logger.log_info("🏇 Pipeline system initialized")
    
    # Test phase logging
    phase_ctx = logger.start_phase("Data Acquisition", "phase_1")
    
    # Test stage logging
    stage_ctx = logger.start_stage("Data Download", "stage_1_1", "phase_1")
    
    # Test process logging
    logger.log_process("auto_downloader", "Successfully downloaded 61 races", 
                      phase="phase_1", stage="stage_1_1",
                      metrics={"race_count": 61, "file_size_mb": 2.5})
    
    # Test data quality logging
    logger.log_data_quality({
        "quality_score": 97,
        "missing_data": "2%",
        "validation_passed": True
    }, phase="phase_1", stage="stage_1_1")
    
    # Test ML metrics logging
    logger.log_ml_metrics("XGBoost", {
        "accuracy": 0.765,
        "auc": 0.823,
        "precision": 0.741
    }, phase="phase_2", stage="stage_2_1")
    
    # Test error logging
    try:
        raise ValueError("Test error for logging")
    except Exception as e:
        logger.log_error("Test error occurred", error=e, phase="test")
    
    # End stage and phase
    logger.end_stage(stage_ctx, success=True, metrics={"files_processed": 15})
    logger.end_phase(phase_ctx, success=True)
    
    print(f"\n✅ Logger testing completed! Correlation ID: {logger.correlation_id}")
    print(f"📁 Logs saved to: logs/pipeline_{datetime.now().strftime('%Y%m%d')}.log")
