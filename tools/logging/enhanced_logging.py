#!/usr/bin/env python3
"""
Enhanced Logging System for Horse Racing AI v2.04
Provides centralized logging configuration for all services
"""

import logging
import logging.config
import logging.handlers
import os
import sys
import yaml
from pathlib import Path
from datetime import datetime
import json


class HorseRacingLogger:
    """Enhanced logging system for Horse Racing AI"""

    def __init__(self, service_name: str = "horse_racing", log_level: str = "INFO"):
        self.service_name = service_name
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.logs_dir = Path("/app/logs")
        self.config_path = Path("/app/config/logging_config.yaml")

        # Ensure logs directory exists
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Initialize logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            # Try to load YAML config first
            if self.config_path.exists():
                with open(self.config_path, "r") as f:
                    config = yaml.safe_load(f)
                logging.config.dictConfig(config)
            else:
                # Fallback to basic configuration
                self._setup_basic_logging()

        except Exception as e:
            # Ultimate fallback
            self._setup_basic_logging()
            logging.warning(f"Failed to load logging config: {e}")

    def _setup_basic_logging(self):
        """Setup basic logging configuration as fallback"""
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(self.log_level)
        console_handler.setFormatter(formatter)

        # File handler
        log_file = self.logs_dir / f"{self.service_name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=5
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)

        # Root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)

    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance"""
        if name:
            return logging.getLogger(f"{self.service_name}.{name}")
        return logging.getLogger(self.service_name)

    def log_system_info(self):
        """Log system information"""
        logger = self.get_logger("system")
        logger.info("=" * 60)
        logger.info(f"🏇 Horse Racing AI v2.04 - {self.service_name.title()} Service")
        logger.info("=" * 60)
        logger.info(f"📅 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"📂 Logs Directory: {self.logs_dir}")
        logger.info(f"📝 Log Level: {logging.getLevelName(self.log_level)}")
        logger.info(f"🐳 Container: {os.getenv('HOSTNAME', 'unknown')}")
        logger.info("=" * 60)

    def log_database_config(self, db_configs: dict):
        """Log database configuration"""
        logger = self.get_logger("database")
        logger.info("🗄️ Database Configuration:")
        for db_name, db_url in db_configs.items():
            # Hide password in logs
            safe_url = (
                db_url.replace(db_url.split("@")[0].split(":")[-1], "***")
                if "@" in db_url
                else db_url
            )
            logger.info(f"  {db_name}: {safe_url}")

    def log_performance_metrics(self, metrics: dict):
        """Log performance metrics"""
        logger = self.get_logger("performance")
        logger.info("📊 Performance Metrics:")
        for metric, value in metrics.items():
            logger.info(f"  {metric}: {value}")

    def log_ml_training_start(self, records_count: int, features_count: int):
        """Log ML training start"""
        logger = self.get_logger("ml_training")
        logger.info("🧠 ML Training Started:")
        logger.info(f"  📊 Training Records: {records_count:,}")
        logger.info(f"  🔢 Features: {features_count}")
        logger.info(f"  ⏰ Start Time: {datetime.now().strftime('%H:%M:%S')}")

    def log_ml_training_result(
        self, model_name: str, accuracy: float, auc: float = None
    ):
        """Log ML training results"""
        logger = self.get_logger("ml_training")
        logger.info("✅ ML Training Completed:")
        logger.info(f"  🤖 Model: {model_name}")
        logger.info(f"  🎯 Accuracy: {accuracy:.3f}")
        if auc:
            logger.info(f"  📈 AUC: {auc:.3f}")
        logger.info(f"  ⏰ Complete Time: {datetime.now().strftime('%H:%M:%S')}")

    def log_error_with_context(self, error: Exception, context: dict = None):
        """Log error with additional context"""
        logger = self.get_logger("error")
        logger.error(f"❌ {type(error).__name__}: {error}")
        if context:
            logger.error(f"📋 Context: {json.dumps(context, indent=2)}")
        logger.error(
            f"📍 Location: {sys.exc_info()[2].tb_frame.f_code.co_filename}:"
            f"{sys.exc_info()[2].tb_lineno}"
        )


def get_enhanced_logger(
    service_name: str = "horse_racing", log_level: str = "INFO"
) -> HorseRacingLogger:
    """Get enhanced logger instance"""
    return HorseRacingLogger(service_name, log_level)


# Example usage and testing
if __name__ == "__main__":
    # Test the logging system
    enhanced_logger = get_enhanced_logger("test_service", "DEBUG")
    enhanced_logger.log_system_info()

    test_logger = enhanced_logger.get_logger("test")
    test_logger.info("✅ Enhanced logging system initialized successfully")
    test_logger.debug("🔍 Debug logging is working")
    test_logger.warning("⚠️ Warning logging is working")
    test_logger.error("❌ Error logging is working")

    # Test database config logging
    enhanced_logger.log_database_config(
        {
            "cards": "postgresql://user:password@host:5432/cards_db",
            "results": "postgresql://user:password@host:5432/results_db",
        }
    )

    # Test performance metrics
    enhanced_logger.log_performance_metrics(
        {
            "training_records": 2379,
            "training_time_seconds": 45.6,
            "model_accuracy": 0.876,
        }
    )

    print("✅ Enhanced logging system test completed")
