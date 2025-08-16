#!/usr/bin/env python3
"""
Enhanced Pipeline ML Integration Manager
Horse Racing AI v2.02 - Docker Integration

Integrates early morning ML training with the pipeline system,
providing comprehensive error handling, logging, and monitoring.
"""

import asyncio
import json
import logging
import os
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

# Docker-specific imports
sys.path.append('/app/docker/pipeline_management')
sys.path.append('/app/docker/ml_training')

from dynamic_pipeline_timing import PipelineTimeAllocator
from enhanced_ml_cycle_manager import EnhancedMLCycleManager, DockerLoggingSetup

# Initialize logging for pipeline integration
logger = DockerLoggingSetup.setup_logging("pipeline_ml_integration")
perf_logger = logging.getLogger("pipeline_ml_integration_performance")


class PipelineMLIntegrationManager:
    """
    Enhanced Pipeline ML Integration with comprehensive error handling
    and early morning training optimization.
    """
    
    def __init__(self):
        self.pipeline_allocator = None
        self.ml_manager = None
        self.integration_config = self._load_integration_config()
        self.health_status = {
            'pipeline': False,
            'ml_training': False,
            'database': False,
            'last_check': None
        }
        
        # Early morning training configuration
        self.early_morning_config = {
            'download_start': "00:01",
            'training_start': "00:30", 
            'training_end': "04:00",
            'data_processing_end': "13:30",
            'first_race_buffer_minutes': 15
        }
        
        logger.info("Pipeline ML Integration Manager initialized")
        
    def _load_integration_config(self) -> Dict[str, Any]:
        """Load integration configuration from Docker environment"""
        return {
            'training_mode': os.getenv('ML_TRAINING_MODE', 'auto'),
            'training_cycles': int(os.getenv('TRAINING_CYCLES', 10)),
            'training_sessions': int(os.getenv('TRAINING_SESSIONS', 1000)),
            'max_training_time_minutes': int(os.getenv('MAX_TRAINING_TIME_MINUTES', 210)),
            'enable_early_morning': os.getenv('ENABLE_EARLY_MORNING', 'true').lower() == 'true',
            'health_check_interval': int(os.getenv('HEALTH_CHECK_INTERVAL', 300)),  # 5 minutes
            'performance_monitoring': os.getenv('PERFORMANCE_MONITORING', 'true').lower() == 'true',
            'auto_recovery': os.getenv('AUTO_RECOVERY', 'true').lower() == 'true'
        }
    
    async def initialize_components(self) -> bool:
        """Initialize pipeline and ML training components with error handling"""
        try:
            logger.info("🚀 Initializing Pipeline ML Integration components...")
            
            # Initialize pipeline allocator
            try:
                self.pipeline_allocator = PipelineTimeAllocator()
                logger.info("✅ Pipeline allocator initialized")
                self.health_status['pipeline'] = True
            except Exception as e:
                logger.error(f"❌ Failed to initialize pipeline allocator: {e}")
                self.health_status['pipeline'] = False
            
            # Initialize ML manager
            try:
                self.ml_manager = EnhancedMLCycleManager(self.integration_config)
                logger.info("✅ ML training manager initialized")
                self.health_status['ml_training'] = True
            except Exception as e:
                logger.error(f"❌ Failed to initialize ML manager: {e}")
                self.health_status['ml_training'] = False
            
            # Test database connectivity
            try:
                if self.ml_manager:
                    async with self.ml_manager.db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT 1")
                    logger.info("✅ Database connectivity verified")
                    self.health_status['database'] = True
            except Exception as e:
                logger.error(f"❌ Database connectivity failed: {e}")
                self.health_status['database'] = False
            
            self.health_status['last_check'] = datetime.now()
            
            # Check overall health
            all_healthy = all(self.health_status[key] for key in ['pipeline', 'ml_training', 'database'])
            
            if all_healthy:
                logger.info("🎉 All components initialized successfully")
                return True
            else:
                failed_components = [k for k, v in self.health_status.items() if not v and k != 'last_check']
                logger.warning(f"⚠️ Some components failed to initialize: {failed_components}")
                return False
                
        except Exception as e:
            logger.error(f"💥 Critical error during component initialization: {e}")
            logger.error(traceback.format_exc())
            return False
    
    async def get_current_pipeline_schedule(self, first_race_time: Optional[str] = None) -> Dict[str, Any]:
        """Get current pipeline schedule with enhanced error handling"""
        try:
            if not self.pipeline_allocator:
                raise RuntimeError("Pipeline allocator not initialized")
            
            # Use early morning configuration
            schedule = self.pipeline_allocator.allocate_stage_times(
                download_time=self.early_morning_config['download_start'],
                first_race_time=first_race_time or "13:45"
            )
            
            logger.info(f"📋 Pipeline schedule loaded: {schedule.get('timing_analysis', {}).get('schedule_type', 'unknown')} mode")
            
            # Log key timing information
            timing_analysis = schedule.get('timing_analysis', {})
            available_minutes = timing_analysis.get('available_minutes', 0)
            required_minutes = timing_analysis.get('total_required_minutes', 0)
            time_pressure = timing_analysis.get('time_pressure', 0)
            
            perf_logger.info(
                f"Pipeline Schedule - Available: {available_minutes}min, "
                f"Required: {required_minutes}min, Pressure: {time_pressure:.2f}"
            )
            
            return schedule
            
        except Exception as e:
            logger.error(f"❌ Error loading pipeline schedule: {e}")
            return self._create_fallback_schedule()
    
    def _create_fallback_schedule(self) -> Dict[str, Any]:
        """Create fallback schedule when primary allocation fails"""
        logger.warning("🔄 Creating fallback pipeline schedule")
        
        return {
            'stage_schedule': {
                'ml_model_training': {
                    'start_time': self.early_morning_config['training_start'],
                    'end_time': self.early_morning_config['training_end'],
                    'duration_minutes': 210,
                    'phase': 'early_ml_training'
                }
            },
            'timing_analysis': {
                'schedule_type': 'fallback',
                'available_minutes': 210,
                'time_pressure': 0.5,
                'early_morning_mode': True
            }
        }
    
    async def execute_early_morning_training(self) -> Dict[str, Any]:
        """Execute the complete early morning ML training pipeline"""
        execution_start = datetime.now()
        execution_results = {
            'start_time': execution_start,
            'end_time': None,
            'success': False,
            'pipeline_schedule': None,
            'training_results': None,
            'errors': [],
            'performance_metrics': {}
        }
        
        try:
            logger.info("🌅 Starting Early Morning ML Training Pipeline")
            logger.info("=" * 60)
            
            # Step 1: Get pipeline schedule
            logger.info("📋 Step 1: Loading pipeline schedule...")
            pipeline_schedule = await self.get_current_pipeline_schedule()
            execution_results['pipeline_schedule'] = pipeline_schedule
            
            # Step 2: Validate training window
            current_time = datetime.now().time()
            training_start = datetime.strptime(self.early_morning_config['training_start'], "%H:%M").time()
            training_end = datetime.strptime(self.early_morning_config['training_end'], "%H:%M").time()
            
            if training_start <= current_time <= training_end:
                logger.info(f"✅ In training window ({current_time})")
                
                # Step 3: Execute ML training
                logger.info("🤖 Step 3: Starting ML training session...")
                if self.ml_manager:
                    training_results = await self.ml_manager.run_training_session()
                    execution_results['training_results'] = training_results
                    
                    if training_results.get('success', False):
                        logger.info("🎉 ML training completed successfully")
                        execution_results['success'] = True
                    else:
                        logger.error("❌ ML training failed")
                        execution_results['errors'].append("ML training session failed")
                else:
                    raise RuntimeError("ML manager not initialized")
                    
            else:
                logger.warning(f"⏰ Outside training window (current: {current_time}, window: {training_start}-{training_end})")
                execution_results['errors'].append(f"Outside training window: {current_time}")
                
            # Step 4: Performance analysis
            execution_end = datetime.now()
            execution_results['end_time'] = execution_end
            execution_duration = (execution_end - execution_start).total_seconds() / 60
            
            execution_results['performance_metrics'] = {
                'total_duration_minutes': execution_duration,
                'pipeline_load_time': 0,  # Would track actual timing
                'training_efficiency': execution_results.get('training_results', {}).get('efficiency', 0),
                'memory_peak_mb': 0,  # Would track actual memory usage
                'cpu_utilization': 0   # Would track actual CPU usage
            }
            
            perf_logger.info(
                f"Early Morning Training Execution - Duration: {execution_duration:.1f}min, "
                f"Success: {execution_results['success']}, "
                f"Errors: {len(execution_results['errors'])}"
            )
            
            return execution_results
            
        except Exception as e:
            logger.error(f"💥 Critical error in early morning training execution: {e}")
            logger.error(traceback.format_exc())
            
            execution_results['end_time'] = datetime.now()
            execution_results['success'] = False
            execution_results['errors'].append(f"Critical error: {str(e)}")
            
            return execution_results
    
    async def health_check(self) -> Dict[str, Any]:
        """Comprehensive health check for all components"""
        try:
            logger.debug("🔍 Performing health check...")
            
            health_report = {
                'timestamp': datetime.now(),
                'overall_health': 'unknown',
                'components': {},
                'recommendations': []
            }
            
            # Check pipeline allocator
            try:
                if self.pipeline_allocator:
                    # Test basic allocation
                    test_schedule = self.pipeline_allocator.allocate_stage_times("00:01", "13:45")
                    health_report['components']['pipeline'] = {
                        'status': 'healthy',
                        'last_test': 'passed',
                        'details': f"Schedule type: {test_schedule.get('timing_analysis', {}).get('schedule_type')}"
                    }
                else:
                    health_report['components']['pipeline'] = {
                        'status': 'error',
                        'last_test': 'failed',
                        'details': 'Pipeline allocator not initialized'
                    }
            except Exception as e:
                health_report['components']['pipeline'] = {
                    'status': 'error',
                    'last_test': 'failed',
                    'details': str(e)
                }
            
            # Check ML manager
            try:
                if self.ml_manager:
                    health_report['components']['ml_training'] = {
                        'status': 'healthy',
                        'last_test': 'passed',
                        'details': f"Config loaded, {self.ml_manager.config.get('cycles_per_session')} cycles per session"
                    }
                else:
                    health_report['components']['ml_training'] = {
                        'status': 'error',
                        'last_test': 'failed',
                        'details': 'ML manager not initialized'
                    }
            except Exception as e:
                health_report['components']['ml_training'] = {
                    'status': 'error',
                    'last_test': 'failed',
                    'details': str(e)
                }
            
            # Check database connectivity
            try:
                if self.ml_manager:
                    async with self.ml_manager.db_manager.get_connection() as conn:
                        with conn.cursor() as cursor:
                            cursor.execute("SELECT NOW()")
                            result = cursor.fetchone()
                    
                    health_report['components']['database'] = {
                        'status': 'healthy',
                        'last_test': 'passed',
                        'details': f"Connected, server time: {result[0] if result else 'unknown'}"
                    }
                else:
                    health_report['components']['database'] = {
                        'status': 'warning',
                        'last_test': 'skipped',
                        'details': 'ML manager not available for DB test'
                    }
            except Exception as e:
                health_report['components']['database'] = {
                    'status': 'error',
                    'last_test': 'failed',
                    'details': str(e)
                }
            
            # Determine overall health
            component_statuses = [comp['status'] for comp in health_report['components'].values()]
            
            if all(status == 'healthy' for status in component_statuses):
                health_report['overall_health'] = 'healthy'
            elif any(status == 'error' for status in component_statuses):
                health_report['overall_health'] = 'error'
                health_report['recommendations'].append("Check error logs and restart failed components")
            else:
                health_report['overall_health'] = 'warning'
                health_report['recommendations'].append("Some components need attention")
            
            # Update health status
            self.health_status['last_check'] = datetime.now()
            
            return health_report
            
        except Exception as e:
            logger.error(f"❌ Error during health check: {e}")
            return {
                'timestamp': datetime.now(),
                'overall_health': 'error',
                'components': {},
                'error': str(e)
            }


