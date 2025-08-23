#!/usr/bin/env python3
"""
Enhanced Pipeline Integration with Time-Aware ML Training
Horse Racing AI v2.04 - Complete Workflow with ML Optimization

Integrates the time-aware ML training optimizer into the pipeline workflow.
After data upload, automatically triggers intelligent ML training cycles
that respect race time constraints.
"""

import sys
import os
import logging
import subprocess
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from tools.ml_training.time_aware_ml_optimizer import TimeAwareMLOptimizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedPipelineIntegration:
    """
    Enhanced pipeline that integrates time-aware ML training optimization.
    """
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else project_root
        self.ml_optimizer = TimeAwareMLOptimizer(base_path=str(self.base_path))
        
        # Pipeline configuration
        self.pipeline_config = {
            "enable_ml_optimization": True,
            "ml_trigger_after_upload": True,
            "skip_ml_if_no_time": True,
            "notification_enabled": True
        }
    
    def check_data_freshness(self) -> Dict[str, Any]:
        """Check if new data has been uploaded recently."""
        try:
            # Check database for recent uploads
            result = subprocess.run([
                "docker", "exec", "-it", "horse_racing_postgres_clean",
                "psql", "-U", "horse_racing", "-d", "horse_racing_db",
                "-c",
                ("SELECT MAX(updated_at) FROM files "
                 "WHERE updated_at > NOW() - INTERVAL '2 hours';")
            ], capture_output=True, text=True)
            
            data_status = {
                "has_new_data": False,
                "last_update": None,
                "data_tables": {}
            }
            
            if result.returncode == 0:
                # Check for recent data
                output = result.stdout.strip()
                if "rows)" not in output or "0 rows" not in output:
                    data_status["has_new_data"] = True
                
                # Get table counts
                tables_to_check = [
                    "result_races", "jockeys_stats",
                    "trainers_stats", "card_races"
                ]
                for table in tables_to_check:
                    count_result = subprocess.run([
                        "docker", "exec", "-it", "horse_racing_postgres_clean",
                        "psql", "-U", "horse_racing", "-d", "horse_racing_db",
                        "-c", f"SELECT COUNT(*) FROM {table};"
                    ], capture_output=True, text=True)
                    
                    if count_result.returncode == 0:
                        count_lines = count_result.stdout.strip().split('\n')
                        for line in count_lines:
                            if line.strip().isdigit():
                                data_status["data_tables"][table] = int(line.strip())
                                break
            
            return data_status
            
        except Exception as e:
            logger.error(f"Failed to check data freshness: {e}")
            return {"has_new_data": False, "error": str(e)}
    
    def should_trigger_ml_training(self, data_status: Dict[str, Any]) -> bool:
        """Determine if ML training should be triggered."""
        # Check if ML optimization is enabled
        if not self.pipeline_config.get("enable_ml_optimization", True):
            logger.info("ML optimization disabled in configuration")
            return False
        
        # Check if new data is available
        if not data_status.get("has_new_data", False):
            logger.info("No new data available for ML training")
            return False
        
        # Check if we have sufficient data
        total_records = sum(data_status.get("data_tables", {}).values())
        if total_records < 1000:  # Minimum data threshold
            logger.info(f"Insufficient data for ML training: {total_records} records")
            return False
        
        # Check time constraints
        available_time = self.ml_optimizer.calculate_available_training_time()
        min_training_time = self.ml_optimizer.training_config.get(
            "minimum_training_time_minutes", 120
        )
        
        if available_time < min_training_time:
            if self.pipeline_config.get("skip_ml_if_no_time", True):
                logger.warning(
                    f"Insufficient time for ML training: "
                    f"{available_time} < {min_training_time} minutes"
                )
                return False
            else:
                logger.info(
                    f"Limited time available but proceeding: "
                    f"{available_time} minutes"
                )
        
        return True
    
    def run_enhanced_pipeline(self) -> Dict[str, Any]:
        """Run the complete enhanced pipeline with ML optimization."""
        pipeline_start = datetime.now()
        
        results = {
            "pipeline_start": pipeline_start,
            "steps_completed": [],
            "ml_training_results": None,
            "total_duration": 0,
            "success": False
        }
        
        logger.info("""
╭─────────────────────────────────────────╮
│      Enhanced Pipeline Starting        │
│                                         │
│  🔄 Data Processing                     │
│  📊 Database Upload                     │
│  🤖 Time-Aware ML Training             │
│  ⚡ Performance Optimization            │
╰─────────────────────────────────────────╯
        """)
        
        try:
            # Step 1: Run standard pipeline (CSV processing + Database upload)
            logger.info("🔄 Step 1: Running standard data pipeline...")
            
            standard_result = subprocess.run([
                "python", "tools/automation/pipeline_automation.py", "--run-pipeline"
            ], cwd=self.base_path, capture_output=True, text=True)
            
            if standard_result.returncode == 0:
                results["steps_completed"].append("data_pipeline")
                logger.info("✅ Data pipeline completed successfully")
            else:
                logger.error(f"❌ Data pipeline failed: {standard_result.stderr}")
                results["error"] = "Data pipeline failed"
                return results
            
            # Step 2: Check data status
            logger.info("📊 Step 2: Checking data status...")
            data_status = self.check_data_freshness()
            results["data_status"] = data_status
            results["steps_completed"].append("data_check")
            
            # Step 3: ML Training Decision
            logger.info("🤖 Step 3: Evaluating ML training requirements...")
            
            if self.should_trigger_ml_training(data_status):
                logger.info("🚀 Triggering time-aware ML training optimization...")
                
                # Run ML optimization
                ml_results = self.ml_optimizer.run_optimization_cycles()
                results["ml_training_results"] = ml_results
                results["steps_completed"].append("ml_training")
                
                if ml_results.get("training_completed", False):
                    logger.info("✅ ML training optimization completed successfully")
                else:
                    logger.warning("⚠️ ML training completed with issues")
            
            else:
                logger.info("⏭️ Skipping ML training (conditions not met)")
                results["ml_training_results"] = {
                    "skipped": True,
                    "reason": "Conditions not met"
                }
                results["steps_completed"].append("ml_training_skipped")
            
            # Step 4: Post-processing and notifications
            logger.info("📧 Step 4: Post-processing and notifications...")
            self._send_pipeline_completion_notification(results)
            results["steps_completed"].append("notifications")
            
            results["success"] = True
            duration_seconds = (datetime.now() - pipeline_start).total_seconds()
            results["total_duration"] = duration_seconds / 60
            
            logger.info(f"""
╭─────────────────────────────────────────╮
│        Enhanced Pipeline Complete      │
│                                         │
│  ✅ Total Duration: {results['total_duration']:.1f} minutes          │
│  📊 Steps Completed: {len(results['steps_completed'])}                │
│  🤖 ML Training: {'✅' if results.get('ml_training_results', {}).get('training_completed') else '⏭️'}                    │
│                                         │
│  System ready for race predictions!    │
╰─────────────────────────────────────────╯
            """)
            
        except Exception as e:
            logger.error(f"❌ Enhanced pipeline failed: {e}")
            results["error"] = str(e)
            results["total_duration"] = (datetime.now() - pipeline_start).total_seconds() / 60
        
        return results
    
    def _send_pipeline_completion_notification(self, results: Dict[str, Any]):
        """Send notification about pipeline completion."""
        if not self.pipeline_config.get("notification_enabled", True):
            return
        
        try:
            # Prepare notification message
            success = results.get("success", False)
            duration = results.get("total_duration", 0)
            ml_completed = results.get("ml_training_results", {}).get("training_completed", False)
            
            message = f"""
🏇 Horse Racing AI Pipeline Complete

Status: {'✅ Success' if success else '❌ Failed'}
Duration: {duration:.1f} minutes
ML Training: {'✅ Completed' if ml_completed else '⏭️ Skipped'}

Steps: {', '.join(results.get('steps_completed', []))}
            """
            
            # Save notification to file for external pickup
            notification_file = self.base_path / "notifications" / f"pipeline_complete_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            notification_file.parent.mkdir(exist_ok=True)
            
            with open(notification_file, 'w') as f:
                f.write(message)
            
            logger.info("📧 Notification saved")
            
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
    
    def monitor_and_optimize_continuous(self, check_interval_minutes: int = 60):
        """Continuously monitor for new data and optimize ML models."""
        logger.info(f"🔄 Starting continuous monitoring (check every {check_interval_minutes} minutes)")
        
        import time
        
        while True:
            try:
                # Check for new data
                data_status = self.check_data_freshness()
                
                if data_status.get("has_new_data", False):
                    logger.info("🔔 New data detected - triggering enhanced pipeline")
                    self.run_enhanced_pipeline()
                else:
                    logger.info("💤 No new data - continuing monitoring")
                
                # Wait for next check
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("⏹️ Continuous monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in continuous monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying


def main():
    """Main function for enhanced pipeline integration."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhanced Pipeline with ML Optimization")
    parser.add_argument("--base-path", default=None, help="Base project path")
    parser.add_argument("--run-once", action="store_true", help="Run pipeline once and exit")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--check-interval", type=int, default=60, help="Check interval in minutes")
    parser.add_argument("--disable-ml", action="store_true", help="Disable ML optimization")
    
    args = parser.parse_args()
    
    # Initialize enhanced pipeline
    pipeline = EnhancedPipelineIntegration(base_path=args.base_path)
    
    # Configure options
    if args.disable_ml:
        pipeline.pipeline_config["enable_ml_optimization"] = False
    
    try:
        if args.continuous:
            # Run continuous monitoring
            pipeline.monitor_and_optimize_continuous(check_interval_minutes=args.check_interval)
        else:
            # Run once
            results = pipeline.run_enhanced_pipeline()
            
            # Exit with appropriate code
            if results.get("success", False):
                return 0
            else:
                return 1
    
    except KeyboardInterrupt:
        logger.info("🛑 Pipeline stopped by user")
        return 0
    except Exception as e:
        logger.error(f"❌ Pipeline failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
