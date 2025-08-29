#!/usr/bin/env python3
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
                    output_lines = result.stdout.split('\n')
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
        
        print(f"\n📈 PERFORMANCE TRACKING SUMMARY")
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
            print("\n🚀 Daily performance tracking completed!")
        else:
            print("\n❌ Daily performance tracking failed!")
            return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
