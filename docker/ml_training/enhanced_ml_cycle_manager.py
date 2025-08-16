#!/usr/bin/env python3
"""
Enhanced ML Training Cycle Manager with Comprehensive Logging and Error Handling
Horse Racing AI v2.02 - Docker Integration

Early Morning ML Training System (00:30-04:00)
- Designed for 3.5-hour training window after auto-download
- Comprehensive error handling and retry logic
- Docker-native logging and monitoring
- Performance tracking and optimization
"""

import asyncio
import json
import logging
import os
import sys
import traceback
import time
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import numpy as np
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "pipeline_management"))

# Docker logging configuration
class DockerLoggingSetup:
    """Configure comprehensive logging for Docker environment"""
    
    @staticmethod
    def setup_logging(component_name: str = "early_morning_ml") -> logging.Logger:
        """Setup comprehensive logging with Docker-friendly configuration"""
        
        # Create logs directory if it doesn't exist
        log_dir = Path("/app/logs") if Path("/app/logs").exists() else Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Configure logger
        logger = logging.getLogger(component_name)
        logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers
        logger.handlers.clear()
        
        # Formatter with detailed context
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[PID:%(process)d] [Thread:%(thread)d] - %(message)s"
        )
        
        # Console handler for Docker logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"{component_name}_detailed.log", 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Error-specific handler
        error_handler = logging.FileHandler(
            log_dir / f"{component_name}_errors.log", 
            mode='a', 
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)
        
        # Performance metrics handler
        perf_handler = logging.FileHandler(
            log_dir / f"{component_name}_performance.log", 
            mode='a', 
            encoding='utf-8'
        )
        perf_handler.setLevel(logging.INFO)
        perf_formatter = logging.Formatter(
            "%(asctime)s - PERF - %(message)s"
        )
        perf_handler.setFormatter(perf_formatter)
        
        # Create performance logger
        perf_logger = logging.getLogger(f"{component_name}_performance")
        perf_logger.setLevel(logging.INFO)
        perf_logger.addHandler(perf_handler)
        
        return logger

# Initialize logging
logger = DockerLoggingSetup.setup_logging("ml_training_cycle_manager")
perf_logger = logging.getLogger("ml_training_cycle_manager_performance")


@dataclass
class TrainingMetrics:
    """Enhanced training performance metrics with error tracking"""
    
    cycle_id: int
    batch_id: int
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_seconds: Optional[float] = None
    records_processed: int = 0
    model_accuracy: Optional[float] = None
    training_loss: Optional[float] = None
    validation_score: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    cpu_usage_percent: Optional[float] = None
    error_count: int = 0
    warning_count: int = 0
    retry_count: int = 0
    success: bool = False
    error_details: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        # Convert datetime objects to ISO strings
        if self.start_time:
            result['start_time'] = self.start_time.isoformat()
        if self.end_time:
            result['end_time'] = self.end_time.isoformat()
        return result


@dataclass 
class SessionSummary:
    """Enhanced session summary with comprehensive error tracking"""
    
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    total_records: int = 0
    avg_accuracy: Optional[float] = None
    total_errors: int = 0
    total_warnings: int = 0
    total_retries: int = 0
    session_success: bool = False
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    error_summary: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        result = asdict(self)
        if self.start_time:
            result['start_time'] = self.start_time.isoformat()
        if self.end_time:
            result['end_time'] = self.end_time.isoformat()
        return result


class DatabaseManager:
    """Enhanced database manager with connection pooling and error handling"""
    
    def __init__(self):
        self.connection_params = self._get_connection_params()
        self.max_retries = 3
        self.retry_delay = 2.0
        
    def _get_connection_params(self) -> Dict[str, str]:
        """Get database connection parameters from environment"""
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Parse DATABASE_URL
            import urllib.parse
            parsed = urllib.parse.urlparse(db_url)
            return {
                'host': parsed.hostname,
                'port': parsed.port or 5432,
                'database': parsed.path[1:] if parsed.path else 'horse_racing_db',
                'user': parsed.username,
                'password': parsed.password
            }
        else:
            # Fallback to individual environment variables
            return {
                'host': os.getenv('DB_HOST', 'localhost'),
                'port': int(os.getenv('DB_PORT', 5432)),
                'database': os.getenv('DB_NAME', 'horse_racing_db'),
                'user': os.getenv('DB_USER', 'horse_racing'),
                'password': os.getenv('DB_PASSWORD', 'secure_password_123')
            }
    
    @asynccontextmanager
    async def get_connection(self):
        """Get database connection with automatic retry and cleanup"""
        connection = None
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                connection = psycopg2.connect(**self.connection_params)
                connection.autocommit = True
                logger.debug(f"Database connection established (attempt {retry_count + 1})")
                yield connection
                return
                
            except psycopg2.Error as e:
                retry_count += 1
                logger.warning(
                    f"Database connection failed (attempt {retry_count}/{self.max_retries}): {e}"
                )
                
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                    connection = None
                
                if retry_count < self.max_retries:
                    await asyncio.sleep(self.retry_delay * retry_count)
                else:
                    logger.error("Database connection failed after all retry attempts")
                    raise
                    
            except Exception as e:
                logger.error(f"Unexpected error in database connection: {e}")
                if connection:
                    try:
                        connection.close()
                    except:
                        pass
                raise
            
            finally:
                if connection:
                    try:
                        connection.close()
                        logger.debug("Database connection closed")
                    except Exception as e:
                        logger.warning(f"Error closing database connection: {e}")


