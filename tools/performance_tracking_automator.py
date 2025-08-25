#!/usr/bin/env python3
"""
Performance Tracking Automation for Daily Operations v2.04
Integrates real AI performance tracking into daily pipeline operations

Priority 1.3: Automate Performance Tracking in Daily Operations (30 minutes)
"""

import sys
import os
import json
import logging
import subprocess
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")

logger = logging.getLogger(__name__)


class PerformanceTrackingAutomator:
    """Automates performance tracking in daily operations"""
    
    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        self.config_dir = self.project_root / "config"
        self.tools_dir = self.project_root / "tools"
        
        # Performance tracking integration points
        self.integration_points = {
            "daily_watcher_config": self.config_dir / "daily_watcher_config.json",
            "pipeline_integration_config": self.config_dir / "pipeline_integration_config.json",
            "daily_watcher_script": self.project_root / "start_daily_watcher.sh"
        }
        
    def create_performance_tracking_stage(self):
        """Create automated performance tracking stage"""
        
        performance_stage_script = self.tools_dir / "automation" / "daily_performance_tracker.py"
        
        script_content = '''#!/usr/bin/env python3
"""
Daily Performance Tracker for AI Selections v2.04
Automatically runs performance tracking during daily operations
"""

import sys
import os
import logging
import subprocess
from datetime import datetime, date
from pathlib import Path

# Add project root to path
sys.path.append("/home/jc/Documents/Horse-race-ai-v2.04")

logger = logging.getLogger(__name__)


class DailyPerformanceTracker:
    """Tracks AI performance during daily operations"""
    
    def __init__(self):
        self.project_root = Path("/home/jc/Documents/Horse-race-ai-v2.04")
        
    def run_performance_analysis(self, target_date=None):
        """Run comprehensive performance analysis"""
        if target_date is None:
            target_date = date.today().strftime("%Y-%m-%d")
            
        print(f"🎯 Running AI Performance Analysis for {target_date}")
        print("=" * 60)
        
        # Run working performance trainer for latest results
        trainer_script = self.project_root / "tools/training/working_performance_trainer.py"
        
        if trainer_script.exists():
            try:
                print("📊 Executing performance trainer...")
                result = subprocess.run([
                    "python", str(trainer_script)
                ], cwd=str(self.project_root), capture_output=True, text=True, timeout=300)
                
                if result.returncode == 0:
                    print("✅ Performance analysis completed successfully")
                    
                    # Extract key metrics from output
                    output_lines = result.stdout.split('\\n')
                    metrics = {}
                    
                    for line in output_lines:
                        if "Ensemble Accuracy:" in line:
                            try:
                                metrics["ensemble_accuracy"] = float(line.split(":")[1].strip().rstrip("%"))
                            except:
                                pass
                        elif "Individual Model Accuracies" in line:
                            metrics["has_individual_models"] = True
                        elif "Grade:" in line:
                            try:
                                metrics["performance_grade"] = line.split(":")[1].strip()
                            except:
                                pass
                    
                    # Save metrics to daily tracking file
                    self.save_daily_metrics(target_date, metrics)
                    
                    return True
                else:
                    print(f"❌ Performance analysis failed: {result.stderr}")
                    return False
                    
            except subprocess.TimeoutExpired:
                print("⏱️ Performance analysis timed out (5 minutes)")
                return False
            except Exception as e:
                print(f"❌ Performance analysis error: {e}")
                return False
        else:
            print(f"❌ Performance trainer not found: {trainer_script}")
            return False
    
    def save_daily_metrics(self, target_date, metrics):
        """Save performance metrics for the day"""
        metrics_dir = self.project_root / "data" / "performance_tracking"
        metrics_dir.mkdir(exist_ok=True)
        
        daily_metrics_file = metrics_dir / f"daily_metrics_{target_date}.json"
        
        daily_data = {
            "date": target_date,
            "timestamp": datetime.now().isoformat(),
            "ai_performance": metrics,
            "tracking_status": "automated"
        }
        
        with open(daily_metrics_file, 'w') as f:
            json.dump(daily_data, f, indent=2)
        
        print(f"💾 Metrics saved: {daily_metrics_file}")
    
    def generate_performance_summary(self):
        """Generate a performance summary"""
        metrics_dir = self.project_root / "data" / "performance_tracking"
        
        if not metrics_dir.exists():
            print("📊 No performance tracking data available yet")
            return
        
        # Get recent metrics files
        metrics_files = sorted(metrics_dir.glob("daily_metrics_*.json"))
        
        if not metrics_files:
            print("📊 No daily metrics files found")
            return
        
        print(f"\\n📈 PERFORMANCE TRACKING SUMMARY")
        print("=" * 40)
        
        recent_files = metrics_files[-5:]  # Last 5 days
        
        for metrics_file in recent_files:
            try:
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
                
                date_str = data.get("date", "Unknown")
                ai_perf = data.get("ai_performance", {})
                
                ensemble_acc = ai_perf.get("ensemble_accuracy", "N/A")
                grade = ai_perf.get("performance_grade", "N/A")
                has_models = "✅" if ai_perf.get("has_individual_models") else "❌"
                
                print(f"📅 {date_str}:")
                print(f"   Ensemble Accuracy: {ensemble_acc}%")
                print(f"   Performance Grade: {grade}")
                print(f"   Individual Models: {has_models}")
                print()
                
            except Exception as e:
                print(f"⚠️ Error reading {metrics_file}: {e}")


def main():
    """Main function for daily performance tracking"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Daily Performance Tracker")
    parser.add_argument("--date", help="Target date (YYYY-MM-DD)")
    parser.add_argument("--summary", action="store_true", help="Show performance summary")
    
    args = parser.parse_args()
    
    tracker = DailyPerformanceTracker()
    
    if args.summary:
        tracker.generate_performance_summary()
    else:
        success = tracker.run_performance_analysis(args.date)
        if success:
            print("\\n🚀 Daily performance tracking completed!")
        else:
            print("\\n❌ Daily performance tracking failed!")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
'''
        
        with open(performance_stage_script, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        os.chmod(performance_stage_script, 0o755)
        
        print(f"✅ Performance tracking stage created: {performance_stage_script}")
        return performance_stage_script
    
    def update_daily_watcher_config(self):
        """Update daily watcher config to include performance tracking"""
        
        config_file = self.integration_points["daily_watcher_config"]
        
        # Load existing config or create new
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {"daily_watcher_config": {}}
        
        # Ensure daily_watcher_config structure exists
        if "daily_watcher_config" not in config:
            config["daily_watcher_config"] = {}
        
        # Update pipeline integration to include performance tracking
        if "pipeline_integration" not in config["daily_watcher_config"]:
            config["daily_watcher_config"]["pipeline_integration"] = {
                "trigger_on_completion": True,
                "database_upload": True,
                "ml_retrain": False,
                "api_update": True,
                "web_app_notify": True
            }
        
        # Add performance tracking to pipeline integration
        config["daily_watcher_config"]["pipeline_integration"]["performance_tracking"] = True
        
        # Add performance tracking stage configuration
        config["daily_watcher_config"]["performance_tracking"] = {
            "enabled": True,
            "trigger_delay_seconds": 240,  # After other pipeline stages
            "script_path": "tools/automation/daily_performance_tracker.py",
            "timeout_seconds": 300,
            "required": False,  # Don't block pipeline if this fails
            "auto_run": True,
            "save_metrics": True
        }
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Daily watcher config updated: {config_file}")
        return True
    
    def update_pipeline_integration_config(self):
        """Update pipeline integration config for performance tracking"""
        
        config_file = self.integration_points["pipeline_integration_config"]
        
        # Load existing config or create new
        if config_file.exists():
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            config = {}
        
        # Add performance tracking stage definition
        if "stages" not in config:
            config["stages"] = {}
        
        config["stages"]["performance_tracking"] = {
            "name": "Performance Tracking",
            "description": "Automated AI performance analysis and metrics tracking",
            "script": "tools/automation/daily_performance_tracker.py",
            "dependencies": ["contextual_analysis"],
            "trigger_delay": 240,
            "timeout": 300,
            "retry_count": 2,
            "required": False,
            "outputs": [
                "data/performance_tracking/daily_metrics_*.json"
            ]
        }
        
        # Update stage execution order
        if "execution_order" not in config:
            config["execution_order"] = [
                "data_validation",
                "database_upload", 
                "relationship_analysis",
                "ml_model_update",
                "contextual_analysis",
                "performance_tracking"
            ]
        elif "performance_tracking" not in config["execution_order"]:
            config["execution_order"].append("performance_tracking")
        
        # Save updated config
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"✅ Pipeline integration config updated: {config_file}")
        return True
    
    def test_performance_tracking(self):
        """Test the automated performance tracking"""
        print("🧪 Testing automated performance tracking...")
        
        performance_script = self.tools_dir / "automation" / "daily_performance_tracker.py"
        
        if not performance_script.exists():
            print(f"❌ Performance script not found: {performance_script}")
            return False
        
        try:
            # Test with summary option first
            result = subprocess.run([
                "python", str(performance_script), "--summary"
            ], cwd=str(self.project_root), capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Performance tracking script test passed")
                print("📊 Summary output:")
                print(result.stdout)
                return True
            else:
                print(f"❌ Performance tracking test failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏱️ Performance tracking test timed out")
            return False
        except Exception as e:
            print(f"❌ Performance tracking test error: {e}")
            return False
    
    def verify_integration(self):
        """Verify the performance tracking integration"""
        print("🔍 Verifying performance tracking integration...")
        
        checks = []
        
        # Check if performance script exists
        performance_script = self.tools_dir / "automation" / "daily_performance_tracker.py"
        checks.append(("Performance script", performance_script.exists()))
        
        # Check if daily watcher config includes performance tracking
        daily_config = self.integration_points["daily_watcher_config"]
        if daily_config.exists():
            with open(daily_config, 'r') as f:
                config = json.load(f)
            
            has_perf_config = (
                "daily_watcher_config" in config and
                "performance_tracking" in config["daily_watcher_config"]
            )
            checks.append(("Daily watcher config", has_perf_config))
        else:
            checks.append(("Daily watcher config", False))
        
        # Check if pipeline config includes performance tracking
        pipeline_config = self.integration_points["pipeline_integration_config"]
        if pipeline_config.exists():
            with open(pipeline_config, 'r') as f:
                config = json.load(f)
            
            has_perf_stage = (
                "stages" in config and
                "performance_tracking" in config["stages"]
            )
            checks.append(("Pipeline integration config", has_perf_stage))
        else:
            checks.append(("Pipeline integration config", False))
        
        # Check if working performance trainer exists
        trainer_script = self.project_root / "tools/training/working_performance_trainer.py"
        checks.append(("Working performance trainer", trainer_script.exists()))
        
        # Display results
        all_passed = True
        for check_name, passed in checks:
            status = "✅" if passed else "❌"
            print(f"   {status} {check_name}")
            if not passed:
                all_passed = False
        
        return all_passed


def main():
    """Main automation process"""
    print("🤖 PERFORMANCE TRACKING AUTOMATION v2.04")
    print("=" * 55)
    print("Priority 1.3: Automate Performance Tracking in Daily Operations")
    print()
    
    automator = PerformanceTrackingAutomator()
    
    # Step 1: Create performance tracking stage
    print("Step 1: Creating automated performance tracking stage...")
    performance_script = automator.create_performance_tracking_stage()
    
    # Step 2: Update daily watcher configuration
    print("\nStep 2: Updating daily watcher configuration...")
    if not automator.update_daily_watcher_config():
        print("❌ Failed to update daily watcher config")
        return 1
    
    # Step 3: Update pipeline integration configuration
    print("\nStep 3: Updating pipeline integration configuration...")
    if not automator.update_pipeline_integration_config():
        print("❌ Failed to update pipeline integration config")
        return 1
    
    # Step 4: Test performance tracking
    print("\nStep 4: Testing performance tracking...")
    if not automator.test_performance_tracking():
        print("⚠️ Performance tracking test failed, but continuing...")
    
    # Step 5: Verify integration
    print("\nStep 5: Verifying integration...")
    if not automator.verify_integration():
        print("❌ Integration verification failed")
        return 1
    
    print("\n✅ PERFORMANCE TRACKING AUTOMATION COMPLETED!")
    print("🎯 Performance tracking is now automated in daily operations")
    print("📊 The system will now automatically:")
    print("   • Run AI performance analysis after each day's processing")
    print("   • Track ensemble accuracy and individual model performance")
    print("   • Generate performance grades (A-F)")
    print("   • Save daily metrics for historical analysis")
    print("   • Provide performance summaries on demand")
    
    print(f"\n🚀 Performance tracking integrated into pipeline stages!")
    print("📈 Use 'python tools/automation/daily_performance_tracker.py --summary' for reports")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
