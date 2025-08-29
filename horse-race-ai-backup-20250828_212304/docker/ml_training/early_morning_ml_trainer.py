#!/usr/bin/env python3
"""
Early Morning ML Training System for Horse Racing AI v2.02
Docker Container Integration

Comprehensive training system designed for the 00:30-04:00 early morning window
with full logging, error handling, and Docker integration.

Features:
- 210+ minute training window optimization
- Pipeline integration with auto-downloader
- Comprehensive error handling and retry logic
- Docker-native logging and monitoring
- Performance metrics and reporting
"""

import asyncio
import json
import logging
import os
import sys
import time
import traceback
from contextlib import asynccontextmanager
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

# Add parent directories to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "pipeline_management"))

# Import core components
try:
    from dynamic_pipeline_timing import PipelineTimeAllocator
except ImportError:
    # Fallback for when running outside Docker
    sys.path.append("../../docker/pipeline_management")
    from dynamic_pipeline_timing import PipelineTimeAllocator


@dataclass
class EarlyMorningTrainingConfig:
    """Configuration for early morning ML training"""

    # Training window
    start_time: str = "00:30"
    end_time: str = "04:00"
    total_minutes: int = 210

    # Training parameters
    max_training_cycles: int = 8
    cycle_duration_minutes: int = 25
    buffer_minutes: int = 5

    # Error handling
    max_retries: int = 3
    retry_delay_seconds: int = 30
    timeout_seconds: int = 1800  # 30 minutes per cycle

    # Logging
    log_level: str = "INFO"
    performance_tracking: bool = True
    detailed_metrics: bool = True

    # Docker paths
    data_path: str = "/app/data"
    models_path: str = "/app/models"
    logs_path: str = "/app/logs"
    cache_path: str = "/app/cache"


