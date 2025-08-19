#!/usr/bin/env python3
"""
Data Architecture Pipeline Integration - V2.03
===============================================

Pipeline integration for data architecture improvements system.
Integrates comprehensive data architecture enhancements into the V2.03 pipeline.

This module:
- Runs data architecture improvements as Stage 8
- Manages data versioning, backup, encryption, and retention
- Provides quality monitoring and system health checks
- Integrates with existing pipeline orchestration
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Add the parent directory to the path to import data_architecture_manager
sys.path.append(str(Path(__file__).parent.parent))

from data_architecture.data_architecture_manager import DataArchitectureManager

logger = logging.getLogger(__name__)


class DataArchitecturePipelineIntegration:
    """
    Pipeline integration for data architecture improvements.
    
    Provides seamless integration of data architecture enhancements
    into the V2.03 pipeline system with proper stage management.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize the pipeline integration."""
        self.config_path = config_path or "config/data_architecture_config.json"
        self.stage_name = "data_architecture_improvements"
        self.stage_number = 8
        
        # Initialize data architecture manager
        self.data_manager = DataArchitectureManager(config_path=self.config_path)
        
        self.logger = logging.getLogger(__name__)
        self.logger.info("Data Architecture Pipeline Integration initialized")
    
    async def run_data_architecture_stage(
        self, 
        input_data: Optional[Dict] = None,
        stage_config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run data architecture improvements as pipeline stage.
        
        Args:
            input_data: Previous stage results (optional for this stage)
            stage_config: Stage-specific configuration
            
        Returns:
            Stage execution results
        """
        start_time = datetime.now()
        
        try:
            self.logger.info(f"Starting Stage {self.stage_number}: {self.stage_name}")
            
            stage_results = {
                'stage': self.stage_number,
                'stage_name': self.stage_name,
                'timestamp': start_time.isoformat(),
                'status': 'running',
                'data_architecture_results': {},
                'performance_metrics': {},
                'stage_summary': {},
                'next_stage_data': {}
            }
            
            # Apply stage configuration if provided
            if stage_config:
                await self._apply_stage_config(stage_config)
            
            # Validate input data and system state
            validation_results = await self._validate_stage_inputs(input_data)
            stage_results['input_validation'] = validation_results
            
            if not validation_results.get('valid', True):
                stage_results['status'] = 'failed'
                stage_results['error'] = 'Input validation failed'
                return stage_results
            
            # Run comprehensive data architecture improvements
            self.logger.info("Running comprehensive data architecture improvements")
            
            architecture_results = await self.data_manager.run_data_architecture_improvements()
            stage_results['data_architecture_results'] = architecture_results
            
            # Process and enrich results
            processed_results = await self._process_architecture_results(architecture_results)
            stage_results.update(processed_results)
            
            # Generate performance metrics
            performance_metrics = await self._calculate_stage_performance(
                start_time, architecture_results
            )
            stage_results['performance_metrics'] = performance_metrics
            
            # Create stage summary
            stage_summary = await self._create_stage_summary(
                architecture_results, performance_metrics
            )
            stage_results['stage_summary'] = stage_summary
            
            # Prepare data for next stage (if any)
            next_stage_data = await self._prepare_next_stage_data(architecture_results)
            stage_results['next_stage_data'] = next_stage_data
            
            # Save stage results
            await self._save_stage_results(stage_results)
            
            stage_results['status'] = 'completed'
            
            processing_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(
                f"Stage {self.stage_number} completed successfully in {processing_time:.2f}s"
            )
            
            return stage_results
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_msg = f"Error in Stage {self.stage_number}: {e}"
            self.logger.error(error_msg)
            
            return {
                'stage': self.stage_number,
                'stage_name': self.stage_name,
                'timestamp': start_time.isoformat(),
                'status': 'failed',
                'error': str(e),
                'processing_time_seconds': processing_time
            }
    
    async def _apply_stage_config(self, stage_config: Dict) -> None:
        """Apply stage-specific configuration."""
        try:
            # Override data architecture settings if provided
            if 'data_architecture' in stage_config:
                da_config = stage_config['data_architecture']
                
                # Update manager configuration
                self.data_manager.config.update(da_config)
                
                # Apply specific settings
                if 'backup_enabled' in da_config:
                    self.data_manager.config['backup']['enabled'] = da_config['backup_enabled']
                
                if 'encryption_enabled' in da_config:
                    self.data_manager.encryption_enabled = da_config['encryption_enabled']
                
                if 'versioning_enabled' in da_config:
                    self.data_manager.versioning_enabled = da_config['versioning_enabled']
                
                if 'monitoring_enabled' in da_config:
                    self.data_manager.monitoring_enabled = da_config['monitoring_enabled']
            
            self.logger.info("Applied stage configuration")
            
        except Exception as e:
            self.logger.warning(f"Error applying stage config: {e}")
    
    async def _validate_stage_inputs(self, input_data: Optional[Dict]) -> Dict[str, Any]:
        """Validate stage inputs and system state."""
        try:
            validation_results = {
                'valid': True,
                'warnings': [],
                'system_checks': {},
                'input_data_status': 'not_required'
            }
            
            # Check if data directories exist
            required_dirs = [
                self.data_manager.data_root,
                self.data_manager.backup_root,
                self.data_manager.versioning_root,
                self.data_manager.monitoring_root
            ]
            
            for dir_path in required_dirs:
                if not dir_path.exists():
                    try:
                        dir_path.mkdir(parents=True, exist_ok=True)
                        validation_results['warnings'].append(
                            f"Created missing directory: {dir_path}"
                        )
                    except Exception as e:
                        validation_results['valid'] = False
                        validation_results['warnings'].append(
                            f"Cannot create directory {dir_path}: {e}"
                        )
            
            # Check disk space
            if self.data_manager.data_root.exists():
                total, used, free = os.statvfs(str(self.data_manager.data_root))
                free_gb = (free * total) / (1024**3)
                
                validation_results['system_checks']['free_disk_gb'] = round(free_gb, 2)
                
                if free_gb < 1.0:  # Less than 1GB free
                    validation_results['warnings'].append("Low disk space available")
            
            # Check if previous stages completed (optional)
            if input_data:
                validation_results['input_data_status'] = 'received'
                if input_data.get('status') != 'completed':
                    validation_results['warnings'].append(
                        "Previous stage may not have completed successfully"
                    )
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"Error validating stage inputs: {e}")
            return {
                'valid': False,
                'error': str(e)
            }
    
    async def _process_architecture_results(self, results: Dict) -> Dict[str, Any]:
        """Process and enrich data architecture results."""
        try:
            processed = {
                'operations_summary': {},
                'quality_assessment': {},
                'system_improvements': {},
                'alerts_and_recommendations': {}
            }
            
            # Summarize operations
            operations_completed = results.get('operations_completed', [])
            operations_failed = results.get('operations_failed', [])
            
            processed['operations_summary'] = {
                'total_operations': len(operations_completed) + len(operations_failed),
                'successful_operations': len(operations_completed),
                'failed_operations': len(operations_failed),
                'success_rate': len(operations_completed) / (len(operations_completed) + len(operations_failed)) if (operations_completed or operations_failed) else 1.0,
                'completed_operations': operations_completed,
                'failed_operations': operations_failed
            }
            
            # Extract quality assessment
            quality_data = results.get('quality_assessment', {})
            if quality_data:
                quality_scores = quality_data.get('quality_scores', {})
                processed['quality_assessment'] = {
                    'overall_health_score': quality_scores.get('overall_health', 0.0),
                    'database_health_score': quality_scores.get('database_health', 0.0),
                    'filesystem_health_score': quality_scores.get('filesystem_health', 0.0),
                    'alerts_generated': len(quality_data.get('alerts_generated', [])),
                    'recommendations_count': len(quality_data.get('recommendations', []))
                }
            
            # Extract system improvements
            improvements = {
                'backups_created': 0,
                'files_versioned': 0,
                'files_encrypted': 0,
                'space_freed_mb': 0,
                'old_files_cleaned': 0
            }
            
            # Backup results
            backup_results = results.get('backup_results', {})
            if backup_results.get('backup_success'):
                improvements['backups_created'] = 1
            
            # Versioning results
            versioning_results = results.get('versioning_results', {})
            improvements['files_versioned'] = versioning_results.get('files_versioned', 0)
            
            # Encryption results
            encryption_results = results.get('encryption_results', {})
            improvements['files_encrypted'] = encryption_results.get('files_encrypted', 0)
            
            # Cleanup results
            cleanup_results = results.get('cleanup_results', {})
            improvements['space_freed_mb'] = cleanup_results.get('space_freed_mb', 0)
            improvements['old_files_cleaned'] = cleanup_results.get('files_deleted', 0)
            
            processed['system_improvements'] = improvements
            
            # Aggregate alerts and recommendations
            all_alerts = []
            all_recommendations = []
            
            # From quality assessment
            quality_alerts = quality_data.get('alerts_generated', [])
            quality_recommendations = quality_data.get('recommendations', [])
            
            all_alerts.extend(quality_alerts)
            all_recommendations.extend(quality_recommendations)
            
            # From monitoring results
            monitoring_results = results.get('monitoring_results', {})
            if monitoring_results:
                monitoring_recommendations = monitoring_results.get('recommendations', [])
                all_recommendations.extend(monitoring_recommendations)
            
            processed['alerts_and_recommendations'] = {
                'total_alerts': len(all_alerts),
                'total_recommendations': len(all_recommendations),
                'high_priority_alerts': len([a for a in all_alerts if a.get('severity') == 'high']),
                'alerts': all_alerts[:5],  # Limit to first 5
                'recommendations': all_recommendations[:5]  # Limit to first 5
            }
            
            return processed
            
        except Exception as e:
            self.logger.error(f"Error processing architecture results: {e}")
            return {'error': str(e)}
    
    async def _calculate_stage_performance(
        self, 
        start_time: datetime, 
        results: Dict
    ) -> Dict[str, Any]:
        """Calculate stage performance metrics."""
        try:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            performance = {
                'processing_time_seconds': round(processing_time, 2),
                'processing_time_minutes': round(processing_time / 60, 2),
                'start_time': start_time.isoformat(),
                'end_time': end_time.isoformat(),
                'throughput_metrics': {},
                'efficiency_metrics': {}
            }
            
            # Calculate throughput metrics
            operations_completed = len(results.get('operations_completed', []))
            if operations_completed > 0:
                performance['throughput_metrics'] = {
                    'operations_per_second': round(operations_completed / processing_time, 2),
                    'operations_completed': operations_completed,
                    'avg_time_per_operation': round(processing_time / operations_completed, 2)
                }
            
            # Calculate efficiency metrics
            backup_size = results.get('backup_results', {}).get('backup_size_mb', 0)
            files_processed = (
                results.get('versioning_results', {}).get('files_versioned', 0) +
                results.get('encryption_results', {}).get('files_encrypted', 0) +
                results.get('cleanup_results', {}).get('files_processed', 0)
            )
            
            if files_processed > 0:
                performance['efficiency_metrics'] = {
                    'files_per_second': round(files_processed / processing_time, 2),
                    'total_files_processed': files_processed
                }
            
            if backup_size > 0:
                performance['efficiency_metrics']['backup_mb_per_second'] = round(
                    backup_size / processing_time, 2
                )
            
            return performance
            
        except Exception as e:
            self.logger.error(f"Error calculating stage performance: {e}")
            return {'error': str(e)}
    
    async def _create_stage_summary(
        self, 
        results: Dict, 
        performance: Dict
    ) -> Dict[str, Any]:
        """Create comprehensive stage summary."""
        try:
            summary = {
                'stage_status': 'completed' if not results.get('error') else 'failed',
                'operations_completed': len(results.get('operations_completed', [])),
                'operations_failed': len(results.get('operations_failed', [])),
                'processing_time': performance.get('processing_time_seconds', 0),
                'key_achievements': [],
                'issues_detected': [],
                'recommendations': [],
                'next_steps': []
            }
            
            # Identify key achievements
            achievements = []
            
            # Backup achievements
            backup_results = results.get('backup_results', {})
            if backup_results.get('backup_success'):
                backup_size = backup_results.get('backup_size_mb', 0)
                achievements.append(f"Created backup ({backup_size:.1f} MB)")
            
            # Versioning achievements
            versioning_results = results.get('versioning_results', {})
            files_versioned = versioning_results.get('files_versioned', 0)
            if files_versioned > 0:
                achievements.append(f"Versioned {files_versioned} files")
            
            # Encryption achievements
            encryption_results = results.get('encryption_results', {})
            files_encrypted = encryption_results.get('files_encrypted', 0)
            if files_encrypted > 0:
                achievements.append(f"Encrypted {files_encrypted} sensitive files")
            
            # Cleanup achievements
            cleanup_results = results.get('cleanup_results', {})
            space_freed = cleanup_results.get('space_freed_mb', 0)
            if space_freed > 0:
                achievements.append(f"Freed {space_freed:.1f} MB of disk space")
            
            summary['key_achievements'] = achievements
            
            # Identify issues
            issues = []
            
            # From operations that failed
            failed_ops = results.get('operations_failed', [])
            for op in failed_ops:
                issues.append(f"Failed operation: {op}")
            
            # From quality assessment alerts
            quality_data = results.get('quality_assessment', {})
            alerts = quality_data.get('alerts_generated', [])
            high_priority_alerts = [a for a in alerts if a.get('severity') == 'high']
            
            for alert in high_priority_alerts[:3]:  # Top 3 high priority
                issues.append(f"High priority: {alert.get('message', 'Unknown issue')}")
            
            summary['issues_detected'] = issues
            
            # Extract recommendations
            all_recommendations = []
            
            # From quality assessment
            quality_recommendations = quality_data.get('recommendations', [])
            all_recommendations.extend(quality_recommendations)
            
            # From monitoring
            monitoring_results = results.get('monitoring_results', {})
            monitoring_recommendations = monitoring_results.get('recommendations', [])
            all_recommendations.extend(monitoring_recommendations)
            
            summary['recommendations'] = all_recommendations[:5]  # Top 5
            
            # Suggest next steps
            next_steps = []
            
            if issues:
                next_steps.append("Address detected issues and alerts")
            
            if files_encrypted == 0 and results.get('encryption_results', {}).get('sensitive_data_found', 0) > 0:
                next_steps.append("Review sensitive data encryption requirements")
            
            if not backup_results.get('backup_success'):
                next_steps.append("Ensure backup system is properly configured")
            
            if not next_steps:
                next_steps.append("Monitor system health and maintain current data architecture")
            
            summary['next_steps'] = next_steps
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Error creating stage summary: {e}")
            return {'error': str(e)}
    
    async def _prepare_next_stage_data(self, results: Dict) -> Dict[str, Any]:
        """Prepare data for potential next stage."""
        try:
            # Data architecture is typically the final stage, but prepare summary data
            next_stage_data = {
                'data_architecture_summary': {
                    'backup_status': results.get('backup_results', {}).get('backup_success', False),
                    'versioning_active': results.get('versioning_results', {}).get('files_versioned', 0) > 0,
                    'encryption_active': results.get('encryption_results', {}).get('files_encrypted', 0) > 0,
                    'monitoring_healthy': results.get('quality_assessment', {}).get('quality_scores', {}).get('overall_health', 0) > 0.8,
                    'cleanup_completed': results.get('cleanup_results', {}).get('files_deleted', 0) > 0
                },
                'system_status': {
                    'data_architecture_healthy': not bool(results.get('error')),
                    'operations_successful': len(results.get('operations_completed', [])),
                    'alerts_count': len(results.get('quality_assessment', {}).get('alerts_generated', [])),
                    'last_backup_time': datetime.now().isoformat() if results.get('backup_results', {}).get('backup_success') else None
                },
                'pipeline_metadata': {
                    'stage_completed': 8,
                    'stage_name': 'data_architecture_improvements',
                    'completion_time': datetime.now().isoformat(),
                    'ready_for_next_stage': True  # Always ready since this is typically final
                }
            }
            
            return next_stage_data
            
        except Exception as e:
            self.logger.error(f"Error preparing next stage data: {e}")
            return {'error': str(e)}
    
    async def _save_stage_results(self, results: Dict) -> None:
        """Save stage results to file."""
        try:
            # Create results directory
            results_dir = Path('logs') / 'data_architecture'
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Save with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = results_dir / f'stage8_data_architecture_{timestamp}.json'
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            # Also save as latest
            latest_file = results_dir / 'latest_stage8_results.json'
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            self.logger.info(f"Saved stage results to {results_file}")
            
        except Exception as e:
            self.logger.error(f"Error saving stage results: {e}")


# Async main function for standalone execution
async def main():
    """Main function for standalone execution."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Data Architecture Pipeline Stage')
    parser.add_argument('--config', help='Path to configuration file')
    parser.add_argument('--input-file', help='Input data file from previous stage')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Load input data if provided
    input_data = None
    if args.input_file and os.path.exists(args.input_file):
        try:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
        except Exception as e:
            logger.error(f"Error loading input file: {e}")
    
    # Initialize pipeline integration
    integration = DataArchitecturePipelineIntegration(config_path=args.config)
    
    try:
        # Run data architecture stage
        results = await integration.run_data_architecture_stage(input_data=input_data)
        
        print(json.dumps(results, indent=2, default=str))
        
        # Return appropriate exit code
        if results.get('status') == 'completed':
            sys.exit(0)
        else:
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Error in data architecture pipeline stage: {e}")
        print(json.dumps({'error': str(e)}, indent=2))
        sys.exit(1)


if __name__ == '__main__':
    asyncio.run(main())
