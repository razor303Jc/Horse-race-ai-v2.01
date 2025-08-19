#!/usr/bin/env python3
"""
Data Architecture Stage Runner - V2.03
=======================================

Standalone script for running the data architecture improvements stage.
Can be executed independently or as part of the pipeline system.

Usage:
    python run_data_architecture_stage.py [--config CONFIG_PATH] [--input INPUT_FILE]

Features:
- Data versioning and history tracking
- Automated backup and recovery system
- Data encryption for sensitive information
- Data quality monitoring and alerts
- Data retention policies and cleanup
- Comprehensive system health checks
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from pipeline.data_architecture_pipeline_integration import DataArchitecturePipelineIntegration

logger = logging.getLogger(__name__)


async def run_data_architecture_stage():
    """Run the data architecture improvements stage."""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('logs/data_architecture_stage.log'),
            logging.StreamHandler()
        ]
    )
    
    try:
        logger.info("=" * 80)
        logger.info("STAGE 8: DATA ARCHITECTURE IMPROVEMENTS")
        logger.info("=" * 80)
        
        # Initialize pipeline integration
        config_path = "config/data_architecture_config.json"
        integration = DataArchitecturePipelineIntegration(config_path=config_path)
        
        # Check if we have input from previous stage
        input_data = None
        input_file = "logs/contextual_ai/latest_stage7_results.json"
        
        if os.path.exists(input_file):
            try:
                with open(input_file, 'r', encoding='utf-8') as f:
                    input_data = json.load(f)
                logger.info("Loaded input data from previous stage")
            except Exception as e:
                logger.warning(f"Could not load previous stage data: {e}")
        
        # Run data architecture stage
        start_time = datetime.now()
        logger.info(f"Starting data architecture improvements at {start_time}")
        
        results = await integration.run_data_architecture_stage(input_data=input_data)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        # Log results summary
        logger.info("=" * 80)
        logger.info("DATA ARCHITECTURE STAGE RESULTS")
        logger.info("=" * 80)
        
        status = results.get('status', 'unknown')
        logger.info(f"Stage Status: {status}")
        logger.info(f"Processing Time: {processing_time:.2f} seconds")
        
        # Operations summary
        operations_summary = results.get('operations_summary', {})
        if operations_summary:
            successful_ops = operations_summary.get('successful_operations', 0)
            failed_ops = operations_summary.get('failed_operations', 0)
            logger.info(f"Operations: {successful_ops} successful, {failed_ops} failed")
        
        # System improvements
        improvements = results.get('system_improvements', {})
        if improvements:
            logger.info("System Improvements:")
            for key, value in improvements.items():
                if value and value != 0:
                    logger.info(f"  - {key.replace('_', ' ').title()}: {value}")
        
        # Quality assessment
        quality = results.get('quality_assessment', {})
        if quality:
            overall_health = quality.get('overall_health_score', 0)
            logger.info(f"Overall System Health Score: {overall_health:.2f}")
            
            alerts_count = quality.get('alerts_generated', 0)
            if alerts_count > 0:
                logger.warning(f"Quality Alerts Generated: {alerts_count}")
        
        # Alerts and recommendations
        alerts_recs = results.get('alerts_and_recommendations', {})
        if alerts_recs:
            total_alerts = alerts_recs.get('total_alerts', 0)
            total_recs = alerts_recs.get('total_recommendations', 0)
            
            if total_alerts > 0:
                logger.warning(f"Total Alerts: {total_alerts}")
                
                # Show high priority alerts
                high_priority = alerts_recs.get('high_priority_alerts', 0)
                if high_priority > 0:
                    logger.warning(f"High Priority Alerts: {high_priority}")
            
            if total_recs > 0:
                logger.info(f"Recommendations Generated: {total_recs}")
        
        # Show key achievements
        stage_summary = results.get('stage_summary', {})
        achievements = stage_summary.get('key_achievements', [])
        if achievements:
            logger.info("Key Achievements:")
            for achievement in achievements:
                logger.info(f"  ✓ {achievement}")
        
        # Show issues if any
        issues = stage_summary.get('issues_detected', [])
        if issues:
            logger.warning("Issues Detected:")
            for issue in issues:
                logger.warning(f"  ⚠ {issue}")
        
        # Show next steps
        next_steps = stage_summary.get('next_steps', [])
        if next_steps:
            logger.info("Next Steps:")
            for step in next_steps:
                logger.info(f"  → {step}")
        
        logger.info("=" * 80)
        
        if status == 'completed':
            logger.info("✅ DATA ARCHITECTURE IMPROVEMENTS COMPLETED SUCCESSFULLY")
            return 0
        else:
            logger.error("❌ DATA ARCHITECTURE IMPROVEMENTS FAILED")
            if 'error' in results:
                logger.error(f"Error: {results['error']}")
            return 1
            
    except Exception as e:
        logger.error(f"Critical error in data architecture stage: {e}")
        return 1


async def main():
    """Main function for command line execution."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run Data Architecture Improvements Stage',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python run_data_architecture_stage.py
    python run_data_architecture_stage.py --config custom_config.json
    python run_data_architecture_stage.py --input previous_stage_results.json
        """
    )
    
    parser.add_argument(
        '--config',
        help='Path to data architecture configuration file',
        default='config/data_architecture_config.json'
    )
    
    parser.add_argument(
        '--input',
        help='Input file from previous pipeline stage (optional)',
        default=None
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Run the stage
    exit_code = await run_data_architecture_stage()
    sys.exit(exit_code)


if __name__ == '__main__':
    asyncio.run(main())