class ErrorHandler:
    """Centralized error handling with categorization and recovery strategies"""
    
    def __init__(self):
        self.error_counts = {}
        self.error_categories = {
            'database': ['psycopg2', 'connection', 'sql'],
            'memory': ['memory', 'allocation', 'out of memory'],
            'model': ['model', 'training', 'sklearn', 'numpy'],
            'data': ['data', 'missing', 'null', 'format'],
            'timeout': ['timeout', 'timed out', 'deadline'],
            'network': ['network', 'connection refused', 'unreachable']
        }
        
    def categorize_error(self, error: Exception) -> str:
        """Categorize error for better handling"""
        error_str = str(error).lower()
        error_type = type(error).__name__.lower()
        
        for category, keywords in self.error_categories.items():
            if any(keyword in error_str or keyword in error_type for keyword in keywords):
                return category
        
        return 'unknown'
    
    def should_retry(self, error: Exception, retry_count: int, max_retries: int = 3) -> bool:
        """Determine if error should trigger a retry"""
        if retry_count >= max_retries:
            return False
            
        category = self.categorize_error(error)
        
        # Retryable error categories
        retryable_categories = ['database', 'network', 'timeout']
        
        return category in retryable_categories
    
    def get_recovery_strategy(self, error: Exception) -> Dict[str, Any]:
        """Get recovery strategy for specific error types"""
        category = self.categorize_error(error)
        
        strategies = {
            'database': {
                'wait_time': 5.0,
                'max_retries': 5,
                'action': 'reconnect'
            },
            'memory': {
                'wait_time': 10.0,
                'max_retries': 2,
                'action': 'reduce_batch_size'
            },
            'model': {
                'wait_time': 2.0,
                'max_retries': 3,
                'action': 'reinitialize_model'
            },
            'timeout': {
                'wait_time': 15.0,
                'max_retries': 3,
                'action': 'increase_timeout'
            }
        }
        
        return strategies.get(category, {
            'wait_time': 3.0,
            'max_retries': 2,
            'action': 'generic_retry'
        })


class EnhancedMLCycleManager:
    """
    Enhanced ML Training Cycle Manager with comprehensive error handling,
    logging, and Docker integration for early morning training schedules.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_default_config()
        self.db_manager = DatabaseManager()
        self.error_handler = ErrorHandler()
        
        # Training state
        self.current_session_id = None
        self.training_metrics: List[TrainingMetrics] = []
        self.session_summaries: List[SessionSummary] = []
        
        # Performance tracking
        self.start_time = None
        self.total_cycles_completed = 0
        self.total_errors = 0
        
        # Early morning schedule (00:30-04:00)
        self.early_morning_start = "00:30"
        self.early_morning_end = "04:00"
        self.training_window_minutes = 210  # 3.5 hours
        
        logger.info("Enhanced ML Cycle Manager initialized for early morning training")
        logger.info(f"Training window: {self.early_morning_start} - {self.early_morning_end}")
        
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default configuration optimized for early morning training"""
        return {
            'cycles_per_session': 10,
            'max_sessions': 1000,
            'batch_size': 1000,
            'early_morning_mode': True,
            'max_training_time_minutes': 210,  # 3.5 hours
            'cycle_timeout_minutes': 20,
            'session_timeout_minutes': 210,
            'auto_recovery': True,
            'performance_monitoring': True,
            'detailed_logging': True
        }


async def main():
    """Main entry point for enhanced ML training cycle manager"""
    try:
        logger.info("🌅 Starting Enhanced Early Morning ML Training System")
        logger.info("=" * 60)
        
        # Initialize manager
        manager = EnhancedMLCycleManager()
        
        # Check if we're in the training window
        current_time = datetime.now().time()
        start_time = datetime.strptime(manager.early_morning_start, "%H:%M").time()
        end_time = datetime.strptime(manager.early_morning_end, "%H:%M").time()
        
        if start_time <= current_time <= end_time:
            logger.info(f"✅ In early morning training window ({current_time})")
            # Start training session
            await manager.run_training_session()
        else:
            logger.info(f"⏰ Outside training window (current: {current_time}, window: {start_time}-{end_time})")
            logger.info("Scheduling for next training window...")
            
    except Exception as e:
        logger.error(f"Fatal error in main: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
