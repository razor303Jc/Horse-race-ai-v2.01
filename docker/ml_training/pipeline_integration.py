#!/usr/bin/env python3
"""
Pipeline Integration for Early Morning ML Training
Horse Racing AI v2.02 - Docker Integration

Integrates the early morning ML training system with the existing
pipeline management and auto-downloader systems.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timedelta, time
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add parent directories to path
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.append(str(Path(__file__).parent.parent / "pipeline_management"))

from early_morning_ml_trainer import EarlyMorningMLTrainer, EarlyMorningTrainingConfig
from dynamic_pipeline_timing import PipelineTimeAllocator


class EarlyMorningPipelineIntegration:
    """
    Integration layer between pipeline management and early morning ML training
    """
    
    def __init__(self):
        self.logger = self._setup_logging()
        self.pipeline_allocator = PipelineTimeAllocator()
        self.ml_trainer = None
        
        self.logger.info("Early Morning Pipeline Integration initialized")
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for pipeline integration"""
        logger = logging.getLogger("early_morning_pipeline")
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            # Console handler
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        
        return logger
    
    async def execute_early_morning_ml_phase(
        self, 
        download_completion_time: str = "00:30",
        first_race_time: str = "13:45"
    ) -> Dict:
        """
        Execute the early morning ML training phase within the pipeline
        
        Args:
            download_completion_time: When auto-download completed (HH:MM)
            first_race_time: When first race starts (HH:MM)
            
        Returns:
            Dict: Training results and pipeline status
        """
        self.logger.info(
            f"🌅 Starting early morning ML phase "
            f"(Download: {download_completion_time}, Race: {first_race_time})"
        )
        
        try:
            # Phase 1: Pipeline timing calculation
            pipeline_schedule = await self._calculate_pipeline_timing(
                download_completion_time, first_race_time
            )
            
            # Phase 2: ML training configuration
            ml_config = await self._configure_ml_training(pipeline_schedule)
            
            # Phase 3: Execute ML training
            training_results = await self._execute_ml_training(ml_config)
            
            # Phase 4: Update pipeline status
            pipeline_status = await self._update_pipeline_status(training_results)
            
            self.logger.info("✅ Early morning ML phase completed successfully")
            
            return {
                'success': True,
                'pipeline_schedule': pipeline_schedule,
                'ml_config': ml_config,
                'training_results': training_results,
                'pipeline_status': pipeline_status,
                'completion_time': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"❌ Early morning ML phase failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _calculate_pipeline_timing(
        self, 
        download_time: str, 
        first_race_time: str
    ) -> Dict:
        """Calculate optimal pipeline timing for ML training"""
        
        self.logger.info("📊 Calculating pipeline timing for ML training")
        
        try:
            # Get pipeline allocation
            schedule = self.pipeline_allocator.allocate_stage_times(
                download_time=download_time,
                first_race_time=first_race_time
            )
            
            # Extract ML training window
            stage_schedule = schedule.get('stage_schedule', {})
            ml_stage = stage_schedule.get('ml_model_training', {})
            
            # Calculate timing details
            timing_info = {
                'download_completion': download_time,
                'ml_training_start': ml_stage.get('start_time', '00:30'),
                'ml_training_end': ml_stage.get('end_time', '04:00'),
                'ml_duration_minutes': ml_stage.get('duration_minutes', 210),
                'buffer_to_race_minutes': self._calculate_buffer_time(
                    ml_stage.get('end_time', '04:00'), 
                    first_race_time
                ),
                'first_race_time': first_race_time,
                'schedule_type': schedule.get('timing_analysis', {}).get('schedule_type', 'normal')
            }
            
            self.logger.info(
                f"Pipeline timing calculated: ML {timing_info['ml_training_start']}-"
                f"{timing_info['ml_training_end']} ({timing_info['ml_duration_minutes']} min)"
            )
            
            return timing_info
            
        except Exception as e:
            self.logger.error(f"Failed to calculate pipeline timing: {e}")
            # Fallback timing
            return {
                'download_completion': download_time,
                'ml_training_start': '00:30',
                'ml_training_end': '04:00',
                'ml_duration_minutes': 210,
                'buffer_to_race_minutes': 585,  # 9.75 hours
                'first_race_time': first_race_time,
                'schedule_type': 'fallback'
            }
    
    def _calculate_buffer_time(self, ml_end_time: str, race_start_time: str) -> int:
        """Calculate buffer time between ML completion and race start"""
        try:
            ml_end = datetime.strptime(ml_end_time, "%H:%M").time()
            race_start = datetime.strptime(race_start_time, "%H:%M").time()
            
            # Calculate difference
            ml_end_dt = datetime.combine(datetime.today(), ml_end)
            race_start_dt = datetime.combine(datetime.today(), race_start)
            
            # Handle next day if race is before ML end time
            if race_start < ml_end:
                race_start_dt += timedelta(days=1)
            
            buffer_minutes = int((race_start_dt - ml_end_dt).total_seconds() / 60)
            return buffer_minutes
            
        except Exception:
            return 585  # Default 9.75 hours
    
    async def _configure_ml_training(self, pipeline_timing: Dict) -> EarlyMorningTrainingConfig:
        """Configure ML training based on pipeline timing"""
        
        self.logger.info("⚙️ Configuring ML training parameters")
        
        # Create configuration
        config = EarlyMorningTrainingConfig()
        
        # Update timing from pipeline
        config.start_time = pipeline_timing['ml_training_start']
        config.end_time = pipeline_timing['ml_training_end']
        config.total_minutes = pipeline_timing['ml_duration_minutes']
        
        # Calculate training cycles based on available time
        available_minutes = pipeline_timing['ml_duration_minutes']
        cycle_duration = config.cycle_duration_minutes + config.buffer_minutes
        max_cycles = max(1, (available_minutes - 30) // cycle_duration)  # Reserve 30 min buffer
        
        config.max_training_cycles = min(max_cycles, 8)  # Cap at 8 cycles
        
        # Adjust for Docker environment
        config.data_path = os.environ.get('DATA_PATH', '/app/data')
        config.models_path = os.environ.get('MODELS_PATH', '/app/models')
        config.logs_path = os.environ.get('LOGS_PATH', '/app/logs')
        config.cache_path = os.environ.get('CACHE_PATH', '/app/cache')
        
        # Environment-based overrides
        config.log_level = os.environ.get('ML_LOG_LEVEL', 'INFO')
        config.max_retries = int(os.environ.get('ML_MAX_RETRIES', '3'))
        config.timeout_seconds = int(os.environ.get('ML_CYCLE_TIMEOUT', '1800'))
        
        self.logger.info(
            f"ML training configured: {config.max_training_cycles} cycles, "
            f"{config.total_minutes} min window"
        )
        
        return config
    
    async def _execute_ml_training(self, config: EarlyMorningTrainingConfig) -> Dict:
        """Execute the ML training with the configured parameters"""
        
        self.logger.info(f"🤖 Starting ML training execution")
        
        try:
            # Create ML trainer
            self.ml_trainer = EarlyMorningMLTrainer(config)
            
            # Execute training
            metrics = await self.ml_trainer.run_early_morning_training()
            
            # Convert metrics to dictionary for JSON serialization
            results = {
                'session_id': metrics.session_id,
                'start_time': metrics.start_time.isoformat(),
                'end_time': metrics.end_time.isoformat() if metrics.end_time else None,
                'total_cycles': metrics.total_cycles,
                'successful_cycles': metrics.successful_cycles,
                'failed_cycles': metrics.failed_cycles,
                'average_cycle_duration': metrics.average_cycle_duration,
                'total_training_time': metrics.total_training_time,
                'pipeline_phase': metrics.pipeline_phase,
                'data_download_complete': metrics.data_download_complete,
                'validation_passed': metrics.validation_passed,
                'errors_count': len(metrics.errors),
                'warnings_count': len(metrics.warnings)
            }
            
            self.logger.info(
                f"ML training completed: {results['successful_cycles']}/{results['total_cycles']} "
                f"cycles successful in {results['total_training_time']:.2f}s"
            )
            
            return results
            
        except Exception as e:
            self.logger.error(f"ML training execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _update_pipeline_status(self, training_results: Dict) -> Dict:
        """Update pipeline status after ML training completion"""
        
        self.logger.info("📋 Updating pipeline status")
        
        # Determine ML training success
        ml_success = (
            training_results.get('successful_cycles', 0) > 0 and
            training_results.get('failed_cycles', 0) == 0
        )
        
        # Create status update
        status = {
            'early_morning_ml_complete': True,
            'ml_training_success': ml_success,
            'ml_session_id': training_results.get('session_id'),
            'ml_completion_time': datetime.now().isoformat(),
            'ready_for_next_phase': ml_success,
            'models_updated': ml_success,
            'next_phase': 'data_processing' if ml_success else 'error_recovery'
        }
        
        # Save status to file for other pipeline components
        status_file = Path("/app/data/pipeline_status.json")
        status_file.parent.mkdir(exist_ok=True)
        
        with open(status_file, 'w') as f:
            json.dump(status, f, indent=2)
        
        self.logger.info(f"Pipeline status updated: ML training {'successful' if ml_success else 'failed'}")
        
        return status
    
    def check_training_window(self) -> Tuple[bool, str]:
        """
        Check if we're currently in the early morning training window
        
        Returns:
            Tuple[bool, str]: (is_in_window, status_message)
        """
        current_time = datetime.now().time()
        start_time = time(0, 30)  # 00:30
        end_time = time(4, 0)     # 04:00
        
        if start_time <= current_time <= end_time:
            return True, f"In training window (current: {current_time.strftime('%H:%M')})"
        else:
            return False, f"Outside training window (current: {current_time.strftime('%H:%M')})"
    
    async def get_training_status(self) -> Dict:
        """Get current training status and metrics"""
        
        # Check if we're in training window
        in_window, window_status = self.check_training_window()
        
        # Load pipeline status if available
        status_file = Path("/app/data/pipeline_status.json")
        pipeline_status = {}
        
        if status_file.exists():
            try:
                with open(status_file, 'r') as f:
                    pipeline_status = json.load(f)
            except Exception as e:
                self.logger.warning(f"Failed to load pipeline status: {e}")
        
        return {
            'in_training_window': in_window,
            'window_status': window_status,
            'pipeline_status': pipeline_status,
            'trainer_active': self.ml_trainer is not None,
            'timestamp': datetime.now().isoformat()
        }


# Entry point for Docker container execution
async def main():
    """Main entry point for pipeline integration"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create integration system
    integration = EarlyMorningPipelineIntegration()
    
    # Check if we should run training now
    in_window, status = integration.check_training_window()
    
    if in_window:
        # Execute early morning ML phase
        result = await integration.execute_early_morning_ml_phase()
        
        if result['success']:
            print("✅ Early morning ML training completed successfully")
            return 0
        else:
            print(f"❌ Early morning ML training failed: {result.get('error')}")
            return 1
    else:
        print(f"ℹ️ Not in training window: {status}")
        
        # Show current status
        current_status = await integration.get_training_status()
        print(f"Current status: {json.dumps(current_status, indent=2)}")
        
        return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