async def main():
    """Main entry point for Pipeline ML Integration"""
    try:
        logger.info("🔧 Starting Pipeline ML Integration Manager")
        logger.info("=" * 50)
        
        # Initialize integration manager
        integration_manager = PipelineMLIntegrationManager()
        
        # Initialize all components
        initialization_success = await integration_manager.initialize_components()
        
        if not initialization_success:
            logger.error("💥 Component initialization failed - cannot proceed")
            sys.exit(1)
        
        # Perform health check
        health_report = await integration_manager.health_check()
        logger.info(f"🏥 Health Check: {health_report['overall_health']}")
        
        # Execute early morning training if in window
        current_time = datetime.now().time()
        training_start = datetime.strptime("00:30", "%H:%M").time()
        training_end = datetime.strptime("04:00", "%H:%M").time()
        
        if training_start <= current_time <= training_end:
            logger.info("🌅 Executing early morning training pipeline...")
            results = await integration_manager.execute_early_morning_training()
            
            if results['success']:
                logger.info("🎉 Early morning training pipeline completed successfully")
            else:
                logger.error(f"❌ Training pipeline failed: {results['errors']}")
                sys.exit(1)
        else:
            logger.info(f"⏰ Outside training window, current time: {current_time}")
            logger.info("Integration manager ready for scheduled training")
            
    except Exception as e:
        logger.error(f"💥 Fatal error in Pipeline ML Integration: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