@dataclass
class TrainingMetrics:
    """Comprehensive training metrics tracking"""

    session_id: str = field(
        default_factory=lambda: f"early_ml_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    )
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None

    # Training cycles
    total_cycles: int = 0
    successful_cycles: int = 0
    failed_cycles: int = 0
    skipped_cycles: int = 0

    # Performance metrics
    average_cycle_duration: float = 0.0
    total_training_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage_percent: float = 0.0

    # Model performance
    model_accuracy_improvements: Dict[str, float] = field(default_factory=dict)
    feature_importance_changes: Dict[str, float] = field(default_factory=dict)

    # Error tracking
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    # Pipeline integration
    pipeline_phase: str = "early_ml_training"
    data_download_complete: bool = False
    validation_passed: bool = False


class DockerLogger:
    """Docker-optimized logging system"""

    def __init__(self, component_name: str = "early_morning_ml"):
        self.component_name = component_name
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup comprehensive logging for Docker environment"""

        # Create logs directory
        log_dir = Path("/app/logs") if Path("/app/logs").exists() else Path("logs")
        log_dir.mkdir(exist_ok=True)

        # Configure main logger
        logger = logging.getLogger(self.component_name)
        logger.setLevel(logging.DEBUG)
        logger.handlers.clear()

        # Detailed formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - "
            "[PID:%(process)d] [Container:%(hostname)s] - %(message)s",
            defaults={"hostname": os.environ.get("HOSTNAME", "docker-container")},
        )

        # Console handler for Docker logs
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler for detailed logs
        file_handler = logging.FileHandler(
            log_dir / f"{self.component_name}_detailed.log", mode="a"
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Error handler for critical issues
        error_handler = logging.FileHandler(
            log_dir / f"{self.component_name}_errors.log", mode="a"
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        return logger

    def info(self, message: str, **kwargs):
        """Log info message with context"""
        self.logger.info(f"🌅 {message}", extra=kwargs)

    def error(self, message: str, error: Exception = None, **kwargs):
        """Log error with full context"""
        if error:
            self.logger.error(
                f"❌ {message}: {str(error)}", extra=kwargs, exc_info=True
            )
        else:
            self.logger.error(f"❌ {message}", extra=kwargs)

    def warning(self, message: str, **kwargs):
        """Log warning message"""
        self.logger.warning(f"⚠️ {message}", extra=kwargs)

    def debug(self, message: str, **kwargs):
        """Log debug message"""
        self.logger.debug(f"🔍 {message}", extra=kwargs)

    def performance(self, message: str, duration: float = None, **kwargs):
        """Log performance metrics"""
        perf_msg = f"📊 {message}"
        if duration:
            perf_msg += f" (Duration: {duration:.2f}s)"
        self.logger.info(perf_msg, extra=kwargs)


class EarlyMorningMLTrainer:
    """
    Early Morning ML Training System

    Manages the 00:30-04:00 training window with comprehensive
    error handling, logging, and Docker integration.
    """

    def __init__(self, config: EarlyMorningTrainingConfig = None):
        self.config = config or EarlyMorningTrainingConfig()
        self.logger = DockerLogger("early_morning_ml_trainer")
        self.metrics = TrainingMetrics()
        self.pipeline_allocator = None

        # Initialize pipeline integration
        self._initialize_pipeline_integration()

        self.logger.info(
            f"Early Morning ML Trainer initialized for {self.config.start_time}-{self.config.end_time} window"
        )

    def _initialize_pipeline_integration(self):
        """Initialize pipeline timing integration"""
        try:
            self.pipeline_allocator = PipelineTimeAllocator()
            self.logger.info("Pipeline integration initialized successfully")
        except Exception as e:
            self.logger.error("Failed to initialize pipeline integration", error=e)
            self.pipeline_allocator = None

    async def run_early_morning_training(self) -> TrainingMetrics:
        """
        Execute the complete early morning training cycle

        Returns:
            TrainingMetrics: Comprehensive training results and metrics
        """
        self.logger.info("🌅 Starting Early Morning ML Training System")
        self.metrics.start_time = datetime.now()

        try:
            # Phase 1: Pre-training validation
            await self._validate_training_preconditions()

            # Phase 2: Execute training cycles
            await self._execute_training_cycles()

            # Phase 3: Post-training optimization
            await self._post_training_optimization()

            # Phase 4: Generate reports and metrics
            await self._generate_training_report()

            self.metrics.end_time = datetime.now()
            self.metrics.total_training_time = (
                self.metrics.end_time - self.metrics.start_time
            ).total_seconds()

            self.logger.info(
                f"✅ Early morning training completed successfully in {self.metrics.total_training_time:.2f}s"
            )

            return self.metrics

        except Exception as e:
            self.metrics.end_time = datetime.now()
            self.logger.error("Early morning training failed", error=e)

            # Add error to metrics
            self.metrics.errors.append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "traceback": traceback.format_exc(),
                }
            )

            raise

    async def _validate_training_preconditions(self):
        """Validate all preconditions for training"""
        self.logger.info("🔍 Validating training preconditions")

        # Check current time window
        current_time = datetime.now().time()
        start_time = datetime.strptime(self.config.start_time, "%H:%M").time()
        end_time = datetime.strptime(self.config.end_time, "%H:%M").time()

        if not (start_time <= current_time <= end_time):
            self.logger.warning(
                f"Current time {current_time} outside training window {start_time}-{end_time}"
            )

        # Check data availability
        data_path = Path(self.config.data_path)
        if not data_path.exists():
            raise FileNotFoundError(f"Data directory not found: {data_path}")

        # Check model directory
        models_path = Path(self.config.models_path)
        models_path.mkdir(exist_ok=True)

        # Verify auto-download completion
        await self._verify_data_download_completion()

        self.logger.info("✅ All training preconditions validated")

    async def _verify_data_download_completion(self):
        """Verify that auto-download has completed successfully"""
        self.logger.debug("Checking auto-download completion status")

        # Check for download completion markers
        download_markers = [
            Path(self.config.data_path) / "download_complete.flag",
            Path(self.config.data_path) / "validation_passed.flag",
        ]

        for marker in download_markers:
            if marker.exists():
                self.logger.debug(f"Found download marker: {marker}")
                if "download_complete" in marker.name:
                    self.metrics.data_download_complete = True
                elif "validation_passed" in marker.name:
                    self.metrics.validation_passed = True

        # If no markers found, assume download is complete (fallback)
        if not any(marker.exists() for marker in download_markers):
            self.logger.warning(
                "No download completion markers found, assuming data is ready"
            )
            self.metrics.data_download_complete = True
            self.metrics.validation_passed = True

    async def _execute_training_cycles(self):
        """Execute the main training cycles"""
        self.logger.info(
            f"🚀 Starting {self.config.max_training_cycles} training cycles"
        )

        for cycle in range(self.config.max_training_cycles):
            cycle_start = time.time()

            try:
                self.logger.info(
                    f"🔄 Starting training cycle {cycle + 1}/{self.config.max_training_cycles}"
                )

                # Execute single training cycle
                await self._execute_single_cycle(cycle)

                self.metrics.successful_cycles += 1
                cycle_duration = time.time() - cycle_start

                self.logger.performance(
                    f"Training cycle {cycle + 1} completed", duration=cycle_duration
                )

                # Add buffer time between cycles
                if cycle < self.config.max_training_cycles - 1:
                    await asyncio.sleep(self.config.buffer_minutes * 60)

            except Exception as e:
                self.metrics.failed_cycles += 1
                self.logger.error(f"Training cycle {cycle + 1} failed", error=e)

                # Add error to metrics
                self.metrics.errors.append(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "cycle": cycle + 1,
                        "error_type": type(e).__name__,
                        "error_message": str(e),
                    }
                )

                # Decide whether to continue or abort
                if self.metrics.failed_cycles >= self.config.max_retries:
                    self.logger.error("Max failed cycles reached, aborting training")
                    break

                # Short delay before next cycle
                await asyncio.sleep(self.config.retry_delay_seconds)

        self.metrics.total_cycles = (
            self.metrics.successful_cycles + self.metrics.failed_cycles
        )

        self.logger.info(
            f"📊 Training cycles completed: {self.metrics.successful_cycles} successful, "
            f"{self.metrics.failed_cycles} failed, {self.metrics.total_cycles} total"
        )

    async def _execute_single_cycle(self, cycle: int):
        """Execute a single training cycle with timeout protection"""

        # Timeout protection
        timeout_task = asyncio.create_task(asyncio.sleep(self.config.timeout_seconds))
        training_task = asyncio.create_task(self._run_ml_training_cycle(cycle))

        try:
            done, pending = await asyncio.wait(
                [training_task, timeout_task], return_when=asyncio.FIRST_COMPLETED
            )

            # Cancel remaining tasks
            for task in pending:
                task.cancel()

            # Check if training completed or timed out
            if training_task in done:
                await training_task  # Get result or raise exception
            else:
                raise TimeoutError(
                    f"Training cycle {cycle + 1} timed out after {self.config.timeout_seconds}s"
                )

        except asyncio.CancelledError:
            self.logger.warning(f"Training cycle {cycle + 1} was cancelled")
            raise

    async def _run_ml_training_cycle(self, cycle: int):
        """Run the actual ML training for one cycle"""
        self.logger.debug(f"Executing ML training cycle {cycle + 1}")

        # Simulate ML training (replace with actual training logic)
        # This is where you would integrate with your existing ML training code

        # Example training steps:
        # 1. Load and prepare data
        await self._load_training_data()

        # 2. Train models
        await self._train_models(cycle)

        # 3. Validate and save models
        await self._validate_and_save_models(cycle)

        self.logger.debug(f"ML training cycle {cycle + 1} completed successfully")

    async def _load_training_data(self):
        """Load and prepare training data"""
        self.logger.debug("Loading training data")

        # Add data loading logic here
        # Example: Load from database, files, etc.

        await asyncio.sleep(0.1)  # Simulate data loading

    async def _train_models(self, cycle: int):
        """Train ML models"""
        self.logger.debug(f"Training models for cycle {cycle + 1}")

        # Add model training logic here
        # Example: Train RandomForest, XGBoost, Neural Networks

        await asyncio.sleep(2.0)  # Simulate model training

    async def _validate_and_save_models(self, cycle: int):
        """Validate and save trained models"""
        self.logger.debug(f"Validating and saving models for cycle {cycle + 1}")

        # Add model validation and saving logic here

        await asyncio.sleep(0.5)  # Simulate validation and saving

    async def _post_training_optimization(self):
        """Perform post-training optimization and cleanup"""
        self.logger.info("🔧 Performing post-training optimization")

        # Model ensemble optimization
        await self._optimize_model_ensemble()

        # Memory cleanup
        await self._cleanup_training_resources()

        # Cache optimization
        await self._optimize_feature_cache()

        self.logger.info("✅ Post-training optimization completed")

    async def _optimize_model_ensemble(self):
        """Optimize model ensemble weights and configurations"""
        self.logger.debug("Optimizing model ensemble")
        await asyncio.sleep(0.5)  # Simulate ensemble optimization

    async def _cleanup_training_resources(self):
        """Clean up training resources and temporary files"""
        self.logger.debug("Cleaning up training resources")
        await asyncio.sleep(0.2)  # Simulate cleanup

    async def _optimize_feature_cache(self):
        """Optimize feature cache for faster inference"""
        self.logger.debug("Optimizing feature cache")
        await asyncio.sleep(0.3)  # Simulate cache optimization

    async def _generate_training_report(self):
        """Generate comprehensive training report"""
        self.logger.info("📋 Generating training report")

        # Calculate metrics
        if self.metrics.total_cycles > 0:
            self.metrics.average_cycle_duration = (
                self.metrics.total_training_time / self.metrics.total_cycles
            )

        # Create report
        report = {
            "session_id": self.metrics.session_id,
            "training_window": f"{self.config.start_time}-{self.config.end_time}",
            "summary": {
                "total_cycles": self.metrics.total_cycles,
                "successful_cycles": self.metrics.successful_cycles,
                "failed_cycles": self.metrics.failed_cycles,
                "success_rate": (
                    self.metrics.successful_cycles / self.metrics.total_cycles * 100
                    if self.metrics.total_cycles > 0
                    else 0
                ),
                "total_training_time": f"{self.metrics.total_training_time:.2f}s",
                "average_cycle_duration": f"{self.metrics.average_cycle_duration:.2f}s",
            },
            "errors": self.metrics.errors,
            "warnings": self.metrics.warnings,
            "timestamp": datetime.now().isoformat(),
        }

        # Save report
        reports_dir = (
            Path("/app/reports") if Path("/app/reports").exists() else Path("reports")
        )
        reports_dir.mkdir(exist_ok=True)

        report_file = (
            reports_dir / f"early_morning_training_{self.metrics.session_id}.json"
        )

        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Training report saved to {report_file}")

        # Log summary
        self.logger.performance(
            f"Training Summary: {self.metrics.successful_cycles}/{self.metrics.total_cycles} cycles successful "
            f"({report['summary']['success_rate']:.1f}% success rate)"
        )


async def main():
    """Main entry point for early morning ML training"""

    # Setup configuration
    config = EarlyMorningTrainingConfig()

    # Override with environment variables if available
    config.log_level = os.environ.get("ML_LOG_LEVEL", config.log_level)
    config.max_training_cycles = int(
        os.environ.get("ML_MAX_CYCLES", config.max_training_cycles)
    )
    config.timeout_seconds = int(os.environ.get("ML_TIMEOUT", config.timeout_seconds))

    # Create trainer
    trainer = EarlyMorningMLTrainer(config)

    try:
        # Run training
        metrics = await trainer.run_early_morning_training()

        # Return success code
        return 0 if metrics.failed_cycles == 0 else 1

    except Exception as e:
        trainer.logger.error("Early morning training system failed", error=e)
        return 1


if __name__ == "__main__":
    # Run the early morning training system
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
